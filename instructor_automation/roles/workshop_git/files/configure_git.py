#!/usr/bin/env python3
"""Configure containers and create missing Gitea users without printing passwords."""
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def command(args):
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode:
        # Docker/Gitea errors can repeat arguments containing passwords.
        raise RuntimeError('A container command failed. Inspect container logs on the instance.')
    return result.stdout


def ensure_container(name, image, args, force=False):
    digest = hashlib.sha256(json.dumps([image, args], sort_keys=True).encode()).hexdigest()
    result = subprocess.run(['docker', 'inspect', name], text=True, capture_output=True, check=False)
    current = json.loads(result.stdout)[0] if result.returncode == 0 else None
    if current and current['Config']['Labels'].get('workshop.config') == digest and not force:
        if not current['State']['Running']:
            command(['docker', 'start', name])
            return True
        return False
    command(['docker', 'pull', image])
    if current:
        command(['docker', 'rm', '-f', name])
    command(['docker', 'run', '-d', '--name', name, '--restart', 'unless-stopped',
             '--label', 'workshop.config=' + digest] + args + [image])
    return True


def wait_for_gitea():
    for _ in range(120):
        try:
            with urllib.request.urlopen('http://127.0.0.1:3000/api/healthz', timeout=5) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(5)
    raise RuntimeError('Gitea did not become healthy before the timeout.')


def usernames_from_list(output):
    users = set()
    for line in output.splitlines():
        columns = line.split()
        if len(columns) >= 2 and columns[0].isdigit():
            users.add(columns[1].lower())
    return users


def create_missing_users(users, existing, run=command):
    created = []
    base = ['docker', 'exec', '--user', 'git', 'workshop-gitea', 'gitea',
            '--config', '/data/gitea/conf/app.ini', 'admin', 'user', 'create']
    for user in users:
        if user['username'].lower() in existing:
            continue
        args = base + ['--username', user['username'], '--email', user['email'],
                       '--password', user['password'],
                       '--must-change-password=' + str(user['must_change_password']).lower()]
        if user['admin']:
            args.append('--admin')
        run(args)
        created.append(user['username'])
    return created


def fetch_students(client, prefix, student_ids):
    users = []
    for offset in range(0, len(student_ids), 10):
        names = [prefix + '/' + student for student in student_ids[offset:offset + 10]]
        result = client.get_parameters(Names=names, WithDecryption=True)
        if result.get('InvalidParameters') or len(result['Parameters']) != len(names):
            raise RuntimeError('Student credentials are missing from Parameter Store.')
        expected = {prefix + '/' + student: student for student in student_ids[offset:offset + 10]}
        for parameter in result['Parameters']:
            user = json.loads(parameter['Value'])
            if user['username'] != expected[parameter['Name']]:
                raise RuntimeError('Student credential username does not match its parameter name.')
            users.append(user)
    return users


def configure(config):
    import boto3
    root = Path('/opt/workshop-git')
    data = root / 'gitea'
    data.mkdir(exist_ok=True)
    os.chown(data, 1000, 1000)
    args = ['-p', '127.0.0.1:3000:3000', '-v', str(data) + ':/data',
            '-e', 'USER_UID=1000', '-e', 'USER_GID=1000',
            '-e', 'GITEA__database__DB_TYPE=sqlite3', '-e', 'GITEA__database__PATH=/data/gitea/gitea.db',
            '-e', 'GITEA__server__ROOT_URL=https://' + config['fqdn'] + '/',
            '-e', 'GITEA__server__DOMAIN=' + config['fqdn'],
            '-e', 'GITEA__server__DISABLE_SSH=true', '-e', 'GITEA__security__INSTALL_LOCK=true',
            '-e', 'GITEA__service__DISABLE_REGISTRATION=true', '-e', 'GITEA__service__REQUIRE_SIGNIN_VIEW=true']
    changed = ensure_container('workshop-gitea', config['gitea_image'], args)
    wait_for_gitea()
    users = fetch_students(boto3.client('ssm', region_name=config['region']),
                           config['parameter_prefix'], config['student_ids'])
    output = command(['docker', 'exec', '--user', 'git', 'workshop-gitea', 'gitea',
                      '--config', '/data/gitea/conf/app.ini', 'admin', 'user', 'list'])
    created = create_missing_users(users, usernames_from_list(output))
    caddyfile = root / 'Caddyfile'
    content = config['fqdn'] + ' {\n    reverse_proxy 127.0.0.1:3000\n}\n'
    config_changed = not caddyfile.exists() or caddyfile.read_text() != content
    if config_changed:
        caddyfile.write_text(content)
        os.chmod(caddyfile, 0o644)
    caddy_changed = ensure_container('workshop-caddy', config['caddy_image'], [
        '--network', 'host', '-v', str(caddyfile) + ':/etc/caddy/Caddyfile:ro',
        '-v', 'workshop-caddy-data:/data', '-v', 'workshop-caddy-config:/config'], force=config_changed)
    return {'changed': bool(changed or created or caddy_changed), 'created_users': created}


if __name__ == '__main__':
    try:
        print(json.dumps(configure(json.loads(sys.argv[1]))))
    except Exception as exc:
        # Never include command arguments, fetched credentials, or exception payloads.
        print('Git setup failed: ' + type(exc).__name__, file=sys.stderr)
        sys.exit(1)

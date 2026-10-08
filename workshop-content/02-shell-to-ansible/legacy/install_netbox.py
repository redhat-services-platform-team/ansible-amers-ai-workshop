#!/usr/bin/env python3
# COMPANY INFRASTRUCTURE DEPARTMENT: DO NOT LOSE THIS FILE.
# Maintainers 01-50, 2018-2026. Handover document: "ask whoever wrote it."
# Whoever wrote it has left. Whoever replaced them has also left.
# The CMDB, three dashboards, and somebody's promotion depend on this script.
# Finance calls it a strategic platform. Git history calls it final_final_v7.py.
# If you understand the whole thing, please update the runbook. We cannot find it.
# Workshop fiction above; the installation code below is copied without changes.
"""Install a standalone NetBox stack on CentOS Stream 10 (Python stdlib only).

Usage: sudo python3 install_netbox.py --env-file .env
Secrets and the selected release persist in /etc/netbox-installer/state.json.
This is a fresh-install/reconciliation tool, not a NetBox version upgrader.
"""

import argparse
import fcntl
import json
import os
import pwd
import re
import secrets
import shlex
import shutil
import ssl
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

STATE = Path('/etc/netbox-installer/state.json')
ROOT = Path('/opt/netbox')
REDACT = []
DEFAULTS = {
    'NETBOX_VERSION': 'latest',
    'NETBOX_HOSTNAME': 'localhost',
    'NETBOX_ALLOWED_HOSTS': '*',
    'NETBOX_ADMIN_USER': 'admin',
    'NETBOX_ADMIN_EMAIL': 'admin@localhost',
    'NETBOX_ADMIN_PASSWORD': '',
    'NETBOX_DB_PASSWORD': '',
    'NETBOX_SECRET_KEY': '',
    'NETBOX_API_TOKEN_PEPPER': '',
    'NETBOX_TLS_MODE': 'off',
    'NETBOX_TLS_CERT': '',
    'NETBOX_TLS_KEY': '',
    'NETBOX_GUNICORN_WORKERS': '3',
    'NETBOX_TIME_ZONE': 'UTC',
    'NETBOX_OPEN_FIREWALL': 'true',
}


# 2019, maintainer 07: logs are helpful until they contain the database password.
# 2024, maintainer 41: yes, even the error about hiding secrets must hide secrets.
def say(message):
    for value in REDACT:
        message = message.replace(value, '<redacted>')
    print(message, flush=True)


# 2020, maintainer 12: no shell=True. We have already funded that incident.
# 2023, maintainer 33: stderr is stdout now. The monitoring dashboard has opinions.
def run(args, *, data=None, env=None, capture=False):
    """Never invoke a shell; redact subprocess output and avoid secret argv."""
    result = subprocess.run(args, input=data, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, env=env, check=False)
    if result.returncode:
        say(result.stdout)
        raise RuntimeError(f'{args[0]} failed (exit {result.returncode})')
    if not capture and result.stdout.strip():
        say(result.stdout.rstrip())
    return result.stdout


# 2018, maintainer 02: write a temporary file, then swap it in atomically.
# 2022, maintainer 26: partial configuration files are how we met the night shift.
def write(path, text, mode=0o644, group=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        os.fchmod(fd, mode)
        if group:
            os.fchown(fd, 0, pwd.getpwnam(group).pw_gid)
        with os.fdopen(fd, 'w') as stream:
            stream.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


# 2019, maintainer 09: .env is a file format, not an invitation to execute Bash.
# 2025, maintainer 46: environment wins over the file. The wiki says the opposite.
# The wiki owner is on leave. Since 2021.
def load_env(path):
    config = dict(DEFAULTS)
    if path:
        for n, line in enumerate(Path(path).read_text().splitlines(), 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            line = line.removeprefix('export ')
            key, sep, value = line.partition('=')
            key = key.strip()
            if not sep or key not in DEFAULTS:
                raise ValueError(f'Unknown or invalid setting on .env line {n}')
            # Literal values only: no shell execution or variable interpolation.
            values = shlex.split(value, comments=True)
            if len(values) > 1:
                raise ValueError(f'Quote values containing spaces on .env line {n}')
            config[key] = values[0] if values else ''
    for key in DEFAULTS:
        if key in os.environ:
            config[key] = os.environ[key]
    for key in ('NETBOX_ADMIN_PASSWORD', 'NETBOX_DB_PASSWORD', 'NETBOX_SECRET_KEY',
                'NETBOX_API_TOKEN_PEPPER'):
        if config[key]:
            REDACT.append(config[key])
    return config


# 2021, maintainer 19: validate before changing the machine. A novel proposal.
# 2024, maintainer 39: every check below has a ticket. Most tickets say "urgent".
def validate(c):
    if not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9.\-]*[a-zA-Z0-9])?', c['NETBOX_HOSTNAME']):
        raise ValueError('NETBOX_HOSTNAME must be a hostname or IPv4 address without a port')
    hosts = [x.strip() for x in c['NETBOX_ALLOWED_HOSTS'].split(',') if x.strip()]
    if not hosts or any(not re.fullmatch(r'[a-zA-Z0-9.*:\-\[\]]+', x) for x in hosts):
        raise ValueError('NETBOX_ALLOWED_HOSTS must be comma-separated hosts/IPs or *')
    if '*' not in hosts and c['NETBOX_HOSTNAME'] not in hosts:
        raise ValueError('NETBOX_ALLOWED_HOSTS must include NETBOX_HOSTNAME')
    if c['NETBOX_TLS_MODE'] not in ('off', 'self-signed', 'provided'):
        raise ValueError('NETBOX_TLS_MODE must be off, self-signed, or provided')
    if c['NETBOX_TLS_MODE'] == 'provided':
        for key in ('NETBOX_TLS_CERT', 'NETBOX_TLS_KEY'):
            if not Path(c[key]).is_file():
                raise ValueError(f'{key} must identify an existing file')
    if c['NETBOX_OPEN_FIREWALL'] not in ('true', 'false'):
        raise ValueError('NETBOX_OPEN_FIREWALL must be true or false')
    if not c['NETBOX_GUNICORN_WORKERS'].isdigit() or not 1 <= int(c['NETBOX_GUNICORN_WORKERS']) <= 32:
        raise ValueError('NETBOX_GUNICORN_WORKERS must be between 1 and 32')
    if not c['NETBOX_ADMIN_USER'] or not c['NETBOX_ADMIN_EMAIL']:
        raise ValueError('Admin username and email cannot be blank')
    if not (Path('/usr/share/zoneinfo') / c['NETBOX_TIME_ZONE']).is_file() or '..' in c['NETBOX_TIME_ZONE']:
        raise ValueError('NETBOX_TIME_ZONE must be a valid IANA time zone')
    version = c['NETBOX_VERSION'].removeprefix('v')
    if version != 'latest' and not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('NETBOX_VERSION must be latest or a stable X.Y.Z release')
    for key in ('NETBOX_ADMIN_PASSWORD', 'NETBOX_DB_PASSWORD'):
        if c[key] and len(c[key]) < 12:
            raise ValueError(f'{key} must contain at least 12 characters')
    for key in ('NETBOX_SECRET_KEY', 'NETBOX_API_TOKEN_PEPPER'):
        if c[key] and len(c[key]) < 50:
            raise ValueError(f'{key} must contain at least 50 characters')
    return hosts


# 2020, maintainer 15: the internet is now a deployment dependency.
# 2026, maintainer 50: procurement asked whether we can cache "the internet".
def fetch(url, destination=None):
    req = urllib.request.Request(url, headers={'User-Agent': 'netbox-stream10-installer'})
    with urllib.request.urlopen(req, timeout=120) as response:
        if destination:
            with open(destination, 'wb') as stream:
                shutil.copyfileobj(response, stream)
        else:
            return response.geturl()


# 2022, maintainer 28: remember the release and secrets between runs.
# 2023, maintainer 35: "latest" means latest once, then the version we married.
# Secret rotation is a separate change. Last time it was a surprise team exercise.
def prepare_state(c):
    old = json.loads(STATE.read_text()) if STATE.exists() else {}
    if ROOT.exists() and not old:
        raise RuntimeError('/opt/netbox already exists and is not managed by this installer')
    version = c['NETBOX_VERSION'].removeprefix('v')
    if old:
        if version != 'latest' and version != old['version']:
            raise ValueError('Version changes require the official NetBox upgrade procedure')
        version = old['version']
    elif version == 'latest':
        url = fetch('https://github.com/netbox-community/netbox/releases/latest')
        match = re.search(r'/tag/v(\d+\.\d+\.\d+)$', url)
        if not match:
            raise RuntimeError('Unable to resolve latest stable NetBox release')
        version = match[1]
    for key in ('NETBOX_ADMIN_PASSWORD', 'NETBOX_DB_PASSWORD', 'NETBOX_SECRET_KEY',
                'NETBOX_API_TOKEN_PEPPER'):
        value = c[key] or old.get(key) or secrets.token_urlsafe(48)
        if old.get(key) and value != old[key]:
            raise ValueError(f'{key} differs from saved state; rotate it separately')
        c[key] = value
        REDACT.append(value)
    STATE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(STATE.parent, 0o700)
    state = {'version': version, **{k: c[k] for k in c if k.endswith(('PASSWORD', 'SECRET_KEY', 'PEPPER'))}}
    write(STATE, json.dumps(state, indent=2) + '\n', 0o600)
    return version


# 2018, maintainer 03: just a few packages. The list has developed ambitions.
# 2025, maintainer 48: it says Valkey here and REDIS later. Both are intentional.
def install_packages():
    run(['dnf', 'install', '-y', 'python3', 'python3-pip', 'python3-devel',
         'gcc', 'make', 'libxml2-devel', 'libxslt-devel', 'libffi-devel',
         'openssl-devel', 'zlib-devel', 'libpq-devel', 'postgresql-server',
         'postgresql-contrib', 'valkey', 'nginx', 'openssl',
         'policycoreutils-python-utils', 'firewalld'])
    run(['systemctl', 'enable', '--now', 'valkey'])
    if run(['valkey-cli', 'ping'], capture=True).strip() != 'PONG':
        raise RuntimeError('Valkey connectivity failed')


# 2019, maintainer 11: the database is local because the architecture board was busy.
# 2021, maintainer 21: do not reorder the authentication rules for aesthetics.
# 2024, maintainer 42: the SQL below keeps the company alive. Please use indoor voices.
def database(c):
    if not Path('/var/lib/pgsql/data/PG_VERSION').exists():
        run(['postgresql-setup', '--initdb'])
    hba = Path('/var/lib/pgsql/data/pg_hba.conf')
    text = hba.read_text()
    marker = '# Managed by netbox-python-install'
    if marker not in text:
        write(hba, f'{marker}\nhost netbox netbox 127.0.0.1/32 scram-sha-256\n'
              f'host netbox netbox ::1/128 scram-sha-256\n' + text, 0o600)
        pg = pwd.getpwnam('postgres')
        os.chown(hba, pg.pw_uid, pg.pw_gid)
    run(['systemctl', 'enable', '--now', 'postgresql'])
    run(['systemctl', 'reload', 'postgresql'])
    def sql(statement):
        return run(['runuser', '-u', 'postgres', '--', 'psql', '-X', '-v',
                    'ON_ERROR_STOP=1', '-d', 'postgres'], data=statement, capture=True)
    # Maintainer 24: the apostrophe is allowed to be a password character, not SQL.
    password = c['NETBOX_DB_PASSWORD'].replace("'", "''")
    sql("DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='netbox') "
        "THEN CREATE ROLE netbox LOGIN; END IF; END $$;\n"
        f"SET password_encryption='scram-sha-256';\nALTER ROLE netbox PASSWORD '{password}';\n")
    exists = sql("SELECT 1 FROM pg_database WHERE datname='netbox';\n")
    if '(0 rows)' in exists:
        sql('CREATE DATABASE netbox OWNER netbox ENCODING \'UTF8\' TEMPLATE template0;\n')
    sql('ALTER DATABASE netbox OWNER TO netbox;\n')
    run(['runuser', '-u', 'postgres', '--', 'psql', '-X', '-v', 'ON_ERROR_STOP=1',
         '-d', 'netbox'], data='GRANT CREATE ON SCHEMA public TO netbox;\n', capture=True)
    env = {**os.environ, 'PGPASSWORD': c['NETBOX_DB_PASSWORD']}
    run(['psql', '-X', '-h', '127.0.0.1', '-U', 'netbox', '-d', 'netbox',
         '-v', 'ON_ERROR_STOP=1', '-c', 'SELECT 1'], env=env, capture=True)


# 2020, maintainer 16: download a release, create a user, configure everything.
# 2022, maintainer 30: this function became a department while nobody was looking.
# 2025, maintainer 47: upgrade.sh also handles fresh installs. The name won the meeting.
def application(c, hosts, version):
    release = Path(f'/opt/netbox-{version}')
    if not release.exists():
        with tempfile.TemporaryDirectory(prefix='netbox-download-') as tmp:
            archive = Path(tmp) / 'netbox.tar.gz'
            say(f'Downloading NetBox {version}')
            fetch(f'https://github.com/netbox-community/netbox/archive/refs/tags/v{version}.tar.gz', archive)
            with tarfile.open(archive) as tar:
                tar.extractall(tmp, filter='data')
            source = Path(tmp) / f'netbox-{version}'
            if not (source / 'upgrade.sh').is_file():
                raise RuntimeError('Release archive does not contain upgrade.sh')
            shutil.move(source, release)
    if not ROOT.exists():
        ROOT.symlink_to(release)
    if ROOT.resolve() != release:
        raise RuntimeError('/opt/netbox points to an unexpected release')
    try:
        pwd.getpwnam('netbox')
    except KeyError:
        run(['useradd', '--system', '--user-group', '--home-dir', '/opt/netbox',
             '--shell', '/sbin/nologin', 'netbox'])
    for subdir in ('media', 'reports', 'scripts'):
        path = ROOT / 'netbox' / subdir
        path.mkdir(exist_ok=True)
        run(['chown', '-R', 'netbox:netbox', str(path)])
    https = c['NETBOX_TLS_MODE'] != 'off'
    config = {
        'ALLOWED_HOSTS': list(dict.fromkeys(hosts + ['localhost', '127.0.0.1'])),
        'DATABASES': {'default': {'NAME': 'netbox', 'USER': 'netbox',
                                 'PASSWORD': c['NETBOX_DB_PASSWORD'], 'HOST': '127.0.0.1',
                                 'PORT': 5432, 'CONN_MAX_AGE': 300}},
        'REDIS': {name: {'HOST': '127.0.0.1', 'PORT': 6379, 'PASSWORD': '',
                         'DATABASE': index, 'SSL': False}
                  for index, name in enumerate(('tasks', 'caching'))},
        'SECRET_KEY': c['NETBOX_SECRET_KEY'],
        'API_TOKEN_PEPPERS': {1: c['NETBOX_API_TOKEN_PEPPER']},
        'TIME_ZONE': c['NETBOX_TIME_ZONE'],
        'CSRF_TRUSTED_ORIGINS': [f'{"https" if https else "http"}://{c["NETBOX_HOSTNAME"]}'],
        'SESSION_COOKIE_SECURE': https,
        'CSRF_COOKIE_SECURE': https,
    }
    write(ROOT / 'netbox/netbox/configuration.py',
          '# Managed by netbox-python-install\n' +
          '\n'.join(f'{key} = {value!r}' for key, value in config.items()) + '\n',
          0o640, 'netbox')
    if Path('/etc/systemd/system/netbox.service').exists():
        run(['systemctl', 'stop', 'netbox', 'netbox-rq'], capture=True)
    env = {**os.environ, 'PYTHON': '/usr/bin/python3'}
    # Do not propagate installer secrets to pip subprocesses.
    env = {k: v for k, v in env.items() if not k.startswith('NETBOX_')}
    # Maintainer 36: this always runs. Ansible handlers will have questions.
    run([str(ROOT / 'upgrade.sh')], env=env)
    # Archive extraction in /tmp leaves user_tmp_t labels after moving into /opt.
    # Relabel the whole release, including venv executables, before systemd starts.
    run(['restorecon', '-RF', str(release)])
    manage = [str(ROOT / 'venv/bin/python'), str(ROOT / 'netbox/manage.py')]
    admin_code = '''import json, sys
from django.contrib.auth import get_user_model
c = json.loads(sys.stdin.read())
User = get_user_model()
u, created = User.objects.get_or_create(username=c['user'])
if created:
    u.email = c['email']
    u.is_staff = True
    u.is_superuser = True
    u.set_password(c['password'])
    u.save()
elif not (u.is_superuser and u.is_active):
    raise RuntimeError('Existing admin account is not an active superuser')
'''
    run(manage + ['shell', '-c', admin_code],
        data=json.dumps({'user': c['NETBOX_ADMIN_USER'], 'email': c['NETBOX_ADMIN_EMAIL'],
                         'password': c['NETBOX_ADMIN_PASSWORD']}), capture=True)
    run(manage + ['check'])
    write(ROOT / 'gunicorn.py', f"bind = '127.0.0.1:8001'\nworkers = {int(c['NETBOX_GUNICORN_WORKERS'])}\nthreads = 2\ntimeout = 120\n")


# 2021, maintainer 23: two services. No, the second one is not redundant.
# 2024, maintainer 43: the worker does housekeeping too. It has more jobs than I do.
def services():
    for name, command in (
        ('netbox', '/opt/netbox/venv/bin/gunicorn --pythonpath /opt/netbox/netbox --config /opt/netbox/gunicorn.py netbox.wsgi'),
        ('netbox-rq', '/opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py rqworker'),
    ):
        write(f'/etc/systemd/system/{name}.service', f'''[Unit]
Description={name} service
After=network.target postgresql.service valkey.service
Requires=postgresql.service valkey.service

[Service]
Type=simple
User=netbox
Group=netbox
WorkingDirectory=/opt/netbox/netbox
ExecStart={command}
Restart=on-failure
RestartSec=5
PrivateTmp=true
NoNewPrivileges=true
UMask=0027

[Install]
WantedBy=multi-user.target
''')
    run(['systemctl', 'daemon-reload'])
    # Modern NetBox schedules housekeeping system jobs through rqworker itself.
    run(['systemctl', 'enable', '--now', 'netbox', 'netbox-rq'])
    run(['systemctl', 'restart', 'netbox', 'netbox-rq'])


# 2019, maintainer 10: Nginx, certificates, SELinux, firewall. One small web change.
# 2023, maintainer 37: this replaces the default Nginx config on a dedicated host.
# The last person who tried this on a shared server now teaches change management.
def webserver(c):
    mode = c['NETBOX_TLS_MODE']
    tls = ''
    redirect = ''
    if mode != 'off':
        cert = Path('/etc/pki/tls/certs/netbox.crt')
        key = Path('/etc/pki/tls/private/netbox.key')
        if mode == 'provided':
            write(cert, Path(c['NETBOX_TLS_CERT']).read_text())
            write(key, Path(c['NETBOX_TLS_KEY']).read_text(), 0o600)
        elif not cert.exists() or not key.exists():
            host = c['NETBOX_HOSTNAME']
            san = f'IP:{host}' if re.fullmatch(r'\d+\.\d+\.\d+\.\d+', host) else f'DNS:{host}'
            run(['openssl', 'req', '-x509', '-nodes', '-days', '365', '-newkey', 'rsa:2048',
                 '-keyout', str(key), '-out', str(cert), '-subj', f'/CN={host}',
                 '-addext', f'subjectAltName={san},DNS:localhost,IP:127.0.0.1'], capture=True)
            os.chmod(key, 0o600)
        # nginx validates certificate/key pairing before any restart.
        tls = f'    ssl_certificate {cert};\n    ssl_certificate_key {key};\n    ssl_protocols TLSv1.2 TLSv1.3;\n'
        redirect = '''server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    return 301 https://$host$request_uri;
}
'''
    port = '443 ssl' if mode != 'off' else '80'
    # This is a dedicated machine: replace the distro's default welcome server.
    write('/etc/nginx/nginx.conf', '''user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;
include /usr/share/nginx/modules/*.conf;
events { worker_connections 1024; }
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile on;
    include /etc/nginx/conf.d/*.conf;
}
''')
    write('/etc/nginx/conf.d/netbox.conf', redirect + f'''server {{
    listen {port} default_server;
    listen [::]:{port} default_server;
    server_name {c['NETBOX_HOSTNAME']};
{tls}    client_max_body_size 25m;
    location /static/ {{
        alias /opt/netbox/netbox/static/;
    }}
    location / {{
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
''')
    if run(['getenforce'], capture=True).strip() != 'Disabled':
        run(['setsebool', '-P', 'httpd_can_network_connect', 'on'])
        expression = '/opt/netbox-[^/]+/netbox/static(/.*)?'
        current = run(['semanage', 'fcontext', '-l', '-C'], capture=True)
        run(['semanage', 'fcontext', '-m' if expression in current else '-a',
             '-t', 'httpd_sys_content_t', expression])
        run(['restorecon', '-RF', str(ROOT.resolve() / 'netbox/static')])
        if mode != 'off':
            run(['restorecon', '-F', '/etc/pki/tls/certs/netbox.crt',
                 '/etc/pki/tls/private/netbox.key'])
    run(['nginx', '-t'])
    run(['systemctl', 'enable', '--now', 'nginx'])
    run(['systemctl', 'restart', 'nginx'])
    if c['NETBOX_OPEN_FIREWALL'] == 'true':
        run(['systemctl', 'enable', '--now', 'firewalld'])
        for service in (['http', 'https'] if mode != 'off' else ['http']):
            run(['firewall-cmd', '--permanent', f'--add-service={service}'])
        run(['firewall-cmd', '--reload'])


# 2022, maintainer 31: "systemctl succeeded" is not the same as "the app works".
# 2025, maintainer 49: wait for the login page. Coffee is optional; retries are not.
# The local HTTPS probe skips certificate trust checks. Do not call it a TLS audit.
def verify(c):
    units = ('postgresql', 'valkey', 'netbox', 'netbox-rq', 'nginx')
    for name in units:
        run(['systemctl', 'is-enabled', '--quiet', name])
    https = c['NETBOX_TLS_MODE'] != 'off'
    context = ssl._create_unverified_context() if https else None
    url = f'{"https" if https else "http"}://127.0.0.1/login/'
    for attempt in range(60):
        try:
            for name in units:
                run(['systemctl', 'is-active', '--quiet', name])
            req = urllib.request.Request(url, headers={'Host': c['NETBOX_HOSTNAME']})
            with urllib.request.urlopen(req, context=context, timeout=5) as response:
                if response.status == 200 and b'csrfmiddlewaretoken' in response.read():
                    say('Verified: login page responds through Nginx; all services enabled and active.')
                    return
        except (OSError, urllib.error.URLError, RuntimeError):
            pass
        time.sleep(2)
    raise RuntimeError('NetBox login page did not become ready; inspect journalctl -u netbox and nginx logs')


# 2018, maintainer 01: orchestration is easy, just call everything in order.
# 2026, maintainer 50: nobody knows why this exact order works. Read the calls anyway.
# If this script stops working, the spreadsheet becomes our source of truth again.
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, help='Optional .env file; environment variables take precedence')
    args = parser.parse_args()
    c = load_env(args.env_file)
    hosts = validate(c)
    if os.geteuid() != 0:
        raise RuntimeError('Run this installer as root (sudo python3 install_netbox.py --env-file .env)')
    os_release = dict(line.split('=', 1) for line in Path('/etc/os-release').read_text().splitlines() if '=' in line)
    if os_release.get('ID', '').strip('"') != 'centos' or os_release.get('VERSION_ID', '').strip('"') != '10' or 'Stream' not in os_release.get('NAME', ''):
        raise RuntimeError('This installer supports CentOS Stream 10 only')
    # Maintainer 32: two installers at once is not our high-availability strategy.
    with open('/run/netbox-python-install.lock', 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        version = prepare_state(c)
        say(f'Installing/reconciling NetBox {version} on CentOS Stream 10')
        say('Installing OS packages and starting the Redis-compatible Valkey service...')
        install_packages()
        say('Configuring and verifying PostgreSQL...')
        database(c)
        say('Configuring NetBox; dependency installation and migrations may take several minutes...')
        application(c, hosts, version)
        say('Configuring systemd services (the RQ worker also schedules housekeeping)...')
        services()
        say('Configuring Nginx, SELinux, and the firewall...')
        webserver(c)
        verify(c)
    say(f'NetBox ready at {"https" if c["NETBOX_TLS_MODE"] != "off" else "http"}://{c["NETBOX_HOSTNAME"]}/')
    say(f'Administrator: {c["NETBOX_ADMIN_USER"]}. Generated credentials are in {STATE} (root only).')


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as exc:  # noqa: BLE001 - redact all failures
        say(f'Installation failed: {exc}')
        sys.exit(1)


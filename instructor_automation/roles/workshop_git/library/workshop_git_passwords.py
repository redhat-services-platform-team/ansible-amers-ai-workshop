#!/usr/bin/python
"""Keep initial student passwords on the controller across reruns."""
import json
import os
import re
import secrets
import tempfile
from pathlib import Path
from ansible.module_utils.basic import AnsibleModule


def validate_students(students):
    if not students or len({s.lower() for s in students}) != len(students):
        raise ValueError('Student IDs must be nonempty and unique, ignoring case.')
    for student in students:
        if not re.fullmatch(r'[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*', student) or len(student) > 40:
            raise ValueError('Student IDs must be 1-40 letters or digits, with single internal dots, hyphens, or underscores.')
        reserved = {
            'api', 'metrics', 'v2', 'assets', 'attachments', 'avatar', 'avatars', 'repo-avatars',
            'captcha', 'login', 'org', 'repo', 'user', 'explore', 'issues', 'pulls', 'milestones',
            'notifications', 'favicon.ico', 'manifest.json', 'robots.txt', 'sitemap.xml',
            'ssh_info', 'swagger.v1.json', 'openapi3.v1.json', 'ghost', 'gitea-actions',
        }
        if student.lower() in reserved or student.lower().endswith(('.keys', '.gpg', '.rss', '.atom', '.png')):
            raise ValueError('Student ID is reserved by Gitea: ' + student)


def reconcile_passwords(path, students, check_mode=False, required_students=()):
    validate_students(students)
    path = Path(path)
    if path.is_symlink():
        raise ValueError('The password file must not be a symbolic link.')
    existing = json.loads(path.read_text()) if path.exists() else {}
    if not isinstance(existing, dict) or any(not isinstance(value, str) or len(value) < 20 for value in existing.values()):
        raise ValueError('Invalid password state. Restore the original password file.')
    by_name = {name.lower(): name for name in existing}
    if len(by_name) != len(existing):
        raise ValueError('Password state contains duplicate student IDs ignoring case.')
    missing = {student.lower() for student in required_students} - set(by_name)
    if missing:
        raise ValueError('Saved passwords are missing for previously provisioned students. Restore the original password file.')
    changed = not path.exists() or (path.stat().st_mode & 0o777) != 0o600
    current = {}
    for student in students:
        saved_name = by_name.get(student.lower())
        if saved_name is None:
            existing[student] = 'Aa1!' + secrets.token_urlsafe(24)
            saved_name = student
            changed = True
        current[student] = existing[saved_name]
    if not check_mode:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if changed:
            fd, temporary = tempfile.mkstemp(dir=path.parent)
            try:
                with os.fdopen(fd, 'w') as stream:
                    json.dump(existing, stream, indent=2)
                    stream.write('\n')
                os.replace(temporary, path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        os.chmod(path, 0o600)
    return changed, current


def main():
    module = AnsibleModule(argument_spec={
        'path': {'type': 'path', 'required': True},
        'students': {'type': 'list', 'elements': 'str', 'required': True},
        'required_students': {'type': 'list', 'elements': 'str', 'default': []},
    }, supports_check_mode=True)
    try:
        changed, passwords = reconcile_passwords(module.params['path'], module.params['students'], module.check_mode, module.params['required_students'])
        module.exit_json(changed=changed, passwords=passwords)
    except (ValueError, OSError) as exc:
        module.fail_json(msg=str(exc))


if __name__ == '__main__':
    main()

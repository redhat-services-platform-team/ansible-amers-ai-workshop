#!/usr/bin/python
"""List Gitea usernames and create missing accounts without resetting passwords."""
from ansible.module_utils.basic import AnsibleModule


def usernames_from_list(output):
    return {columns[1].lower() for line in output.splitlines()
            if len(columns := line.split()) >= 2 and columns[0].isdigit()}


def create_missing_users(users, existing, run, check_mode=False):
    created = []
    for user in users:
        if user['username'].lower() in existing:
            continue
        args = ['admin', 'user', 'create', '--username', user['username'],
                '--email', user['email'], '--password', user['password'],
                '--must-change-password=' + str(user['must_change_password']).lower(),
                '--admin=' + str(user['admin']).lower()]
        if not check_mode:
            run(args)
        created.append(user['username'])
    return created


def main():
    module = AnsibleModule(argument_spec={
        'binary': {'type': 'path', 'default': '/usr/local/bin/gitea'},
        'config': {'type': 'path', 'default': '/etc/gitea/gitea.ini'},
        'users': {'type': 'list', 'elements': 'dict', 'default': [], 'no_log': True,
                  'options': {
                      'username': {'type': 'str', 'required': True},
                      'email': {'type': 'str', 'required': True},
                      'password': {'type': 'str', 'required': True, 'no_log': True},
                      'admin': {'type': 'bool', 'default': True},
                      'must_change_password': {'type': 'bool', 'default': True},
                  }},
    }, supports_check_mode=True)
    def run(args):
        rc, output, _ = module.run_command([module.params['binary'], '-c', module.params['config']] + args,
                                           cwd='/var/lib/gitea')
        if rc:
            module.fail_json(msg='Gitea user command failed. Inspect the Gitea service on the server.')
        return output
    existing = usernames_from_list(run(['admin', 'user', 'list']))
    created = create_missing_users(module.params['users'], existing, run, module.check_mode)
    module.exit_json(changed=bool(created), usernames=sorted(existing), created_users=created)


if __name__ == '__main__':
    main()

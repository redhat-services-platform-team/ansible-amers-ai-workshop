# Instructor AWS Git environment

Deploy one Gitea server in one AWS account. Give each student a Git URL and local login. The playbook creates a private organization, permission group, and starter repository for each team.

The example has five teams: `comet`, `nebula`, `orbit`, `pulsar`, and `quasar`. Use as many teams as your class needs.

## Install

Install Ansible Navigator and Podman or Docker on the controller. Run these commands from `instructor_automation/`.

`ansible-navigator.yml` uses `quay.io/igou/igou-awx-ee` pinned to the tested image digest. The image supplies Ansible, the AWS SDK, and the required collections.

```sh
# Create a private directory for credentials and generated files.
ansible-navigator exec -- install -d -m 0700 private
# Copy the input example for your class, then edit it for your account and teams.
ansible-navigator exec -- cp environments.example.yml private/environment.yml
# Install the pinned upstream Gitea role into the project.
ansible-navigator exec -- ansible-galaxy role install -r requirements.yml -p external_roles
```

`site.yml` calls [roles-ansible.gitea](https://github.com/roles-ansible/ansible_role_gitea) to install Gitea and its `local_git_users` tasks to create local accounts. The workshop role uses Ansible modules and filters to discover AWS resources, save passwords, and manage organizations.

Navigator passes `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` into the container. Add `session_token` to the account dictionary when using temporary credentials. Project files, including `private/` and the generated inventory, are available inside the container. Keep SSH keys and password files under the project directory when using this configuration.

The configuration uses stdout mode and disables playbook artifacts because the playbook handles credentials.

## Inputs

```yaml
workshop_git_aws_account:
  name: demo-a
  region: us-east-2
  access_key: "{{ lookup('ansible.builtin.env', 'AWS_ACCESS_KEY_ID') }}"
  secret_key: "{{ lookup('ansible.builtin.env', 'AWS_SECRET_ACCESS_KEY') }}"

workshop_git_teams:
  comet: [student01]
  nebula: [student02]
  orbit: [student03]
  pulsar: [student04]
  quasar: [student05]
```

Each team name becomes an organization and permission group. Its value lists the student usernames.

Use each student ID in only one team. Usernames and organization names must differ even when compared without case. Gitea reserves `Owners` for its ownership group. A team can have no members, but the dictionary must contain at least one team.

The role discovers the account's public Route 53 zone. The server hostname is `git.<zone>` by default. Set `workshop_git_dns_label` to change `git` to another prefix. If the account has multiple public zones, select one with `hosted_zone_id` or `hosted_zone_name` in the account dictionary.

The role checks a DNS ownership record before using an existing hostname.

Export the access key and secret key before running, or store them in an Ansible Vault-encrypted input file. Temporary AWS credentials also require `session_token`. The account needs permission to manage EC2 networking, instances, key pairs, and Route 53 records.

```sh
# Provision the instance and configure student access.
ansible-navigator run site.yml -e @private/environment.yml
```

If the input file contains credentials, encrypt it and enable Vault prompts when running the playbook:

```sh
ansible-navigator exec -- ansible-vault encrypt private/environment.yml
ansible-navigator run site.yml -e @private/environment.yml --enable-prompts --ask-vault-pass
```

Add the same Vault options to discovery and teardown commands when using encrypted inputs.

## AWS dynamic inventory

Ansible starts with `inventory/localhost.ini`. After provisioning, the role writes `inventory/workshop.aws_ec2.yml` and the playbook refreshes inventory.

The `amazon.aws.aws_ec2` plugin finds the instance by its deployment, account name, ownership, and resource-name tags. It provides the public IP, instance ID, Git hostname, and `ec2-user` SSH login. The playbook checks that inventory found exactly the provisioned instance before configuring Gitea.

The generated inventory contains AWS credentials. The role sets the file mode to `0600` and directory mode to `0700`. Git ignores the file, and inventory caching is disabled. Discovery-only and check mode skip server configuration even if inventory already contains a host.

```sh
# Inspect the discovered hosts without printing host variables or credentials.
ansible-navigator exec -- ansible-inventory --graph
```

Existing Ubuntu deployments need a separate migration. This playbook stops before reusing an instance whose image is not an official RHEL 9 image. Use a new `workshop_git_deployment_id` and `workshop_git_dns_label` to create a separate RHEL deployment while preserving the old server and its data.

## Student permissions

Students are local Gitea users. Each team group has `write` access to its organization's repositories, and students can create repositories there. Set `workshop_git_team_permission` to `read`, `write`, or `admin`. Repository admin access does not make a student a site administrator. The separate `instructor` account owns the organizations and administers the site.

On reruns, the role makes each named organization's membership match its roster. It removes extra members, keeps students out of Owners, and revokes site administrator access from students in the input. Moving a student between teams does not reset their password.

Removing a team or student from the input does not delete the organization or account. Remove or archive those separately. Use organizations whose memberships this automation can manage.

## Access sheet and reruns

`private/git-access.json` contains the server URL, organization and repository URLs, team rosters, initial passwords, and the instructor username. Give each student their own credentials and organization's URL. Keep the instructor credentials private.

The playbook saves generated passwords in `private/student-passwords.json` before creating users. By default, students must change their password at first login. The access sheet keeps the initial password; it stops working once the student changes it.

The instructor account has no required first-login password change because the playbook uses it for API requests on reruns. If you change that password, update its saved value too.

Keep the private directory across runs. The playbook needs the original SSH key and saved passwords for existing accounts. It stops if required password state is missing and does not reset existing passwords.

Password tasks suppress output. Credential files use mode `0600` inside a `0700` directory that Git ignores.

## Infrastructure and HTTPS

The default server is a RHEL 9 `t3.medium` with a 30 GiB encrypted gp3 root volume. It requires IMDSv2. The role creates a VPC, public subnet, internet gateway, route table, and security group.

SSH allows the controller's public IPv4 address as a `/32` by default. Set `workshop_git_ssh_cidr` to allow another source network. Students use HTTPS. Git over SSH is disabled.

Gitea uses SQLite and its built-in ACME client to obtain a Let's Encrypt certificate. Public DNS must resolve to the instance. Ports 80 and 443 are public for ACME validation and HTTPS. Set `workshop_git_acme_email` for renewal notices. The playbook checks trusted HTTPS before configuring users and organizations.

## Tear down the environment

Teardown permanently deletes Gitea data on the instance's root volume. Export any repositories you need before running it. Use the same account, deployment ID, DNS label, and hosted zone settings as the deployment. Student rosters, saved passwords, and the SSH key are not required for teardown.

```sh
# Preview removal.
ansible-navigator run teardown.yml -e @private/environment.yml --check
# Remove the deployed environment.
ansible-navigator run teardown.yml -e @private/environment.yml
```

Add the Vault options above if needed. Teardown checks ownership before deleting resources. It removes the Git A record, terminates the instance and its root volume, then removes the dedicated subnet, route table, security group, internet gateway, VPC, and EC2 key pair. It releases the DNS ownership TXT record last and removes the generated local inventory. Rerunning teardown after successful removal makes no changes.

The preexisting Route 53 zone and unrelated records remain. Teardown refuses resources with missing or conflicting ownership tags and refuses a VPC containing another active instance. Local passwords, the access sheet, and SSH keys remain in `private/`. Archive or remove them separately after the workshop. The retained access sheet describes the deleted deployment until the next successful build.

## Validate changes

```sh
# Check playbook syntax.
ansible-navigator run site.yml --syntax-check -e @environments.example.yml
ansible-navigator run teardown.yml --syntax-check -e @environments.example.yml
# Check team inputs and saved password handling without AWS access.
ansible-navigator run tests/validate.yml -i localhost,
# Check teardown ownership rejection without AWS access.
ansible-navigator run tests/teardown.yml -i localhost,
# Check organization membership and repository permissions on a deployed server.
ansible-navigator run tests/live.yml -i localhost,
```

The pinned execution environment does not include `ansible-lint`. Install its dependencies in a private directory through Navigator, then run lint in the container:

```sh
ansible-navigator exec -- python3 -m venv private/lint-venv
ansible-navigator exec -- private/lint-venv/bin/python -m pip install -r requirements-dev.txt
ansible-navigator exec -- private/lint-venv/bin/ansible-lint --offline site.yml teardown.yml roles/workshop_git tests
```

To test another deployment, pass `-e test_access_file=/absolute/path/to/git-access.json`. The live check creates a temporary user and repository, checks access and writes, then deletes both. It does not change student passwords.

See the [role reference](roles/workshop_git/README.md) for all configuration variables.

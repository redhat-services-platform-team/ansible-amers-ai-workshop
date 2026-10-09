# Instructor AWS Git environment

Deploy one Gitea server in one AWS account. Give each student a Git URL and local login. The playbook creates a private organization, permission group, and starter repository for each team.

The example has five teams: `comet`, `nebula`, `orbit`, `pulsar`, and `quasar`. Use as many teams as your class needs.

## Install

Run these commands from `instructor_automation/`.

```sh
# Create a local environment for Ansible and the AWS SDK.
python3 -m venv .venv
# Activate that environment.
source .venv/bin/activate
# Install Ansible and its AWS dependencies.
python -m pip install -r requirements.txt
# Install the AWS and SSH key collections.
ansible-galaxy collection install -r requirements.yml
# Install the pinned upstream Gitea role.
ansible-galaxy role install -r requirements.yml -p external_roles
# Create a private directory for credentials and generated files.
mkdir -p private && chmod 700 private
# Copy the input example for your class.
cp environments.example.yml private/environment.yml
```

`site.yml` calls [roles-ansible.gitea](https://github.com/roles-ansible/ansible_role_gitea) to install Gitea and its `local_git_users` tasks to create local accounts. The workshop role uses Ansible modules and filters to discover AWS resources, save passwords, and manage organizations.

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
# Encrypt inputs if they contain credentials.
ansible-vault encrypt private/environment.yml
# Discover the zone and deployment without writing files or provisioning.
ansible-playbook site.yml -e @private/environment.yml -e workshop_git_discover_only=true --ask-vault-pass
# Provision the instance and configure student access.
ansible-playbook site.yml -e @private/environment.yml --ask-vault-pass
```

Omit `--ask-vault-pass` when the input file is not encrypted.

## AWS dynamic inventory

Ansible starts with `inventory/localhost.ini`. After provisioning, the role writes `inventory/workshop.aws_ec2.yml` and the playbook refreshes inventory.

The `amazon.aws.aws_ec2` plugin finds the instance by its deployment, account name, ownership, and resource-name tags. It provides the public IP, instance ID, Git hostname, and `ec2-user` SSH login. The playbook checks that inventory found exactly the provisioned instance before configuring Gitea.

The generated inventory contains AWS credentials. The role sets the file mode to `0600` and directory mode to `0700`. Git ignores the file, and inventory caching is disabled. Discovery-only and check mode skip server configuration even if inventory already contains a host.

```sh
# Inspect the discovered hosts without printing host variables or credentials.
ansible-inventory --graph
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

This creates billable AWS resources. There is no teardown playbook. Remove the tagged EC2 instance and its networking resources, EC2 key pair, and Git A and ownership TXT records after the workshop. Keep unrelated Route 53 records and the preexisting zone.

## Validate changes

```sh
# Install lint dependencies.
python -m pip install -r requirements-dev.txt
# Check playbook syntax.
ansible-playbook site.yml --syntax-check -e @environments.example.yml
# Lint the instructor role.
ansible-lint --offline site.yml roles/workshop_git tests
# Check team inputs and saved password handling without AWS access.
ansible-playbook -i localhost, tests/validate.yml
# Check organization membership and repository permissions on a deployed server.
ansible-playbook -i localhost, tests/live.yml
```

To test another deployment, pass `-e test_access_file=/absolute/path/to/git-access.json`. The live check creates a temporary user and repository, checks access and writes, then deletes both. It does not change student passwords.

See the [role reference](roles/workshop_git/README.md) for all configuration variables.

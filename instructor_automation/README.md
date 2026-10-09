# Instructor AWS Git environment

The playbook deploys one Gitea instance in one AWS account. Students get a Git URL and local login. A team dictionary creates private organizations and permission groups, with one starter repository per organization.

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

The playbook calls [roles-ansible.gitea](https://github.com/roles-ansible/ansible_role_gitea) directly for installation and calls its `local_git_users` tasks directly for local accounts. Both calls are in `site.yml`. AWS discovery, password storage, and Gitea organization management use Ansible modules and filters. The role has no embedded Python or custom modules.

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

Each dictionary key becomes both an organization name and a Gitea permission group name. Values are lists of usernames. Student IDs must be unique across teams. Usernames and organization names must differ, including case. `Owners` is reserved for Gitea's built-in ownership group. Empty member lists are allowed; an empty team dictionary is rejected.

The role discovers public Route 53 zones and selects the only public zone. If several exist, add `hosted_zone_id` or `hosted_zone_name` to the account dictionary. The Git hostname defaults to `git.<zone>`. `workshop_git_dns_label` changes the prefix. A DNS ownership record prevents this deployment from taking over an existing hostname.

Export your AWS credentials before running, or use Ansible Vault for inputs containing keys. An access key and secret key are sufficient for this setup. A session token is only needed for temporary AWS credentials. The account needs permission to manage EC2 networking, instances, key pairs, and Route 53 records.

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

Ansible loads `inventory/localhost.ini` to start provisioning. The role then writes `inventory/workshop.aws_ec2.yml` and the playbook refreshes inventory. The `amazon.aws.aws_ec2` plugin discovers the running instance by its deployment, account name, ownership, and resource-name tags. It supplies the public IP, instance ID, Git hostname, and `ec2-user` SSH login. The playbook requires exactly the instance it provisioned before configuring Gitea.

The generated inventory source contains AWS credentials. The role sets its mode to `0600`, restricts the inventory directory to `0700`, and Git ignores the generated file. It disables inventory caching. Discovery-only and check mode skip all server configuration, including when an existing inventory source already contains a host.

```sh
# Inspect the discovered hosts without printing host variables or credentials.
ansible-inventory --graph
```

Existing Ubuntu deployments need a separate migration. This playbook stops before reusing an instance whose image is not an official RHEL 9 image. Use a new `workshop_git_deployment_id` and `workshop_git_dns_label` to create a separate RHEL deployment while preserving the old server and its data.

## Student permissions

Students are regular local Gitea users. Their named group gets `write` permission on every repository in their own organization, and they can create repositories there. `workshop_git_team_permission` can be `read`, `write`, or `admin`. Organization repository admin permission does not grant site administrator access. A separate `instructor` account owns the organizations and has site administrator access.

The role manages membership of every organization named in the dictionary. Reruns remove members outside that organization's roster, keep students out of the Owners group, and revoke global administrator privileges from requested students. Membership changes move students between teams without resetting passwords. Organizations removed from the dictionary and user accounts removed from all teams remain on the server; remove or archive them separately. Do not use existing organizations whose memberships you want to preserve.

## Access sheet and reruns

`private/git-access.json` contains the server URL, organization and repository URLs, team rosters, initial passwords, and the instructor username. Give each student their own credentials and organization's URL. Keep the instructor credentials private.

The playbook generates random passwords and saves them in `private/student-passwords.json` before creating users. Students must change their password at first login by default. The instructor account does not require that change so the playbook can authenticate API requests on reruns. If you change the instructor password, update its saved value too. Initial student passwords in the sheet no longer work after students change them.

Preserve the private directory. Existing instances require the original generated SSH key. Existing requested users require saved passwords; the role stops if that state is missing. Reruns do not reset existing passwords. Password tasks suppress output, and credential files have mode `0600` inside a `0700` directory. The directory is ignored by Git.

## Infrastructure and HTTPS

The default instance is a RHEL 9 `t3.medium` with a 30 GiB encrypted gp3 root volume and IMDSv2 required. The role creates a dedicated VPC, public subnet, internet gateway, route table, and security group. Instructor SSH access defaults to the controller's public IPv4 address with a `/32` rule. Set `workshop_git_ssh_cidr` to use another source network. Students use HTTPS; Git SSH access is disabled.

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

To test another deployment, pass `-e test_access_file=/absolute/path/to/git-access.json`. The live check creates a temporary regular user and repository, verifies access and writes, then deletes both. It leaves student passwords unchanged.

See the [role reference](roles/workshop_git/README.md) for all configuration variables.

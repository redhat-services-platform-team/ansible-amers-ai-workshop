# Instructor AWS Git servers

Run one Ansible playbook with a list of AWS environments and a list of student IDs. The `workshop_git` role builds one Gitea server per environment and creates every student on every server.

Each server uses a `t3.medium`, Ubuntu 24.04, native Gitea with SQLite, and built-in Let's Encrypt HTTPS. The role creates a dedicated VPC and public subnet, so the account does not need a default VPC. It discovers the account's public Route 53 zone and publishes `git.<zone>`. An environment can override the DNS label or select a zone when discovery is ambiguous.

Students are Gitea administrators by default. They have no AWS permissions from this automation. Students use HTTPS for browser and Git access. The instructor playbook generates an Ed25519 SSH key and registers its public key in every account. SSH access defaults to the instructor's public IPv4 address. Students do not need the SSH key.

## Install dependencies

Run these commands from this directory:

```bash
# Create an isolated Python environment for Ansible and the AWS SDK.
python3 -m venv .venv
# Activate that environment in this terminal.
source .venv/bin/activate
# Install Ansible and the AWS SDK in the same Python environment.
python -m pip install -r requirements.txt
# Install the AWS and SSH-key collections used by the role.
ansible-galaxy collection install -r requirements.yml
# Install the pinned Gitea role from GitHub.
ansible-galaxy role install -r requirements.yml -p external_roles
```

## Set the inputs

```bash
# Create a private directory for input keys and generated passwords.
mkdir -p private
# Restrict access to the instructor's local user.
chmod 700 private
# Copy the example inputs before adding accounts and student IDs.
cp environments.example.yml private/environments.yml
# Restrict access to the input file.
chmod 600 private/environments.yml
```

Edit `private/environments.yml`. Both inputs are required:

```yaml
workshop_git_aws_environments:
  - name: demo-a
    region: us-east-2
    access_key: FIRST_ACCOUNT_ACCESS_KEY
    secret_key: FIRST_ACCOUNT_SECRET_KEY
  - name: demo-b
    region: us-east-2
    access_key: SECOND_ACCOUNT_ACCESS_KEY
    secret_key: SECOND_ACCOUNT_SECRET_KEY

workshop_git_student_ids:
  - alice
  - bob
  - charlie
```

Each environment needs a unique name. Student IDs must be unique ignoring case and use 1 to 40 letters or digits, with single internal dots, hyphens, or underscores. Gitea also reserves some names; use student IDs such as `student01` rather than route names such as `api`.

For a single account, the example reads `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from your shell environment. If your keys are in the repository's `.env`, load them before running Ansible:

```bash
# Export assignments from the repository's credentials file to this shell.
set -a
# Load the AWS keys from the repository root.
source ../.env
# Stop automatically exporting subsequent shell assignments.
set +a
```

For multiple accounts, put each account's keys in its dictionary. You can also use environment lookups with different variable names. An optional `session_token` supports temporary credentials.

Encrypt a file containing keys with Ansible Vault:

```bash
# Encrypt the private input file before keeping or sharing it.
ansible-vault encrypt private/environments.yml
```

The role does not copy the account's admin keys onto the instances. The private SSH key and initial passwords stay on the instructor's machine.

## Discover first, then deploy

```bash
# Read account identity, hosted zones, existing deployment records, and the AMI.
ansible-playbook site.yml -e @private/environments.yml --ask-vault-pass -e workshop_git_discover_only=true
# Provision the servers and create the student accounts.
ansible-playbook site.yml -e @private/environments.yml --ask-vault-pass
```

Omit `--ask-vault-pass` when using an unencrypted input file. Ansible check mode also runs discovery without provisioning or writing password files.

Discovery selects the single public hosted zone in each account. It stops when there are no public zones or multiple candidates. To choose among multiple zones, add `hosted_zone_id` or `hosted_zone_name` to that environment. Private hosted zones are excluded.

The domain must already have working public DNS delegation. Gitea needs inbound ports 80 and 443 to obtain a trusted certificate. It serves HTTPS directly and renews certificates through built-in ACME support. The role accepts the Let's Encrypt terms of service and verifies the HTTPS health endpoint before reporting success. Set `workshop_git_acme_email` for certificate account notices. See [Gitea's HTTPS setup](https://docs.gitea.com/administration/https-setup/).

The role marks ownership with `_workshop-owner.git.<zone>` and refuses to overwrite an existing Git hostname owned by something else. Use a different `dns_label` if that hostname is occupied. Every environment must resolve to a different Git hostname.

## Read the access sheet

The playbook keeps these files under the ignored `private/` directory:

- `ai-workshop_ed25519` is the generated private SSH key, with mode `0600`. Keep its `.pub` file too.
- `known_hosts` records SSH host identities on first connection.
- `student-passwords.json`, with mode `0600`, retains the generated initial passwords across reruns.
- `git-access.json`, with mode `0600`, lists the server URLs, instance IDs, student IDs, and initial passwords.

```bash
# Display the private access sheet for distribution to participants.
cat private/git-access.json
```

Each student receives a different random password. Their initial password works on every newly created server account, so you can give each student the same credentials for all servers. The default requires a password change at first login. After that, the password can differ per server; the access sheet still records the initial password.

Reruns create missing accounts and leave existing passwords unchanged. Keep the generated SSH key and `student-passwords.json` with the deployment inputs. If an existing instance has no saved SSH key, the role stops. It also checks each server's existing Gitea users before generating passwords. A requested existing student with no saved password stops configuration. Restore a backup before rerunning. Removing a student from the input list does not delete their account.

Set `workshop_git_students_are_admins: false` to create regular users. Set `workshop_git_must_change_password: false` to keep the generated password after first login. These settings apply when an account is created; reruns do not change existing account privileges or password settings. See [Gitea's user commands](https://docs.gitea.com/administration/command-line/).

Ansible sends student credentials over SSH only when creating accounts. The server stores Gitea's password hashes. AWS credentials and student passwords never enter EC2 user data. Tasks that handle credentials suppress their output.

## Settings and resource ownership

All inputs and their defaults are documented in the [role README](roles/workshop_git/README.md). Defaults are in `roles/workshop_git/defaults/main.yml`. You can override the instance type, volume size, DNS label, deployment ID, the Gitea version, SSH source network, or output paths in your input file. Use x86_64 instance types with the default Ubuntu AMI. The Gitea role and binary versions are pinned. Changing the binary version updates the native installation.

Keep environment names and `workshop_git_deployment_id` stable across reruns. They identify the EC2 instance, VPC, key pair, and DNS records. A different deployment ID creates a separate deployment. Run one instructor process at a time for a deployment.

The instructor credentials need permission to read STS identity and Route 53 zones, manage the deployment's EC2 networking and instances, manage EC2 key pairs, and update DNS records in the selected zone. The demo platform's admin keys cover those actions. Account service restrictions or quotas can still prevent provisioning.

Tag names `WorkshopDeployment`, `WorkshopEnvironment`, and `ManagedBy` identify the resources. Data and certificates live on the instance's encrypted root volume. This is a single-server workshop deployment. Back up `/var/lib/gitea` and `/etc/gitea` if you need to retain repositories after the AWS environment expires.

## SSH access

The generated private key is for instructor administration. The security group permits SSH only from `workshop_git_ssh_cidr`. When that variable is empty, the playbook discovers your current public IPv4 address and permits its `/32`. Override it when your SSH connection uses a different VPN or gateway address.

The playbook records host keys with SSH's `accept-new` policy in `private/known_hosts`. An unexpected changed host key stops the connection. If you intentionally replace a server, verify its identity before removing its old known-hosts entry.

Servers from the earlier Docker/SSM implementation need a separate migration. Use a fresh deployment ID and DNS label for this native setup. See the [role README](roles/workshop_git/README.md) for entry points and recovery behavior.

## Cleanup

After the workshop, use the instance IDs in `git-access.json` and the deployment tags to identify the resources. Remove the deployment's A record and ownership TXT record, terminate its instances, then remove its subnet, route table, security group, internet gateway, and VPC. Remove the deployment's EC2 key pair. Preserve the preexisting hosted zone and any resources without this deployment's tags.

Terminating the instance deletes its root volume and repositories. Keep the password state and input files until you have completed the handover or cleanup.

## Validation

```bash
# Check the playbook and role syntax without calling AWS.
ansible-playbook site.yml --syntax-check -e @environments.example.yml
# Lint the Ansible tasks.
ansible-lint --offline site.yml roles/workshop_git
# Test zone selection, DNS ownership, password reuse, and remote setup behavior.
python -m unittest discover -s tests -v
```

The tests cover discovery decisions, password persistence, and native account creation. A discovery run checks real account access and naming without creating resources. Deployment is the step that verifies EC2 provisioning, Gitea startup, user creation, and HTTPS end to end.

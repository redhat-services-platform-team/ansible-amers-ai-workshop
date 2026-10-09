# workshop_git

Provision one Ubuntu 24.04 Gitea server per AWS environment and create every student on every server. The instructor connects with a generated SSH key. Students receive a Git URL, username, and password.

The role creates a dedicated VPC, public subnet, security group, EC2 key pair, `t3.medium` instance, and Route 53 records. The pinned [roles-ansible Gitea role](https://github.com/roles-ansible/ansible_role_gitea) installs a native binary and systemd service with SQLite. Gitea's built-in ACME support obtains and renews a Let's Encrypt certificate. There are no container, instance IAM, or SSM credential resources.

## Requirements

Use Ansible Core 2.19 through 2.21, the Python dependencies in `../../requirements.txt`, and collections and roles in `../../requirements.yml`. Install the upstream role under `../../external_roles`. The controller needs `ssh` and `ssh-keygen`. Provisioned hosts use Canonical's x86_64 Ubuntu 24.04 image and the `ubuntu` SSH user.

Each account needs a publicly delegated Route 53 hosted zone and instructor permission to manage EC2 networking, instances, key pairs, and DNS. The role never sends the AWS admin keys to the servers.

Ports 80 and 443 must be publicly reachable for ACME validation and student access. SSH port 22 accepts the instructor's public IPv4 address by default. Set `workshop_git_ssh_cidr` to a stable network when working through a VPN or shared gateway. Generated SSH keys use Ed25519 and remain on the controller with mode `0600`.

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `workshop_git_aws_environments` | `Required` | AWS accounts and regions in which to deploy Git servers. |
| `workshop_git_student_ids` | `Required` | Student usernames to create on every server. |
| `workshop_git_discover_only` | `false` | Read AWS state and validate inputs without provisioning or writing files. |
| `workshop_git_deployment_id` | `ai-workshop` | Stable identifier used in resource names, tags, and parameter paths. |
| `workshop_git_dns_label` | `git` | Default Git subdomain label in each selected hosted zone. |
| `workshop_git_instance_type` | `t3.medium` | An x86_64 EC2 instance type compatible with Ubuntu 24.04. |
| `workshop_git_volume_size` | `30` | Encrypted gp3 root volume size in GiB, from 8 to 16384. |
| `workshop_git_vpc_cidr` | `10.77.0.0/16` | IPv4 VPC network with a prefix length from 16 to 28. |
| `workshop_git_subnet_cidr` | `10.77.1.0/24` | IPv4 subnet inside the VPC with a prefix length from 16 to 28. |
| `workshop_git_students_are_admins` | `true` | Grant administrator privileges to newly created Gitea users. |
| `workshop_git_must_change_password` | `true` | Require newly created users to change their password at first login. |
| `workshop_git_private_dir` | `{{ playbook_dir }}/private` | Dedicated controller directory whose permissions the role manages as 0700. |
| `workshop_git_password_file` | `{{ workshop_git_private_dir }}/student-passwords.json` | Controller file that retains initial student passwords with mode 0600. |
| `workshop_git_output_file` | `{{ workshop_git_private_dir }}/git-access.json` | Controller access sheet containing server details and initial passwords. |
| `workshop_git_timeout` | `1200` | SSH connection timeout in seconds. |
| `workshop_git_gitea_version` | `28.1.0` | Pinned Gitea binary release installed by the upstream role. |
| `workshop_git_ssh_private_key_file` | `{{ workshop_git_private_dir }}/{{ workshop_git_deployment_id }}_ed25519` | Generated instructor SSH key on the controller. Preserve it across reruns. |
| `workshop_git_ssh_cidr` | `Empty` | SSH source network. Empty discovers the instructor public IPv4 address and uses its /32. |
| `workshop_git_acme_email` | `Empty` | Optional contact address for Let's Encrypt renewal notices. |

Each AWS environment dictionary requires `name`, `region`, `access_key`, and `secret_key`. Optional keys are `session_token`, `hosted_zone_id`, `hosted_zone_name`, and `dns_label`. Names start with a lowercase letter and contain at most 24 lowercase letters, digits, or hyphens. Select a hosted zone explicitly when an account has multiple public zones.

Student IDs are unique ignoring case and contain 1 to 40 letters or digits, with single internal dots, underscores, or hyphens. Reserved Gitea usernames are rejected. DNS labels contain 1 to 63 letters, digits, or internal hyphens.

Use different paths for the password file and access sheet. The role manages its dedicated private directory as `0700` and files as `0600`; other existing parent directory permissions remain unchanged. Custom key and output parent directories must exist.

## Playbook entry points

Use [site.yml](../../site.yml), which runs the required plays in order:

```yaml
---
- name: Provision Git servers
  hosts: local
  gather_facts: false
  roles:
    - workshop_git

- name: Configure Gitea over SSH
  hosts: workshop_git_servers
  gather_facts: false
  any_errors_fatal: true
  tasks:
    - name: Configure each server
      ansible.builtin.include_role:
        name: workshop_git
        tasks_from: configure

- name: Write the access sheet
  hosts: local
  gather_facts: false
  tasks:
    - name: Report verified servers
      ansible.builtin.include_role:
        name: workshop_git
        tasks_from: report
```

Supply the AWS environments and student IDs with an input file, as shown in the [instructor guide](../../README.md). The provision entry point adds SSH hosts to the in-memory `workshop_git_servers` group. The configure entry point waits for SSH, installs Gitea, verifies trusted HTTPS, and creates missing users. The report entry point runs only after configuration succeeds and writes the access sheet.

## Reruns and password recovery

Preserve the generated SSH key and `student-passwords.json`. An existing instance with a missing private key stops provisioning. During SSH setup, the role reads existing Gitea usernames and checks saved passwords on every server before it writes password state or creates users. If a requested existing user has no saved password, restore the original password file. The playbook aborts configuration across all servers when a preflight check fails.

New students receive random passwords. The role reuses saved initial passwords, creates missing accounts, and leaves existing passwords and privileges unchanged. Students must change their password at first login by default; their passwords can then differ by server. The access sheet retains the initial password. Removing students from the inputs does not delete existing accounts.

Changing `workshop_git_gitea_version` asks the upstream role to update the binary and restart the service. Certificate state persists under `/var/lib/gitea/custom/https`. Keep deployment IDs and environment names stable so reruns find their original resources.

## Check mode

Check mode and `workshop_git_discover_only: true` validate inputs and read AWS state. They create no keys, resources, or password files and skip the SSH configuration and report plays. They do not predict provisioning changes or test Gitea startup.

## HTTPS

Gitea obtains and renews its certificate through [built-in ACME support](https://docs.gitea.com/administration/https-setup/). This configuration accepts the Let's Encrypt terms of service, listens on port 443, and redirects HTTP on port 80. Set `workshop_git_acme_email` to receive account notices. DNS delegation and inbound reachability must work before issuance can succeed. The playbook verifies the endpoint with certificate validation enabled before reporting success.

## Rollback and cleanup

There is no automatic rollback or teardown. Interrupted provisioning can leave billable resources. Rerun with the same deployment inputs and SSH key after fixing the failure. Back up `/var/lib/gitea` and `/etc/gitea` before upgrading. An older binary may require a matching database backup.

Follow the [instructor cleanup guide](../../README.md#cleanup). Remove the deployment's EC2 key pair along with its instance, networking, and DNS records. Preserve the preexisting hosted zone. Terminating the instance deletes the root volume and repositories. Keep private keys and password state until handover or cleanup is complete.

Servers from the former Docker/SSM implementation need a separate migration. This playbook does not import their data, replace their operating system, or attach an SSH key to a running instance. Use a fresh deployment ID and DNS label for the native installation, then retire the old deployment after preserving any data.

## Author and license

Maintained by the Red Hat Services Platform Team. The repository has no declared redistribution license. Role metadata uses `Proprietary` to reflect that status. The upstream Gitea role retains its BSD-3-Clause license.

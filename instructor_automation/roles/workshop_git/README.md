# workshop_git

Deploy one Gitea server on AWS with local users and private team organizations. Supply an AWS account dictionary and a team dictionary. Team names become organizations and permission groups; each team's value lists its student usernames.

See [the instructor guide](../../README.md) for installation, credentials, examples, and rerun behavior.

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `workshop_git_discover_only` | `False` | Read AWS state and validate inputs without provisioning or writing files. |
| `workshop_git_deployment_id` | `ai-workshop` | Stable identifier used in resource names and tags. |
| `workshop_git_dns_label` | `git` | Default Git subdomain label in the selected hosted zone. |
| `workshop_git_instance_type` | `t3.medium` | An x86_64 EC2 instance type compatible with RHEL 9. |
| `workshop_git_volume_size` | `30` | Encrypted gp3 root volume size in GiB, from 8 to 16384. |
| `workshop_git_vpc_cidr` | `10.77.0.0/16` | IPv4 VPC network with a prefix length from 16 to 28. |
| `workshop_git_subnet_cidr` | `10.77.1.0/24` | IPv4 subnet inside the VPC with a prefix length from 16 to 28. |
| `workshop_git_must_change_password` | `True` | Require newly created users to change their password at first login. |
| `workshop_git_private_dir` | `{{ playbook_dir }}/private` | Controller directory for generated credentials and keys, with mode 0700. |
| `workshop_git_password_file` | `{{ workshop_git_private_dir }}/student-passwords.json` | Controller file that retains initial student passwords with mode 0600. |
| `workshop_git_output_file` | `{{ workshop_git_private_dir }}/git-access.json` | Controller access sheet with server URLs and initial passwords. |
| `workshop_git_timeout` | `1200` | SSH connection timeout in seconds. |
| `workshop_git_gitea_version` | `28.1.0` | Pinned Gitea binary release installed by the upstream role. |
| `workshop_git_ssh_private_key_file` | `{{ workshop_git_private_dir }}/{{ workshop_git_deployment_id }}_ed25519` | Generated instructor SSH key on the controller. Preserve it across reruns. |
| `workshop_git_ssh_cidr` | `` | SSH source network. Leave empty to discover the instructor's public IPv4 address and allow its /32. |
| `workshop_git_acme_email` | `` | Optional contact address for Let's Encrypt renewal notices. |
| `workshop_git_aws_account` | `Required` | Single AWS account and region for the Gitea instance. |
| `workshop_git_teams` | `Required` | Organization and permission group names mapped to lists of student usernames. Any nonempty number of teams is supported. |
| `workshop_git_admin_user` | `instructor` | Separate instructor site administrator, excluded from student teams. |
| `workshop_git_team_permission` | `write` | Repository permission granted to each organization group. |
| `workshop_git_repository_name` | `netbox-migration` | Private starter repository created in each organization. |

## Role entry points

| Entry point | What it does |
| --- | --- |
| `main` | Validate inputs, discover AWS resources, provision RHEL 9, and write the EC2 inventory. |
| `prepare` | Check the RHEL server and save credentials. |
| `users` | Check HTTPS and prepare missing local accounts. |
| `configure` | Verify users and set organization permissions. |
| `report` | Write the access sheet. |

The supplied `site.yml` calls `roles-ansible.gitea` directly for installation and calls its `local_git_users` tasks directly for user creation. It refreshes `amazon.aws.aws_ec2` inventory between provisioning and server configuration.

The role uses native Ansible modules, filters, and lookups. Upstream Gitea handlers manage the service. On reruns, each named organization's membership must match its roster. The role leaves organizations outside the dictionary unchanged.

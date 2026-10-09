# workshop_git

Deploy one AWS Gitea instance with local users, private organizations, and named permission groups. Supply one AWS account dictionary and a team dictionary whose keys name organizations and whose values list their students.

See [the instructor guide](../../README.md) for installation, credentials, examples, and rerun behavior.

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `workshop_git_discover_only` | `False` | Read AWS state and validate inputs without provisioning or writing files. |
| `workshop_git_deployment_id` | `ai-workshop` | Stable identifier used in resource names and tags. |
| `workshop_git_dns_label` | `git` | Default Git subdomain label in the selected hosted zone. |
| `workshop_git_instance_type` | `t3.medium` | An x86_64 EC2 instance type compatible with Ubuntu 24.04. |
| `workshop_git_volume_size` | `30` | Encrypted gp3 root volume size in GiB, from 8 to 16384. |
| `workshop_git_vpc_cidr` | `10.77.0.0/16` | IPv4 VPC network with a prefix length from 16 to 28. |
| `workshop_git_subnet_cidr` | `10.77.1.0/24` | IPv4 subnet inside the VPC with a prefix length from 16 to 28. |
| `workshop_git_must_change_password` | `True` | Require newly created users to change their password at first login. |
| `workshop_git_private_dir` | `{{ playbook_dir }}/private` | Dedicated controller directory whose permissions the role manages as 0700. |
| `workshop_git_password_file` | `{{ workshop_git_private_dir }}/student-passwords.json` | Controller file that retains initial student passwords with mode 0600. |
| `workshop_git_output_file` | `{{ workshop_git_private_dir }}/git-access.json` | Controller access sheet containing server details and initial passwords. |
| `workshop_git_timeout` | `1200` | SSH connection timeout in seconds. |
| `workshop_git_gitea_version` | `28.1.0` | Pinned Gitea binary release installed by the upstream role. |
| `workshop_git_ssh_private_key_file` | `{{ workshop_git_private_dir }}/{{ workshop_git_deployment_id }}_ed25519` | Generated instructor SSH key on the controller. Preserve it across reruns. |
| `workshop_git_ssh_cidr` | `` | SSH source network. Empty discovers the instructor public IPv4 address and uses its /32. |
| `workshop_git_acme_email` | `` | Optional contact address for Let's Encrypt renewal notices. |
| `workshop_git_aws_account` | `Required` | Single AWS account and region for the Gitea instance. |
| `workshop_git_teams` | `Required` | Organization and permission group names mapped to lists of student usernames. Any nonempty number of teams is supported. |
| `workshop_git_admin_user` | `instructor` | Separate instructor site administrator, excluded from student teams. |
| `workshop_git_team_permission` | `write` | Repository permission granted to each organization group. |
| `workshop_git_repository_name` | `netbox-migration` | Private starter repository created in each organization. |

## Role entry points

`main` validates inputs, reads saved passwords, discovers AWS state, and provisions the instance. `configure` installs Gitea over SSH, calls the upstream role's local-user tasks, and manages organization permissions through the Gitea API. `report` writes the instructor access sheet on the controller. The supplied `site.yml` runs these in order.

The role uses native Ansible modules, filters, and lookups. Upstream Gitea handlers manage the service. The role treats named organization memberships as authoritative and leaves organizations omitted from the dictionary untouched.

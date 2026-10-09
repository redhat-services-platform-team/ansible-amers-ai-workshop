# workshop_git

Deploy one Gitea server per AWS environment and create every student on every server. Each server runs Amazon Linux 2023, Gitea with SQLite, and Caddy with HTTPS. The role manages dedicated EC2 networking, an instance role, Route 53 records, and encrypted student credential parameters.

## Requirements

Run the role on the controller with `connection: local` and `gather_facts: false`. Use Ansible Core 2.19 through 2.21, Python and SDK dependencies from `../../requirements.txt`, and AWS collections from `../../requirements.yml`. The provisioned server must use the role's x86_64 Amazon Linux 2023 AMI.

Each account needs a publicly delegated Route 53 hosted zone and instructor permissions to manage EC2, IAM, SSM, and DNS. The role uses SSM instead of SSH. Ports 80 and 443 must be reachable for Caddy certificate issuance and student access.

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `workshop_git_aws_environments` | `Required` | AWS accounts and regions in which to deploy Git servers. |
| `workshop_git_student_ids` | `Required` | Student usernames to create on every server. |
| `workshop_git_discover_only` | `false` | Read AWS state and validate inputs without provisioning or writing files. |
| `workshop_git_deployment_id` | `ai-workshop` | Stable identifier used in resource names, tags, and parameter paths. |
| `workshop_git_dns_label` | `git` | Default Git subdomain label in each selected hosted zone. |
| `workshop_git_instance_type` | `t3.medium` | An x86_64 EC2 instance type compatible with Amazon Linux 2023. |
| `workshop_git_volume_size` | `30` | Encrypted gp3 root volume size in GiB, from 8 to 16384. |
| `workshop_git_vpc_cidr` | `10.77.0.0/16` | IPv4 VPC network with a prefix length from 16 to 28. |
| `workshop_git_subnet_cidr` | `10.77.1.0/24` | IPv4 subnet inside the VPC with a prefix length from 16 to 28. |
| `workshop_git_students_are_admins` | `true` | Grant administrator privileges to newly created Gitea users. |
| `workshop_git_must_change_password` | `true` | Require newly created users to change their password at first login. |
| `workshop_git_gitea_image` | `docker.gitea.com/gitea:28.1.0` | Pinned Gitea container image to deploy. |
| `workshop_git_caddy_image` | `docker.io/library/caddy:2.11.7` | Pinned Caddy container image to deploy. |
| `workshop_git_private_dir` | `{{ playbook_dir }}/private` | Dedicated controller directory whose permissions the role manages as 0700. |
| `workshop_git_password_file` | `{{ workshop_git_private_dir }}/student-passwords.json` | Controller file that retains initial student passwords with mode 0600. |
| `workshop_git_output_file` | `{{ workshop_git_private_dir }}/git-access.json` | Controller access sheet containing server details and initial passwords. |
| `workshop_git_timeout` | `1200` | SSM registration and command timeout in seconds, from 30 to 172800. |

Each AWS environment dictionary requires `name`, `region`, `access_key`, and `secret_key`. Optional keys are `session_token`, `hosted_zone_id`, `hosted_zone_name`, and `dns_label`. Names must start with a lowercase letter and contain at most 24 lowercase letters, digits, or hyphens. Select a hosted zone explicitly when the account has multiple public zones.

Student IDs are unique ignoring case and contain 1 to 40 letters or digits, with single internal dots, underscores, or hyphens. Gitea's reserved usernames are rejected. DNS labels contain 1 to 63 letters, digits, or internal hyphens.

Keep deployment and environment names stable across runs. Use an x86_64 instance type. The default `t3.medium` uses standard CPU credits. Password and output files must have different paths. Custom file parents must already exist or be creatable by the controller user. The role changes permissions only on its dedicated `workshop_git_private_dir` and generated files; it preserves other existing parent directory permissions.

## Example playbook

```yaml
---
- name: Deploy workshop Git servers
  hosts: localhost
  connection: local
  gather_facts: false
  vars:
    workshop_git_aws_environments:
      - name: demo-a
        region: us-east-2
        access_key: "{{ lookup('ansible.builtin.env', 'AWS_ACCESS_KEY_ID') }}"
        secret_key: "{{ lookup('ansible.builtin.env', 'AWS_SECRET_ACCESS_KEY') }}"
    workshop_git_student_ids:
      - student01
      - student02
  roles:
    - workshop_git
```

Set `roles_path` to the directory containing this role. See the [instructor guide](../../README.md) for dependency installation, private inputs, and playbook commands.

## Reruns and password recovery

The role reuses AWS resources and initial passwords, creates missing student accounts, and leaves existing Gitea passwords and privileges unchanged. Students can change their password after first login. The access sheet retains their initial passwords.

Keep a backup of `student-passwords.json`. Before provisioning, discovery reads the names of existing credential parameters without decrypting their values. If any requested student has a parameter but no saved password, the role stops before it changes AWS resources or local password state. It also stops if an existing instance has no password file. Restore the original file before rerunning. These checks depend on retaining the deployment's SSM parameters and resource tags.

Container image or configuration changes recreate the affected container while retaining its data. The Caddy container digest includes its configuration contents, so a failed update retries on the next run. Removing students from the inputs does not delete existing accounts or parameters.

## Check mode

Check mode and `workshop_git_discover_only: true` run input validation and read AWS state. They create no resources or password files. They do not predict provisioning changes or test remote container startup. AWS credentials and dependencies are still required.

## Rollback and cleanup

The role does not perform automatic rollback or teardown. An interrupted deployment can leave billable resources; rerun with the same inputs and saved passwords after resolving the failure. Restore prior image settings to roll back containers. Back up Gitea data before changes that might migrate its database; an older image may require a matching database backup.

Follow the [cleanup instructions](../../README.md#cleanup) to remove deployment resources. Preserve the preexisting hosted zone. Terminating the instance deletes its root volume and repositories. Back up `/opt/workshop-git` and Caddy's Docker volumes before teardown if those data must survive.

## Author and license

Maintained by the Red Hat Services Platform Team. The repository has no declared redistribution license. Role metadata uses `Proprietary` to reflect that status.

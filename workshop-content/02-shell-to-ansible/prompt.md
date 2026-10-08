Migrate the legacy Python NetBox installer into a maintainable Ansible project.

Read these source files:
- workshop-content/02-shell-to-ansible/legacy/install_netbox.py
- workshop-content/02-shell-to-ansible/legacy/.env.example

The script installs and reconciles a standalone NetBox stack on a dedicated CentOS Stream 10 host. Its fictional maintainer comments are part of the workshop story; use the executable code to establish behavior.

Start with a short plan, including a behavior map and any unresolved decisions. Then implement the project under the output directory supplied with this prompt. Do not restructure the rest of the workshop repository or modify the legacy inputs.

Requirements:
- Use site.yml targeting the netbox_lab inventory group with privilege escalation on the managed host. The RHEL or macOS control workstation is not the deployment target.
- Use tasks or roles, templates, variables, and handlers where they make the project easier to review. Include inventory.ini.example, vars/example.yml with non-secret inputs, and a README with validation and deployment commands. Add requirements.yml with explicit collection versions if additional collections are required.
- Preserve the script's supported inputs, defaults, validation, package dependencies, PostgreSQL role/database and authentication rules, Valkey, NetBox release layout and service account, application configuration, administrator bootstrap, systemd services, Nginx, TLS modes, SELinux, optional firewall changes, and readiness checks.
- Explain how NETBOX_* inputs map into Ansible variables and their precedence. An intentional change from .env/environment handling must be documented rather than silently lost.
- Persist generated credentials and the selected release across runs. Protect secrets at rest and with no_log where needed. Do not regenerate or rotate secrets on reruns, or silently upgrade a managed release. Refuse to adopt an unmanaged /opt/netbox directory. Describe concurrent-run protection.
- Prefer idempotent Ansible modules and fully qualified collection names. Explain unavoidable commands, their change detection, and their check-mode behavior. Use handlers for changes that require reloads or restarts. Do not use changed_when: false to conceal actual mutations.
- Preserve useful safeguards; identify security limitations in the legacy defaults and local readiness probe. Do not disable SELinux, weaken authentication, or invent new infrastructure.
- Keep real credentials out of generated examples, repository files, prompts, and logs. Do not execute the Python installer or run a deployment during generation.

Definition of done for this generation exercise:
- The Ansible project and its README exist in the requested output directory.
- ansible-playbook -i inventory.ini.example --syntax-check site.yml passes from that project directory using the existing Ansible installation, once declared collection dependencies are available.
- A short coverage report maps every installer stage to the generated files, identifies behavior changes and gaps, and distinguishes static checks from untested runtime claims.
- Rerun behavior is explicit for credentials, release selection, migrations, configuration, and service restarts.
- Report checks performed and any checks that could not run. Deployment and actual idempotency remain unverified until tested on a disposable CentOS Stream 10 host.

Migrate the legacy Python NetBox installer into an Ansible project that another maintainer can review and run.

Read these source files:

- workshop-content/02-shell-to-ansible/legacy/install_netbox.py
- workshop-content/02-shell-to-ansible/legacy/.env.example

The script installs and reconciles a standalone NetBox stack on a dedicated CentOS Stream 10 host. The maintainer comments are workshop fiction. Read the code to determine behavior.

Start with a short plan that maps the installer stages and lists unresolved decisions. Create the project in the output directory supplied with this prompt. Keep the legacy inputs and the rest of the workshop repository unchanged.

Requirements:

- Use site.yml targeting the netbox_lab inventory group. Use privilege escalation on the managed host. The RHEL or macOS workstation runs Ansible; deployment uses a dedicated CentOS Stream 10 host.
- Organize the project with tasks or roles, templates, variables, and handlers as needed. Include inventory.ini.example, vars/example.yml with non-secret inputs, and a README with validation and deployment commands. Declare additional collections and their versions in requirements.yml if needed.
- Preserve the supported inputs, defaults, and validation rules. Account for package dependencies, PostgreSQL role and database setup, authentication rules, and Valkey.
- Preserve the NetBox release layout, service account, application configuration, admin bootstrap, and systemd services.
- Account for Nginx, all TLS modes, SELinux, optional firewall changes, and readiness checks.
- Map NETBOX_* inputs to Ansible variables and explain their precedence. Document any changes to .env parsing or environment handling.
- Reuse generated credentials and the selected release across runs. Protect stored secrets and use no_log for tasks that could expose them. Reject secret rotation, unsupported release changes, and adoption of an unmanaged /opt/netbox directory. Describe how concurrent runs are prevented.
- Prefer idempotent Ansible modules and fully qualified collection names. For unavoidable commands, explain change detection and check-mode behavior. Use handlers for required reloads and restarts. Do not hide real changes with changed_when: false.
- Preserve the source safeguards and identify limitations in its defaults and local readiness probe. Do not disable SELinux, weaken authentication, or add unrelated infrastructure.
- Keep real credentials out of examples, repository files, prompts, and logs. Do not execute the Python installer or deploy during generation.

Definition of done for generation:

- The project and README exist in the requested output directory.
- After declared collection dependencies are available, ansible-playbook -i inventory.ini.example --syntax-check site.yml passes from that directory using the existing Ansible installation.
- A short report maps every installer stage to the generated files and lists behavior changes and missing implementation details. Separate static review from runtime checks that have not occurred.
- Explain what a second run does to credentials, the selected release, migrations, configuration, and services.
- Report the checks completed and those that could not run. Deployment and actual idempotency remain unverified until tested on a disposable CentOS Stream 10 host.

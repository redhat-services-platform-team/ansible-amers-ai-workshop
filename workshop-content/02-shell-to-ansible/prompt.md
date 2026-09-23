Convert the legacy shell script into a minimal Ansible playbook.

Source script:
- workshop-content/02-shell-to-ansible/legacy/configure-workshop-app.sh

Constraints:
- Produce a single playbook file (suggested path: workshop-content/02-shell-to-ansible/output/<your-name>/site.yml).
- Use localhost with connection: local; gather_facts: false is acceptable.
- Prefer Ansible modules over command/shell when a module exists.
- Use fully qualified collection names (FQCN) for modules you add.
- Do not restructure the rest of the workshop repository.

Definition of done:
- ansible-playbook --syntax-check on your playbook passes.
- The playbook should be idempotent in intent (a second run should not require repeated destructive changes).
- Keep scope limited to what the shell script does (app directory + config file + status message).

Start with a short plan (3 bullets max), then provide the minimal diff.

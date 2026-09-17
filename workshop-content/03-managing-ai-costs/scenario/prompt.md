Fix the Ansible play in site.yml for idempotency and basic best practices.

Constraints:
- Work only in site.yml and group_vars/all.yml unless you must read one other file—ask before widening scope.
- Prefer Ansible modules over command/shell when a module exists.
- Use FQCN for any module you add or change.
- Do not add new roles or restructure the workshop repo.

Definition of done:
- ansible-playbook --syntax-check on site.yml passes.
- A second run should not show unnecessary changed tasks (explain check mode or logical reasoning if no inventory is available).

Start with a short plan (3 bullets max), then provide the minimal diff.

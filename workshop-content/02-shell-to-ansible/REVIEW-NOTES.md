# Module 2 review notes

## Current scenario

Lab 2 migrates `legacy/install_netbox.py` and `legacy/.env.example`, copied from `~/netbox-python`.
The copied Python script has fictional comments about fifty maintainers and an undocumented company-critical deployment.
Only comments changed; its Python AST matches the original.
The example environment file is unchanged and contains blank secret values.

The previous shell script and toy reference playbook have been removed.
The existing module directory and Antora page filenames remain stable to preserve links.
The page title, navigation, overview, canonical prompt, Lab 1 handoff, and Module 3 dependencies now describe Python-to-Ansible migration.

## Exercise design

- Generate separate Ansible projects for Model A and Model B using identical legacy inputs, migration checklist, and prompt.
- Use the existing RHEL/macOS Ansible control environment. Target the script's supported dedicated CentOS Stream 10 managed host.
- Require behavior coverage, persistent secrets and release state, clear input mapping, modules/templates/handlers, explicit command exceptions, and project instructions.
- The base definition of done is static generation, syntax validation, and an honest coverage report. Actual installation and idempotency remain unverified without a disposable target.
- Keep deployment optional and separate from model-generation timing. Use clean, independent target baselines.
- Preserve Module 3's fresh run directories and turn cap. Reaching the cap with gaps is an incomplete result, not a successful migration.

## Remaining delivery review

- Pilot the proposed 60 to 90 minutes and choose a common generation time limit.
- Decide whether the workshop provides disposable CentOS Stream 10 VMs for optional deployment validation.
- Confirm approved model assignments and collection-installation access.
- Validate generated projects on real disposable targets before treating any output as a deployable reference solution.

## Shared dependencies

Changes to the source inputs, canonical prompt, or benchmark stopping rule require review of the Module 3 learner page, facilitator talk track, deck outline, and scorecard.

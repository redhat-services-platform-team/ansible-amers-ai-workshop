# Module 2 review notes

## Current scenario

Lab 2 migrates `legacy/install_netbox.py` and `legacy/.env.example`, copied from `~/netbox-python`.
The script's fictional comments describe fifty people maintaining a company-critical installer without a reliable handover.
The comments have prank names, full timestamps, and inconsistent formatting.
The Python AST matches the original. The environment example is unchanged and has blank secret values.

The previous shell script and toy reference playbook were removed.
The module directory and Antora page filenames stay the same so existing links work.
The lab title, navigation, overview, prompt, Lab 1 handoff, and Module 3 inputs now describe the Python migration.

## Exercise design

- Generate separate Model A and Model B projects with identical inputs, checklist, and prompt.
- Use the existing RHEL or macOS control environment. Target a dedicated CentOS Stream 10 host, as the source requires.
- Require a report showing where each installer stage is implemented, how inputs map to variables, and how the project preserves secrets and release state.
- Complete generation, syntax validation, and code review in the base exercise. Deployment and second-run behavior need separate runtime testing.
- Keep optional deployment time separate from generation time. Use a fresh VM or restored clean snapshot for each model.
- Use fresh project directories in Module 3. Record incomplete results when its turn limit is reached.

## Review before delivery

- Try the proposed 60 to 90 minutes and choose the same generation time limit for both models.
- Decide whether to supply disposable CentOS Stream 10 VMs for deployment checks.
- Confirm approved models and access to collection installation.
- Test generated projects on disposable targets before offering any as a deployment reference.

## Shared inputs

If the source files, canonical prompt, or stopping rule change, update the Module 3 learner page, talk track, deck outline, and scorecard together.

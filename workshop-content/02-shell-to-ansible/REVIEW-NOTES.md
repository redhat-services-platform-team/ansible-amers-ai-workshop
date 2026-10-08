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

- Learners write and send their own first prompt before consulting `prompt.md`.
- Offer the supplied prompt as a resource after that attempt. Learners can borrow requirements, edit it, or compare a separate run.
- Encourage follow-up requests and changes to approved models, file context, and interaction modes. Save prompts, output, and observations under `attempt-1/` and optional `attempt-2/` folders.
- Accept plans and partial conversions when learners can explain what they tried and what remains. Tool familiarity and review are the completion goals.
- Use the existing RHEL or macOS control environment. Optional deployment targets a dedicated disposable CentOS Stream 10 host.
- Keep Module 3's fixed-prompt comparison separate. Its inputs, run directories, and turn limit remain unchanged.

## Review before delivery

- Try the proposed 45 to 60 minute exploration and check whether new users have enough time for follow-up requests.
- Decide whether to supply disposable CentOS Stream 10 VMs for deployment checks.
- Confirm approved models and access to collection installation.
- Test generated projects on disposable targets before offering any as a deployment reference.

## Shared inputs

If the source files, canonical prompt, or stopping rule change, update the Module 3 learner page, talk track, deck outline, and scorecard together.

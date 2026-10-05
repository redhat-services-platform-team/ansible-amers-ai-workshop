# Module 4 — Delivering with AI (facilitator)
Learner doc: `documentation/modules/ROOT/pages/04-aws-lab-provisioning.adoc`

**Format:** Random groups of 4. One hour to design/build/test. Five minutes per team to present. Attendees judge.

**Prize:** 100 Reward Zone points, split across the winning team.

## Before the session

- [ ] Create remote branches from current `main` for each team you expect, named `group_1`, `group_2`, … (`git checkout -b group_N main && git push -u origin group_N`). Extra unused branches are fine.
- [ ] Confirm attendees can log in to [catalog.demo.redhat.com](https://catalog.demo.redhat.com/).
- [ ] Catalog item (share this URL): [AWS Blank Open Environment](https://catalog.demo.redhat.com/catalog/babylon-catalog-prod?item=babylon-catalog-prod/sandboxes-gpte.sandbox-open.prod)
- [ ] Print or share `judging-scorecard.adoc`.
- [ ] Decide Salesforce / purpose answers for the order form (recommend **Practice / Enablement**, region **us-east-2**, workshop UI **off**).
- [ ] Remind: one RHDP order **per team**, not per person.
- [ ] Randomly assign groups of four and announce team numbers that match branch names.

## Timing (about 90 minutes plus presentations)

| Minutes | Segment |
|---------|---------|
| 0–10 | Brief, groups, branches, catalog walkthrough |
| 10–20 | Teams order RHDP; wait for credentials (~10 min provision) |
| 20–80 | **One-hour clock** — design, Ansible, deploy, test |
| 80–85 | Time called — commit and push `group_N` only |
| 85+ | 5 minutes per team + judging + Reward Zone |

If RHDP is slow, start the hour when the first teams have keys, or park architecture discussion during provision.

## What you say

1. This is not a scripted architecture. Requirements are only: fault tolerant, Ansible for app and all AWS, code on `group_N` when time is called.
2. Work independently. No sharing playbooks or AWS keys across teams.
3. Prefer small instance types; RHDP charges the orderer’s cost center. Delete the service after demos.
4. Cursor AI is allowed. Secrets are not allowed in git.

## RHDP order form (current catalog UI)

- Activity: Practice / Enablement
- Purpose: whatever you standardize for enablement
- Salesforce ID or “I'll provide the Salesforce ID within 48 hours”
- Region: us-east-2
- Enable workshop user interface: off
- Start: now
- Confirm cost warning, then Order — do not place a second order unless the first fails

Auto-stop defaults to hours, not minutes; if instances stop mid-lab, disable auto-stop on the service.

## After presentations

- Collect scorecards; break ties on “met requirements” then “Ansible best practices.”
- Ask teams to destroy AWS resources and delete the RHDP service.
- Do not merge `group_*` branches to `main` unless you explicitly want those demos in the workshop repo.

## Session log

- 2026-10-05 — Initial talk track for RHDP AWS Blank Open Environment team challenge.

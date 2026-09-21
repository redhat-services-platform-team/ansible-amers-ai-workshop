# Module 2 — review notes (scaffold from Module 3 / cost lab work)

**Owner:** Person building full Module 2 Antora lab. **Do not delete** until merged into final Module 2 docs.

## What we added (assumptions)

| Item | Purpose |
|------|---------|
| `legacy/configure-workshop-app.sh` | Single legacy script for shell→Ansible exercise |
| `prompt.md` | **Canonical migration prompt** — Module 3 reuses this verbatim for A/B/C model runs |
| `README.adoc` | Paths for learner output under `output/<name>/` |
| `documentation/modules/ROOT/pages/02-shell-to-ansible.adoc` | Minimal step-by-step lab (learner-first); expand, don’t replace tone |

## What Module 3 depends on

- **Same script:** `legacy/configure-workshop-app.sh`
- **Same prompt:** `prompt.md`
- **Scorecard rows:** “Module 2 — Model A/B” in `workshop-content/03-managing-ai-costs/lab-scorecard.adoc`

If you change the script path, prompt text, or definition of done, update:

- `documentation/modules/ROOT/pages/03-managing-ai-costs.adoc`
- `workshop-content/03-managing-ai-costs/facilitator-talk-track.md`
- `workshop-content/03-managing-ai-costs/deck-slide-outline.md`

## Open questions for review

1. **Script realism** — Is `configure-workshop-app.sh` the right size/story for customer engagements, or should we swap in a multi-file bash example?
2. **Output layout** — We assumed `output/<learner>/site.yml` and `run-a|b|c/` for Module 3; OK for gitignore / facilitator grading?
3. **Model names** — Antora uses “Model A / B / C” placeholders; align with deck and org-approved model list.
4. **Validation** — Do we require `ansible-playbook --check` against localhost, or syntax-check only (current)?
5. **Module 2 compare section** — We stubbed a simple table; add rubric (idempotency, FQCN, readability) when you flesh out §5.
6. **Remove duplicate content** — Module 2 overview is minimal; long-form Ansible migration teaching can live in slides or facilitator notes, not Antora essay.

## Removed from Module 3 (do not resurrect without discussion)

- Idempotency-only scenario under `workshop-content/03-managing-ai-costs/scenario/` (playbook refactor). Cost lab is **same migration task as Module 2**, not a second Ansible exercise.

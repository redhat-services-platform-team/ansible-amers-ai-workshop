# Managing AI Costs — deck outline (build slides here)

_Use this file to author the slide deck. Antora Module 3 references these slide numbers/titles; update numbers here if the deck order changes._

Facilitator depth: `facilitator-talk-track.md`. Learner steps: `documentation/modules/ROOT/pages/03-managing-ai-costs.adoc`.

---

## Slide 1 — Title

**Title:** Managing AI Costs in Ansible Automation Work
**On slide:** Workshop title, module number, Ansible + AI motif
**Speaker:** Same automation work can cost very different amounts depending on how you use AI—not whether the answer was “good.”

---

## Slide 2 — Bridge from Module 2 (save money with habits, not luck)

**Title:** You Already Compared Models—Now Compare *Spend*
**On slide:** Module 2 = same Python NetBox installer → Ansible project with two models. Module 3 = same task again with cost lens + dashboard.
**Speaker points:**

- Module 2 proved two models can produce different Ansible from the **same** `install_netbox.py` and **same** prompt.
- The expensive model is not always faster or better; the cheap model is not always good enough.
- Module 3 turns that into dollars and habits: pools, tokens, turns, rework.
- **Efficiency = right model + small context + verify once**—that is how teams stretch included usage without giving up Agent for hard problems.

**Learner hook (say aloud):** “Open your Module 2 scorecard rows—we’ll add Run A/B/C on the identical migration.”

---

## Slide 3 — How Cursor bills (categories, not memorized prices)

**Title:** What You Pay For
**On slide:** Four buckets—plan/pools, model tier, tokens (in/out/cache), surface (Tab / Chat / Agent / CLI)
**Speaker:** Link to current pricing docs; prices change, categories don’t.
**Learner:** None (listen); lab step 1 opens Spending dashboard.

---

## Slide 4 — Usage pools

**Title:** Subscription & Usage Pools
**On slide:** Cursor Models vs Other Models (or enterprise equivalent); billing cycle reset
**Speaker:** Know which pool your default model draws from before a long Agent session.
**Learner:** Record pool names + reset date on scorecard or notebook (lab step 1).

---

## Slide 5 — Model selection

**Title:** Right-Sizing the Model
**On slide:** Cheap/balanced/frontier; Router Cost vs Intelligence (if applicable)
**Speaker:** Use the same Python NetBox migration to measure whether model capability reduces omissions and review work.
**Bridge:** Module 2 Model A/B choices → Module 3 Run A/B/C with **unchanged** `prompt.md`.

---

## Slide 6 — Tokens

**Title:** Input, Output, and Context
**On slide:** Prompt + attachments + history = input; long answers and big diffs = output
**Speaker:** `@` whole repo for one script = self-inflicted cost. Module 2 attaches the installer, example env file, and migration checklist, with a target project directory.
**Learner:** Lab runs attach `legacy/install_netbox.py`, `legacy/.env.example`, and `migration-checklist.adoc`; note exceptions on the scorecard.

---

## Slide 7 — Product surface

**Title:** Tab, Chat, Agent, CLI
**On slide:** Agent = many model calls; good for unknowns, costly for known edits
**Speaker:** Python→Ansible is a defined task—prefer Chat/Agent with a tight prompt, not open-ended “fix my repo.”
**Optional demo:** Same `prompt.md` in-editor vs `cursor-agent` (homework).

---

## Slide 8 — Human factors

**Title:** Retry Loops & Rework
**On slide:** Vague prompt → retry loop; huge diff → review rework
**Speaker:** Ask room who hit retry loop in Module 2; tie to **quality** column on scorecard (merge / edit / discard).
**Efficiency line:** Syntax-check before the second Agent message saves tokens and time.

---

## Slide 9 — Usage patterns (table)

**Title:** Patterns, Not Willpower
**On slide:** Surgical / Architect / Agent marathon / Retry loop (one line each)
**Speaker:** The full NetBox migration needs planning. Keep its context and outputs bounded, and discuss when repeated agent loops stop improving coverage.
**Learner:** Lab step 2—one real example per pattern (workshop or job).

---

## Slide 10 — The scorecard

**Title:** Workshop Scorecard (No Spreadsheet Required)
**On slide:** Columns: model, surface, minutes, turns, quality, notes
**Speaker:** Hold prompt constant; only change model (Run A cost-efficient, B balanced, C escalation).
**File:** `workshop-content/03-managing-ai-costs/lab-scorecard.adoc`

---

## Slide 11 — Live demo checklist

**Title:** Demo: Same Script, Two Models
**On slide:** Script path + prompt path + attach list
**Speaker / demo:**

1. Show `workshop-content/02-shell-to-ansible/legacy/install_netbox.py`, `legacy/.env.example`, and `migration-checklist.adoc`
2. Paste `workshop-content/02-shell-to-ansible/prompt.md`
3. Time-box Run A or review a prepared project; fill coverage and syntax results on the scorecard
4. Compare prepared Run B, or start a new chat if time permits; same inputs and prompt
5. Glance at Spending dashboard (low/medium/high)

Use prepared outputs if a full generation exceeds demo time. Assign remaining runs as homework. No deployments during timed cost runs.

---

## Slide 12 — Three rules

**Title:** Personal Guardrails
**On slide:** Examples—cheap model first; no repo-root context; verify before re-prompt
**Speaker:** Three written rules on scorecard = takeaway for team norms.
**Learner:** Lab final step.

---

## Slide 13 — Balance frame

**Title:** AI Cost vs Delay vs Rework
**On slide:** Three-way tradeoff; “cheap wrong Ansible” = rework cost
**Speaker:** Paying for a frontier model once can beat a day of manual migration; recording unresolved gaps on a capped NetBox migration helps explain review cost.

---

## Slide 14 — Close / Module 4

**Title:** Next: AWS Lab Provisioning
**On slide:** Homework = Run C + rules; Module 4 teaser
**Speaker:** Point to Antora lab steps for async completion.

---

## Sync checklist (when you edit slides)

- [ ] Slide titles match xref labels in `03-managing-ai-costs.adoc` (update slide numbers in Antora if order changes)
- [ ] `facilitator-talk-track.md` minute map still aligns
- [ ] Module 2 script/prompt paths unchanged or all three files above updated

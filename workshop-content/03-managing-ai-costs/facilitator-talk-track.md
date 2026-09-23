# Module 3 — Managing AI Costs (30 min talk + demo)

_Facilitator talk track for Showroom module `documentation/modules/ROOT/pages/03-managing-ai-costs.adoc`._

**Learner doc is step-only.** Teach from this file + `deck-slide-outline.md`; attendees follow Antora steps and the scorecard.

**Total time:** 30 minutes (≈18 min teach, ≈10 min live demo, ≈2 min close)

**Audience outcome:** Can name cost drivers, compare model runs on the **same shell-to-Ansible task** as Module 2, and adopt three personal spend guardrails.

**Repo artifacts:**

- Antora (learners): `documentation/modules/ROOT/pages/03-managing-ai-costs.adoc`
- Deck build guide: `workshop-content/03-managing-ai-costs/deck-slide-outline.md`
- Module 2 task (shared): `workshop-content/02-shell-to-ansible/legacy/configure-workshop-app.sh` + `prompt.md`
- Scorecard: `workshop-content/03-managing-ai-costs/lab-scorecard.adoc`
- Module 2 scaffold / review: `workshop-content/02-shell-to-ansible/REVIEW-NOTES.md`

---

## Before session (5 min prep, not counted)

- [ ] Confirm attendees completed or skimmed Module 2 (two-model migration on the same script).
- [ ] Open Cursor **Spending** dashboard on screen (or enterprise equivalent).
- [ ] Paths ready: `workshop-content/02-shell-to-ansible/legacy/configure-workshop-app.sh`, `prompt.md`.
- [ ] Paste `prompt.md` into a scratch buffer for demo copy-paste.
- [ ] Decide demo models: **Run A** = cost-efficient (Composer / Cost router), **Run B** = balanced — skip Run C live; assign as homework.
- [ ] Slides aligned to `deck-slide-outline.md` (especially slide 2 bridge from Module 2).

---

## Minute-by-minute

| Min | Segment | Say / do |
|-----|---------|----------|
| 0–2 | Hook (deck slide 2) | "Same bash script, same prompt, different model—usage and rework can differ wildly." Show Spending pools. Tie Module 2 Model A/B rows on scorecard to today's Runs A/B/C. |
| 2–6 | Cost factors (slides 3–4) | Plan/pools, model tier, tokens, surface. Team Token Rate on third-party models—link to docs, not prices. |
| 6–8 | Tokens + context (slide 6) | For migration lab: attach **only** the shell script. Repo-root `@` is how teams burn pools on a 20-line script. |
| 8–10 | Surface + human factors (slides 7–8) | Agent vs Chat; retry loops. Ask who hit retry loop in Module 2. |
| 10–12 | Patterns + scorecard (slides 9–10) | Archetypes; hold `prompt.md` constant; only model changes. |
| 12–16 | Optimization frame (slides 12–13) | Cheap model first on small migrations; verify before re-prompt; AI cost vs delay vs rework. |
| 16–26 | Live demo (slide 11) | **Same task as Module 2.** Attach only `configure-workshop-app.sh`. Run A + scorecard; new chat Run B + scorecard; optional dashboard glance. |
| 26–30 | Close (slide 14) | Homework: Run C + three rules on scorecard. Tease Module 4. Q&A. |

---

## Demo script (narration)

1. **Show the legacy script** — `mkdir` + write config; "This is what customers still run; Module 2 and 3 both migrate it with AI."
2. **Read definition of done** from `workshop-content/02-shell-to-ansible/prompt.md` — syntax-check, idempotent intent, minimal scope.
3. **Run A** — paste `prompt.md`; emphasize *identical* prompt for fair compare. Narrate: plan length, diff size, turns to accept.
4. **Check dashboard** — qualitative low/medium/high if dollar delta not visible.
5. **New chat / Run B** — stronger model; same attachment. "Not always cheaper to go smart first on a tiny script."
6. **Debrief** — Module 2 rows vs Run A/B; which they'd ship under a monthly cap.

---

## Lab homework (attendee-facing)

Antora steps 1–8. Minimum if time-boxed in session:

1. Spending snapshot (step 1)
2. Live or async: Runs A and B (steps 4–5); Run C + three rules as homework (steps 6–8)
3. Backfill Module 2 scorecard rows if missing

**CLI variant:**

```bash
cd workshop-content/02-shell-to-ansible
# Example — adjust flags to your installed cursor-agent version
cursor-agent "$(cat prompt.md)" --model <model-id>
```

Remind: agent loops multiply tool+model calls; time-box 15 turns per run.

---

## Antora / deck map

| Talk segment | Deck outline | Learner Antora |
|--------------|--------------|----------------|
| Bridge Module 2 → cost | Slide 2 | Step 7 |
| Cost factors | Slides 3–4 | Step 1 |
| Context / tokens | Slide 6 | Steps 3–6 (attach list) |
| Patterns | Slide 9 | Step 2 |
| Scorecard + demo | Slides 10–11 | Steps 3–6 |
| Rules + tradeoff | Slides 12–13 | Steps 7–8 |
| Close | Slide 14 | Next Steps |

---

## Fallbacks

- **No dashboard access:** use turns + wall clock + diff size as proxies; discuss enterprise reporting separately.
- **Plans without frontier models:** Run C = escalation model org approves, or Run B with Agent instead of Chat.
- **Module 2 incomplete:** attendees still run A/B/C on script + `prompt.md`; Module 2 scorecard rows stay blank.
- **Short on time:** cut Run B live; assign full lab async.

---

## Session log

- 2026-09-17 — Initial talk track (idempotency scenario).
- 2026-09-21 — Aligned to Module 2 shell migration; learner step-only Antora; deck outline added; idempotency scenario removed.

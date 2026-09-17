# Module 3 — Managing AI Costs (30 min talk + demo)

_Facilitator talk track for Showroom module `documentation/modules/ROOT/pages/03-managing-ai-costs.adoc`._

**Total time:** 30 minutes (≈18 min teach, ≈10 min live demo, ≈2 min close)

**Audience outcome:** Can name cost drivers, compare model runs on the same task, and adopt three personal spend guardrails.

**Repo artifacts:**

- Antora: `documentation/modules/ROOT/pages/03-managing-ai-costs.adoc`
- Lab: `workshop-content/03-managing-ai-costs/` (scorecard + idempotency scenario)
- This file: `workshop-content/03-managing-ai-costs/facilitator-talk-track.md`

---

## Before session (5 min prep, not counted)

- [ ] Confirm attendees completed or skimmed Module 2 (two-model migration) — used as usage-pattern baseline.
- [ ] Open Cursor **Spending** dashboard on screen (or enterprise equivalent).
- [ ] Clone/open workshop repo; path ready: `workshop-content/03-managing-ai-costs/scenario/`.
- [ ] Paste `scenario/prompt.md` into a scratch buffer for demo copy-paste.
- [ ] Decide demo models: **Run A** = cost-efficient (Composer / Cost router), **Run B** = balanced frontier — skip Run C live to save time; mention as homework.

---

## Minute-by-minute

| Min | Segment | Say / do |
|-----|---------|----------|
| 0–2 | Hook | "Same prompt, different model — cost and rework can differ by an order of magnitude." Show Spending dashboard pools (Cursor Models vs Other Models). |
| 2–6 | §2 Cost factors | Walk four buckets: plan/pools, model tier, tokens (in/out/cache), surface (Tab/Chat/Agent/CLI). Mention team Token Rate on third-party models — link to current docs, not memorized prices. |
| 6–10 | §2 Exercise framing | Ask room to name one factor they control vs policy. Tie human factors: retry loops, huge `@` context. |
| 10–14 | §3 Usage patterns | Archetypes table: surgical vs architect vs agent marathon vs retry loop. Ask who saw "retry loop" in Module 2. Introduce `lab-scorecard.adoc` columns. |
| 14–18 | §4 Optimization | Right-size model, shrink context, prompt+verify once, agent discipline. Frame productivity balance: AI cost vs delay vs rework. |
| 18–27 | Live demo | **Same task, two models.** Attach only `site.yml` + `group_vars/all.yml`. Run A with cheap model; fill scorecard row. Reset thread; Run B with balanced model; fill row. Optionally show usage tick on dashboard. Show `cursor-agent` only if room uses CLI — same prompt file, compare turns. |
| 27–30 | Close | Attendees complete Run C + three personal rules as homework. Tease Module 4 AWS lab. Q&A. |

---

## Demo script (narration)

1. **Show the broken play** — `command`/`shell` mkdir and echo; "idempotency nightmare, tiny scope — perfect for cost lab."
2. **Read definition of done** from `scenario/README.adoc` — syntax-check, no spurious change.
3. **Run A** — paste `prompt.md`; emphasize *identical* prompt for fair compare. Narrate: plan length, diff size, turns to accept.
4. **Check dashboard** — qualitative "low/medium/high" if dollar delta not visible yet.
5. **New chat / Run B** — stronger model; same attachments. Often fewer turns but heavier usage — "not always cheaper to go smart first."
6. **Debrief table** — ask room which they'd ship under a team monthly cap.

---

## Lab homework (attendee-facing)

Full module procedures in Antora §2–§4. Minimum homework:

1. Three scorecard runs (A/B/C) on the scenario with constant prompt.
2. Three written optimization rules on scorecard.
3. Optional: one Module 2 row backfilled from notes.

**CLI variant:**

```bash
cd workshop-content/03-managing-ai-costs/scenario
# Example — adjust flags to your installed cursor-agent version
cursor-agent "$(cat prompt.md)" --model <model-id>
```

Remind: agent loops multiply tool+model calls; time-box 15 turns per run.

---

## Antora section map

| Talk segment | Antora section |
|--------------|----------------|
| Cost factors | `== 2: Identify Cost Factors` |
| Usage patterns + scorecard | `== 3: Analyze Usage Patterns` |
| Optimization + triple run | `== 4: Optimize AI-Assisted Development Spend` |

---

## Fallbacks

- **No dashboard access:** use turns + wall clock + diff size as proxies; discuss enterprise reporting separately.
- **Plans without frontier models:** Run C = "escalation model your org approves" or repeat Run B with Agent instead of Chat.
- **Short on time:** cut Run B live; describe scorecard and assign full lab async.

---

## Session log

- 2026-09-17 — Initial talk track aligned to filled Antora module and lab scenario.

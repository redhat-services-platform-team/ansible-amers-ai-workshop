# Module 3: Managing AI costs

Allow 30 minutes for teaching and a short generation or review demo.
Learners follow `documentation/modules/ROOT/pages/03-managing-ai-costs.adoc` and record results in `lab-scorecard.adoc`.
Use `deck-slide-outline.md` to build the slides.

The task is the same Python NetBox migration as Module 2.
Learners compare usage, time, and corrections, then write three rules for their own work.
The shared inputs are under `workshop-content/02-shell-to-ansible/`: `legacy/install_netbox.py`, `legacy/.env.example`, `migration-checklist.adoc`, and `prompt.md`.

## Prepare

- [ ] Confirm learners completed or read Module 2.
- [ ] Open Cursor Spending or the enterprise usage report available to the group.
- [ ] Open the shared inputs and copy the canonical prompt for the demo.
- [ ] Choose the approved Run A and Run B models. Assign Run C as homework.
- [ ] Prepare generated projects for comparison if a live run exceeds the available time.
- [ ] Check the slide order against `deck-slide-outline.md`.

## Timing

| Minutes | Slides | What to cover |
|---------|--------|---------------|
| 0 to 2 | 2 | Show the shared task and connect the Module 2 scorecard rows to Runs A, B, and C. |
| 2 to 6 | 3 and 4 | Show plan allowances, model choice, tokens, interaction mode, and usage pools. Refer to current provider documentation for rates. |
| 6 to 8 | 6 | Explain prompt, attachment, and history usage. Show the installer inputs and exclude unrelated files and prior outputs. |
| 8 to 10 | 7 and 8 | Explain agent calls within a user turn. Ask which Module 2 output needed corrections. |
| 10 to 12 | 9 and 10 | Discuss usage patterns and the scorecard. Keep the prompt and inputs constant across runs. |
| 12 to 16 | 12 and 13 | Compare usage with review time and corrections. Ask learners to choose practical rules for future work. |
| 16 to 26 | 11 | Demonstrate one run or compare prepared projects. Record missing behavior and syntax results, then check visible usage. |
| 26 to 30 | 14 | Assign remaining runs and personal rules as homework. Introduce Module 4 and take questions. |

## Demo

1. Show the installer and example inputs. Trace where the source stores credentials and the selected release.
2. Read the definition of done in `prompt.md`. It requires a project, syntax validation, a coverage report, and a description of rerun behavior. Runtime checks remain untested.
3. Start Run A with the unchanged prompt, or show a prepared output. Record elapsed time, user turns, corrections, and missing behavior.
4. Check the dashboard. If the exact spend change is unavailable, record a subjective low, medium, or high usage estimate.
5. Compare a prepared Run B or start a new conversation if time permits. Use the same attachments and prompt.
6. Ask which result learners would accept under a monthly usage limit and what corrections it still needs.

Do not deploy during this comparison. Stop each run at the canonical definition of done or 15 user turns, whichever comes first.
Record incomplete results when the turn limit is reached.

## Homework

Learners complete the dashboard record, Runs A and B, and the Run C comparison if these did not finish in class.
They write three personal rules in the scorecard.
Keep Module 2 rows blank if those runs did not occur.

For an optional CLI comparison, use the same inputs and prompt with the learner's installed `cursor-agent`.
Use its help to select supported flags, and specify the output directory for that run.
Record CLI mode in the scorecard. A user turn can still contain several tool and model calls.

## Slide references

| Talk segment | Deck slides | Learner steps |
|--------------|-------------|---------------|
| Module 2 comparison | 2 | 7 |
| Cost and usage pools | 3 and 4 | 1 |
| Context | 6 | 3 to 6 |
| Usage patterns | 9 | 2 |
| Scorecard and demo | 10 and 11 | 3 to 6 |
| Rules and review cost | 12 and 13 | 7 and 8 |
| Next module | 14 | Next steps |

## Alternatives

- If the dashboard is unavailable, record turns, elapsed time, and diff size. These measurements do not establish spend; discuss enterprise reporting separately.
- If no escalation model is available, use another approved model or repeat Run B in Agent mode. Record the mode change.
- If Module 2 is incomplete, learners can still run the shared task in Module 3. Leave missing Module 2 rows blank.
- If the demo runs out of time, compare prepared outputs and assign the remaining runs as homework.

## Revision history

- 2026-09-17: Wrote the initial talk track with an idempotency scenario.
- 2026-09-21: Aligned the migration task and removed the separate idempotency scenario.
- 2026-10-08: Switched to the Python NetBox installer. Timed generation and static review remain separate from optional VM deployment checks.

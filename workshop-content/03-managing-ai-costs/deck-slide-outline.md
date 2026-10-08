# Managing AI costs: deck outline

Use this outline to build the deck. The Module 3 learner page refers to these slide numbers, so update its references if you reorder the slides.
Use `facilitator-talk-track.md` for delivery notes and `documentation/modules/ROOT/pages/03-managing-ai-costs.adoc` for learner steps.

## Slide 1: Managing AI costs in Ansible work

Introduce the workshop and module. Explain that model choice, attached context, and repeated requests affect usage even when the final Ansible output is similar.

## Slide 2: Compare spending after comparing models

Module 2 let learners try their own prompts while exploring the NetBox migration. Module 3 uses the same installer with the supplied prompt unchanged to compare model runs.
Ask learners to open their Module 2 notes. Explain that those experiments may have different prompts and modes, so their timings are not directly comparable to fixed-prompt runs.

- Keep `install_netbox.py`, `.env.example`, the checklist, and `prompt.md` identical across runs.
- Compare accepted results and omissions, as well as time and turns.
- Check whether a more capable model reduced the corrections needed.

## Slide 3: What you pay for

Show the plan or enterprise allowance, model, token usage, and interaction mode.
Explain input, output, and cached tokens using the current provider documentation.
Use links to current pricing rather than putting fixed prices on the slide.
Learners open the Spending dashboard in lab step 1.

## Slide 4: Usage pools

Show the pool names and billing-period reset date in the dashboard.
Use the names visible in the account, such as Cursor Models or Other Models.
Ask learners to record their own pool names and reset date on the scorecard.

## Slide 5: Choose models for the comparison

Assign a cost-efficient model for Run A, a balanced model for Run B, and an approved escalation model for Run C.
If the account has no escalation model, repeat B using Agent and record the mode change.
Use the supplied `prompt.md` unchanged for all Module 3 runs. Compare whether model choice changes coverage gaps and review time.

## Slide 6: Inputs, outputs, and context

Explain that the prompt, attachments, and conversation history contribute to input usage. Generated text and code contribute to output usage.
Show the lab's input files and output directory.
Attach `legacy/install_netbox.py`, `legacy/.env.example`, and `migration-checklist.adoc`.
Ask learners to record extra attachments and keep prior generated projects out of later runs.

## Slide 7: Chat, Agent, and CLI

Explain that an agent can make several model and tool calls within one user turn.
Keep the migration prompt specific about inputs, output files, and completion checks.
For optional homework, compare the same prompt in the editor and `cursor-agent`.

## Slide 8: Follow-up prompts and corrections

Ask which Module 2 result needed corrections and why.
Show how to read a syntax error or coverage gap before sending another request.
Record manual edits as well as follow-up prompts in the scorecard.

## Slide 9: Usage patterns

Show examples of a narrow request, project planning, a long agent session, and repeated fix requests.
Use the NetBox migration to discuss when planning helps and when another agent loop stops improving coverage.
In lab step 2, learners write an example of each listed pattern from their work or this workshop.

## Slide 10: The scorecard

Show the model, tool and mode, minutes, turns, review decision, and notes columns in `workshop-content/03-managing-ai-costs/lab-scorecard.adoc`.
Keep inputs and the completion rule constant across runs.
Record syntax results, missing behavior, and whether runtime checks occurred.

## Slide 11: Demo the shared migration

1. Show `workshop-content/02-shell-to-ansible/legacy/install_netbox.py`, its `.env.example`, and `migration-checklist.adoc`.
2. Paste `workshop-content/02-shell-to-ansible/prompt.md` and name a Run A output directory.
3. Demonstrate one run within the available time, or review a prepared project. Fill in coverage and syntax results on the scorecard.
4. Compare a prepared Run B, or start a new conversation if time permits. Keep the inputs and prompt unchanged.
5. Check the dashboard and record any visible usage change. If exact spend is unavailable, label the usage estimate as subjective.

Use prepared projects if full generation exceeds the demo time. Assign remaining runs as homework. Keep deployments out of timed cost runs.

## Slide 12: Personal rules

Ask learners to write three rules they will use after the workshop.
Examples include trying a cheaper model before escalating, limiting attachments to relevant files, and reading validation errors before requesting a fix.

## Slide 13: Cost, delay, and corrections

Compare a model's usage with the time spent reviewing and correcting its output.
An inexpensive incomplete migration can need more work before acceptance.
Ask which run learners would choose under a monthly usage limit, and what evidence supports that choice.

## Slide 14: Continue to Module 4

Assign any unfinished model runs and personal rules as homework.
Point to the learner page, then introduce the AWS team challenge in Module 4.

## Review before delivery

- [ ] Slide numbers match the references in `03-managing-ai-costs.adoc`.
- [ ] The talk track's timing still fits the deck.
- [ ] The deck, talk track, and learner page use the same script, prompt, and checklist.

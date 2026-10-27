# Lab 1 supporting files

Follow the [workspace lab](../../docs/01-cursor-workspace.adoc) for installation,
enterprise sign-in, permissions, and local Ansible verification on RHEL or macOS.
These instructions are maintained there rather than duplicated in this README.

The optional examples below and the sample files support that lab.
Commands were originally checked on 2026-10-07 with Codex CLI 0.160.1;
check your installed CLI help after upgrades.

## Optional Codex configuration

### Update Codex policy settings

Cursor users can skip these Codex-specific settings.

Sandbox settings determine file/network access for generated commands. Approval
settings determine when Codex asks before proceeding. `on-request` allows
routine actions inside the sandbox without prompting for every command.
`never` removes approval prompts and returns blocked actions as failures; it
does not grant full access. See
[approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security).

The optional user settings and backup instructions are in the
[workspace lab](../../docs/01-cursor-workspace.adoc). These examples are for reference; the lab does
not require you to change configuration files.

#### Change policy for one session

Flags override normal config defaults for that invocation:

```bash
# Inspect the checkout with a read-only sandbox.
codex -s read-only -a on-request

# Edit within the workspace with human review for escalation requests.
codex -s workspace-write -a on-request

# Allow generated commands to use the network for this workspace session.
codex -s workspace-write -a on-request \
  -c 'sandbox_workspace_write.network_access=true'
```

The network override grants general command network access for that session;
use it when the task requires downloads or remote services. To make this change
persistent, edit `network_access` in the existing `[sandbox_workspace_write]`
table and restart Codex. See [network access](https://learn.chatgpt.com/docs/agent-approvals-security#network-access).

#### Named review profile and project settings

Create a review profile without replacing your base configuration:

```bash
# Copy the example review profile without overwriting an existing file.
cp -n workshop-content/01-codex-workspace/samples/review.config.toml \
  "$HOME/.codex/review.config.toml"
# Start Codex with the review profile layered over your base settings.
codex --profile review
```

`cp -n` preserves an existing profile; inspect or edit it if one already exists.
Current Codex profiles use `~/.codex/<name>.config.toml`. Since 0.134.0,
`[profiles.<name>]` tables and the top-level `profile` selector in `config.toml`
are no longer supported. See [profiles](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles).

Project defaults can live at `<repo>/.codex/config.toml`, using the same policy
keys as the user sample. Inspect that folder before trusting a checkout; project
configuration loads only for trusted projects. CLI overrides take precedence
over project config, then selected profile, then user config. Admin requirements
constrain all of them. See [configuration precedence](https://learn.chatgpt.com/docs/config-file/config-basic#configuration-precedence).

#### Command rules

[samples/workshop.rules](samples/workshop.rules) prompts for `git push` and
forbids `sudo` when evaluating requests to run outside the sandbox. Install it
alongside your user config:

```bash
# Create a directory for optional command-policy rules.
mkdir -p "$HOME/.codex/rules"
# Copy the example rules without overwriting existing workshop rules.
cp -n workshop-content/01-codex-workspace/samples/workshop.rules \
  "$HOME/.codex/rules/workshop.rules"
# Check the rule decision for the command below without executing it.
codex execpolicy check --pretty --rules "$HOME/.codex/rules/workshop.rules" \
  -- git push origin workshop/codex-lab
# Check the rule decision for the command below without executing it.
codex execpolicy check --pretty --rules "$HOME/.codex/rules/workshop.rules" \
  -- sudo dnf install git
```

These checks evaluate policy without executing the commands. Expect `prompt`
for the push and `forbidden` for sudo. Restart Codex after editing rules.
Rules use argument prefixes and are experimental. These two examples are not a
complete command security policy; alternate invocations and commands inside the
sandbox need separate consideration. See [rules](https://learn.chatgpt.com/docs/agent-configuration/rules).

#### Administrator-enforced limits

User config provides defaults. For enforced limits on Linux/macOS, administrators
can manage `/etc/codex/requirements.toml`. The
[sample requirements](samples/requirements.toml) permits `on-request` approvals
and only the `read-only` / `workspace-write` sandbox modes:

```toml
allowed_approval_policies = ["on-request"]
allowed_sandbox_modes = ["read-only", "workspace-write"]
```

Merge this example through the organization's device-management process and
restart Codex. macOS also supports MDM requirements in the `com.openai.codex`
preference domain. User flags cannot bypass active managed requirements; resolve
policy conflicts with the administrator. See
[managed configuration](https://learn.chatgpt.com/docs/enterprise/managed-configuration).

### Codex CLI flags and commands

| Option / command | Purpose | Example |
| --- | --- | --- |
| `-h`, `--help` | Show options for the installed version | `codex --help` |
| `-V`, `--version` | Show CLI version | `codex --version` |
| `-C`, `--cd` | Set the working directory | `codex -C workshop-content/02-shell-to-ansible` |
| `-s`, `--sandbox` | Select command access boundaries | `codex -s read-only` |
| `-a`, `--ask-for-approval` | Select `on-request` or `never` | `codex -a on-request` |
| `-c`, `--config` | Override a TOML key for this run | `codex -c 'approval_policy="on-request"'` |
| `-p`, `--profile` | Select a named config file | `codex -p review` |
| `-m`, `--model` | Select an available model | `codex --model <available-model-id>` |
| `--search` | Enable live hosted web search | `codex --search` |
| `--add-dir` | Add another writable directory | `codex --add-dir ../shared-lab` |
| `--no-alt-screen` | Keep terminal scrollback visible | `codex --no-alt-screen` |
| `resume --last` | Continue the most recent session | `codex resume --last` |
| `exec` | Run a noninteractive task | `codex exec -s read-only "Explain this repository"` |
| `exec --json` | Emit JSONL events | `codex exec --json -s read-only "Explain this repository"` |
| `exec -o` | Save the final answer | `codex exec -s read-only -o /tmp/codex-summary.txt "Explain this repository"` |

Replace `<available-model-id>` with a model available to your account. Use
`codex exec --help` for subcommand options. Noninteractive tasks should be scoped
so they can finish within the configured permissions. `--search` controls hosted
web search separately from shell networking. See the
[CLI reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli).

`danger-full-access` removes the command sandbox. The
`--dangerously-bypass-approvals-and-sandbox` flag also skips approval prompts;
reserve it for an independently isolated environment under an approved policy.
The workshop examples use restricted modes. Older examples with `--full-auto`,
`--ask-for-approval untrusted`, or `on-failure` do not match this CLI's help.

### Give Codex Ansible-specific instructions

[samples/AGENTS.md.example](samples/AGENTS.md.example) shows reusable working
agreements. Review and merge them into a repository-root `AGENTS.md`, or copy
them if the repository has none. Codex reads global and project instruction
files when starting a session; restart after changes. These instructions guide
behavior and do not enforce sandbox permissions. See
[AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

Try a focused task in a workspace-write session:

```text
Read workshop-content/02-shell-to-ansible/legacy/install_netbox.py.
Read workshop-content/02-shell-to-ansible/legacy/.env.example too. Explain the assumptions,
then propose an idempotent Ansible project for a dedicated CentOS Stream 10 host.
Wait for my choice of output directory before creating the project. My RHEL or
macOS workstation is the control host. After generation, use my existing Ansible
installation for syntax validation. Report the diff and validation results. Do not connect to managed hosts for this task.
```

Review `git diff` and `git status --short` after the task. Confirm the output is
appropriate before committing it or running a playbook against a lab inventory.

## Troubleshooting

- If `codex` is not found, open a new terminal. For the standalone installer, check `~/.local/bin/codex` and your `PATH`. For Homebrew, check its executable path with `command -v codex`.
- If login fails over SSH, use `codex login --device-auth` with device login enabled, or follow the authentication guide's SSH callback forwarding steps.
- If Codex rejects a policy flag, check the installed CLI's help and your organization's requirements. Update older configuration formats before retrying.
- If project settings do not apply, check the working directory and whether the checkout is trusted. Check for CLI flags that override them.
- If a shell download or Ansible connection is blocked, check command network access, sandbox permissions, and host connectivity. Hosted web search does not enable shell networking.
- If Ansible is missing, restore its installation or activate its environment. Ask the instructor for help if it remains unavailable.

## Included assets

| File | Purpose |
| --- | --- |
| [playbooks/hello.yml](playbooks/hello.yml) | Local runtime verification for RHEL and macOS |
| [Cursor CLI config](samples/cursor/cli-config.json) | CLI allowlist and deny examples to merge with existing settings |
| [Cursor desktop permissions](samples/cursor/permissions.json) | Auto-review guidance to merge with existing settings |
| [config.toml](samples/config.toml) | User defaults for workspace edits with human approvals |
| [review.config.toml](samples/review.config.toml) | Named read-only review profile |
| [workshop.rules](samples/workshop.rules) | Example command escalation rules |
| [requirements.toml](samples/requirements.toml) | Administrator limits for Linux/macOS |
| [AGENTS.md.example](samples/AGENTS.md.example) | Ansible working agreements to review and adopt |

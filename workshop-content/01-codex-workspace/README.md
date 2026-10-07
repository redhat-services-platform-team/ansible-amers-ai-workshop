# Lab 1 — ChatGPT / Codex Workspace Setup

Set up Codex on **RHEL** or **macOS (OS X)**, connect your account, and choose the
permissions for an Ansible workshop repository. Use ChatGPT for explanations and
prompt development, and Codex CLI for working with local files and commands.

Commands and configuration were checked against official OpenAI documentation
on **2026-10-07** and local **Codex CLI 0.160.1** help. Check `codex --help` after
upgrading; available models and features depend on your account and workspace.

## Choose your interface

| Interface | RHEL | macOS | Workshop use |
| --- | --- | --- | --- |
| ChatGPT in a browser | Open `https://chatgpt.com` | Open `https://chatgpt.com` | Discuss Ansible and review supplied code |
| Codex CLI | Install below | Install below | Inspect and edit the local checkout; run installed tools |
| ChatGPT desktop app | Use the CLI/browser route for this RHEL lab | Download from `https://chatgpt.com/download/`, install, and sign in | Choose Codex and open the workshop folder |

Browser ChatGPT does not automatically see your local checkout. Supply the
relevant files or excerpts. The local Codex `config.toml` examples below apply to
Codex local execution; they do not configure ordinary browser chats. For desktop
Codex, inspect the permissions control beneath the composer before running work.
See the [desktop app guide](https://learn.chatgpt.com/docs/app) and
[sandboxing guide](https://learn.chatgpt.com/docs/sandboxing).

## Install on RHEL

Use a regular user account on a workshop host. These host setup commands run in
your own terminal, before starting Codex. This route uses the standalone Linux
installer and does not require Node.js. It assumes a registered RHEL system with
enabled repositories and outbound HTTPS access.

```bash
sudo dnf install -y git curl tar gzip
uname -m
```

The installer supports Linux `x86_64` and `aarch64`. Download and inspect it, then
run it as your user:

```bash
curl -fsSL https://chatgpt.com/codex/install.sh -o /tmp/codex-install.sh
less /tmp/codex-install.sh
sh /tmp/codex-install.sh
export PATH="$HOME/.local/bin:$PATH"
codex --version
codex --help
```

The default install directory is `~/.local/bin`. The installer configures your
shell path; open a new terminal afterward. To update a standalone installation,
download and run the installer again. Use the
[official CLI installation guide](https://learn.chatgpt.com/docs/codex/cli).

Codex uses a Linux sandbox based on `bwrap` and `seccomp`. Restricted containers
or host policies can prevent it from starting. If that occurs, capture the error
and work with the lab administrator on the supported environment; keep SELinux
enabled. See [OS sandbox details](https://learn.chatgpt.com/docs/agent-approvals-security#os-level-sandbox).

## Install on macOS (OS X)

Open Terminal. If Git is unavailable, install Apple's Command Line Tools and
finish the installer dialog:

```bash
xcode-select --install
```

Choose **one** Codex installation method. If Homebrew is already installed:

```bash
brew install --cask codex
codex --version
codex --help
```

Update that installation with `brew upgrade --cask codex`.

Alternatively, use the standalone installer without Homebrew:

```bash
curl -fsSL https://chatgpt.com/codex/install.sh -o /tmp/codex-install.sh
less /tmp/codex-install.sh
sh /tmp/codex-install.sh
export PATH="$HOME/.local/bin:$PATH"
codex --version
```

The standalone CLI installer supports Apple Silicon and Intel macOS. Use the
installer again to update, and open a new terminal to pick up its shell path
changes. macOS Codex sandboxing uses Seatbelt. See
[CLI installation](https://learn.chatgpt.com/docs/codex/cli) and
[OS sandbox details](https://learn.chatgpt.com/docs/agent-approvals-security#os-level-sandbox).

For an existing user-managed Node.js/npm environment on either OS, another
installation option is `npm install -g @openai/codex`; the same command updates
it. Avoid mixing installation methods. Use `command -v codex` to see which
installation your shell runs.

## Sign in and open the workspace

On a machine with a browser:

```bash
codex login
codex login status
```

Choose **Sign in with ChatGPT** and use the account/workspace assigned for the
workshop. For a RHEL SSH session without a local browser:

```bash
codex login --device-auth
```

Open the printed link on your laptop and enter the one-time code. Device login
must be enabled in your account security settings or by your workspace admin.

If the workshop uses an API key, obtain it through your approved secret process,
make it available as `OPENAI_API_KEY`, and pass it through stdin:

```bash
printenv OPENAI_API_KEY | codex login --with-api-key
```

API key usage is billed to the OpenAI Platform account separately from ChatGPT
plan usage. Treat `~/.codex/auth.json`, if present, as a credential; keep it out
of the repository. See [authentication](https://learn.chatgpt.com/docs/auth).

From an existing checkout, or clone once if needed:

```bash
git clone https://github.com/redhat-services-platform-team/ansible-amers-ai-workshop.git
cd ansible-amers-ai-workshop
git status --short
git switch -c workshop/codex-lab
codex --sandbox read-only --ask-for-approval on-request
```

Start with this prompt:

```text
Read README.adoc and workshop-content/02-shell-to-ansible/README.adoc.
Explain the workshop structure and the prerequisites for converting the legacy
shell script to Ansible. Include differences between a RHEL control host and a
macOS control host. Keep this task to inspection and explanation.
```

In browser ChatGPT, attach those README files and use the same prompt. Add the
legacy script when discussing its conversion. Codex installation does not
install Ansible or provision the later labs; follow their prerequisites before
asking Codex to run validation or connect to hosts.

## Update the policy configuration

Sandbox settings determine file/network access for generated commands. Approval
settings determine when Codex asks before proceeding. `on-request` allows
routine actions inside the sandbox without prompting for every command.
`never` removes approval prompts and returns blocked actions as failures; it
does not grant full access. See
[approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security).

### Persistent user defaults

On both RHEL and macOS, the default user file is `~/.codex/config.toml`. If you
already set a custom `CODEX_HOME`, use its `config.toml` instead. The examples
here assume the default location.

From the repository root, inspect [samples/config.toml](samples/config.toml),
back up any existing settings, and edit the active file:

```bash
mkdir -p "$HOME/.codex"
if [ -f "$HOME/.codex/config.toml" ]; then
  cp "$HOME/.codex/config.toml" "$HOME/.codex/config.toml.backup-$(date +%Y%m%d-%H%M%S)"
fi
${EDITOR:-vi} "$HOME/.codex/config.toml"
```

Merge these keys into the existing TOML, preserving unrelated settings and
avoiding duplicate keys or tables. Put top-level keys before table headers:

```toml
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"
web_search = "disabled"

[sandbox_workspace_write]
network_access = false
```

Restart Codex and use `/permissions` to inspect the active permissions. These
defaults permit workspace edits and local commands; generated shell commands
have network access disabled. Hosted web search has its own setting, which this
sample also disables. Codex itself still needs connectivity to sign in and use
the model service. See [configuration basics](https://learn.chatgpt.com/docs/config-file/config-basic).

### Change policy for one session

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

### Named review profile and project settings

Create a review profile without replacing your base configuration:

```bash
cp -n workshop-content/01-codex-workspace/samples/review.config.toml \
  "$HOME/.codex/review.config.toml"
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

### Command rules

[samples/workshop.rules](samples/workshop.rules) prompts for `git push` and
forbids `sudo` when evaluating requests to run outside the sandbox. Install it
alongside your user config:

```bash
mkdir -p "$HOME/.codex/rules"
cp -n workshop-content/01-codex-workspace/samples/workshop.rules \
  "$HOME/.codex/rules/workshop.rules"
codex execpolicy check --pretty --rules "$HOME/.codex/rules/workshop.rules" \
  -- git push origin workshop/codex-lab
codex execpolicy check --pretty --rules "$HOME/.codex/rules/workshop.rules" \
  -- sudo dnf install git
```

These checks evaluate policy without executing the commands. Expect `prompt`
for the push and `forbidden` for sudo. Restart Codex after editing rules.
Rules use argument prefixes and are experimental. These two examples are not a
complete command security policy; alternate invocations and commands inside the
sandbox need separate consideration. See [rules](https://learn.chatgpt.com/docs/agent-configuration/rules).

### Administrator-enforced limits

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

## Common flags and commands

| Option / command | Purpose | Example |
| --- | --- | --- |
| `-h`, `--help` | Show options for the installed version | `codex --help` |
| `-V`, `--version` | Show CLI version | `codex --version` |
| `-C`, `--cd` | Set the working directory | `codex -C workshop-content/02-shell-to-ansible` |
| `-s`, `--sandbox` | Select command access boundaries | `codex -s read-only` |
| `-a`, `--ask-for-approval` | Select `on-request` or `never` | `codex -a on-request` |
| `-c`, `--config` | Override a TOML key for this run | `codex -c 'web_search="disabled"'` |
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

## Give Codex Ansible-specific instructions

[samples/AGENTS.md.example](samples/AGENTS.md.example) shows reusable working
agreements. Review and merge them into a repository-root `AGENTS.md`, or copy
them if the repository has none. Codex reads global and project instruction
files when starting a session; restart after changes. These instructions guide
behavior and do not enforce sandbox permissions. See
[AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

Try a focused task in a workspace-write session:

```text
Read workshop-content/02-shell-to-ansible/legacy/configure-workshop-app.sh.
Explain its assumptions, then propose an idempotent Ansible conversion.
Wait for my choice of output filename before creating the playbook. Target RHEL
managed nodes and account for macOS as a possible control host. After creating
the playbook, run syntax validation if Ansible is installed. Report the diff
and validation results. Do not connect to managed hosts for this task.
```

Review `git diff` and `git status --short` after the task. Confirm the output is
appropriate before committing it or running a playbook against a lab inventory.

## Troubleshooting

- **`codex: command not found`:** Open a new terminal. For the standalone
  installer, check `~/.local/bin/codex` and the `PATH` above. For Homebrew/npm,
  inspect that package manager's bin path with `command -v codex`.
- **Login cannot complete over SSH:** Use `codex login --device-auth` with device
  login enabled, or the SSH callback forwarding flow in the authentication guide.
- **A policy flag is rejected:** Check the installed CLI's help and managed
  requirements. Update old config/profile formats before retrying.
- **A project config seems ignored:** Confirm the working directory and whether
  the checkout is trusted; inspect higher-priority CLI settings.
- **A shell download or Ansible connection is blocked:** Check command network
  access, sandbox permissions, and host connectivity. Hosted web search does not
  enable shell networking.
- **Ansible is missing:** Complete the later module's control environment setup;
  Codex uses the tools installed where its commands execute.

## Included samples

| File | Purpose |
| --- | --- |
| [config.toml](samples/config.toml) | User defaults for workspace edits with human approvals |
| [review.config.toml](samples/review.config.toml) | Named read-only review profile |
| [workshop.rules](samples/workshop.rules) | Example command escalation rules |
| [requirements.toml](samples/requirements.toml) | Administrator limits for Linux/macOS |
| [AGENTS.md.example](samples/AGENTS.md.example) | Ansible working agreements to review and adopt |

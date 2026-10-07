# Lab 1 — Codex and Cursor Workspace Setup

Set up Codex and Cursor on **RHEL** or **macOS (OS X)** and run Ansible directly
on the workstation. Codex sign-in uses enterprise OAuth/SSO with access to the
assigned enterprise workspace; Cursor uses the approved associate account.
Both tools work with the same checkout and host Python environment.

Full workshop page: [Codex and Cursor Workspace Setup](../../documentation/modules/ROOT/pages/01-cursor-workspace.adoc).

Commands and configuration were checked against official OpenAI documentation
on **2026-10-07** and local **Codex CLI 0.160.1** help. Check `codex --help` after
upgrading; available models and features depend on your account and workspace.

## Choose your interface

| Interface | RHEL | macOS | Workshop use |
| --- | --- | --- | --- |
| Cursor | Install the Linux RPM below | Install the macOS `.dmg` below | Edit the checkout and use Agent with local tools |
| Codex CLI | Install below | Install below | Inspect and edit the local checkout; run installed tools |
| Codex in the ChatGPT desktop app | Optional RPM installation below; unsupported preview on RHEL | Download from `https://chatgpt.com/download/`, install, and sign in through enterprise OAuth | Choose Codex and open the workshop folder |

Desktop Codex is available on Linux through the ChatGPT desktop app preview.
The documented supported desktop distributions are Ubuntu 24.04/26.04 LTS,
Debian 13, Fedora 43/44, and current Arch Linux, on x64 and ARM64. RHEL is not
listed; compatibility of the Fedora RPM with RHEL is not established by that
support list. The optional RPM steps below let you try the desktop app on RHEL
as an **unsupported preview**. See the
[Linux desktop installation and support guide](https://learn.chatgpt.com/docs/linux/linux-app).

On macOS, download and install the ChatGPT desktop app, complete enterprise
OAuth sign-in, select the assigned enterprise workspace, choose Codex, and open
the workshop repository folder. Inspect the permissions control beneath the
composer before running work. See the
[desktop app guide](https://learn.chatgpt.com/docs/app) and
[sandboxing guide](https://learn.chatgpt.com/docs/sandboxing).

## Install the shared host Ansible tools

Use RHEL 9.4+ in the RHEL 9 series, RHEL 10, or macOS. OS package installation
runs in your own terminal. On RHEL 9.4+, install Python 3.12:

```bash
sudo dnf install -y git curl tar gzip less bubblewrap python3.12 python3.12-pip
python3.12 --version
```

On RHEL 10:

```bash
sudo dnf install -y git curl tar gzip less bubblewrap python3 python3-pip
python3 --version
```

Use `python3` instead of `python3.12` when creating the environment below. See the
[RHEL 9 Python guide](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/installing_and_using_dynamic_programming_languages/assembly_installing-and-using-python_installing-and-using-dynamic-programming-languages)
and [RHEL 10 Python guide](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/installing_and_using_dynamic_programming_languages/installing-and-using-python).

On macOS, install Apple's Command Line Tools with `xcode-select --install` if
Git is missing. With [Homebrew](https://brew.sh/) installed:

```bash
brew install python@3.12
python3.12 --version
```

Clone the workshop once, or change to your existing checkout. From the repository
root, create and activate a user-owned environment:

```bash
python3.12 -m venv "$HOME/.venvs/ansible-workshop"
source "$HOME/.venvs/ansible-workshop/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r workshop-content/01-codex-workspace/requirements.txt
ansible-playbook --version
ansible-lint --version
```

[requirements.txt](requirements.txt) pins Ansible 13.4.0 and ansible-lint 26.9.0
for Python 3.12. These community workshop tools install into the user environment,
leaving system Python intact. Activate this environment in each new OS, Cursor,
or Codex desktop terminal before running the labs:

```bash
source "$HOME/.venvs/ansible-workshop/bin/activate"
```

For Codex-generated shell commands, include that activation step in your prompt
or use the environment's absolute executable paths. Desktop launches may not
inherit an already-activated terminal environment.

## Install Codex on RHEL

Use a regular user account on a workshop host. These host setup commands run in
your own terminal, before starting Codex. The CLI route uses the standalone
Linux installer and does not require Node.js. The optional desktop route uses
the Linux preview RPM. Both assume a registered RHEL system with enabled
repositories and outbound HTTPS access.

### Codex CLI — standalone installer

```bash
sudo dnf install -y git curl tar gzip less bubblewrap
uname -m
bwrap --version
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

The `bubblewrap` package supplies `bwrap` for the Linux sandbox; see
[sandbox prerequisites](https://learn.chatgpt.com/docs/sandboxing).
Codex uses a Linux sandbox based on `bwrap` and `seccomp`. Restricted containers
or host policies can prevent it from starting. If that occurs, capture the error
and work with the lab administrator on the supported environment; keep SELinux
enabled. See [OS sandbox details](https://learn.chatgpt.com/docs/agent-approvals-security#os-level-sandbox).

### Desktop RPM — unsupported preview on RHEL

The Linux desktop app is a preview, and **RHEL is not a supported desktop
distribution**. These steps adapt the official Fedora RPM instructions for
RHEL; installation and runtime compatibility have not been verified on RHEL.
Use a RHEL machine with a graphical desktop session to try this option.

Check the architecture with `uname -m`, then download the matching RPM:

| Architecture | Official desktop RPM |
| --- | --- |
| `x86_64` (x64) | [Download chatgpt.x86_64.rpm](https://persistent.oaistatic.com/codex-app-prod/linux/rpm/latest/chatgpt.x86_64.rpm) |
| `aarch64` (ARM64) | [Download chatgpt.aarch64.rpm](https://persistent.oaistatic.com/codex-app-prod/linux/rpm/latest/chatgpt.aarch64.rpm) |

Save the file in `~/Downloads`. For x64, install it with:

```bash
cd "$HOME/Downloads"
sudo dnf install ./chatgpt.x86_64.rpm
```

For ARM64, use `sudo dnf install ./chatgpt.aarch64.rpm` instead. Let DNF resolve
package dependencies from the enabled repositories. If it cannot resolve them,
use Codex CLI for the lab rather than forcing the RPM installation.

Open **ChatGPT** from the applications menu, or run `chatgpt` in a terminal
inside the graphical desktop session. Complete enterprise OAuth/SSO sign-in,
select the assigned enterprise workspace, choose **Codex**, and open the
workshop repository folder. Inspect the permissions control before starting.

The official RPM installation configures an OpenAI package repository. If that
repository was configured successfully, update with:

```bash
sudo dnf upgrade --refresh chatgpt
```

These download links and the install/update commands come from the
[official Linux desktop guide](https://learn.chatgpt.com/docs/linux/linux-app#install-on-fedora).
RHEL remains an unsupported preview target even if the package installs.

## Install Codex on macOS (OS X)

Open Terminal. If Git is unavailable, install Apple's Command Line Tools and
finish the installer dialog:

```bash
xcode-select --install
```

Choose **one** CLI installation method below.

### Homebrew

If Homebrew is already installed:

```bash
brew install --cask codex
codex --version
codex --help
```

Update that installation with `brew upgrade --cask codex`.

### Standalone installer

Use the standalone installer without Homebrew:

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

## Install Cursor on the host OS

Red Hat associates should review the current
[Cursor access guidance](https://source.redhat.com/projects_and_programs/ai/ai_tools/cursor)
and submit the [license request](https://devservices.dpp.openshift.com/support/cursor_license_request/)
(VPN required). Complete the confirmation-email setup with the assigned account;
use current internal guidance for eligibility and regional availability.

### RHEL RPM

Download the Linux RPM matching `uname -m` from
[Cursor downloads](https://cursor.com/download). Save it in `~/Downloads` and
replace the placeholder below with the exact downloaded filename:

```bash
cd "$HOME/Downloads"
sudo dnf install './<downloaded-cursor-package>.rpm'
```

Launch Cursor from the applications menu and sign in with the approved account.
For repository-based installation and updates, see
[Cursor's RHEL/Fedora quickstart](https://cursor.com/docs/get-started/quickstart).

### macOS installer

Download the Apple Silicon or Intel `.dmg` from
[Cursor downloads](https://cursor.com/download), open it, move Cursor into
Applications, and launch it. Sign in with the approved account.

### Open the local checkout

Choose **File → Open Folder…** and select `ansible-amers-ai-workshop`. Open
**Terminal → New Terminal**, activate the shared environment, and verify its path:

```bash
source "$HOME/.venvs/ansible-workshop/bin/activate"
command -v python
command -v ansible-playbook
```

Both paths should point into `~/.venvs/ansible-workshop/bin`. An optional Ansible
extension published by Red Hat provides editing support; Ansible commands use
the host tools installed above. Codex policy settings below are independent of
Cursor settings.

## Sign in to Codex and open the workspace

Confirm that your enterprise account has Codex access and membership in the
workshop workspace. On a machine with a browser, start the OAuth sign-in flow:

```bash
codex login
codex login status
```

Choose **Sign in with ChatGPT**, use your work identity, and complete the
organization's enterprise OAuth/SSO flow when prompted. Select the enterprise
workspace assigned for the workshop rather than a personal workspace.
`codex login status` confirms the authentication method; verify workspace
selection during sign-in. For a RHEL SSH session without a local browser:

```bash
codex login --device-auth
```

Open the printed link on your laptop, complete the same enterprise OAuth/SSO
sign-in, and enter the one-time code. Device login must be enabled by the
enterprise workspace administrator. If it is disabled, use the SSH callback
forwarding flow in the [authentication guide](https://learn.chatgpt.com/docs/auth#fallback-forward-the-localhost-callback-over-ssh).

Codex subscription access follows the signed-in enterprise workspace's access
and data-handling policies. Treat `~/.codex/auth.json`, if present, as a
credential; keep it out of the repository. See
[authentication](https://learn.chatgpt.com/docs/auth).

If you have not cloned the workshop yet:

```bash
git clone https://github.com/redhat-services-platform-team/ansible-amers-ai-workshop.git
cd ansible-amers-ai-workshop
git status --short
```

From your checkout, create a learner branch and launch Codex with the host
Python environment active:

```bash
git switch -c workshop/codex-lab
source "$HOME/.venvs/ansible-workshop/bin/activate"
codex --sandbox read-only --ask-for-approval on-request
```

Start with this prompt in Codex or Cursor:

```text
Read README.adoc and workshop-content/02-shell-to-ansible/README.adoc.
Explain the workshop structure and the prerequisites for converting the legacy
shell script to Ansible. Include differences between a RHEL control host and a
macOS control host. Before running Ansible commands, activate
~/.venvs/ansible-workshop/bin/activate. Keep this task to inspection and explanation.
```

Install the shared host tools above before validation. Follow later-lab
prerequisites before connecting to managed hosts.

## Verify the local runtime

From the repository root, in your OS terminal, Cursor terminal, or Codex desktop
terminal:

```bash
source "$HOME/.venvs/ansible-workshop/bin/activate"
cd workshop-content/01-codex-workspace
ansible-playbook --syntax-check playbooks/hello.yml
ansible-lint playbooks/hello.yml
ansible-playbook playbooks/hello.yml
```

The playbook targets only localhost. It prints the OS, Ansible version, and Python
executable and checks for Linux or macOS without changing host configuration.
[inventory/hosts.yml](inventory/hosts.yml) selects the same Python executable that
runs Ansible. [ansible.cfg](ansible.cfg) selects the lab inventory when commands
run from this directory.

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
the playbook, activate ~/.venvs/ansible-workshop/bin/activate and run syntax validation. Report the diff
and validation results. Do not connect to managed hosts for this task.
```

Review `git diff` and `git status --short` after the task. Confirm the output is
appropriate before committing it or running a playbook against a lab inventory.

## Troubleshooting

- **`codex: command not found`:** Open a new terminal. For the standalone
  installer, check `~/.local/bin/codex` and the `PATH` above. For Homebrew,
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
- **Ansible is missing:** Activate the shared host environment in the command
  shell and install from this module's requirements.txt. Codex and Cursor use
  tools installed where their commands execute.

## Included assets

| File | Purpose |
| --- | --- |
| [requirements.txt](requirements.txt) | Pinned host Ansible tooling |
| [playbooks/hello.yml](playbooks/hello.yml) | Local runtime verification for RHEL and macOS |
| [config.toml](samples/config.toml) | User defaults for workspace edits with human approvals |
| [review.config.toml](samples/review.config.toml) | Named read-only review profile |
| [workshop.rules](samples/workshop.rules) | Example command escalation rules |
| [requirements.toml](samples/requirements.toml) | Administrator limits for Linux/macOS |
| [AGENTS.md.example](samples/AGENTS.md.example) | Ansible working agreements to review and adopt |

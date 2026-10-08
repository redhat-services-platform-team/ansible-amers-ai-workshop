# Lab 1 — Workspace Setup

Choose **Codex or Cursor** on **RHEL** or **macOS (OS X)** and run Ansible
directly on the workstation. You only need **one tool and one interface: CLI or
desktop**. Codex uses enterprise OAuth/SSO; Cursor uses the approved associate
account. Every path uses the same checkout and your existing Ansible installation.

Full workshop page: [Workspace Setup](../../documentation/modules/ROOT/pages/01-cursor-workspace.adoc).

Commands and configuration were checked against official OpenAI documentation
on **2026-10-07** and local **Codex CLI 0.160.1** help. Check `codex --help` after
upgrading; available models and features depend on your account and workspace.

## Choose one setup path

Verify the Ansible prerequisite, then follow only one path below. Installing both
tools or both interfaces is optional. Desktop users can skip CLI installation;
Cursor users can skip Codex sign-in, configuration, and flag examples.


| Interface | RHEL | macOS | Workshop use |
| --- | --- | --- | --- |
| Cursor CLI | Install the CLI below | Install the CLI below | Use Agent from the terminal |
| Cursor desktop | Install the Linux RPM below | Install the macOS `.dmg` below | Edit the checkout and use Agent with local tools |
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

## Prerequisites — working Ansible installation

- A RHEL or macOS workstation with **Ansible already installed and working**.
- `ansible-playbook` accessible in the terminal used for the labs.
- Git, installer download utilities, and access to the account for your selected tool.
- A graphical desktop session only if you choose a desktop interface.

This lab assumes a working Ansible installation and does not install or replace
it. Activate your existing Ansible environment if needed, then verify:

```bash
command -v ansible-playbook
ansible-playbook --version
git --version
```

Note the executable path and Python runtime. Use the same installation in your
OS terminal and your selected AI tool. If your normal workflow requires an
activation command, provide that actual command to the tool; desktop launches
may not inherit your shell environment. An absolute executable path is another
option. `ansible-lint` is optional for the additional lint check.

## Codex setup (choose CLI or desktop)

Follow only the selected OS and interface.

### RHEL installation

Choose CLI or desktop. Follow only the instructions for the interface you chose.

Use a regular user account on a workshop host. These host setup commands run in
your own terminal, before starting Codex. The CLI route uses the standalone
Linux installer and does not require Node.js. The optional desktop route uses
the Linux preview RPM. Both assume a registered RHEL system with enabled
repositories and outbound HTTPS access.

#### Codex CLI — standalone installer

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

#### Desktop RPM — unsupported preview on RHEL

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

### macOS installation

For desktop, use the app download and sign-in steps above. For CLI, choose one
of the installers below.

Open Terminal. If Git is unavailable, install Apple's Command Line Tools and
finish the installer dialog:

```bash
xcode-select --install
```

Choose **one** CLI installation method below.

#### Homebrew

If Homebrew is already installed:

```bash
brew install --cask codex
codex --version
codex --help
```

Update that installation with `brew upgrade --cask codex`.

#### Standalone installer

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

### Sign in to Codex CLI and open the workspace (Codex CLI users only)

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
Ansible environment available:

```bash
git switch -c workshop/codex-lab
codex --sandbox read-only --ask-for-approval on-request
```

Start with this prompt in Codex or Cursor:

```text
Read README.adoc and workshop-content/02-shell-to-ansible/README.adoc.
Explain the workshop structure and the prerequisites for converting the legacy
Python NetBox installer to Ansible. Include differences between a RHEL control
host and a macOS control host, with a dedicated CentOS Stream 10 managed host.
Use my existing working Ansible installation.
Keep this task to inspection and explanation.
```

Verify the existing Ansible prerequisite before validation. Follow later-lab
prerequisites before connecting to managed hosts.

### Permissions

Permissions determine where Codex can write files, whether generated commands can use the network, and when an action needs approval. In the CLI, use `/permissions` to inspect the active policy; in desktop Codex, use the permissions control beneath the composer. Routine commands allowed by the sandbox can run without asking every time. Enterprise requirements can restrict the options available to you.

#### Recommended settings for this lab

Use workspace editing with human review for requests that need more access. The default configuration file on RHEL and macOS is `~/.codex/config.toml`; if you already use `CODEX_HOME`, edit its `config.toml` instead.

*This file may already contain settings*, including model choices, project entries, and enterprise defaults. Inspect it first and back it up. Merge the proposed keys into the existing file; do not replace the whole file or append duplicate keys or table headers. For a new file, the example below is a complete starting point. These are user defaults and cannot override managed requirements.

```bash
mkdir -p "$HOME/.codex"
if [ -f "$HOME/.codex/config.toml" ]; then
  cp "$HOME/.codex/config.toml" "$HOME/.codex/config.toml.backup-$(date +%Y%m%d-%H%M%S)"
fi
${EDITOR:-vi} "$HOME/.codex/config.toml"
```

```toml
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"
web_search = "disabled"

[sandbox_workspace_write]
network_access = false
```

| Setting | What it means for a first-time user |
| --- | --- |
| `approval_policy = "on-request"` | Codex can perform routine actions inside its permissions. When it requests an action requiring more access, it can ask you to approve it; this does not prompt for every command. |
| `approvals_reviewer = "user"` | Approval requests go to you rather than an automatic reviewer, so you can read the proposed command and its purpose. |
| `sandbox_mode = "workspace-write"` | Generated commands can edit the workspace and run local validation. Writes outside the permitted roots are restricted; this is not a promise that reads are limited to the workspace. |
| `web_search = "disabled"` | Hosted web search is off for the local workshop exercises; supplied files provide the initial context. |
| `network_access = false` | Commands inside the workspace sandbox cannot freely contact remote services. This is separate from web search and does not block Codex's own sign-in or model connection. |

Place top-level keys before TOML table headers. If `[sandbox_workspace_write]` already exists, update `network_access` inside that table. Restart Codex and check the active permissions before your first prompt. The same sample is available at `samples/config.toml`.

Common CLI examples, using your existing Ansible installation:

```bash
codex -s read-only -a on-request
codex -s workspace-write -a on-request
codex -C workshop-content/02-shell-to-ansible
codex resume --last
```

If Ansible needs environment activation, tell Codex your actual activation command or give it the absolute executable path verified in the prerequisites. The lab folder's guide also covers named profiles, command rules, and administrator requirements.

### References

- [Codex CLI installation](https://learn.chatgpt.com/docs/codex/cli)
- [Desktop app and Codex](https://learn.chatgpt.com/docs/app)
- [Linux desktop preview and RPM support](https://learn.chatgpt.com/docs/linux/linux-app)
- [Enterprise account sign-in and SSH authentication](https://learn.chatgpt.com/docs/auth)
- [Configuration locations and precedence](https://learn.chatgpt.com/docs/config-file/config-basic)
- [Permissions, approvals, and sandboxing](https://learn.chatgpt.com/docs/sandboxing)
- [CLI commands and flags](https://learn.chatgpt.com/docs/developer-commands?surface=cli)

## Cursor setup (choose CLI or desktop)

Request access, then choose CLI or desktop. Skip the other interface.

Red Hat associates should review the current
[Cursor access guidance](https://source.redhat.com/projects_and_programs/ai/ai_tools/cursor)
and submit the [license request](https://devservices.dpp.openshift.com/support/cursor_license_request/)
(VPN required). Complete the confirmation-email setup with the assigned account;
use current internal guidance for eligibility and regional availability.

### CLI — RHEL and macOS

Run the installer as your regular user, then sign in with the approved account:

```bash
curl -fsSL https://cursor.com/install -o /tmp/cursor-install.sh
less /tmp/cursor-install.sh
bash /tmp/cursor-install.sh
export PATH="$HOME/.local/bin:$PATH"
agent --version
agent login
agent status
```

From the workshop repository root, use your existing Ansible environment and run
`agent` to start a session. Update with `agent update`. See
[CLI installation](https://cursor.com/docs/cli/installation) and
[CLI authentication](https://cursor.com/docs/cli/reference/authentication).
CLI users can skip the desktop installation steps below and continue to Permissions and References.

### Desktop — RHEL RPM

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

### Desktop — macOS installer

Download the Apple Silicon or Intel `.dmg` from
[Cursor downloads](https://cursor.com/download), open it, move Cursor into
Applications, and launch it. Sign in with the approved account.

### Open the local checkout (desktop users only)

Choose **File → Open Folder…** and select `ansible-amers-ai-workshop`. Open
**Terminal → New Terminal**, activate your existing Ansible environment if needed, and verify it:

```bash
command -v ansible-playbook
```

Use the same Ansible installation verified in the prerequisites. An optional
Ansible extension published by Red Hat provides editing support; commands use
your existing installation. Codex policy settings below are independent of
Cursor settings.

### Permissions

Cursor desktop and Cursor CLI have different configuration files. Use only the instructions for your chosen interface. In desktop Cursor, open *Settings → Agents → Approvals & Execution*. In the CLI, permissions are configured in `~/.cursor/cli-config.json` or the project-specific `.cursor/cli.json`. A CLI configuration file does not configure the desktop Run Mode.

#### Recommended settings for this lab — desktop

Use *Auto-review* with sandboxing enabled. Routine allowlisted calls run immediately, supported shell commands run in the sandbox, and other calls are evaluated by an automatic reviewer. Some actions therefore run without a human prompt. For Cursor 3.23 or later, choose *Read Access → Workspace* so reads outside the workspace require approval unless included in the read allowlist. Keep the existing enterprise restrictions in place.

To steer Auto-review toward asking before publishing, installing software, or changing remote systems, merge this example into `~/.cursor/permissions.json` (all projects) or `<repo>/.cursor/permissions.json` (this workshop only):

```json
{
  "autoRun": {
    "allow_instructions": [],
    "block_instructions": [
      "Commands that publish code, including git push, should require my approval first.",
      "Commands that install software or change host configuration should require my approval first.",
      "Commands that connect to managed hosts or change AWS resources should require my approval first."
    ]
  }
}
```

`allow_instructions` is empty because the lab adds no special automatic exceptions. `block_instructions` describes actions the reviewer should block so the agent can choose another approach or ask you to approve. These sentences guide a model-based reviewer; they are not deterministic command-deny rules. Team Auto-review policy can take precedence over these local files. If Auto-review is unavailable under your enterprise policy, use *Allowlist* with no added automatic allowances and follow the administrator's restrictions.

#### Recommended settings for this lab — CLI

Inspect and back up `~/.cursor/cli-config.json`, then merge these settings. The CLI may already have created this file when you signed in. If you use `CURSOR_CONFIG_DIR` or `XDG_CONFIG_HOME`, use the configured location instead. For a new file, this is a complete starting point:

```json
{
  "version": 1,
  "editor": { "vimMode": false },
  "approvalMode": "allowlist",
  "permissions": {
    "allow": [],
    "deny": ["Shell(sudo)", "Shell(rm)"]
  }
}
```

| Setting | What it means for a first-time user |
| --- | --- |
| `version: 1` | Selects the documented CLI configuration format. |
| `editor.vimMode: false` | Uses normal text-input keys; preserve your preference if you already use Vim bindings. |
| `approvalMode: "allowlist"` | Uses explicit permission rules rather than unrestricted execution or automatic review. |
| `permissions.allow: []` | Adds no blanket automatic approvals. Review approval requests before accepting them; existing sandbox behavior can still permit supported actions. |
| `permissions.deny` | Blocks commands whose base command is `sudo` or `rm`. These token rules do not block every possible way to change or remove files, and deny entries take precedence over allow entries. |

Use an interactive `agent` session for this lab and inspect each command request. If a deny rule blocks a task you intended, review the task and perform the approved host operation yourself or deliberately revise the applicable rule.

#### Preserve existing settings before editing

*All of these files may already have contents.* Back up only the files you intend to edit, using commands such as:

```bash
mkdir -p "$HOME/.cursor"
if [ -f "$HOME/.cursor/cli-config.json" ]; then
  cp "$HOME/.cursor/cli-config.json" "$HOME/.cursor/cli-config.json.backup-$(date +%Y%m%d-%H%M%S)"
fi
if [ -f "$HOME/.cursor/permissions.json" ]; then
  cp "$HOME/.cursor/permissions.json" "$HOME/.cursor/permissions.json.backup-$(date +%Y%m%d-%H%M%S)"
fi
```

For project-scoped files, back up the corresponding file under the repository's `.cursor/` directory instead. Preserve unrelated settings and existing restrictions. Update an existing JSON object instead of pasting a second top-level object; merge permission arrays without duplicate entries. An empty example array does not mean you should erase existing rules. JSON cannot contain comments or trailing commas. Restart the selected interface after editing and inspect its active mode and permissions. Samples are in `samples/cursor/`; review them before merging, rather than copying over an existing file.

### References

- [Desktop installation and first workspace](https://cursor.com/docs/get-started/quickstart)
- [Desktop downloads](https://cursor.com/download)
- [CLI installation and updates](https://cursor.com/docs/cli/installation)
- [CLI account sign-in](https://cursor.com/docs/cli/reference/authentication)
- [Desktop Run Modes, Auto-review, read access, and configuration files](https://cursor.com/docs/agent/security/run-modes)
- [CLI configuration locations and schema](https://cursor.com/docs/cli/reference/configuration)
- [CLI permission tokens and rule matching](https://cursor.com/docs/cli/reference/permissions)

## Verify the local runtime

From the repository root, in your OS terminal, Cursor terminal, or Codex desktop
terminal:

```bash
cd workshop-content/01-codex-workspace
ansible-playbook --syntax-check playbooks/hello.yml
ansible-playbook playbooks/hello.yml
```

If `ansible-lint` is already installed, optionally run
`ansible-lint playbooks/hello.yml`.

The playbook targets only localhost. It prints the OS, Ansible version, and Python
executable and checks for Linux or macOS without changing host configuration.
[inventory/hosts.yml](inventory/hosts.yml) selects the same Python executable that
runs Ansible. [ansible.cfg](ansible.cfg) selects the lab inventory when commands
run from this directory.

## Advanced Codex configuration (optional)

### Update the policy configuration (Codex users only)

Cursor users can skip these Codex-specific settings.

Sandbox settings determine file/network access for generated commands. Approval
settings determine when Codex asks before proceeding. `on-request` allows
routine actions inside the sandbox without prompting for every command.
`never` removes approval prompts and returns blocked actions as failures; it
does not grant full access. See
[approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security).

The recommended user defaults and backup/merge instructions are in the Codex
Permissions subsection above. The examples below cover optional changes after
you have completed that first setup.

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

#### Command rules

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

### Common Codex flags and commands (Codex CLI users only)

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
Also read legacy/.env.example in the same directory. Explain the assumptions,
then propose an idempotent Ansible project for a dedicated CentOS Stream 10 host.
Wait for my choice of output directory before creating the project. My RHEL or
macOS workstation is the control host. After generation, use my existing Ansible
installation for syntax validation. Report the diff
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
- **Ansible is missing:** Restore your existing installation or activate its
  environment in the command shell. A working Ansible installation is a
  prerequisite for this lab; ask the facilitator if it is unavailable.

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

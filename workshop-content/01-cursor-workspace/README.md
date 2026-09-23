# Lab 1 — Cursor Workspace Setup

Sample Ansible content and **Dev Container / workspace config samples** for Lab 1.

## Contents

| Path | Purpose |
|------|---------|
| `samples/.devcontainer/devcontainer.json` | Sample ADT Dev Container config (copy to repo root) |
| `samples/.vscode/settings.json` | Sample settings that point Dev Containers at `podman` (copy to repo root) |
| `ansible.cfg` / `inventory/` / `playbooks/` | Sample Ansible content for verification |

## How to use

1. Confirm **Podman** is installed and ready (`podman info` succeeds).
2. Install the **Dev Containers** extension in Cursor (`anysphere.remote-containers`).
3. **File → Open Folder…** → select the **workshop repository root**.
4. From the repository root, copy the samples:

```sh
cp -R workshop-content/01-cursor-workspace/samples/.devcontainer .
cp -R workshop-content/01-cursor-workspace/samples/.vscode .
```

5. Command Palette → **Dev Containers: Reopen in Container**.
6. In the container terminal:

```sh
cd workshop-content/01-cursor-workspace
ansible-playbook playbooks/hello.yml
```

Root `.devcontainer/` and `.vscode/` are gitignored—do not commit your copies.

Full instructions: `documentation/modules/ROOT/pages/01-cursor-workspace.adoc`.

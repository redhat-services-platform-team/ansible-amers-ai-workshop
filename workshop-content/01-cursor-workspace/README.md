# Lab 1 — Cursor Workspace Setup

Assets for *Cursor Workspace Setup*. This lab uses **Cursor Dev Containers** with **Podman** as the default container engine and the community Ansible Development Tools (ADT) image.

## Prerequisites

- **Podman** installed and working on your local machine (machine running on macOS/Windows; `podman.socket` on Linux)
- Cursor access (covered in the lab guide)

## Contents

| Path | Purpose |
|------|---------|
| `.devcontainer/devcontainer.json` | Primary Dev Container config (Podman-oriented `runArgs`) |
| `.devcontainer/docker/devcontainer.json` | Fallback config if you must use Docker |
| `.vscode/settings.json` | Points Cursor Dev Containers at `podman` |
| `ansible.cfg` / `inventory/` / `playbooks/` | Sample Ansible content for verification |

## How to use

1. Confirm **Podman** is installed and ready (`podman info` succeeds).
2. Install the **Dev Containers** extension in Cursor (`anysphere.remote-containers`).
3. Confirm Cursor uses Podman (`dev.containers.dockerPath` = `podman`) — this folder sets that via `.vscode/settings.json`.
4. **File → Open Folder…** → select this directory.
5. Command Palette → **Dev Containers: Reopen in Container**.
6. In the container terminal: `ansible-playbook playbooks/hello.yml`

Full instructions: `documentation/modules/ROOT/pages/01-cursor-workspace.adoc`.

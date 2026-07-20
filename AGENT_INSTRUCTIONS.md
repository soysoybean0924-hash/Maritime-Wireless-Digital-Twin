# Agent Instructions

## Workspace Rule

The only development directory for this project is:

```text
D:\GitHubProjects\Maritime-Wireless-Digital-Twin
```

The original desktop directory is retained only as a backup:

```text
C:\Users\sypxx\Desktop\海陆通信场景
```

Do not modify, refactor, test, or continue development in the desktop source directory.

## Git Workflow

- Work only in `D:\GitHubProjects\Maritime-Wireless-Digital-Twin`.
- After every project change, run an appropriate test or validation step.
- After validation, commit the change with a clear commit message.
- Push committed changes to the configured remote.
- Do not use force push.
- Do not rewrite shared history unless the project owner explicitly approves a safe recovery plan.

## Commit Boundaries

- Inspect `git status` before staging files.
- Inspect diffs before committing tracked file changes.
- Do not blindly run `git add .` before checking the project contents.
- Stage only files that belong to the intended change.

## Safety Rules

- Do not commit secrets, credentials, tokens, passwords, private keys, or environment files.
- Do not commit `.env` or `.env.*` files.
- Do not commit dependency folders such as `node_modules/`.
- Do not commit build outputs such as `dist/`, `build/`, `.next/`, `out/`, or coverage output unless explicitly required.
- Do not commit large generated artifacts unless they are intentionally part of the research record.
- Keep `.gitignore` aligned with the actual technology stack as the project evolves.

## Current Project Type

This repository currently contains a static HTML/JavaScript Three.js research prototype. The main entry is:

```text
maritime-wireless-digital.html
```

Recommended local validation:

```powershell
cd D:\GitHubProjects\Maritime-Wireless-Digital-Twin
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/maritime-wireless-digital.html
```
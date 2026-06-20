---
name: deploy
description: Deploy and monitor the website deployment pipeline for development or production environments. Automatically coordinates Git branching and waits for GitHub Actions and GitHub Pages workflows to finish successfully.
---

# Deploy Skill

Use this skill to deploy clinic website changes to development or production, and monitor the build process until the updates are live.

## Triggering the Skill
Trigger this skill whenever you are asked to deploy changes to the development environment or production environment, or when the user wants to push updates and verify they are live on the web.

## Usage Guide

Execute the deployment by running the deployment monitor script:

### 1. Deploy to Development Environment (Dev)
```bash
python3 .agents/skills/deploy/scripts/deploy_monitor.py dev
```
* **What it does:**
  1. Verifies that the workspace is clean (no uncommitted files).
  2. Switches to the `dev` branch if not already on it.
  3. Pushes the `dev` branch to the remote origin on GitHub.
  4. Polls the GitHub Actions API to find the workflow run for the pushed commit SHA.
  5. Waits for the custom workflow to build, copy contents to the `/dev/` subfolder, and commit to `gh-pages`.
  6. Waits for the subsequent GitHub Pages built-in builder to complete.
  7. Exits successfully when the dev site at `https://maliyil-clinic.github.io/dev/` is fully updated.

### 2. Deploy to Production Environment (Prod)
```bash
python3 .agents/skills/deploy/scripts/deploy_monitor.py prod
```
* **What it does:**
  1. Verifies that the workspace is clean.
  2. Switches to the `main` branch.
  3. Merges the tested changes from the `dev` branch into the `main` branch.
  4. Pushes `main` to the remote origin on GitHub.
  5. Polls and monitors the custom build workflow for the merged commit.
  6. Monitors the Pages build workflow to verify it successfully deploys to the root of the site.
  7. Exits successfully when the live site at `https://maliyil-clinic.github.io/` is fully updated.

## Troubleshooting

### API Rate Limits
If the script encounters API rate limit warnings from GitHub, it will print warning logs. The script uses a polling interval of 5 to 10 seconds to avoid exceeding standard public API limit thresholds.

### Deployment Failures
If any step in the pipeline fails, the script will exit with code `1`. Inspect the standard output to see if the error was in:
* **Local Git operations:** (e.g. merge conflicts, uncommitted changes).
* **GitHub Actions compilation:** (e.g. syntax errors in config files).
* **GitHub Pages compilation:** (e.g. CDN hosting/routing problems).

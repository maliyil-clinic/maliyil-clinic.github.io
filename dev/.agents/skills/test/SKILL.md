---
name: test
description: Run automated tests to verify the deployment's status, API connections, and code integrity. Supports targeting dev or prod environments.
---

# Test Skill

Use this skill to run verification tests after deploying changes to the website. It ensures that the pages are active, the Google Sheets API connects successfully, and local file structure is intact.

## Triggering the Skill
Trigger this skill whenever you are asked to test or verify the deployment, check the status of dev or prod environments, or run verification scripts to confirm the booking system is working correctly.

## Usage Guide

Execute the test suite using the python testing script:

### 1. Test the Development Environment (Dev)
```bash
python3 .agents/skills/test/scripts/run_tests.py dev
```
* **Checks performed:**
  - Queries `https://maliyil-clinic.github.io/dev/index.html` to confirm it returns HTTP 200.
  - Queries the DEV Google Apps Script endpoint to verify slot-checking is responsive.
  - Verifies local file integrity (e.g. presence of `Holter Monitoring (HM)` and configurations).

### 2. Test the Production Environment (Prod)
```bash
python3 .agents/skills/test/scripts/run_tests.py prod
```
* **Checks performed:**
  - Queries `https://maliyil-clinic.github.io/index.html` to confirm it returns HTTP 200.
  - Queries the PROD Google Apps Script endpoint to verify slot-checking is responsive.
  - Verifies local file integrity.

## Troubleshooting

### HTTP 404/Connection Errors
If the frontend test fails:
- Check that the repo builds correctly on GitHub Actions.
- Verify that GitHub Pages is active and has finished deploying the branch.

### Apps Script Connection Failures
If the Apps Script connection test fails:
- Verify that the web app is deployed on Google Sheets with **Execute as:** `Me` and **Who has access:** `Anyone`.
- Verify the Web App URL matches the one configured in `contact.html` and `staff-booking.html`.

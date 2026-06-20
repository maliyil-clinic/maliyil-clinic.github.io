#!/usr/bin/env python3
import sys
import subprocess
import time
import urllib.request
import json
from datetime import datetime, timezone, timedelta

REPO = "maliyil-clinic/maliyil-clinic.github.io"
HEADERS = {"User-Agent": "Python-Deploy-Monitor"}

def run_git(cmd):
    """Helper to run a git command and return stripped output."""
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error executing: {cmd}")
        print(f"stdout: {res.stdout}")
        print(f"stderr: {res.stderr}")
        sys.exit(1)
    return res.stdout.strip()

def get_current_branch():
    return run_git("git branch --show-current")

def get_latest_sha():
    return run_git("git rev-parse HEAD")

def api_get(url):
    """Helper to perform HTTP GET requests to GitHub API using urllib."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"API Request Failed for {url}: {e}")
        return None

def monitor_workflow(commit_sha, branch_name):
    """Step 1: Monitor the custom deploy workflow run for our commit SHA."""
    url = f"https://api.github.com/repos/{REPO}/actions/runs?event=push"
    print(f"\n🔍 Searching for Deploy Website run for commit: {commit_sha[:7]} on branch: {branch_name}...")
    
    run_id = None
    # Wait up to 2 minutes for the run to appear
    for _ in range(24):
        data = api_get(url)
        if data and "workflow_runs" in data:
            for run in data["workflow_runs"]:
                # Check for matching commit SHA and branch name
                if run.get("head_sha") == commit_sha and run.get("head_branch") == branch_name:
                    run_id = run["id"]
                    print(f"✅ Found Workflow Run! ID: {run_id} | HTML URL: {run.get('html_url')}")
                    break
        if run_id:
            break
        time.sleep(5)
        
    if not run_id:
        print("❌ Error: Deploy workflow run did not start on GitHub within 2 minutes.")
        sys.exit(1)
        
    # Poll status of custom deploy run
    print("⏳ Monitoring Deploy Website run status...")
    status_url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}"
    while True:
        run = api_get(status_url)
        if not run:
            time.sleep(5)
            continue
            
        status = run.get("status")
        conclusion = run.get("conclusion")
        print(f"   Status: {status} | Conclusion: {conclusion or 'in-progress'}")
        
        if status == "completed":
            if conclusion == "success":
                print("🎉 Deploy Website workflow succeeded!")
                return datetime.now(timezone.utc)
            else:
                print(f"❌ Deploy Website workflow failed with conclusion: {conclusion}")
                sys.exit(1)
        time.sleep(10)

def monitor_pages_deployment(since_time):
    """Step 2: Monitor the automatic GitHub Pages deployment workflow run."""
    print("\n🔍 Waiting for GitHub Pages deployment run to start...")
    url = f"https://api.github.com/repos/{REPO}/actions/runs"
    
    # Account for clock skew between local machine and GitHub servers
    check_time = since_time - timedelta(seconds=60)
    
    run_id = None
    # Wait up to 3 minutes for Pages deployment to be triggered
    for _ in range(36):
        data = api_get(url)
        if data and "workflow_runs" in data:
            for run in data["workflow_runs"]:
                if run.get("name") == "pages build and deployment" and run.get("head_branch") == "gh-pages":
                    # Verify this run started after our push
                    created_at_str = run.get("created_at")
                    if created_at_str:
                        # Parse ISO 8601 string
                        created_time = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                        if created_time > check_time:
                            run_id = run["id"]
                            print(f"✅ Found Pages Deployment Run! ID: {run_id} | HTML URL: {run.get('html_url')}")
                            break
        if run_id:
            break
        time.sleep(5)
        
    if not run_id:
        print("❌ Error: GitHub Pages build run did not start within 3 minutes.")
        sys.exit(1)
        
    print("⏳ Monitoring Pages Build and Deployment status...")
    status_url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}"
    while True:
        run = api_get(status_url)
        if not run:
            time.sleep(5)
            continue
            
        status = run.get("status")
        conclusion = run.get("conclusion")
        print(f"   Status: {status} | Conclusion: {conclusion or 'in-progress'}")
        
        if status == "completed":
            if conclusion == "success":
                print("\n🚀 SUCCESS! The changes are fully live on the web!")
                return
            else:
                print(f"❌ Pages build and deployment failed with conclusion: {conclusion}")
                sys.exit(1)
        time.sleep(10)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 deploy_monitor.py [dev|prod]")
        sys.exit(1)
        
    env = sys.argv[1].lower()
    if env not in ["dev", "prod"]:
        print("Error: environment must be either 'dev' or 'prod'")
        sys.exit(1)
        
    print(f"🚀 Initializing deployment workflow for: {env.upper()}")
    
    # Check git status
    status = run_git("git status --porcelain")
    if status:
        print("⚠️ Warning: You have uncommitted changes in your workspace:")
        print(status)
        print("Please commit or stash your changes before running deploy.")
        sys.exit(1)
        
    current_branch = get_current_branch()
    
    if env == "dev":
        if current_branch != "dev":
            print("🔄 Switching to branch: dev")
            run_git("git checkout dev")
        
        print("📤 Pushing branch 'dev' to remote origin...")
        run_git("git push origin dev")
        branch_name = "dev"
        
    else: # prod
        print("🔄 Switching to branch: main")
        run_git("git checkout main")
        
        print("🔄 Merging branch 'dev' into 'main'...")
        run_git("git merge dev")
        
        print("📤 Pushing branch 'main' to remote origin...")
        run_git("git push origin main")
        branch_name = "main"
        
    commit_sha = get_latest_sha()
    print(f"📌 Pushed Commit SHA: {commit_sha}")
    
    # Step 1: Wait for custom builder
    completion_time = monitor_workflow(commit_sha, branch_name)
    
    # Step 2: Wait for Pages hosting deploy
    monitor_pages_deployment(completion_time)
    
    # Switch back to main for prod, or keep dev for dev
    if env == "dev" and get_current_branch() != "dev":
        run_git("git checkout dev")
    elif env == "prod" and get_current_branch() != "main":
        run_git("git checkout main")

if __name__ == "__main__":
    main()

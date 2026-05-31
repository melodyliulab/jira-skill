#!/usr/bin/env python3
import sys
import subprocess
import os

def create_branch(issue_key):
    """Create a new git branch for the issue."""
    branch_name = f"feature/{issue_key}"
    try:
        # Check if we are in a git repository
        subprocess.run(["git", "status"], check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        print(f"Successfully created and checked out branch: {branch_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating branch. Please ensure you are in a valid git repository. Details: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def draft_release_notes(issue_key, text):
    """Append a note to a local draft file."""
    filename = "draft_release_notes.md"
    try:
        with open(filename, "a") as f:
            f.write(f"- **{issue_key}**: {text}\n")
        print(f"Added note to {filename}")
    except Exception as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python local_workspace.py <action> [args...]")
        sys.exit(1)
    
    action = sys.argv[1]
    if action == "create_branch" and len(sys.argv) >= 3:
        create_branch(sys.argv[2])
    elif action == "draft_release_notes" and len(sys.argv) >= 4:
        draft_release_notes(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown action or missing arguments for action: '{action}'")


import requests
import json

# 故意留下的问题：
# 1. hardcoded credentials
# 2. 没有error handling
# 3. 没有注释
# 4. 变量名不清晰

JIRA_TOKEN = "hardcoded_secret_token_12345"
JIRA_EMAIL = "user@company.com"

def get_jira_ticket(x):
    r = requests.get(
        f"https://company.atlassian.net/rest/api/2/issue/{x}",
        auth=(JIRA_EMAIL, JIRA_TOKEN)
    )
    data = r.json()
    return data

def update_ticket(x, y):
    r = requests.put(
        f"https://company.atlassian.net/rest/api/2/issue/{x}",
        auth=(JIRA_EMAIL, JIRA_TOKEN),
        json={"fields": {"status": y}}
    )
    return r

result = get_jira_ticket("PROJ-001")
print(result)

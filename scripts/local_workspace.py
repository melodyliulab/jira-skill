#!/usr/bin/env python3
import sys
import subprocess
import os
import requests

JIRA_BASE_URL = "https://company.atlassian.net/rest/api/2/issue"
JIRA_TOKEN = os.environ.get("JIRA_TOKEN")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL")

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

def get_jira_ticket(issue_key):
    """Retrieve details for a JIRA issue by its key.

    Args:
        issue_key: The JIRA issue key (e.g. 'PROJ-001').

    Returns:
        A dict containing the issue details, or None on failure.
    """
    if not JIRA_TOKEN or not JIRA_EMAIL:
        print("Error: JIRA_TOKEN and JIRA_EMAIL environment variables must be set.")
        return None
    try:
        response = requests.get(
            f"{JIRA_BASE_URL}/{issue_key}",
            auth=(JIRA_EMAIL, JIRA_TOKEN),
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error fetching ticket {issue_key}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching ticket {issue_key}: {e}")
    return None

def update_ticket(issue_key, status):
    """Update the status of a JIRA issue.

    Args:
        issue_key: The JIRA issue key (e.g. 'PROJ-001').
        status: The new status value to set.

    Returns:
        True if the update succeeded, False otherwise.
    """
    if not JIRA_TOKEN or not JIRA_EMAIL:
        print("Error: JIRA_TOKEN and JIRA_EMAIL environment variables must be set.")
        return False
    try:
        response = requests.put(
            f"{JIRA_BASE_URL}/{issue_key}",
            auth=(JIRA_EMAIL, JIRA_TOKEN),
            json={"fields": {"status": status}},
        )
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error updating ticket {issue_key}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error updating ticket {issue_key}: {e}")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python local_workspace.py <action> [args...]")
        sys.exit(1)

    action = sys.argv[1]
    if action == "create_branch" and len(sys.argv) >= 3:
        create_branch(sys.argv[2])
    elif action == "draft_release_notes" and len(sys.argv) >= 4:
        draft_release_notes(sys.argv[2], sys.argv[3])
    elif action == "get_jira_ticket" and len(sys.argv) >= 3:
        result = get_jira_ticket(sys.argv[2])
        print(result)
    elif action == "update_ticket" and len(sys.argv) >= 4:
        success = update_ticket(sys.argv[2], sys.argv[3])
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown action or missing arguments for action: '{action}'")

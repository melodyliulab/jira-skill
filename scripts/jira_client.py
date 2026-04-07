import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import json
import subprocess

def get_secret_from_pass(path):
    """Retrieve a secret from 'pass' password manager."""
    try:
        result = subprocess.run(["pass", "show", path], capture_output=True, text=True, check=True)
        return result.stdout.strip().split("\n")[0]  # Take first line only
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

# Priority: Environment Variables > 'pass' > Default
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL") or get_secret_from_pass("jira/email")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN") or get_secret_from_pass("jira/token")

def adf_to_markdown(node):
    """Recursively convert Jira ADF (Atlassian Document Format) to Markdown."""
    if not node:
        return ""
    
    # Base Case: Text node
    if node.get("type") == "text":
        text = node.get("text", "")
        for mark in node.get("marks", []):
            if mark["type"] == "strong": text = f"**{text}**"
            if mark["type"] == "em": text = f"*{text}*"
        return text
    
    # Recursive Case: Parent node
    result = ""
    for child in node.get("content", []):
        text = adf_to_markdown(child)
        ntype = child.get("type")
        
        if ntype == "paragraph": result += f"\n{text}\n"
        elif ntype == "heading": result += f"\n{'#' * child.get('attrs', {}).get('level', 1)} {text}\n"
        elif ntype == "bulletList": result += f"{text}"
        elif ntype == "listItem": result += f"* {text}"
        elif ntype == "hardBreak": result += "\n"
        else: result += text
        
    return result.strip()

def get_issue(issue_key):
    """Fetch all relevant fields from Jira issue."""
    if not JIRA_URL or not JIRA_EMAIL or not JIRA_API_TOKEN:
        return {"error": "Missing credentials. Set JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN (or store them in 'pass' as jira/email and jira/token)."}
    
    # We add expand=names to see what the custom fields actually represent
    api_endpoint = f"{JIRA_URL}/rest/api/3/issue/{issue_key}?expand=names"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}
    
    response = requests.get(api_endpoint, headers=headers, auth=auth)
    if response.status_code != 200:
        return {"error": f"Failed: {response.status_code}", "detail": response.text}
    
    data = response.json()
    fields = data['fields']
    field_names = data.get('names', {})
    
    # Extract standard fields
    result = {
        "key": issue_key,
        "summary": fields.get('summary', 'No summary'),
        "status": (fields.get('status') or {}).get('name', 'Unknown'),
        "issue_type": (fields.get('issuetype') or {}).get('name', 'Unknown'),
        "reporter": (fields.get('reporter') or {}).get('displayName', 'Unknown'),
        "assignee": (fields.get('assignee') or {}).get('displayName', 'Unassigned'),
        "url": f"{JIRA_URL}/browse/{issue_key}",
        "custom_fields": {}
    }

    # Parse main description
    raw_desc = fields.get('description')
    result["description"] = adf_to_markdown(raw_desc) if isinstance(raw_desc, dict) else str(raw_desc or "")

    # Look for other useful fields (including custom ones)
    for key, value in fields.items():
        if value and key not in ["summary", "description", "status", "assignee", "reporter", "comment", "worklog", "issuetype", "priority", "lastViewed"]:
            readable_name = field_names.get(key, key)
            
            # Handle ADF content in custom fields
            if isinstance(value, dict) and value.get("type") == "doc":
                val_text = adf_to_markdown(value)
            elif isinstance(value, dict):
                val_text = str(value.get("value") or value.get("name") or value)
            elif isinstance(value, list):
                val_text = ", ".join([str(v.get("value") or v.get("name") or v) if isinstance(v, dict) else str(v) for v in value])
            else:
                val_text = str(value)
                
            if val_text and val_text.strip() and val_text != "None":
                # Filter out system noise
                if readable_name.lower() not in ["creator", "votes", "watches", "updated", "created", "project", "aggregatetimeoriginalestimate", "aggregateprogress", "progress", "workratio", "lastviewed", "issuelinks"]:
                    result["custom_fields"][readable_name] = val_text

    # Extract issue links (Dependencies)
    links = fields.get("issuelinks", [])
    if links:
        result["links"] = []
        for link in links:
            direction = "outwardIssue" if "outwardIssue" in link else "inwardIssue"
            issue_data = link.get(direction)
            if issue_data:
                type_name = link["type"]["outward" if "outwardIssue" in link else "inward"]
                result["links"].append(f"{type_name} {issue_data['key']} ({issue_data['fields']['status']['name']})")

    # Handle Parent issue
    parent = fields.get("parent")
    if parent:
        result["parent"] = f"{parent['key']} ({parent['fields']['summary']})"

    return result

def print_summary(issue_key):
    """Print a detailed human-readable summary of the issue."""
    issue = get_issue(issue_key)
    if "error" in issue:
        print(f"Error: {issue['error']}")
        return
        
    print(f"\n\033[1;34m[{issue['key']}] {issue['summary']}\033[0m")
    print(f"\033[1;32mStatus:\033[0m {issue['status']} | \033[1;32mReporter:\033[0m {issue['reporter']} | \033[1;32mAssignee:\033[0m {issue['assignee']}")
    print("-" * 40)
    print(f"\033[1;33mDescription:\033[0m\n{issue['description']}")
    
    if issue.get("parent"):
        print(f"\033[1;33mParent:\033[0m {issue['parent']}")

    if issue.get("custom_fields"):
        print("-" * 40)
        for name, val in issue["custom_fields"].items():
            print(f"\033[1;33m{name}:\033[0m {val}")

    if issue.get("links"):
        print("-" * 40)
        print("\033[1;33mLinked Issues (Dependencies):\033[0m")
        for link in issue["links"]:
            print(f"  * {link}")

    print("-" * 40)
    print(f"\033[1;36mURL:\033[0m {issue['url']}\n")

def add_comment(issue_key, text):
    """Add a comment to a Jira issue."""
    api_endpoint = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Jira API v3 expects a specific document format (ADF), but for simple text:
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "text": text,
                            "type": "text"
                        }
                    ]
                }
            ]
        }
    }
    
    response = requests.post(api_endpoint, headers=headers, auth=auth, json=payload)
    if response.status_code != 201:
        return {"error": f"Failed: {response.status_code}", "detail": response.text}
    
    return {"status": "Comment added successfully"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python jira_client.py <action> <issue-key> [args...]")
        sys.exit(1)
        
    action = sys.argv[1]
    if action == "get_issue":
        print(json.dumps(get_issue(sys.argv[2])))
    elif action == "summarize":
        print_summary(sys.argv[2])
    elif action == "add_comment":
        print(json.dumps(add_comment(sys.argv[2], sys.argv[3])))
    else:
        print(f"Unknown action: {action}")

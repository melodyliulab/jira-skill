---
name: jira-skill
description: Interacts with Jira tickets on Atlassian. Use when fetching, summarizing, or managing tickets.
---

# Jira Skill

This skill allows Gemini CLI to interact with Jira issues at your organization's Atlassian site.

## Prerequisites

- **Authentication**: Set the following environment variables:
  - `JIRA_URL`: The URL of your organization's Atlassian site.
  - `JIRA_EMAIL`: Your email address.
  - `JIRA_API_TOKEN`: Your Jira API token.

## Tools

- `scripts/jira_client.py get_issue <ISSUE-KEY>`: Fetches ticket details (summary, description, status, assignee) as a JSON object.
- `scripts/jira_client.py add_comment <ISSUE-KEY> "<COMMENT>"`: Adds a comment to the specified issue.

## Usage Guidelines

1. **Summarization**: Use `get_issue` to fetch data, then provide a concise summary. **Always** include the **Work Type** (issue_type) and the **Parent** ticket (if applicable) in your summary.
2. **Commentary**: After a task (like code refactoring or bug investigation), you can use `add_comment` to update the Jira ticket.
3. **Status Check**: Use `get_issue` to verify the current status or assignee before starting work.

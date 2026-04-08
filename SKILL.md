---
name: jira-skill
description: Instructs the AI to use the Atlassian MCP server for Jira tasks.
---

# Jira Skill

This skill acts as a router to ensure the proper Atlassian tools are used.

## Usage Guidelines

**CRITICAL INSTRUCTION:** 
For **ANY** task involving Jira (fetching tickets, searching, getting ticket summaries, adding comments, finding relationships, etc.), you **MUST NOT** use any local scripts or attempt to write your own API calls.

Instead, you **MUST** use the registered `atlassian` MCP server tools (e.g., `search_jira_issues`, `summarize_jira_issue`, `add_jira_comment`, `get_issue_relationships`).

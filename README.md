# Jira Skill for Gemini CLI

This is a specialized skill for [Gemini CLI](https://github.com/google/gemini-cli) that allows the agent to interact with Jira tickets at your organizations Atlassian site (e.g. `https://<your-org>.atlassian.net`).

## Features
- **Fetch & Summarize**: Get clean, Markdown-formatted summaries of Jira issues.
- **ADF Parsing**: Automatically converts complex Atlassian Document Format (ADF) into readable text.
- **Field Awareness**: Pulls in standard fields (Status, Reporter, Assignee, Parent) and relevant Custom Fields (Target Dates, Blocked status, etc.).
- **Comment Support**: Ability to add comments to Jira tickets directly from the CLI.

## Security & Credentials
This skill uses the **`pass`** (Unix password manager) to store and retrieve credentials securely. It never stores your plain-text token or email in the code.

### Setup Instructions
1. **Store your credentials** in your local `pass` store:
   ```bash
   echo "your-actual-api-token" | pass insert -e jira/token
   echo "your-email@example.com" | pass insert -e jira/email
   ```
2. **Install the skill** in Gemini CLI:
   ```bash
   gemini skills install https://github.com/melodyliulab/jira-skill
   ```
3. **Reload Skills**:
   In your Gemini CLI session, run:
   ```bash
   /skills reload
   ```

## Usage
- "Gemini, summarize PROJ-123"
- "Gemini, check the status and reporter of PROJ-456"
- "Gemini, add a comment to PROJ-789 saying 'This is fixed in the latest PR'"

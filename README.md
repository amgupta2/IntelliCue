# IntelliCue
A service that uses Slack/email messages (fully anonymized) to deliver a weekly feedback report to company executives to improve their employee experience and product. The report has two sections: one, the most common pieces of employee feedback for the week as well as customer interaction analysis; and two, ideas for easy actionable next steps.

## Goals
Extract keywords from slack messages and emails and automate weekly emails with pdf layout of insights (such as sentiment analysis, concerns, improving customer relations, resource allocation, workload, pacing, and culture of an organization) and actionable feedback to improve bussiness processes, internal communication, and create a better product for the customer. 

## Layout
- Slack API/Email Scraper (Google Vault, etc)
- Data Processing Layer (PySpark, PyDoc)
- LLM Layer (Claude/ChatGPT API)
- Server/Database (AWS, GCP)

## Github Structure
| Component         | Folder         | Details                                                                 |
|------------------|----------------|-------------------------------------------------------------------------|
| Slack App         | `src/slack_app/` | Contains all Slack event handlers and slash command logic. Uses `slack_sdk`. |
| LLM Processing    | `src/pipeline/` | Core pipeline: preprocessing, sentiment scoring, insight generation, and summarization via LLMs. |
| Shared Utilities  | `src/shared/`   | Common helper functions for Slack clients, database access, and S3 I/O. |
| AWS Lambdas       | `lambdas/`      | Each Lambda function lives in its own folder with a `lambda_function.py`. |
| Environment Config| `config/`       | Gitignored secrets, `.env` files, and Slack tokens for local/dev use.  |
| Tests             | `tests/`        | Unit tests and integration tests. Uses `pytest`, `moto` for AWS mocking. |
| Dev Tools         | `tools/`        | Scripts for deploying Lambdas, mocking Slack events, and running pipelines locally. |


## How to Run / Local Setup (DEMO CODE)

*Step 0:* Contact the IntelliCue team via Slack to get added to:
  - Development workspace
  - Slack API dashboard (for API tokens)

*Step 1:*  
- Run: `git checkout demo-branch`
- Then: `git pull` to ensure you're up to date
- Install dependencies: `pip install -r requirements.txt`

*Step 2:*  
Create a `.env` file in the *root* of the project directory. This will hold your API keys.

*Step 3:*  
Navigate to https://api.slack.com/apps and do the following:

  *3.1* Enter the IntelliCue bot API dashboard  
  *3.2* Under *Basic Information* → *App-Level Tokens*  
    - Click on `WebSocket`, copy the token  
    - Add to `.env`:  
      `SLACK_APP_TOKEN=<your_token_here>`

  *3.3* Under *OAuth & Permissions*  
    - Scroll to *OAuth Tokens*  
    - Copy the Bot User OAuth Token  
    - Add to `.env`:  
      `SLACK_BOT_TOKEN=<your_token_here>`

*Step 4:*  
Navigate to https://aistudio.google.com/app/

- Open sidebar → Click *Get API Key*
- On the *API Keys* page, click *Create API Key*
- Add to `.env`:  
  `GEMINI_API_KEY=<your_key_here>`

*Step 5:*  
With all three keys in your `.env`, run the app from the root directory:  
`python run_pipeline_demo.py`

*Step 6:*  
Once the app is running:
- Open the IntelliCue Slack workspace (browser or app)
- Send a message about your work experience as if you are an employee
- Trigger analysis by using the slash command:  
  `/generate_feedback`

IntelliCue will respond with feedback and insights in the `#all-intellicue` channel


## Resources
- Weekly Updates: https://docs.google.com/document/d/14xlioL8x9TDKSeNkuvv2ZztGRhxHaSIjMrBktPaLzaE/edit?usp=sharing
- Requirements and Team Policies: https://docs.google.com/document/d/1gAFhhVxmP1W6-If2BCgHGcfAQwVaOZMq96XCnqS2454/edit?usp=sharing
- Other Team Resources: https://github.com/amgupta2/IntelliCue/blob/main/team-resources.md

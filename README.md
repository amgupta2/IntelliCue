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


## Resources
- Weekly Updates: https://docs.google.com/document/d/14xlioL8x9TDKSeNkuvv2ZztGRhxHaSIjMrBktPaLzaE/edit?usp=sharing
- Requirements and Team Policies: https://docs.google.com/document/d/1gAFhhVxmP1W6-If2BCgHGcfAQwVaOZMq96XCnqS2454/edit?usp=sharing
- Other Team Resources: https://github.com/amgupta2/IntelliCue/blob/main/team-resources.md

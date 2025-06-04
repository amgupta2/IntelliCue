# IntelliCue
A service that uses Slack/email messages (fully anonymized) to deliver a weekly feedback report to company executives to improve their employee experience and product. The report has two sections: one, the most common pieces of employee feedback for the week as well as customer interaction analysis; and two, ideas for easy actionable next steps.

## Goals
Extract keywords from slack messages and emails and automate weekly emails with pdf layout of insights (such as sentiment analysis, concerns, improving customer relations, resource allocation, workload, pacing, and culture of an organization) and actionable feedback to improve bussiness processes, internal communication, and create a better product for the customer. 

## Layout
- Slack API
- Data Processing Layer (Sentiment Analysis and Scoring)
- LLM Layer (Gemini API)
- Server/Database (AWS)

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
| Documentation     | `documentation/`| User and Developer Guides for using and contributing to IntelliCue.    |

Please find the Developer Docs and the User docs here:
- [User Guide](documentation/USER.md) - Complete guide for using IntelliCue
- [Developer Guide](documentation/DEVELOPER.md) - Detailed guide for developers contributing to IntelliCue

## AWS Deployment (Production Use)
⚠️ Note: IntelliCue is now hosted on AWS for production use. Local setup is only needed for development and testing changes.

For production/user use, IntelliCue is always running and fully deployed on AWS. No local setup is needed.

### How to Use IntelliCue
1. Currently, IntelliCue is not available on the Slack Marketplace. Because of this, users must contact the IntelliCue Team (amgupta2@uw.edu) to be added to the Development Slack Workspace where IntelliCue lives.
   
2. Go to any Slack channel where IntelliCue is present or add the Intellue bot to a new channel.

3. Post new messages or use existing conversations in the channel.

4. Go to the `#all-intellicue channel.

5. Run the following slash command:
   ```bash
   /generate_feedback
   ```

6. Within 5-6 minutes, IntelliCue will analyze all conversation and return a PDF report with:
   - Sentiment breakdown
   - Key themes
   - Suggested improvements
   - Summary insights

The PDF report will be posted directly in the `#all-intellicue` Slack channel.

## How to Develop / Local Setup

IntelliCue is fully deployed and running on AWS for production use. Currently, the application is exclusively available in the IntelliCue workspace and is not published on the Slack App Marketplace. If you'd like to deploy IntelliCue in your own workspace, please contact the IntelliCue team. For development and testing purposes, you can run the application locally by following the setup instructions in the Developer Doc linked above.

## Running Unit Tests
Unit Tests live in the `tests/` folder of the repository. They use Pytest as the testing automation framework and then use `moto`, `requests_mock`, and `unittest.mock` libaries for mocking AWS resources and Slack Web API requests. When contributing or using the test suite, you should not need to be setup with real API tokens as we are mocking all resources instead of using physical API calls. We use code coverage as a guideline for where we need to add more tests so we will be using a standardized baseline of 80% per file as the minimum code coverage before deploying into production.

In order to run tests, you will need to clone the repo locally. Make sure to install python and pytest.

```bash
# Clone the repo
git clone https://github.com/amgupta2/IntelliCue.git
cd IntelliCue

# [Optional] Set up a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python (if not already installed)
# For Ubuntu/Debian:
sudo apt install python3 python3-pip

# For macOS with Homebrew:
brew install python

# Install project dependencies
pip install -r requirements.txt

# Install Pytest for testing
pip install pytest

```

```bash
pytest --cov=src tests/
```

### Note:
If you are receiving errors with importing packages from the `src/` folder, please try the following pytest command. That should help solve that

```bash
PYTHONPATH=. pytest tests/
```

## Resources
- Weekly Updates: https://docs.google.com/document/d/14xlioL8x9TDKSeNkuvv2ZztGRhxHaSIjMrBktPaLzaE/edit?usp=sharing
- Requirements and Team Policies: https://docs.google.com/document/d/1gAFhhVxmP1W6-If2BCgHGcfAQwVaOZMq96XCnqS2454/edit?usp=sharing
- Other Team Resources: https://github.com/amgupta2/IntelliCue/blob/main/team-resources.md

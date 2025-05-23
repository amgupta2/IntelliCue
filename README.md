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
| Documentation     | `documentation/`| User and Developer Guides for using and contributing to IntelliCue.    |



## How to Run / Local Setup (DEMO CODE)

> ⚠️ **Note:** Please make sure you are working on the `demo-branch` when running, testing, or building IntelliCue. This branch reflects the current stable demo configuration.

Currently, IntelliCue can only be ran locally in a development workspace for accessing the Slack API. It is not configured with AWS meaning we are using local file creation to create JSON objects instead of utilizing the Databases and Step Function. IntelliCue is setup in socket mode meaning that it cannot be published on the Slack App Marketplcae and your network must allow network requests since your laptop will be acting as the host. For the preprocessing use cases, IntelliCue is configured with a very basic preprocessing script to anonymize messages, filter our basic noise such as user joining channels, and then uses sentiment analsysis that still needs to be tuned.

### Step 0: Access Setup
Contact the IntelliCue team via Slack to be added to:
- The development Slack workspace
- The Slack API dashboard (for obtaining API tokens)

---

### Step 1: Get the Demo Code
```bash
# Clone code locally
git checkout demo-branch
git pull

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 2: Create a `.env` File
In the root directory of the project, create a `.env` file to hold the required API keys.

---

### Step 3: Slack API Keys

1. Go to [Slack API Dashboard](https://api.slack.com/apps)
2. Enter the IntelliCue bot's app dashboard
3. On the **Basic Information** tab:
   - Scroll to **App-Level Tokens**
   - Click on `WebSocket`
   - Copy the token and add it to your `.env` file:
     ```
     SLACK_APP_TOKEN=<your_token_here>
     ```
4. On the **OAuth & Permissions** tab:
   - Scroll to **OAuth Tokens**
   - Copy the **Bot User OAuth Token** and add it to your `.env` file:
     ```
     SLACK_BOT_TOKEN=<your_token_here>
     ```

---

### Step 4: Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/)
2. Open the sidebar and click **Get API Key**
3. On the **API Keys** page, click **Create API Key**
4. Add the key to your `.env` file:
   ```
   GEMINI_API_KEY=<your_key_here>
   ```

---

### Step 5: Run the App

With all three keys configured in your `.env`, start the app from the root directory:

```bash
python run_pipeline_demo.py
```

---

### Step 6: Use the Slack App

1. In the IntelliCue Slack workspace, send a message about your work experience (acting as an employee).
2. Trigger the analysis using the following Slack slash command:
   ```
   /generate_feedback
   ```
3. IntelliCue will process the message and respond with feedback and actionable insights in the `#all-intellicue` channel.

---

### Notes

- Make sure your virtual environment is activated before installing requirements or running the app.
- If you encounter issues with API tokens or permissions, double-check that your Slack app has been granted the correct scopes.
- The Slack app runs in socket mode; ensure your network does not block WebSocket connections.

## Running Unit Tests
Unit Tests live in the `tests/` folder of the repository. They use Pytest as the testing automation framework and then use `moto`, `requests_mock`, and `unittest.mock` libaries for mocking AWS resources and Slack Web API requests. When contributing or using the test suite, you should not need to be setup with real API tokens as we are mocking all resources instead of using physical API calls. We use code coverage as a guideline for where we need to add more tests so we will be using a standardized baseline of 80% per file as the minimum code coverage before deploying into production.

```bash
pytest --cov=src tests/
```

## Resources
- Weekly Updates: https://docs.google.com/document/d/14xlioL8x9TDKSeNkuvv2ZztGRhxHaSIjMrBktPaLzaE/edit?usp=sharing
- Requirements and Team Policies: https://docs.google.com/document/d/1gAFhhVxmP1W6-If2BCgHGcfAQwVaOZMq96XCnqS2454/edit?usp=sharing
- Other Team Resources: https://github.com/amgupta2/IntelliCue/blob/main/team-resources.md

# IntelliCue Developer Guide

This document is for developers working on the IntelliCue system. It outlines instructions for cloning, configuring, running, testing, and contributing to the software.

---

## Cloning the Code (Local Development)

```bash
git clone https://github.com/amgupta2/IntelliCue.git
cd IntelliCue
```

We use a single repository without submodules. To contribute, you'll also need access to the Slack API Dashboard, Slack Development Workspace, and AWS Cloud Console. Contact the IntelliCue core team to be granted access.

---

## Repository Structure

| Component               | Folder                 | Description                                                                    |
|-------------------------|------------------------|--------------------------------------------------------------------------------|
| Slack App               | `src/slack_app/`       | Slack event handlers and slash command logic (`slack_bolt`)                    |
| LLM Pipeline            | `src/pipeline/`        | Preprocessing, sentiment scoring, summarization via LLMs                       |
| Shared Utilities        | `src/shared/`          | Slack clients, AWS S3 I/O, shared helpers                                      |
| AWS Lambdas             | `lambdas/`             | Standalone Lambda functions with `lambda_function.py` entrypoints              |
| Config                  | `config/`              | Git-ignored environment config files (e.g., `.env`)                            |
| Tests                   | `tests/`               | Unit and integration tests (`pytest`, `moto`, `requests_mock`)                 |
| Dev Tools               | `tools/`               | CLI scripts for Slack event mocking, local testing, and Lambda deploys         |
| Local Orchestrator      | `run_pipeline_demo.py` | Script to run the local pipeline end-to-end                                    |
| Documentation / Guides  | `documentation/`       | Developer and User Guides                                                      |

---

## AWS Deployment

IntelliCue is deployed on AWS using Lambda and ECS. The system runs continuously and does not require local runtime in production.

### Architecture Overview

#### 1. Triggering the Workflow
- User types `/generate_feedback` in Slack.
- Hits **API Gateway**, which invokes the **Orchestrator Lambda**.

#### 2. Orchestration with SQS & ECS
- Orchestrator Lambda dispatches the request to **4 SQS queues**, each corresponding to a stage:
  - `Message Extraction`
  - `Preprocessing & Sentiment Analysis`
  - `Insight Generation (LLM)`
  - `PDF Generation`
- Each queue triggers a dedicated **ECS container** to process its task.

#### 3. Shared State via S3
- Each container reads/writes intermediate results to S3:
  - Raw messages
  - Preprocessed insights
  - Final PDF
- S3 acts as the pipeline backbone.

#### 4. Final Delivery
- When the PDF is uploaded, an **S3 event** triggers a final Lambda that posts it back to the Slack channel.

---

## Deployment Steps

1. **AWS Access**
   - Ensure you can log into the AWS Management Console.
   - Get access to the IntelliCue AWS account (contact core team).

2. **Lambda Functions**
   - Located in `lambdas/`.
   - Each has a `lambda_function.py` entrypoint.
   - Deploy via AWS Console or CLI.

3. **ECS Containers**
   - If changes affect a pipeline stage, repackage and redeploy the related container.
   - ECS handles long-running tasks triggered via SQS queues.

4. **Verification**
   - Confirm IAM roles, S3 events, and queue permissions are correctly configured.

---

## Running in Production

- IntelliCue monitors Slack channels where the bot is invited.
- On `/generate_feedback`, the system:
  - Pulls recent messages
  - Sends them through the LLM pipeline
  - Generates a PDF report
  - Posts the report to Slack

---

## Local Setup

### API Token Access

To test locally, you'll need valid **Slack** and **Gemini** API tokens. These must be saved in a `.env` file **(never committed)**.

### 1. Slack App Access

Contact a core contributor to:
- Be added to the **IntelliCue Dev Slack workspace**
- Get access to the **Slack API Dashboard**

### 2. Create Your `.env` File

Create a `.env` file in the project root:

```
SLACK_APP_TOKEN=<your_app_token_here>
SLACK_BOT_TOKEN=<your_bot_token_here>
GEMINI_API_KEY=<your_gemini_key_here>
```

### 3. Where to Get API Keys

#### Slack API Tokens

1. Go to [Slack API Dashboard](https://api.slack.com/apps)
2. Select the IntelliCue app
3. Under **App-Level Tokens** → copy the WebSocket token → `SLACK_APP_TOKEN`
4. Under **OAuth & Permissions** → copy the Bot OAuth token → `SLACK_BOT_TOKEN`

#### Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/)
2. Click **Get API Key**
3. Generate and copy your key
4. Paste it as `GEMINI_API_KEY` in `.env`

---

## Python Environment

We use **Python 3.10+**.

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

---

## Running Locally

While production testing is handled via AWS Console and real-time Slack commands, developers should **simulate the pipeline locally**. Use JSON files to chain outputs between modules and test each feature individually.

For example:
- Run message extraction
- Save output to `message.json`
- Load `message.json` into the next stage (e.g., preprocessing)

This allows you to test full pipeline flow **without needing live SQS or S3**.

To run the orchestrated demo:

```bash
# Make sure you're on demo-branch
python run_pipeline_demo.py
```

---

## Running Tests

```bash
pytest --cov=src tests/
```

- All tests are under `tests/`
- AWS and Slack APIs are mocked:
  - `moto` for AWS (e.g., S3, SQS)
  - `requests_mock` or `unittest.mock` for Slack

> If you encounter import issues, try:

```bash
PYTHONPATH=. pytest tests/
```

You do **not** need real API tokens to run tests.

---

## Writing New Tests

- Use `test_<feature>.py` naming
- Each test should:
  - Mock all external dependencies
  - Cover normal + edge cases
- Maintain **≥80% code coverage per file**

Example:

```python
# tests/test_pipeline.py

def test_preprocess_message_removes_noise():
    ...
```

---

## Continuous Integration (CI)

CI is powered by **GitHub Actions** and runs on every push or pull request.

Checks include:
- Test suite (`pytest --cov`)
- Code linting via `flake8` for PEP 8 compliance

> CI failures **block merges** into `main`.

---

## Build & Release Process

- No versioned releases yet
- Slack app is **not published** (runs in private dev workspace via socket mode)
- Manual deploys to AWS for now
- Slack App Marketplace publishing is a future goal

---

## Additional Notes

- We use **Amazon SQS** to manage message flow across pipeline stages.
- If a stage hangs (e.g., PDF generation), check the corresponding **SQS queue for backlog** to identify bottlenecks.

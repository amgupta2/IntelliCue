# IntelliCue Developer Guide

This document is for developers working on the IntelliCue system. It will outline instructions for cloning, configuring, running, testing, and overall contributing to the software.

---

## Cloning the Code (local development)
```bash
git clone https://github.com/amgupta2/IntelliCue.git
cd IntelliCue
```

Since we are using a single respository, we do not have any other submodules. As part of development, you will also need access to the Slack API Dashboard, Slack Development Workspace, and AWS Cloud Computing Platform. Contact IntelliCue core team to gain access

---

## Repository Structure

| Component               | Folder                 | Description                                                                    |
|-------------------------|------------------------|--------------------------------------------------------------------------------|
| Slack App               | `src/slack_app/`       | Slack event handlers and slash command logic (`slack_bolt`)                    |
| LLM Pipeline            | `src/pipeline/`        | Preprocessing, sentiment scoring, summarization via LLMs                       |
| Shared Utilities        | `src/shared/`          | Slack clients, AWS S3 I/O, shared helpers                                      |
| AWS Lambdas             | `lambdas/`             | Standalone Lambda functions with `lambda_function.py` entrypoints              |
| Config                  | `config/`              | Gitignored environment configuration files (e.g. `.env`)                       |
| Tests                   | `tests/`               | Unit and integration tests (`pytest`, `moto`, `requests_mock`)                 |
| Dev Tools               | `tools/`               | CLI scripts for Slack event mocking, local testing, and Lambda deploys         |
| Local Orchestrator      | `run_pipeline_demo.py` | Script to run the local pipeline: Slack → Preprocess → LLM Inference           |
| Documentation / Guides  | `documentation/`       | Developer and User Guides on how to contribute to and use IntelliCue           |

---

## API Token Access

To contribute to the code base, you will need the system to be running locally in order to confirm functionality before making changes. This requires the use of **Slack and Gemini API keys**. These are stored in a `.env` file which is not to be committed due to the file contaning secrets.

### 1. Access the Slack App

Contact a core contributor to:
- Be added to the IntelliCue **development Slack workspace**
- Gain access to the **Slack API Dashboard**

### 2. Create Your `.env` File

In the project root, create a `.env` file:

```
SLACK_APP_TOKEN=<your_app_token_here>
SLACK_BOT_TOKEN=<your_bot_token_here>
GEMINI_API_KEY=<your_gemini_key_here>
```

### 3. How to Get Each Key

#### Slack API Tokens

1. Go to [Slack API Dashboard](https://api.slack.com/apps)
2. Select the IntelliCue app (you need access)
3. In **Basic Information** tab:
   - Scroll to **App-Level Tokens**
   - Copy the token labeled “WebSocket” → `SLACK_APP_TOKEN`
4. In **OAuth & Permissions** tab:
   - Copy the **Bot User OAuth Token** → `SLACK_BOT_TOKEN`

#### Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/)
2. In the sidebar, click **Get API Key**
3. Create a new key
4. Paste it into `.env` as `GEMINI_API_KEY`

---

## Local Setup

We use Python 3.10+ with a virtual environment. To setup, follow the instructions below

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Running the App Locally

> ⚠️ **Note:** Please make sure you are working on the `demo-branch` when running or testing IntelliCue. This branch reflects the current stable demo configuration.

```bash
python run_pipeline_demo.py
```

This will:
- Start the Slack app in socket mode (your machine acts as a WebSocket client)
- Wait for Slack messages (you will need to run the `/generate_feedback` command in a slack channel with the bot invited)
- Preprocess incoming data and run it through the LLM pipeline
- Output insights locally and (in Slack) to `#all-intellicue` channel

---

## Running Tests

```bash
pytest --cov=src tests/
```

- Tests live in `tests/`
- Slack and AWS APIs are **mocked**:
  - `moto` mocks AWS (e.g. `boto3`)
  - `requests_mock` or `unittest.mock` for Slack Web API

You do **not** need real tokens for testing.

---

## Adding New Tests

- Use the naming convention: `test_<feature>.py`
- Tests should:
  - Cover both core logic and edge cases
  - Mock external calls (Slack, AWS)
- Target code coverage: **≥80% per file** (enforced by CI)

Example test file:

```python
# tests/test_pipeline.py

def test_preprocess_message_removes_noise():
    ...
```

---

## Continuous Integration

CI is managed via **GitHub Actions**:

- Runs on all pushes and PRs
- Performs:
  - `pytest` with coverage
  - Linting via flake8 to enfoce Python PEP 8 Standards
- Test failures or linting errors will block merges

---

## Build & Release Process

- No formal release tagging yet
- The Slack app is **not published** (runs locally via socket mode)
- All deployment is local or manual for now
- Publishing to Slack Marketplace is a future stretch goal

## Developer Notes

- **Socket Mode**: The app listens via WebSocket — your network **must allow outbound connections**.
- If nothing happens after a slash command, confirm your bot tokens are correct and the app is running.
- If you're creating a new Lambda, place it in its own folder in `lambdas/` and follow AWS packaging guidelines.
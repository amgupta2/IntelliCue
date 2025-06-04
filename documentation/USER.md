# IntelliCue User Guide

This guide helps you understand what IntelliCue is, how to install and use it in your Slack workspace, and how to report issues or contribute to its improvement.

---

## What is IntelliCue?

**IntelliCue** is an automated feedback tool for Slack that uses large language models (LLMs) to generate insightful, anonymized PDF-based reports from your teamâ€™s messages. It helps teams:

- Get continuous feedback without surveys
- Understand morale and communication tone
- Identify key themes, complaints, and improvements

All analysis is done securely via an AI pipeline - no manual tagging or setup needed.

---

## Quick Start

### Requirements
- A Slack workspace with permission to install third-party apps
- Permission to invite bots to public and private channels
- No API keys or additional software required

### Installation

#### Option 1: IntelliCue Demo Workspace

> If the app hasn't been published to the Slack Marketplace yet:

1. Join our [IntelliCue demo workspace](https://join.slack.com/t/intellicue/shared_invite/zt-368ufefd1-T22gsbVr6m48qFEePu7m3Q)
2. Create or join a channel for testing (public or private)
3. Invite IntelliCue to that channel using:
   ```bash
   /invite @IntelliCue
   ```

#### Option 2: Slack Marketplace (Future) - NOT IMPLEMENTED

1. Visit the [Slack App Marketplace](https://slack.com/apps) and search for **IntelliCue**
2. Click **Add to Slack**
3. Approve the permission prompts (message reading, slash commands)
4. Invite IntelliCue to any channel you'd like it to analyze:
   ```bash
   /invite @IntelliCue
   ```
5. Complete the Slack-native message permission flow

---

## Running IntelliCue

1. Ensure messages have been posted in the past 7 days
   
2. Run the slash command in the `#all-intellicue` channel:
   ```bash
   /generate_feedback
   ```

3. IntelliCue will:
   - Analyze the conversation history
   - Generate a PDF report with:
     - Sentiment breakdown
     - Key themes
     - Suggested improvements
     - Summary insights
  
4. The PDF will appear in-channel, within 5-6 minutes

> Note: `/generate_feedback` only works in channels where IntelliCue is present and authorized to read messages.

---

## Tips for Use

- **Frequency**: Run the command as often as needed (e.g., weekly)
- **Multiple Channels**: Can analyze any number of channels in parallel
- **Data Storage**: Slack messages are not stored long-term. PDFs are securely uploaded to cloud storage (read-only access)

---

## Upcoming Features

We are working on:

- **Slack Marketplace Availability**
- **Scheduled Reports** (auto-run feedback weekly)
- **Feedback Dashboards** (visualize trends over time)
- **Custom Date Filtering** for reports
- **Feedback Memory**: use past reports to inform new ones

---

## Reporting Bugs

Found something broken? Submit a bug at our [GitHub Issues Tracker](https://github.com/amgupta2/IntelliCue/issues).

Please include:
- Summary of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Screenshots (if applicable)
- Channel name and whether it was public or private

Use the prefilled **Bug Report template** on GitHub for consistency.

---

## Known Issues

See all known bugs [here](https://github.com/amgupta2/IntelliCue/issues?q=is%3Aissue+is%3Aopen+label%3Abug).

---

Thanks for using IntelliCue!
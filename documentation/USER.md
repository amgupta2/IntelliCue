
# IntelliCue User Guide

This document is the user manual and contains information for what IntelliCue is, how to install and use it, and if needed, report bugs back to us for continual improvement.

---

## Description

**IntelliCue** is an automated feedback tool for Slack that uses large language models (LLMs) to analyze conversations and generate insightful, PDF-based feedback reports. Designed for teams who want continuous feedback without interrupting workflows, IntelliCue replaces surveys with real-time analysis of Slack messages unqiue to you.

Instead of relying on tedious forms or low-response surveys, IntelliCue scans Slack messages from channels you select, runs them through a secure AI pipeline, and provides concise, anonymized feedback that helps managers and teams understand employee morale, identify themes, and track positive/negative trends over time.

---

## Software Installation

To install IntelliCue:

**Prerequisites**:
- A Slack workspace with permission to install third-party apps.
- Workspace members must have permission to invite bots to channels.
- No third-party tools or software required. All AI processing is handled on our secure backend — **users do not need any API keys.**

For Local Set up:
**NOTE: We haven't released to [Slack App Marketplace](https://slack.com/apps) yet, so for now users must get added to our IntelliCue workspace**
1. Join the Intellicue workspace using this [link](https://join.slack.com/t/intellicue/shared_invite/zt-368ufefd1-T22gsbVr6m48qFEePu7m3Q)
2. OPTIONAL: Create a new channel (either public/private channel) with any permissions you'd like
4. After installation, invite IntelliCue to any public or private channels where you'd like it to collect feedback:
   ```bash
   /invite @IntelliCue
   ```
5. Grant message-reading permission as requested (you will be guided through a Slack-native authorization flow).
6. IntelliCue is already deployed on AWS. You do not need to install or host anything.

---

## Running the Software

Once installed:

Local Set Up:
1. Type any messsages, preferably related to feedback, complaints, questions, ...(to avoid getting filtered out)
2. Go to the channel #all-intellicue
3. Run the following slash command:
   ```bash
   /generate_feedback
   ```
4. Within 4-5 minutes (AWS), IntelliCue will analyze the past 7 days of conversation in that channel and return a **PDF report** with:
   - Sentiment breakdown
   - Key themes
   - Suggested improvements
   - Summary insights
5. The report will appear directly in the Slack channel where the command was issued.


**Note**: You can only run the `/generate_feedback` command in channels where IntelliCue is present and has permission to read messages.
 

---

## Using the Software

- **Feedback frequency**: You can run `/generate_feedback` anytime. Daily or weekly use is recommended for ongoing feedback cycles.
- **Private channels**: IntelliCue works in private channels, but must be explicitly invited and granted permission.
- **Multiple channels**: IntelliCue can be used in multiple channels concurrently.
- **PDF storage**: Generated PDFs are posted in-channel and also stored securely in the cloud. Your Slack data is never stored beyond what's needed for inference.

**Work in progress**:
- Scheduled auto-feedback (e.g., weekly reports sent automatically)
- Feedback dashboards with trend graphs, providing more specifc analytics
- Custom analysis range (date filtering)
- Using feedback generated from the past as context for new feedback (better trend tracking)

---

## Reporting Bugs

If you encounter issues, please submit a bug report via our [GitHub Issues Tracker](https://github.com/amgupta2/IntelliCue/issues).

When reporting a bug, include:
- A clear description of the issue
- Steps to reproduce
- What you expected to happen
- What actually happened
- Screenshots (if relevant)
- Slack channel name (if applicable)
- Whether the issue involved a private or public channel

Please use the “Bug Report” template in the GitHub Issues tab to ensure all required details are captured.

---

## Known Bugs

All known issues are tracked [here](https://github.com/amgupta2/IntelliCue/issues?q=is%3Aissue+is%3Aopen+label%3Abug).

---

## ⚠️ IMPORTANT NOTE

Please make sure you are on the `demo-branch` when running or testing IntelliCue. This branch reflects the current stable demo configuration.

This user guide is only applicable after we've hosted our backend on AWS and published to the Slack Marketplace. Until then, please refer to the README to use a beta version of this project locally specifically on the `demo-branch`

---

Thank you for using IntelliCue!


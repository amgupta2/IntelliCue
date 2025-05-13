import subprocess
import time
import os
from slack_bolt import App
from dotenv import load_dotenv
from src.pipeline.insight import generate_insights_from_json
import json


def send_slack_message(app_client, message, channel="#general"):
    """Send a message to a Slack channel using the Slack Bolt client."""
    try:
        response = app_client.chat_postMessage(channel=channel, text=message)
        print(f"Message sent to Slack channel {channel}, response: {response}")
    except Exception as e:
        print(f"Error sending message to Slack: {e}")


def run_pipeline():
    load_dotenv()
    # Initialize Slack app client
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    app = App(token=slack_token)
    app_client = app.client

    # Step 1: Call the Slack app
    print("Starting Slack app...")
    slack_app_process = subprocess.Popen(
        ["python", "-m", "src.slack_app.app"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Step 2: Wait for the JSON file to be created
    output_file = "output/messages.json"
    print(f"Waiting for {output_file} to be created...")
    while not os.path.exists(output_file):
        time.sleep(1)

    print(f"{output_file} has been created.")

    # Step 3: Call the preprocessing step
    print("Starting preprocessing...")
    preprocessing_process = subprocess.run(
        ["python", "-m", "src.pipeline.preprocessing"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Print output and errors from preprocessing
    print("Preprocessing output:")
    print(preprocessing_process.stdout.decode())
    if preprocessing_process.stderr:
        print("Preprocessing errors:")
        print(preprocessing_process.stderr.decode())

    # Ensure the Slack app process is terminated
    slack_app_process.terminate()

    # Generate insights from the preprocessed messages
    with open("output/preprocessed_messages.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    insights_data = generate_insights_from_json(data)

    # Step 4: Send insights to Slack in Formatted Message
    print("Sending insights to Slack...")
    send_slack_message(app_client, insights_data["slack_message"],
                       channel="#all-intellicue")

    print("Pipeline execution completed.")


if __name__ == "__main__":
    run_pipeline()

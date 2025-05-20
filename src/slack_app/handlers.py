import os
import json
from slack_bolt import App
from slack_sdk import WebClient
from src.slack_app.client import get_joined_channels, format_message


def register_handlers(app: App, client: WebClient):
    @app.command("/generate_feedback")
    def handle_generate_feedback(ack, body, respond, logger):
        ack()

        try:
            all_messages = []
            channels = get_joined_channels(client)

            for channel in channels:
                channel_id = channel["id"]
                channel_name = channel["name"]
                cursor = None

                while True:
                    history = client.conversations_history(
                        channel=channel_id, cursor=cursor, limit=200)
                    messages = history.get("messages", [])

                    for msg in messages:
                        all_messages.append(
                            format_message(msg, channel_id, channel_name))

                    cursor = history.get(
                        "response_metadata", {}).get("next_cursor")
                    if not cursor:
                        break

            # Save to JSON
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "messages.json")
            with open(output_path, "w") as f:
                json.dump(all_messages, f, indent=2)

            respond(
                f"Extracted {len(all_messages)} messages from {len(channels)}"
                f" channels and saved to `{output_path}`."
            )

        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            respond("Failed to extract messages due to an error.")

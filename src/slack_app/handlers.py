from slack_bolt import App
from slack_sdk import WebClient
import json


def register_handlers(app: App):
    @app.message("hello")
    def message_hello(message, say):
        say(
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text":
                             f"Hey there <@{message['user']}>!"},
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click Me"},
                        "action_id": "button_click"
                    }
                }
            ],
            text=f"Hey there <@{message['user']}>!"
        )

    def fetch_all_messages(client: WebClient, channel: str):
        messages = []
        cursor = None

        while True:
            response = client.conversations_history(
                channel=channel, limit=200, cursor=cursor)
            messages.extend(response.get("messages", []))
            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        return messages

    @app.action("button_click")
    def action_button_click(body, ack, say, client: WebClient):
        ack()
        other_channel = "C08PH0ZP82E"

        all_messages = fetch_all_messages(client, other_channel)
        msg_str = json.dumps(all_messages, indent=2)

        # Split into 3800-character chunks to avoid hitting char limit
        chunk_size = 3800
        chunks = [msg_str[i:i+chunk_size] for i in
                  range(0, len(msg_str), chunk_size)]

        for i, chunk in enumerate(chunks):
            prefix = (
                "*Full message object"
                f" from <#{other_channel}> — Part {i + 1}/{len(chunks)}:*"
            )
            say(f"{prefix}\n```{chunk}```")

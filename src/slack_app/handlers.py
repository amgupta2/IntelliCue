import os
import json
from slack_bolt import App
from slack_sdk import WebClient

def register_handlers(app: App):
    @app.message("hello")
    def message_hello(message, say):
        say(
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click Me"},
                        "action_id": "button_click"
                    }
                }
            ],
            text=f"Hey there <@{message['user']}>!"
        )

    @app.action("button_click")
    def action_button_click(body, ack, say, client: WebClient):
        ack()
        other_channel = "C08PH0ZP82E"
        result = client.conversations_history(channel=other_channel, limit=1)
        messages = result.get("messages", [])
        msg_str = json.dumps(messages[0], indent=2) if messages else "No messages found."

        if len(msg_str) > 3900:
            msg_str = msg_str[:3900] + "\n... [truncated]"

        say(f"*Full message object from <#{other_channel}>:*\n```{msg_str}```")

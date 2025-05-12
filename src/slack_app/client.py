from slack_sdk import WebClient


def get_latest_message(client: WebClient, channel_id: str):
    result = client.conversations_history(channel=channel_id, limit=1)
    return result.get("messages", [])

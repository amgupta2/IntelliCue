from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_joined_channels(client: WebClient):
    try:
        result = client.conversations_list(types="public_channel,private_channel")

        return [
            {"id": channel["id"], "name": channel["name"]}
            for channel in result["channels"]
            if channel.get("is_member", False)
        ]
    except SlackApiError as e:
        print(f"Error fetching conversations: {e}")
        return []

def format_message(raw_msg, channel_id, channel_name=None):
    return {
        "channel_id": channel_id,
        "channel_name": channel_name,
        "user_id": raw_msg.get("user"),
        "message_text": raw_msg.get("text"),
        "message_type": raw_msg.get("type"),
        "timestamp": raw_msg.get("ts"),
        "parent_thread_ts": raw_msg.get("thread_ts", raw_msg.get("ts")),
        "is_thread_reply": raw_msg.get("thread_ts", raw_msg.get("ts")) != raw_msg.get("ts"),
        "reactions": [
            {
                "name": r.get("name"),
                "count": r.get("count")
            } for r in raw_msg.get("reactions", [])
        ],
        "subtype": raw_msg.get("subtype"),
        "sent_by_bot_id": raw_msg.get("bot_id"),
        "last_edited": (
            {
                "edited_by": raw_msg["edited"]["user"],
                "edit_timestamp": raw_msg["edited"]["ts"]
            } if "edited" in raw_msg else None
        )
    }


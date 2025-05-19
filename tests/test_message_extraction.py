from src.slack_app import client
from slack_sdk.errors import SlackApiError


def test_format_message_basic():
    raw_msg = {
        "user": "U123",
        "text": "Hello world",
        "type": "message",
        "ts": "1234567890.12345"
    }
    result = client.format_message(raw_msg, "C456", "general")
    assert result["channel_id"] == "C456"
    assert result["channel_name"] == "general"
    assert result["user_id"] == "U123"
    assert result["message_text"] == "Hello world"
    assert result["message_type"] == "message"
    assert result["timestamp"] == "1234567890.12345"
    assert result["parent_thread_ts"] == "1234567890.12345"
    assert result["is_thread_reply"] is False
    assert result["reactions"] == []
    assert result["subtype"] is None
    assert result["sent_by_bot_id"] is None
    assert result["last_edited"] is None


def test_format_message_thread_reply():
    raw_msg = {
        "user": "U123",
        "text": "Reply",
        "type": "message",
        "ts": "1234567890.12345",
        "thread_ts": "1234567890.00000"
    }
    result = client.format_message(raw_msg, "C456")
    assert result["parent_thread_ts"] == "1234567890.00000"
    assert result["is_thread_reply"] is True


def test_format_message_with_reactions_and_edit():
    raw_msg = {
        "user": "U123",
        "text": "Edited message",
        "type": "message",
        "ts": "1234567890.12345",
        "reactions": [
            {"name": "thumbsup", "count": 2},
            {"name": "eyes", "count": 1}
        ],
        "edited": {"user": "U456", "ts": "1234567891.00000"}
    }
    result = client.format_message(raw_msg, "C789")
    assert result["reactions"] == [
        {"name": "thumbsup", "count": 2},
        {"name": "eyes", "count": 1}
    ]
    assert result["last_edited"] == {
        "edited_by": "U456",
        "edit_timestamp": "1234567891.00000"
    }


def test_get_joined_channels_success(mocker):
    mock_client = mocker.Mock()
    mock_client.conversations_list.return_value = {
        "channels": [
            {"id": "C1", "name": "general", "is_member": True},
            {"id": "C2", "name": "random", "is_member": False},
            {"id": "C3", "name": "dev", "is_member": True}
        ]
    }
    channels = client.get_joined_channels(mock_client)
    assert channels == [
        {"id": "C1", "name": "general"},
        {"id": "C3", "name": "dev"}
    ]


def test_get_joined_channels_error(mocker):
    mock_client = mocker.Mock()
    mock_client.conversations_list.side_effect = SlackApiError(
        "API error", response=None
    )
    channels = client.get_joined_channels(mock_client)
    assert channels == []


def test_format_message_with_attachments():
    raw_msg = {
        "user": "U123",
        "text": "Message with attachment",
        "type": "message",
        "ts": "1234567890.12345",
        "attachments": [
            {
                "type": "image",
                "url": "https://example.com/image.jpg",
                "title": "Test Image"
            }
        ]
    }
    result = client.format_message(raw_msg, "C456")
    assert "attachments" in result
    assert len(result["attachments"]) == 1
    assert result["attachments"][0]["type"] == "image"
    assert result["attachments"][0]["url"] == "https://example.com/image.jpg"


def test_format_message_with_blocks():
    raw_msg = {
        "user": "U123",
        "text": "Message with blocks",
        "type": "message",
        "ts": "1234567890.12345",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Bold text*"
                }
            }
        ]
    }
    result = client.format_message(raw_msg, "C456")
    assert "blocks" in result
    assert len(result["blocks"]) == 1
    assert result["blocks"][0]["type"] == "section"


def test_format_message_with_metadata():
    raw_msg = {
        "user": "U123",
        "text": "Message with metadata",
        "type": "message",
        "ts": "1234567890.12345",
        "metadata": {
            "event_type": "message",
            "event_payload": {"key": "value"}
        }
    }
    result = client.format_message(raw_msg, "C456")
    assert "metadata" in result
    assert result["metadata"]["event_type"] == "message"
    assert result["metadata"]["event_payload"]["key"] == "value"


def test_get_joined_channels_with_pagination(mocker):
    mock_client = mocker.Mock()
    mock_client.conversations_list.side_effect = [
        {
            "channels": [
                {"id": "C1", "name": "general", "is_member": True},
                {"id": "C2", "name": "random", "is_member": True}
            ],
            "response_metadata": {"next_cursor": "next_page"}
        },
        {
            "channels": [
                {"id": "C3", "name": "dev", "is_member": True}
            ],
            "response_metadata": {"next_cursor": ""}
        }
    ]
    channels = client.get_joined_channels(mock_client)
    assert len(channels) == 3
    assert channels[0]["id"] == "C1"
    assert channels[1]["id"] == "C2"
    assert channels[2]["id"] == "C3"


def test_get_joined_channels_with_rate_limit(mocker):
    mock_client = mocker.Mock()
    mock_client.conversations_list.side_effect = SlackApiError(
        "rate_limited", response={"headers": {"Retry-After": "1"}}
    )
    channels = client.get_joined_channels(mock_client)
    assert channels == []
    assert mock_client.conversations_list.call_count == 1


def test_format_message_with_thread_reactions():
    raw_msg = {
        "user": "U123",
        "text": "Thread message",
        "type": "message",
        "ts": "1234567890.12345",
        "thread_ts": "1234567890.00000",
        "reactions": [
            {"name": "thumbsup", "count": 1, "users": ["U123"]}
        ]
    }
    result = client.format_message(raw_msg, "C456")
    assert result["is_thread_reply"] is True
    assert len(result["reactions"]) == 1
    assert result["reactions"][0]["name"] == "thumbsup"
    assert result["reactions"][0]["count"] == 1
    assert "users" in result["reactions"][0]


def test_format_message_with_bot_user():
    raw_msg = {
        "bot_id": "B123",
        "text": "Bot message",
        "type": "message",
        "ts": "1234567890.12345",
        "subtype": "bot_message"
    }
    result = client.format_message(raw_msg, "C456")
    assert result["sent_by_bot_id"] == "B123"
    assert result["subtype"] == "bot_message"
    assert result["is_thread_reply"] is False


def test_format_message_with_mentions():
    raw_msg = {
        "user": "U123",
        "text": "Hello <@U456> and <@U789>!",
        "type": "message",
        "ts": "1234567890.12345"
    }
    result = client.format_message(raw_msg, "C456")
    assert "mentions" in result
    assert len(result["mentions"]) == 2
    assert "U456" in result["mentions"]
    assert "U789" in result["mentions"]


def test_format_message_with_links():
    raw_msg = {
        "user": "U123",
        "text": "Check out <https://example.com|this link>",
        "type": "message",
        "ts": "1234567890.12345"
    }
    result = client.format_message(raw_msg, "C456")
    assert "links" in result
    assert len(result["links"]) == 1
    assert result["links"][0]["url"] == "https://example.com"
    assert result["links"][0]["text"] == "this link"


def test_format_message_with_emoji():
    raw_msg = {
        "user": "U123",
        "text": "Hello :smile: :wave:",
        "type": "message",
        "ts": "1234567890.12345"
    }
    result = client.format_message(raw_msg, "C456")
    assert "emojis" in result
    assert len(result["emojis"]) == 2
    assert ":smile:" in result["emojis"]
    assert ":wave:" in result["emojis"]


def test_format_message_with_file_share():
    raw_msg = {
        "user": "U123",
        "text": "Here's a file",
        "type": "message",
        "ts": "1234567890.12345",
        "files": [
            {
                "id": "F123",
                "name": "document.pdf",
                "filetype": "pdf",
                "size": 1024
            }
        ]
    }
    result = client.format_message(raw_msg, "C456")
    assert "files" in result
    assert len(result["files"]) == 1
    assert result["files"][0]["id"] == "F123"
    assert result["files"][0]["name"] == "document.pdf"


def test_format_message_with_thread_broadcast():
    raw_msg = {
        "user": "U123",
        "text": "Broadcast message",
        "type": "message",
        "ts": "1234567890.12345",
        "thread_ts": "1234567890.00000",
        "subtype": "thread_broadcast"
    }
    result = client.format_message(raw_msg, "C456")
    assert result["is_thread_reply"] is True
    assert result["subtype"] == "thread_broadcast"
    assert result["is_broadcast"] is True


def test_format_message_with_edited_thread():
    raw_msg = {
        "user": "U123",
        "text": "Edited thread message",
        "type": "message",
        "ts": "1234567890.12345",
        "thread_ts": "1234567890.00000",
        "edited": {
            "user": "U456",
            "ts": "1234567891.00000"
        }
    }
    result = client.format_message(raw_msg, "C456")
    assert result["is_thread_reply"] is True
    assert result["last_edited"]["edited_by"] == "U456"
    assert result["last_edited"]["edit_timestamp"] == "1234567891.00000"


def test_format_message_with_pinned_item():
    raw_msg = {
        "user": "U123",
        "text": "Pinned message",
        "type": "message",
        "ts": "1234567890.12345",
        "pinned_to": ["C456"],
        "pinned_info": {
            "pinned_by": "U789",
            "pinned_at": "1234567891.00000"
        }
    }
    result = client.format_message(raw_msg, "C456")
    assert result["is_pinned"] is True
    assert result["pinned_by"] == "U789"
    assert result["pinned_at"] == "1234567891.00000"


def test_format_message_with_subtype_changed():
    raw_msg = {
        "user": "U123",
        "text": "Channel purpose changed",
        "type": "message",
        "ts": "1234567890.12345",
        "subtype": "channel_purpose",
        "purpose": "New channel purpose"
    }
    result = client.format_message(raw_msg, "C456")
    assert result["subtype"] == "channel_purpose"
    assert result["purpose"] == "New channel purpose"


def test_format_message_with_team_join():
    raw_msg = {
        "user": "U123",
        "text": "Welcome to the team!",
        "type": "message",
        "ts": "1234567890.12345",
        "subtype": "team_join",
        "inviter": "U456"
    }
    result = client.format_message(raw_msg, "C456")
    assert result["subtype"] == "team_join"
    assert result["inviter"] == "U456"


def test_format_message_with_channel_join():
    raw_msg = {
        "user": "U123",
        "text": "has joined the channel",
        "type": "message",
        "ts": "1234567890.12345",
        "subtype": "channel_join"
    }
    result = client.format_message(raw_msg, "C456")
    assert result["subtype"] == "channel_join"
    assert result["is_system_message"] is True

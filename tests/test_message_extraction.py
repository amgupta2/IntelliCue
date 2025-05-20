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
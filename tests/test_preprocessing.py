import sys
import json
import tempfile
import os
# Import the MessageParser class from the module
from src.pipeline.preprocessing import MessageParser


def test_json_single_message(monkeypatch, capsys):
    # Create a temporary file with a single message
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json',
                                     delete=False) as temp_file:
        json.dump([
            {
                "channel_id": "C08PH0ZMY7L",
                "channel_name": "all-intellicue",
                "user_id": "U08PH0ZCNCA",
                "message_text": "hello",
                "message_type": "message",
                "timestamp": "1746565594.746919",
                "parent_thread_ts": "1746565594.746919",
                "is_thread_reply": False,
                "reactions": [],
                "subtype": None,
                "sent_by_bot_id": None,
                "last_edited": None
            }
        ], temp_file)

        temp_file_path = temp_file.name

    # Mock the command line arguments
    monkeypatch.setattr(sys, 'argv', ['script_name', temp_file_path])

    # Create an instance of MessageParser
    parser = MessageParser(temp_file_path)

    # Load messages
    parser.load_messages()
    parser.group_messages()

    # Check if the output is as expected
    assert len(parser.grouped_messages) == 1
    keys = list(parser.grouped_messages.keys())
    assert keys[0] == "C08PH0ZMY7L"
    channel_thr = parser.grouped_messages["C08PH0ZMY7L"]["1746565594.746919"]
    assert channel_thr[0].message_text == "hello"

    # Clean up the temporary file
    os.remove(temp_file_path)

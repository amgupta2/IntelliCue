import sys
import json
import tempfile
import os
# Import the MessageParser class from the module
from src.pipeline.preprocessing import MessageParser

def test_json_single_message(monkeypatch, capsys):
    # Create a temporary file with a single message
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        json.dump({"channel_id": "C08PH0ZMY7L", "channel_name": "all-intellicue", "user_id": "U08P58RHHB8", "message_text": "Hey there <@U08PH0ZCNCA>!", "message_type": "message", "timestamp": "1746565596.670189", "parent_thread_ts": "1746565596.670189", "is_thread_reply": False, "reactions": [], "subtype": None, "sent_by_bot_id": "B08P58RHH7G", "last_edited": None}, temp_file)
        temp_file_path = temp_file.name

    # Mock the command line arguments
    monkeypatch.setattr(sys, 'argv', ['script_name', temp_file_path])

    # Create an instance of MessageParser
    parser = MessageParser(temp_file_path)

    # Load messages
    parser.load_messages()

    # Capture the output
    captured = capsys.readouterr()

    # Check if the output is as expected
    assert len(parser.unscored_messages) == 1
    assert parser.unscored_messages[0].text == "Hey there <@U08PH0ZCNCA>!"
    assert parser.unscored_messages[0].user == "U08P58RHHB8"
    assert parser.unscored_messages[0].team == "T12345"

    # Clean up the temporary file
    os.remove(temp_file_path)
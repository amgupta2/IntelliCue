import sys
import json
import tempfile
import os
# Import the MessageParser class from the module
from src.pipeline.preprocessing import MessageParser

def test_json_single_message(monkeypatch, capsys):
    # Create a temporary file with a single message
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        json.dump({"messages": [{"type": "message", "client_msg_id": "12345", "user": "U12345", "team": "T12345", "text": "Hello, world!", "ts": 1620000000.000000}]}, temp_file)
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
    assert parser.unscored_messages[0].text == "Hello, world!"
    assert parser.unscored_messages[0].user == "U12345"
    assert parser.unscored_messages[0].team == "T12345"

    # Clean up the temporary file
    os.remove(temp_file_path)
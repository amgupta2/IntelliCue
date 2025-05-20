import json
import sys
from datetime import datetime
from pathlib import Path

"""
An object used to represent a message in the Slack export before it is passed 
through the Sentiment Analysis Model.

Fields:
- message_text: The text of the message.
- reactions: The reactions to the message.
- channel_id: The unique identifier of the channel.
- channel_name: The name of the channel.
- timestamp: The timestamp of the message (also used as a unique identifier).
- is_thread_reply: whether the message is a reply in a thread.
- parent_thread_ts: The timestamp of the parent thread if applicable.
"""
class UnscoredMessage:
    def __init__(self, message_text, reactions, channel_id, channel_name, timestamp, is_thread_reply, parent_thread_ts):
        self.message_text = message_text
        self.reactions = reactions
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.timestamp = float(timestamp)
        self.is_thread_reply = is_thread_reply
        self.parent_thread_ts = parent_thread_ts


    def to_dict(self):
        return {
            "message_text": self.message_text,
            "reactions": self.reactions,
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "timestamp": str(self.timestamp),
            "is_thread_reply": self.is_thread_reply,
            "parent_thread_ts": self.parent_thread_ts,
        }


"""
A class used to parse the Slack export JSON file and extract messages.
It loads the messages from the file and creates UnscoredMessage objects.

- checks if the file is a valid JSON file
- filters out non-message types and automated messages
- checks if a message is a thread reply

Also groups messages by channel and parent thread timestamp.
"""
class MessageParser:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.ungrouped_messages = []
        self.grouped_messages = {}

    """
    Load messages from the file and return a list of dictionaries.
    """
    def load_messages(self):
        # Open JSON file
        data = {}
        try:
            with open(self.input_path, 'r') as file:
                # Load JSON data
                data = json.load(file)

                # Run through all messages
                for message in data:
                    # Skip non-messages and automated messages
                    if message['message_type'] != 'message' or message['subtype'] is not None or message['sent_by_bot_id'] is not None:
                        continue

                    # Create new UnscoredMessage object
                    msg = None
                    if message['is_thread_reply']:
                        msg = UnscoredMessage(
                            message_text=message['message_text'],
                            reactions=message['reactions'],
                            channel_id=message['channel_id'],
                            channel_name=message['channel_name'],
                            timestamp=message['timestamp'],
                            is_thread_reply=True,
                            parent_thread_ts=message['parent_thread_ts']
                        )
                    else:
                        msg = UnscoredMessage(
                            message_text=message['message_text'],
                            reactions=message['reactions'],
                            channel_id=message['channel_id'],
                            channel_name=message['channel_name'],
                            timestamp=message['timestamp'],
                            is_thread_reply=False,
                            parent_thread_ts=message['timestamp']
                        )
                    # Add to unscored messages list
                    self.ungrouped_messages.append(msg)

        except json.JSONDecodeError:
            print(f"Error: The file {self.file_path} is not a valid JSON file.")
            sys.exit(1)
        except FileNotFoundError:
            print(f"Error: The file {self.file_path} was not found.")
            sys.exit(1) 

        return self.ungrouped_messages
    
    """
    Group messages by channel and parent thread timestamp.
    """
    def group_messages(self):

        for message in self.ungrouped_messages:
            # Create a channel key for the message
            channel_key = message.channel_id
            if channel_key not in self.grouped_messages:
                self.grouped_messages[channel_key] = {}
            channel_messages = self.grouped_messages[channel_key]

            # Create a parent thread key for the message
            parent_key = message.parent_thread_ts
            if parent_key not in channel_messages:
                channel_messages[parent_key] = []
            channel_messages[parent_key].append(message)

        return self.grouped_messages
    

    """
    Return the unscored messages to a JSON file.
    """
    def get_messages_json(self):
        # Get file path
        output_path = Path(self.output_path)
        self.group_messages()

        # Get grouped message data
        data = {}
        for channel_id, channel_messages in self.grouped_messages.items():
            data[channel_id] = {}
            for parent_ts, messages in channel_messages.items():
                data[channel_id][parent_ts] = [msg.to_dict() for msg in messages]

        # Save to JSON file
        with output_path.open('w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

        print(f"Unscored messages saved to {output_path}")
        return data


def main():
    # Check if the file path is provided
    if len(sys.argv) != 3:
        print("Usage: python preprocessing.py <input_path> <output_path>")
        sys.exit(1)

    # Get the input file path from command line arguments
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    mp = MessageParser(input_path, output_path)
    raw = mp.load_messages()
    
    # Get the output path from command line arguments
    mp.get_messages_json()


if __name__ == "__main__":
    main()
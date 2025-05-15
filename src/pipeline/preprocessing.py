import json
import sys
from datetime import datetime

"""
An object used to represent a message in the Slack export before it is passed 
through the Sentiment Analysis LLM.

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
            "timestamp": datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            "is_thread_reply": self.is_thread_reply,
            "parent_thread_ts": self.parent_thread_ts,
        }

"""
A class used to parse the Slack export JSON file and extract messages.
It loads the messages from the file and creates UnscoredMessage objects.
"""
class MessageParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.unscored_messages = []

    def load_messages(self):
        """
        Load messages from the file and return a list of dictionaries.
        """
        # Open JSON file
        data = {}
        try:
            with open(self.file_path, 'r') as file:
                # Load JSON data
                data = json.load(file)
                # Run through all messages
                for message in data:
                    # Skip non-messages and automated messages
                    if message['message_type'] != 'message' or message['subtype'] is not None or message['sent_by_bot_id'] is not None:
                        continue

                    msg = None
                    if message['is_thread_reply'] == True:
                        
                    # Create UnscoredMessage object
                    msg = UnscoredMessage(
                        message_text=message['message_text'],
                        reactions=message['reactions'],
                        channel_id=message['channel_id'],
                        channel_name=message['channel_name'],

                        # parent=message.get('parent_user_id') -- for now, we are not using parent
                    )
                    # Add to unscored messages list
                    self.unscored_messages.append(msg)

        except json.JSONDecodeError:
            print(f"Error: The file {self.file_path} is not a valid JSON file.")
            sys.exit(1)
        except FileNotFoundError:
            print(f"Error: The file {self.file_path} was not found.")
            sys.exit(1)

        return self.unscored_messages

def main():
    # Check if the file path is provided
    if len(sys.argv) != 2:
        print("Usage: python preprocessing.py <file_path>")
        sys.exit(1)

    # Get the file path from command line arguments
    file_path = sys.argv[1]
    mp = MessageParser(file_path)
    raw = mp.load_messages()
    
    # Print the loaded messages
    for message in raw:
        print(message.to_dict())


if __name__ == "__main__":
    main()
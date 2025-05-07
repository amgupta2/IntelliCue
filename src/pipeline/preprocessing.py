import json
import sys
from datetime import datetime

"""
An object used to represent a message in the Slack export before it is passed 
through the Sentiment Analysis LLM.
"""
class UnscoredMessage:
    def __init__(self, id, user, team, text, timestamp, parent=None):
        self.id = id
        self.user = user
        self.team = team
        self.text = text
        self.timestamp = float(timestamp)
        self.parent = parent


    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "timestamp": datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            "user": self.user,
            "parent": self.parent if self.parent else None,
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
                messsages = data['messages']
                for message in messsages:
                    if message['type'] == 'message' and 'subtype' not in message:
                        # Create UnscoredMessage object
                        msg = UnscoredMessage(
                            id=message['client_msg_id'],
                            user=message['user'],
                            team=message['team'],
                            text=message['text'],
                            timestamp=message['ts'],
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
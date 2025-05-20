from insight import generate_insights_from_json
import json

if __name__ == "__main__":
    # Load the JSON file (must be an array of {"message_text": "..."} entries)
    with open("preprocessed_messages.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    insights = generate_insights_from_json(data)

    print(json.dumps(insights, indent=2))  # or pass to another function

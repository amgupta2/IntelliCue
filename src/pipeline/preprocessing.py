from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import json

# Load the sentiment analysis model and tokenizer
model_name = "tabularisai/multilingual-sentiment-analysis"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


def predict_sentiment(texts):
    inputs = tokenizer(texts, return_tensors="pt",
                       truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentiment_map = {0: "Very Negative", 1: "Negative",
                     2: "Neutral", 3: "Positive", 4: "Very Positive"}
    return [sentiment_map[p] for p in torch.argmax(
        probabilities, dim=-1).tolist()]


def preprocess_messages(messages):
    preprocessed_messages = []
    for message in messages:
        # Skip messages containing the word "hello" (case-insensitive)
        if "hello" in message["message_text"].lower():
            continue

        # Remove unwanted fields
        preprocessed_message = {
            key: value for key, value in message.items()
            if key not in ["user_id", "channel_id", "channel_name"]
        }
        # Add sentiment score
        sentiment = predict_sentiment([message["message_text"]])[0]
        preprocessed_message["sentiment_score"] = sentiment
        preprocessed_messages.append(preprocessed_message)
    return preprocessed_messages


def main():
    with open("output/messages.json", "r") as f:
        messages = json.load(f)
    preprocessed_messages = preprocess_messages(messages)
    with open("output/preprocessed_messages.json", "w") as f:
        json.dump(preprocessed_messages, f, indent=2)
    print(f"Preprocessed {len(messages)} messages")


if __name__ == "__main__":
    main()

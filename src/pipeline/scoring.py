from transformers import pipeline
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification as AutoModel
)
import numpy as np
import torch
import json
import sys
from preprocessing import MessageParser
from pathlib import Path

"""
Used to classify messages into different categories such as question,
feedback, complaint, praise, or other.This is done using a zero-shot
classification model.
"""


class ZeroShotClassifier:
    def __init__(self, model_name="facebook/bart-large-mnli"):
        self.classifier = pipeline("zero-shot-classification",
                                   model=model_name)

    def classify(self, text,
                 labels=["inquiry", "goal", "complaint", "praise", "other"]):
        results = self.classifier(text, labels)
        return results


"""
Used to analyze the sentiment of messages into positive, negative, or neutral.
This is done using a pre-trained sentiment analysis model.
"""


class SentimentAnalyzer:
    def __init__(self, model_name="cardiffnlp/twitter-roberta-base-sentiment"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def analyze_sentiment(self, text):
        encoded_input = self.tokenizer(text, return_tensors='pt')
        result = self.model(**encoded_input)
        scores = result[0][0].detach().numpy()

        normalized_scores = torch.nn.functional.softmax(
            torch.tensor(scores), dim=0)
        return normalized_scores


class ScoredMessage:
    def __init__(self):
        self.message_text = None
        self.timestamp = None
        self.parent_thread_ts = None
        self.sentiment = None
        self.category = None
        self.reactions = None

    def to_dict(self):
        return {
            "message_text": self.message_text,
            "timestamp": self.timestamp,
            "parent_thread_ts": self.parent_thread_ts,
            "sentiment": self.sentiment,
            "category": self.category,
            "reactions": self.reactions
        }


class ScoringPipeline:
    def __init__(self, unscored_messages):
        self.unscored_messages = unscored_messages
        self.scored_messages = []

    def score_messages(self):
        sa = SentimentAnalyzer()
        zcs = ZeroShotClassifier()

        print("Scoring messages...")

        for channel, threads in self.unscored_messages.items():
            for thread_id, thread in threads.items():
                if len(thread) == 0:
                    continue

                context = []
                for message in thread:
                    # Clustering algorithm
                    # - if single message, run normally
                    # - if part of thread, use previous text as context

                    # Filtering algorithm
                    # - if negative, keep no matter what
                    # - if positive or neutral:
                    #   - check categories
                    #   - keep if any category is >= 0.5

                    text = message.message_text
                    if len(context) > 0:
                        text = "\n".join(context) + "\n" + text

                    # Analyze sentiment
                    sentiments = ["negative", "neutral", "positive"]
                    raw_sentiment_scores = sa.analyze_sentiment(text)
                    sentiment_score_idx = np.argmax(raw_sentiment_scores)
                    sentiment = sentiments[sentiment_score_idx]

                    # Classify message
                    raw_category_results = zcs.classify(text)
                    category = raw_category_results['labels']
                    scores = raw_category_results['scores']

                    # Create ScoredMessage object
                    scored_message = ScoredMessage()
                    scored_message.message_text = text
                    scored_message.timestamp = message.timestamp
                    scored_message.parent_thread_ts = message.parent_thread_ts
                    scored_message.sentiment = sentiment
                    scored_message.category = category[0]
                    scored_message.reactions = message.reactions

                    if sentiment != "negative":
                        if category[0] == "other" or scores[0] < 0.5:
                            continue

                    self.scored_messages.append(scored_message.to_dict())

                    context.append(message.message_text)

        print("Scoring completed.")
        return self.scored_messages

    def save_scored_json(self):
        pass


def main():
    if len(sys.argv) != 3:
        print("Usage: python scoring.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    mp = MessageParser(input_path)
    mp.load_messages()
    unscored = mp.group_messages()

    sp = ScoringPipeline(unscored)
    scored = sp.score_messages()

    # Save scored messages to JSON
    # Get file path
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save scored messages to JSON file
    with open(output_path, 'w') as f:
        json.dump(scored, f, indent=4)
    print(f"Scored messages saved to {output_path}")


if __name__ == "__main__":
    main()

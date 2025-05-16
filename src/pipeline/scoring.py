from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import torch

"""
Used to classify messages into different categories such as question, feedback, complaint, praise, or other.
This is done using a zero-shot classification model.
"""
class ZeroShotClassifier:
    def __init__(self, model_name="facebook/bart-large-mnli"):
        self.classifier = pipeline("zero-shot-classification", model=model_name)


    def classify(self, text, labels=["question", "feedback", "complaint", "praise", "other"]):
        results = self.classifier(text, labels)
        return results
    
    
"""
Used to analyze the sentiment of messages into positive, negative, or neutral.
This is done using a pre-trained sentiment analysis model.
"""
class SentimentAnalyzer:
    def __init__(self, model_name="cardiffnlp/twitter-roberta-base-sentiment"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)


    def analyze_sentiment(self, text):
        encoded_input = self.tokenizer(text, return_tensors='pt')
        result = self.model(**encoded_input)
        scores = result[0][0].detach().numpy()

        normalized_scores = torch.nn.functional.softmax(torch.tensor(scores), dim=0)
        return normalized_scores
    
    
class ScoredMessage:
    def __init__(self):
        self.id = None  

"""
class ScoringPipeline:
"""

def main():
    # # Example usage (sentiment)
    # analyzer = SentimentAnalyzer()
    # text = "Hey I need some help on this"
    # scores = analyzer.analyze_sentiment(text)
    # print(scores)

    # # Example usage (emotion)
    # emotion_analyzer = EmotionAnalyzer()
    # text = "Ok so u hate me"
    # emotions = emotion_analyzer.analyze_emotion(text)
    # print(emotions)

    # Example usage (zero-shot classification)
    classifier = ZeroShotClassifier()
    text = "yeah we would like to get that fixed. i will try to modify the docker image directly because the repo producing that docker image is not opensourced. from our side, we took all the protos and generated java files using maven. things seem to work so far."
    print(classifier.classify(text))
    text = "I love bananas!"
    print(classifier.classify(text))



if __name__ == "__main__":
    main()
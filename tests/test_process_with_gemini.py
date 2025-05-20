from src.pipeline.insight import process_with_gemini
from unittest.mock import MagicMock, patch
import json


@patch('google.generativeai.GenerativeModel')
def test_process_with_gemini(mock_model_class):
    # Mock response text (Gemini's output)
    mock_json = {
        "overall_tone_summary": {
            "general_emotional_direction": "Mostly positive",
            "positive_percentage": "40%",
            "negative_percentage": "30%",
            "neutral_percentage": "30%",
            "positive_count": 4,
            "negative_count": 3,
            "neutral_count": 3
        },
        "key_issues": [
            {
                "issue": "Delayed responses",
                "supporting_messages": [
                    "I had to wait a long time for a reply.",
                    "Support was very slow."
                ]
            }
        ],
        "actionable_next_steps": [
            "Improve response time",
            "Hire more support staff",
            "Implement automated replies"
        ],
        "visuals": {
            "sentiment_bar_chart": "Positive: ###\nNegative: ##\nNeutral: ##"
        }
    }

    # Setup mocks
    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_json)
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model

    # Run test
    result = process_with_gemini("Example message with sentiment")
    assert result == mock_json

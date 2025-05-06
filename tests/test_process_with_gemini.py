from src.pipeline.insight import process_with_gemini
from unittest.mock import MagicMock, patch

@patch('google.generativeai.GenerativeModel')
def test_process_with_gemini(mock_model_class):
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "Mocked insight response."
    mock_model_class.return_value = mock_model

    result = process_with_gemini("Test message")
    assert "Mocked insight" in result
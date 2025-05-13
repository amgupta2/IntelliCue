import os
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


def process_with_gemini(messages_text):
    """Sends the combined text to Gemini and returns insights."""
    model = genai.GenerativeModel('gemini-1.5-flash-8b')
    prompt = f"""
    You are an expert business analyst.
    Given the following text messages:

    {messages_text}

    Perform the following tasks:
    1. Summarize the overall positive and negative tones.
    2. Identify key issues or concerns mentioned.
    3. Suggest 3-5 actionable next steps to improve the situation
     based on the messages.

    Be concise but detailed. Use bullet points where appropriate.
    """
    print(prompt)
    response = model.generate_content(prompt)
    return response.text.strip()
    return ""


def generate_insights_from_json(json_data: list[dict]) -> dict:
    """
    Accepts a list of message objects with message_text and sentiment_value,
    prepares them for analysis, and returns Gemini's insights.
    """
    combined_entries = ""
    for entry in json_data:
        text = entry.get("message_text", "").strip()
        sentiment = entry.get("sentiment_score", "").strip()
        combined_entries += f"- Message: {text}\n  Sentiment: {sentiment}\n\n"

    # Generate insights dynamically using Gemini
    insights = process_with_gemini(combined_entries)

    # Dynamically format the insights for Slack
    formatted_insights = f"""
    *Insights Generated from Slack Messages*

    {insights}

    *Actionable Next Steps*
    Please review the above insights
    and take appropriate actions to address the identified issues.
    """

    return {
        "insights": insights.strip(),
        "slack_message": formatted_insights.strip()
    }

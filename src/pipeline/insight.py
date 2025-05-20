import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


def process_with_gemini(messages_text):
    """Sends the combined text to Gemini and returns structured insights."""
    model = genai.GenerativeModel('gemini-1.5-flash-8b')

    prompt = f"""
    You are an expert business analyst.

    Given the following internal messages with sentiment scores:

    {messages_text}

    Perform the following:
    1. Summarize the **overall tone** (positive, neutral, negative) 
     with statistics:
    - Include count and percentage breakdowns.
    - Output a textual summary of the emotional direction.
    2. Summarize **category insights**:
    - Show which categories were most common.
    - Include message counts and percentages.
    - Highlight key categories of concern (e.g. complaints, suggestions).
    3. List **key issues or concerns** mentioned 
     (bulleted list with concise details).
    - For each issue, include 1–3 example messages that support or 
     illustrate the issue (quote them directly).
    4. Recommend **3–5 actionable next steps** to improve team morale 
     and customer satisfaction (with concise details).
    5. Include **basic visuals**, such as an ASCII bar chart or tables 
     for sentiment breakdown.

    Return the results as a valid JSON object using the following structure:
    {{
    "overall_tone_summary": {{
        "general_emotional_direction": "e.g. Mostly positive",
        "positive_percentage": "e.g. 32%",
        "negative_percentage": "e.g. 18%",
        "neutral_percentage": "e.g. 50%",
        "positive_count": int,
        "negative_count": int,
        "neutral_count": int
    }},
    "key_issues": [
        {{
        "issue": "description of the issue",
        "supporting_messages": [
            "example message 1",
            "example message 2"
        ]
        }},
        ...
    ],
    "actionable_next_steps": [ "step 1", "step 2", ... ],
    "visuals": {{
        "sentiment_bar_chart": "your ascii chart here"
    }}
    }}

    Only return the JSON. Do not wrap the output in markdown or use ```json.
    """

    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # If wrapped in triple backticks, unwrap it
    if raw_text.startswith("```json"):
        raw_text = raw_text.strip("```json").strip("```").strip()
    elif raw_text.startswith("```"):
        raw_text = raw_text.strip("```").strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        print("⚠️ Warning: Gemini response is not valid JSON.")
        return {"raw_response": raw_text}


def generate_insights_from_json(json_data: list[dict]) -> dict:
    """Formats input messages and gets Gemini insights."""
    combined_entries = ""
    for entry in json_data:
        text = entry.get("message_text", "").strip()
        sentiment = entry.get("sentiment", "").strip()
        category = entry.get("category", "").strip()
        combined_entries += f"- Message: {text}\n"
        combined_entries += f"  Sentiment: {sentiment}\n  Category: {category}\n\n"

    insights = process_with_gemini(combined_entries)
    return insights
    
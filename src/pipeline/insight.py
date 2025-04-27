import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def extract_data(file):
    bytes_data = file.getvalue()
    # Convert bytes to string
    json_string = bytes_data.decode('utf-8')
    # Load JSON into a Python object (dict or list)
    data = json.loads(json_string)
    return data

def process_with_gemini(text):
    """Process the extracted text with Gemini API."""
    model = genai.GenerativeModel('gemini-1.5-pro')

    prompt = f"""
    You are an expert business analyst. 
    Given the following text messages:
    
    {text}
    
    Perform the following tasks:
    1. Summarize the overall positive and negative tones.
    2. Identify key issues or concerns mentioned.
    3. Suggest 3-5 actionable next steps to improve the situation based on the messages.

    Be concise but detailed. Use bullet points where appropriate.
    """

    response = model.generate_content(prompt)
    return response.text

def main():
    st.title("Upload a CSV File and Ask Questions")

    # File uploader
    uploaded_file = st.file_uploader("Choose a JSON file", type=["json"])

    if uploaded_file is not None:
        # Extract data
        extracted_json = extract_data(uploaded_file)

        # Assuming extracted_json is a list of message objects like [{"text": "message1"}, {"text": "message2"}]
        combined_text = ""
        for entry in extracted_json:
            combined_text += entry.get("text", "") + "\n"

        # Perform OCR
        if st.button("Generate Insights"):
            with st.spinner("Processing . . ."):
                analysis = process_with_gemini(combined_text)
                st.subheader("Insights and Next Steps:")
                st.write(analysis)


if __name__ == "__main__":
    main()
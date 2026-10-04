import os
from fastapi import FastAPI, Query
from google import genai

app = FastAPI()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.get("/ask")
def ask_ai(prompt: str = Query(..., description="Prompt for Gemini")):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

import os
from fastapi import FastAPI, Query
import google.generativeai as genai

app = FastAPI()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

@app.get("/ask")
def ask_ai(prompt: str = Query(..., description="Prompt for Gemini")):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

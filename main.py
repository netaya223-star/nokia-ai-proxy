import os
import requests
from fastapi import FastAPI, Query

app = FastAPI()

API_KEY = os.environ.get("GEMINI_API_KEY")

@app.get("/ask")
def ask_ai(prompt: str = Query(..., description="Prompt for Gemini")):
    if not API_KEY:
        return "Error: GEMINI_API_KEY is missing."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    
    try:
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        if res.status_code == 200:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return f"API Error ({res.status_code}): {data}"
    except Exception as e:
        return f"Exception: {str(e)}"


import os
import requests
from fastapi import FastAPI, Query

app = FastAPI()

API_KEY = os.environ.get("GEMINI_API_KEY")

@app.get("/ask")
def ask_ai(prompt: str = Query(..., description="Prompt for Gemini")):
    if not API_KEY:
        return "Error: GEMINI_API_KEY is missing."
    
    # שימוש בדגם 3.5-flash המורשה למשתמשים חדשים
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    
    try:
        res = requests.post(url, json=payload, timeout=15)
        data = res.json()
        
        if res.status_code == 200:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        
        # גיבוי למודל 3.1-flash-lite אם 3.5 לא זמין בחשבון החינמי
        backup_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={API_KEY}"
        res_backup = requests.post(backup_url, json=payload, timeout=15)
        data_backup = res_backup.json()
        
        if res_backup.status_code == 200:
            return data_backup["candidates"][0]["content"]["parts"][0]["text"]
            
        return f"API Error ({res.status_code}): {data}"
    except Exception as e:
        return f"Exception: {str(e)}"

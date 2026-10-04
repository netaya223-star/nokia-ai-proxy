import os
import requests
from fastapi import FastAPI, Query

app = FastAPI()

API_KEY = os.environ.get("GEMINI_API_KEY")

@app.get("/models")
def list_models():
    """בודק אילו דגמים פתוחים וזמינים עבור המפתח שלך"""
    if not API_KEY:
        return {"error": "GEMINI_API_KEY is missing"}
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    try:
        res = requests.get(url, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/ask")
def ask_ai(prompt: str = Query(..., description="Prompt for Gemini")):
    if not API_KEY:
        return "Error: GEMINI_API_KEY is missing."
    
    # ניסיון פנייה לדגם 2.5 העדכני/תואם
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    
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
        
        # אם יש שגיאת 404, מנסים גיבוי לדגם גרסת 1.5 מפורשת
        backup_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-002:generateContent?key={API_KEY}"
        res_backup = requests.post(backup_url, json=payload, timeout=15)
        data_backup = res_backup.json()
        
        if res_backup.status_code == 200:
            return data_backup["candidates"][0]["content"]["parts"][0]["text"]
            
        return f"API Error ({res.status_code}): {data}"
    except Exception as e:
        return f"Exception: {str(e)}"

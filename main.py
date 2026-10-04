import os
from fastapi import FastAPI, Query
import google.generativeai as genai

app = FastAPI()

# הגדרת המפתח מסביבת העבודה
API_KEY = os.environ.get("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

@app.get("/ask")
def ask_ai(prompt: str = Query(..., description="Prompt for Gemini")):
    if not API_KEY:
        return "Error: GEMINI_API_KEY is missing."
    
    try:
        # הספרייה מנהלת את ה-Endpoints בעצמה
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

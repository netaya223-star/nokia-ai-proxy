import os
from fastapi import FastAPI, Query
from google import genai

app = FastAPI()

# טעינת המפתח מסביבת העבודה של Render
API_KEY = os.environ.get("GEMINI_API_KEY")

@app.get("/ask")
def ask_ai(prompt: str = Query(..., description="Prompt for Gemini")):
    if not API_KEY:
        return "Error: GEMINI_API_KEY is missing in environment variables."
    
    try:
        # יצירת הלקוח הרשמי עם המפתח שלך
        client = genai.Client(api_key=API_KEY)
        
        # קריאה למודל באמצעות ה-SDK הרשמי
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error from Gemini SDK: {str(e)}"

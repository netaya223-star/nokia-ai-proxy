import os
import requests
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

app = FastAPI()

API_KEY = os.environ.get("GEMINI_API_KEY")

# דף HTML מותאם במיוחד למסכים קטנים ודפדפנים ישנים של Nokia
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nokia AI</title>
    <style>
        body { font-family: monospace; padding: 5px; background: #000; color: #fff; }
        input, button { width: 100%; margin-top: 5px; padding: 8px; font-size: 14px; }
        .box { border: 1px solid #555; padding: 8px; margin-top: 10px; background: #111; word-wrap: break-word; }
    </style>
</head>
<body>
    <h3>Nokia AI Proxy</h3>
    <form action="/" method="get">
        <input type="text" name="prompt" placeholder="Ask AI..." value="{prompt}">
        <button type="submit">Send</button>
    </form>
    {response_html}
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home(prompt: str = ""):
    if not prompt:
        return HTML_TEMPLATE.format(prompt="", response_html="")
    
    if not API_KEY:
        res_text = "Error: GEMINI_API_KEY missing."
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            res = requests.post(url, json=payload, timeout=15)
            data = res.json()
            if res.status_code == 200:
                res_text = data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                res_text = f"API Error ({res.status_code})"
        except Exception as e:
            res_text = f"Error: {str(e)}"
            
    response_html = f'<div class="box"><b>AI:</b><br>{res_text}</div>'
    return HTML_TEMPLATE.format(prompt=prompt, response_html=response_html)

@app.get("/ask")
def ask_ai(prompt: str = Query(..., description="Prompt for Gemini")):
    if not API_KEY:
        return "Error: GEMINI_API_KEY is missing."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, json=payload, timeout=15)
        data = res.json()
        if res.status_code == 200:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return f"API Error ({res.status_code})"
    except Exception as e:
        return f"Exception: {str(e)}"

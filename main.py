[05/10/2026 13:47] ת ת: import os
import time
import requests
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

app = FastAPI()

API_KEY = os.environ.get("GEMINI_API_KEY")

ACTIVE_MODEL = "models/gemini-1.5-flash"

def find_working_model():
    global ACTIVE_MODEL
    if not API_KEY:
        return
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            models = res.json().get("models", [])
            for m in models:
                name = m.get("name", "")
                methods = m.get("supportedGenerationMethods", [])
                if "flash" in name.lower() and "generateContent" in methods:
                    ACTIVE_MODEL = name
                    return
            for m in models:
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    ACTIVE_MODEL = m.get("name")
                    return
    except Exception as e:
        print(f"Error fetching models: {e}")

find_working_model()

def paginate_text(text: str, chunk_size: int = 250):
    if not text:
        return [""]
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def call_gemini(prompt: str):
    if not API_KEY:
        return "Error: GEMINI_API_KEY missing."
        
    url = f"https://generativelanguage.googleapis.com/v1beta/{ACTIVE_MODEL}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    for attempt in range(2):
        try:
            res = requests.post(url, json=payload, timeout=25)
            data = res.json()
            if res.status_code == 200:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            elif res.status_code in (404, 503) and attempt == 0:
                find_working_model()
                url = f"https://generativelanguage.googleapis.com/v1beta/{ACTIVE_MODEL}:generateContent?key={API_KEY}"
                time.sleep(1)
                continue
            else:
                return f"Google API Error ({res.status_code}): {data}"
        except Exception as e:
            if attempt == 1:
                return f"Error: {str(e)}"
            time.sleep(1)
    return "Error: Service unavailable after retry."

@app.get("/", response_class=HTMLResponse)
def home(prompt: str = "", page: int = 0):
    res_html = ""
    
    if prompt:
        res_text = call_gemini(prompt)
                
        pages = paginate_text(res_text)
        if page >= len(pages):
            page = len(pages) - 1
        if page < 0:
            page = 0
            
        current_page_text = pages[page]
        
        nav_buttons = ""
        if len(pages) > 1:
            nav_buttons = "<div style='margin-top:5px;'>"
            if page > 0:
                nav_buttons += f'<a href="/?prompt={prompt}&page={page-1}" style="color:#0f0; margin-left:10px;">[Prev]</a>'
            nav_buttons += f" Page {page+1}/{len(pages)} "
            if page < len(pages) - 1:
                nav_buttons += f'<a href="/?prompt={prompt}&page={page+1}" style="color:#0f0; margin-right:10px;">[Next]</a>'
            nav_buttons += "</div>"

        res_html = f'<div style="border:1px solid #555; padding:8px; margin-top:10px; background:#111; word-wrap:break-word;"><b>AI:</b><br>{current_page_text}<br>{nav_buttons}</div>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nokia AI</title>
        <style>
            body {{ font-family: monospace; padding: 5px; background: #000; color: #fff; }}
            input, button {{ width: 100%; margin-top: 5px; padding: 8px; font-size: 14px; box-sizing: border-box; }}
[05/10/2026 13:47] ת ת: </style>
    </head>
    <body>
        <h3>Nokia AI Proxy</h3>
        <form action="/" method="get">
            <input type="text" name="prompt" placeholder="Ask AI..." value="{prompt}">
            <button type="submit">Send</button>
        </form>
        {res_html}
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/ask")
def ask_ai(prompt: str = Query(..., description="Prompt for Gemini"), page: int = Query(0, description="Page number")):
    res_text = call_gemini(prompt)
    pages = paginate_text(res_text)
    if page >= len(pages):
        page = len(pages) - 1
    if page < 0:
        page = 0
    return pages[page]

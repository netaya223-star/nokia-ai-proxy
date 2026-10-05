import os
import time
import requests
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

app = FastAPI()

API_KEY = os.environ.get("GEMINI_API_KEY")

def paginate_text(text: str, chunk_size: int = 120):
    if not text:
        return [""]
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def get_gemini_response(prompt: str):
    if not API_KEY:
        return "Error: GEMINI_API_KEY missing."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    for attempt in range(4):
        try:
            res = requests.post(url, json=payload, timeout=25)
            data = res.json()
            if res.status_code == 200:
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    return f"API Structure Error: {data}"
            elif res.status_code == 503 and attempt < 3:
                time.sleep(2)
                continue
            else:
                return f"API Error ({res.status_code}): {data}"
        except Exception as e:
            if attempt == 3:
                return f"Error: {str(e)}"
            time.sleep(2)
    return "Error: Service unavailable."

@app.get("/", response_class=HTMLResponse)
def home(prompt: str = "", page: int = 0):
    res_html = ""
    
    if prompt:
        res_text = get_gemini_response(prompt)
                
        pages = paginate_text(res_text)
        if page >= len(pages):
            page = len(pages) - 1
        if page < 0:
            page = 0
            
        current_page_text = pages[page] if pages else ""
        
        nav_buttons = ""
        if len(pages) > 1:
            nav_buttons = "<div style='margin-top:3px; text-align:center;'>"
            if page > 0:
                nav_buttons += f'<a href="/?prompt={prompt}&page={page-1}" style="color:#0f0; text-decoration:none;">[&lt;]</a> '
            nav_buttons += f"<b>{page+1}/{len(pages)}</b>"
            if page < len(pages) - 1:
                nav_buttons += f' <a href="/?prompt={prompt}&page={page+1}" style="color:#0f0; text-decoration:none;">[&gt;]</a>'
            nav_buttons += "</div>"

        res_html = f'<div style="border:1px solid #444; padding:3px; margin-top:3px; background:#111; font-size:11px; word-break:break-all;"><b>AI:</b><br>{current_page_text}<br>{nav_buttons}</div>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=128, initial-scale=1.0">
        <title>Nokia AI</title>
        <style>
            body {{ 
                font-family: monospace; 
                background: #000; 
                color: #fff; 
                margin: 0; 
                padding: 2px; 
                width: 124px;
            }}
            input, button {{ 
                width: 100%; 
                margin-top: 2px; 
                padding: 3px; 
                font-size: 11px; 
                box-sizing: border-box; 
                background: #222; 
                color: #fff; 
                border: 1px solid #555;
            }}
            h3 {{ font-size: 12px; margin: 2px 0; text-align: center; }}
        </style>
    </head>
    <body>
        <h3>Nokia AI</h3>
        <form action="/" method="get">
            <input type="text" name="prompt" placeholder="Ask..." value="{prompt}">
            <button type="submit">Send</button>
        </form>
        {res_html}
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/ask")
def ask_ai(prompt: str = Query(..., description="Prompt for Gemini"), page: int = Query(0, description="Page number")):
    res_text = get_gemini_response(prompt)
    pages = paginate_text(res_text)
    if page >= len(pages):
        page = len(pages) - 1
    if page < 0:
        page = 0
    return pages[page] if pages else ""

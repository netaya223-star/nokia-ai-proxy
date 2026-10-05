import os
import requests
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

app = FastAPI()

API_KEY = os.environ.get("GEMINI_API_KEY")

def paginate_text(text: str, chunk_size: int = 250):
    """חיתוך טקסט לעמודים עבור מסכים קטנים כמו בנוקיה"""
    if not text:
        return [""]
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

@app.get("/", response_class=HTMLResponse)
def home(prompt: str = "", page: int = 0):
    res_html = ""
    
    if prompt:
        if not API_KEY:
            res_text = "Error: GEMINI_API_KEY missing."
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            try:
                res = requests.post(url, json=payload, timeout=25)
                data = res.json()
                if res.status_code == 200:
                    res_text = data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    res_text = f"Google API Error ({res.status_code}): {data}"
            except Exception as e:
                res_text = f"Error: {str(e)}"
                
        # חלוקה לעמודים
        pages = paginate_text(res_text)
        if page >= len(pages):
            page = len(pages) - 1
        if page < 0:
            page = 0
            
        current_page_text = pages[page]
        
        # יצירת כפתורי ניווט בין עמודים לנוקיה
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
        </style>
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
    if not API_KEY:
        return "Error: GEMINI_API_KEY is missing."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        res = requests.post(url, json=payload, timeout=25)
        data = res.json()
        if res.status_code == 200:
            full_text = data["candidates"][0]["content"]["parts"][0]["text"]
            pages = paginate_text(full_text)
            if page >= len(pages):
                page = len(pages) - 1
            return pages[page]
        return f"Google API Error ({res.status_code}): {data}"
    except Exception as e:
        return f"Exception: {str(e)}"

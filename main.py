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
    res_text = call_gemini(prompt)
    pages = paginate_text(res_text)
    if page >= len(pages):
        page = len(pages) - 1
    if page < 0:
        page = 0
    return pages[page]

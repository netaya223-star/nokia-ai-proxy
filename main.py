import os
from fastapi import FastAPI, Query
import anthropic

app = FastAPI()

CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

@app.get("/ask")
def ask_ai(prompt: str = Query(..., description="Prompt for Claude")):
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

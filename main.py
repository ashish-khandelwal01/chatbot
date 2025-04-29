import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import requests
import json
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]

app = FastAPI()
templates = Jinja2Templates(directory="templates")

chat_history = []

# Streaming AI Response
def groq_stream(history):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": history,
        "temperature": 0.7,
        "stream": True,
    }

    with requests.post(url, headers=headers, json=payload, stream=True) as response:
        for line in response.iter_lines():
            if line and line.startswith(b'data: '):
                data = line[len(b'data: '):]
                if data == b'[DONE]':
                    break
                chunk = json.loads(data)
                delta = chunk['choices'][0]['delta'].get('content')
                if delta:
                    yield delta

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask", response_class=StreamingResponse)
async def post_question(request: Request, user_input: str = Form(...)):
    chat_history.append({"role": "user", "content": user_input})
    stream = groq_stream(chat_history)
    return StreamingResponse(stream, media_type="text/plain")
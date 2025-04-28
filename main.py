from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import requests
import os
from dotenv import load_dotenv
app = FastAPI()
templates = Jinja2Templates(directory="templates")

chat_history = []

load_dotenv()

def ask_groq(history):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": history,
        "temperature": 0.7
    }
    print(headers)
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    if 'choices' in result:
        return result['choices'][0]['message']['content']
    else:
        return f"Error: {result}"


@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ask", response_class=JSONResponse)
async def post_question(request: Request, user_input: str = Form(...)):
    # Add user message to chat history
    chat_history.append({"role": "user", "content": user_input})

    # Get AI response based on the full chat history
    ai_reply = ask_groq(chat_history)

    # Add AI reply to chat history
    chat_history.append({"role": "assistant", "content": ai_reply})

    return {"answer": ai_reply}

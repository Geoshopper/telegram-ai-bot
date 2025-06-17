import os
import requests, json
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
BOT_USERNAME = 'GurgenGEOBot'  # Without @

# Memory file
MEMORY_FILE = 'memory.json'
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, 'w') as f:
        json.dump({"known_questions": []}, f)

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def telegram_webhook():
    data = request.json

    # Check if it's a message and the bot is tagged
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        if f"@{BOT_USERNAME}" in text:
            question = text.replace(f"@{BOT_USERNAME}", "").strip()
            answer = get_openai_answer(question)
            send_message(chat_id, answer)

    return 'ok'

def get_openai_answer(question):
    # Load memory
    with open(MEMORY_FILE, 'r') as f:
        memory = json.load(f)

    # Call OpenAI API
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    body = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for a Telegram group."},
            {"role": "user", "content": question}
        ]
    }

    r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
    result = r.json()
    answer = result["choices"][0]["message"]["content"]

    # Save to memory
    memory["known_questions"].append({"question": question, "answer": answer})
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f)

    return answer

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# Webhook test route
@app.route('/')
def home():
    return 'Bot is running.'


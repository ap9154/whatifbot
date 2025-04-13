from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Auto-register webhook with Telegram on startup
@app.on_event("startup")
async def register_webhook():
    if WEBHOOK_URL:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{TELEGRAM_API_URL}/setWebhook",
                json={"url": WEBHOOK_URL}
            )

# Generates a creative response to "what if" questions
async def generate_response(question: str) -> str:
    prompt = f"You are a creative AI that answers wild 'what if' questions mixing science, philosophy, and fiction. Here's one:\nQ: {question}\nA:"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.9,
                "max_tokens": 300
            },
        )
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

@app.post("/webhook")
async def telegram_webhook(req: Request):
    payload = await req.json()
    
    if "message" in payload:
        chat_id = payload["message"]["chat"]["id"]
        text = payload["message"].get("text", "")

        if text.lower().startswith("what if"):
            reply = await generate_response(text)
        else:
            reply = "Send me a 'What if?' question, and I'll take you on a wild ride 🌌"

        async with httpx.AsyncClient() as client:
            await client.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": reply
            })

    return {"ok": True}

from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("")
OPENAI_API_KEY = os.getenv("")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{}"

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

@app.post(f"/webhook")
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

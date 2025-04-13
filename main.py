import os
import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import openai
import asyncio

# Load environment variables from .env file
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I'm your What If? bot. Ask me any wild what-if question!",
        reply_markup=ForceReply(selective=True),
    )

# Function to generate response from OpenAI
async def generate_response(text: str):
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a bot that gives wild 'what if' answers based on science, fiction, and philosophy."},
                {"role": "user", "content": text},
            ],
            temperature=0.9,
            max_tokens=300,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        data = response

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        else:
            logger.error("Response structure invalid or 'choices' not found.")
            return "Sorry, I couldn't generate a response."
    except Exception as e:
        logger.error(f"An error occurred in generate_response: {e}")
        return "An error occurred while processing your request."

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    await update.message.chat.send_action(action="typing")
    answer = await generate_response(user_input)
    await update.message.reply_text(answer)

# Main function to start the bot
def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started...")
    application.run_polling()

if __name__ == "__main__":
    main()

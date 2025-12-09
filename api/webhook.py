import json
import os
from src.bot_handler import BotHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def handler(request):
    # POST для webhook
    if request.method == "POST":
        body = await request.json()
        bot_handler = BotHandler(BOT_TOKEN, OPENAI_API_KEY)
        response = await bot_handler.process_update(body)
        return {
            "statusCode": 200,
            "body": json.dumps(response)
        }

    # GET для проверки
    return {
        "statusCode": 200,
        "body": "Telegram AI Bot is running!"
    }

from http.server import BaseHTTPRequestHandler
import json
import os
import logging
from src.bot_handler import BotHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')

            update = json.loads(body)
            logger.info(f"Получен update: {update.get('update_id')}")

            bot_handler = BotHandler(
                bot_token=os.getenv('BOT_TOKEN'),
                openai_api_key=os.getenv('OPENAI_API_KEY')
            )

            response = bot_handler.process_update(update)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            logger.error(f"Ошибка обработки: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Telegram AI Bot is running!')

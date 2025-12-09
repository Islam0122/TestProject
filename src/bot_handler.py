import logging
import requests
from .openapi_client import OpenAIClient

logger = logging.getLogger(__name__)


class BotHandler:
    def __init__(self, bot_token: str, openai_api_key: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.openai_client = OpenAIClient(openai_api_key)

    def process_update(self, update: dict) -> dict:
        try:
            if 'message' not in update:
                return {"status": "ignored", "reason": "no_message"}

            message = update['message']
            chat_id = message['chat']['id']

            if 'text' in message:
                return self._handle_text_message(chat_id, message['text'])
            elif 'photo' in message:
                return self._handle_photo_message(chat_id, message)

            else:
                self.send_message(chat_id, "Извини, я понимаю только текст и изображения 🤖")
                return {"status": "unsupported_type"}

        except Exception as e:
            logger.error(f"Ошибка в process_update: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def _handle_text_message(self, chat_id: int, text: str) -> dict:
        logger.info(f"Обработка текста от {chat_id}: {text[:50]}...")
        self._send_typing(chat_id)
        ai_response = self.openai_client.get_text_response(text)
        self.send_message(chat_id, ai_response)

        return {"status": "success", "type": "text"}

    def _handle_photo_message(self, chat_id: int, message: dict) -> dict:
        logger.info(f"Обработка фото от {chat_id}")

        try:
            photo = message['photo'][-1]
            file_id = photo['file_id']
            caption = message.get('caption', 'Что на этом изображении?')
            self._send_typing(chat_id)
            file_url = self._get_file_url(file_id)
            ai_response = self.openai_client.get_vision_response(file_url, caption)
            self.send_message(chat_id, ai_response)

            return {"status": "success", "type": "photo"}

        except Exception as e:
            logger.error(f"Ошибка обработки фото: {str(e)}")
            self.send_message(chat_id, f"Не удалось обработать изображение: {str(e)}")
            return {"status": "error", "type": "photo"}

    def _get_file_url(self, file_id: str) -> str:
        response = requests.get(f"{self.base_url}/getFile", params={"file_id": file_id})
        response.raise_for_status()

        file_path = response.json()['result']['file_path']
        return f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"

    def _send_typing(self, chat_id: int):
        try:
            requests.post(
                f"{self.base_url}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"}
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить typing: {e}")

    def send_message(self, chat_id: int, text: str):
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Сообщение отправлено в чат {chat_id}")

        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {str(e)}")
            raise
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.text_model = "gpt-4o-mini"
        self.vision_model = "gpt-4o-mini"

    def get_text_response(self, user_message: str) -> str:
        try:
            logger.info(f"Запрос к OpenAI (текст): {user_message[:50]}...")

            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты полезный AI-ассистент в Telegram боте. "
                                   "Отвечай кратко, дружелюбно и по существу. "
                                   "Используй эмодзи когда уместно."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )

            answer = response.choices[0].message.content
            logger.info(f"Получен ответ от OpenAI: {len(answer)} символов")

            return answer

        except Exception as e:
            logger.error(f"Ошибка OpenAI API (текст): {str(e)}")
            return f"❌ Произошла ошибка при обработке запроса: {str(e)}"

    def get_vision_response(self, image_url: str, prompt: str = "Что на этом изображении?") -> str:
        try:
            logger.info(f"Запрос к OpenAI Vision: {prompt[:50]}...")

            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты AI-ассистент, который анализирует изображения. "
                                   "Описывай что видишь детально но лаконично. "
                                   "Используй эмодзи для наглядности."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=500
            )

            answer = response.choices[0].message.content
            logger.info(f"Vision ответ получен: {len(answer)} символов")

            return f"🖼 *Анализ изображения:*\n\n{answer}"

        except Exception as e:
            logger.error(f"Ошибка OpenAI Vision API: {str(e)}")
            return f"❌ Не удалось проанализировать изображение: {str(e)}"
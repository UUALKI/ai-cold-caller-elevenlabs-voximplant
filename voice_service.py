import os
import json
import requests
import uuid
from typing import Dict, Optional
from config import YANDEX_API_KEY, TTS_AUDIO_DIR

class VoiceService:
    def __init__(self):
        self.yandex_api_key = YANDEX_API_KEY
        self.audio_dir = TTS_AUDIO_DIR
        
        # Конфигурация голосов
        self.voices = {
            "dmitriy": {
                "name": "Дмитрий",
                "yandex_voice": "dmitriy",
                "style": "спокойный, внимательный",
                "pitch": 0.9,
                "speed": 1.0
            },
            "alena": {
                "name": "Алена", 
                "yandex_voice": "alena",
                "style": "дружелюбный, теплый",
                "pitch": 1.0,
                "speed": 1.0
            }
        }
    
    def synthesize_speech(self, text: str, voice: str = "dmitriy", emotion: str = "neutral") -> str:
        """Синтез речи через Yandex SpeechKit с использованием SSML для эмоций и пауз.

        Возвращает путь к сохраненному .ogg файлу или None при ошибке.
        """
        try:
            voice_info = self.get_voice_info(voice)
            y_voice = voice_info.get("yandex_voice", "dmitriy")

            # Простое сопоставление эмоций для SSML
            emotion_map = {
                "positive": "good",
                "negative": "evil",
                "neutral": "neutral"
            }
            y_emotion = emotion_map.get(emotion, "neutral")

            # Оборачиваем текст в SSML, добавляем небольшие паузы
            ssml = f"""
<speak version='1.0'>
  <voice name='{y_voice}'>
    <express-as type='{y_emotion}'>
      <break time='200ms'/> {text} <break time='150ms'/>
    </express-as>
  </voice>
</speak>
""".strip()

            url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
            headers = {"Authorization": f"Api-Key {self.yandex_api_key}"}
            data = {
                "ssml": ssml,
                "voice": y_voice,
                "format": "oggopus",
                "sampleRateHertz": 48000,
                "lang": "ru-RU"
            }

            response = requests.post(url, headers=headers, data=data)
            if response.status_code != 200:
                print(f"Yandex TTS error: {response.status_code} {response.text}")
                return None

            filename = f"call_{str(uuid.uuid4())}_{voice}_{emotion}.ogg"
            filepath = os.path.join(self.audio_dir, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            return filepath
        except Exception as e:
            print(f"Ошибка синтеза речи: {e}")
            return None
    
    def get_voice_info(self, voice: str) -> Dict:
        """Возвращает информацию о голосе"""
        return self.voices.get(voice, self.voices["dmitriy"])

# Глобальный экземпляр сервиса
voice_service = VoiceService()


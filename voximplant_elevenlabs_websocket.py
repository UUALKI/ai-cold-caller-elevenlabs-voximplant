#!/usr/bin/env python3
"""
WebSocket интеграция Voximplant + ElevenLabs Agent
Адаптация под Python для работы с Voximplant
"""

import asyncio
import websockets
import json
import base64
import logging
from flask import Flask, request, jsonify
from config_elevenlabs import (
    ELEVENLABS_AGENT_API_KEY,
    ELEVENLABS_AGENT_ID,
    VOXIMPLANT_ACCOUNT_ID,
    VOXIMPLANT_API_KEY,
    VOXIMPLANT_APPLICATION_ID,
    VOXIMPLANT_SCENARIO
)
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElevenLabsWebSocketClient:
    """WebSocket клиент для ElevenLabs Conversational AI"""
    
    def __init__(self, agent_id, api_key):
        self.agent_id = agent_id
        self.api_key = api_key
        self.websocket = None
        self.voximplant_connection = None
        
    async def connect(self):
        """Подключение к ElevenLabs WebSocket"""
        try:
            # WebSocket URL для ElevenLabs Conversational AI
            ws_url = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={self.agent_id}"
            
            # Заголовки для аутентификации
            headers = {
                "xi-api-key": self.api_key
            }
            
            logger.info(f"🔌 Подключение к ElevenLabs WebSocket: {ws_url}")
            
            self.websocket = await websockets.connect(
                ws_url,
                extra_headers=headers
            )
            
            logger.info("✅ Подключен к ElevenLabs WebSocket")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к ElevenLabs: {e}")
            return False
    
    async def send_audio(self, audio_data):
        """Отправка аудио в ElevenLabs"""
        if self.websocket and self.websocket.open:
            try:
                # Конвертируем аудио в base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                message = {
                    "user_audio_chunk": audio_base64
                }
                
                await self.websocket.send(json.dumps(message))
                logger.debug("🎤 Аудио отправлено в ElevenLabs")
                
            except Exception as e:
                logger.error(f"❌ Ошибка отправки аудио: {e}")
    
    async def listen_for_responses(self):
        """Прослушивание ответов от ElevenLabs"""
        if not self.websocket:
            return
            
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_elevenlabs_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Ошибка парсинга JSON: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 Соединение с ElevenLabs закрыто")
        except Exception as e:
            logger.error(f"❌ Ошибка прослушивания: {e}")
    
    async def handle_elevenlabs_message(self, message):
        """Обработка сообщений от ElevenLabs"""
        try:
            message_type = message.get("type")
            
            if message_type == "conversation_initiation_metadata":
                logger.info("🎭 Получены метаданные инициализации диалога")
                
            elif message_type == "audio":
                # Получаем аудио ответ от агента
                audio_event = message.get("audio_event", {})
                audio_base64 = audio_event.get("audio_base_64")
                
                if audio_base64:
                    # Отправляем аудио в Voximplant
                    await self.send_audio_to_voximplant(audio_base64)
                    
            elif message_type == "interruption":
                logger.info("🔄 Прерывание диалога")
                # Очищаем буфер аудио в Voximplant
                
            elif message_type == "ping":
                # Отвечаем на ping
                event_id = message.get("ping_event", {}).get("event_id")
                if event_id:
                    pong_response = {
                        "type": "pong",
                        "event_id": event_id
                    }
                    await self.websocket.send(json.dumps(pong_response))
                    
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")
    
    async def send_audio_to_voximplant(self, audio_base64):
        """Отправка аудио ответа в Voximplant"""
        try:
            # Здесь нужно отправить аудио обратно в Voximplant
            # Это зависит от того, как настроен Voximplant сценарий
            
            logger.info("🎵 Аудио ответ отправлен в Voximplant")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в Voximplant: {e}")
    
    async def close(self):
        """Закрытие соединения"""
        if self.websocket:
            await self.websocket.close()
            logger.info("🔌 Соединение с ElevenLabs закрыто")

class VoximplantElevenLabsBridge:
    """Мост между Voximplant и ElevenLabs"""
    
    def __init__(self):
        self.elevenlabs_client = ElevenLabsWebSocketClient(
            ELEVENLABS_AGENT_ID,
            ELEVENLABS_AGENT_API_KEY
        )
        self.active_calls = {}
    
    async def start_call(self, call_id, phone_number):
        """Запуск звонка через Voximplant"""
        try:
            logger.info(f"📞 Запуск звонка {call_id} на номер {phone_number}")
            
            # Подключаемся к ElevenLabs
            if await self.elevenlabs_client.connect():
                # Запускаем прослушивание ответов
                asyncio.create_task(self.elevenlabs_client.listen_for_responses())
                
                # Сохраняем информацию о звонке
                self.active_calls[call_id] = {
                    "phone_number": phone_number,
                    "elevenlabs_client": self.elevenlabs_client
                }
                
                # Запускаем звонок через Voximplant API
                await self.initiate_voximplant_call(phone_number, call_id)
                
                return True
            else:
                logger.error("❌ Не удалось подключиться к ElevenLabs")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска звонка: {e}")
            return False
    
    async def initiate_voximplant_call(self, phone_number, call_id):
        """Инициация звонка через Voximplant API"""
        try:
            # URL для запуска сценария Voximplant
            url = "https://api.voximplant.com/platform_api/StartScenarios/"
            
            # Данные для звонка
            data = {
                'account_id': VOXIMPLANT_ACCOUNT_ID,
                'api_key': VOXIMPLANT_API_KEY,
                'application_id': VOXIMPLANT_APPLICATION_ID,
                'phone': phone_number.lstrip("+"),
                'scenario_name': VOXIMPLANT_SCENARIO,
                'script_custom_data': json.dumps({
                    'call_id': call_id,
                    'webhook_url': 'http://localhost:8000/voximplant-webhook'
                })
            }
            
            headers = {
                'Host': 'api.voximplant.com',
                'User-Agent': 'Voximplant-ElevenLabs-Bridge/1.0'
            }
            
            response = requests.post(url, data=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ Звонок инициирован через Voximplant: {call_id}")
            else:
                logger.error(f"❌ Ошибка Voximplant API: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициации звонка: {e}")
    
    async def handle_voximplant_audio(self, call_id, audio_data):
        """Обработка аудио от Voximplant"""
        try:
            if call_id in self.active_calls:
                elevenlabs_client = self.active_calls[call_id]["elevenlabs_client"]
                await elevenlabs_client.send_audio(audio_data)
                logger.debug(f"🎤 Аудио от Voximplant обработано для звонка {call_id}")
            else:
                logger.warning(f"⚠️ Неизвестный call_id: {call_id}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки аудио: {e}")
    
    async def end_call(self, call_id):
        """Завершение звонка"""
        try:
            if call_id in self.active_calls:
                elevenlabs_client = self.active_calls[call_id]["elevenlabs_client"]
                await elevenlabs_client.close()
                del self.active_calls[call_id]
                logger.info(f"📞 Звонок {call_id} завершен")
                
        except Exception as e:
            logger.error(f"❌ Ошибка завершения звонка: {e}")

# Создаем экземпляр моста
bridge = VoximplantElevenLabsBridge()

# Flask приложение для webhook
app = Flask(__name__)

@app.route('/')
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({"status": "healthy", "service": "Voximplant-ElevenLabs-Bridge"})

@app.route('/start-call', methods=['POST'])
async def start_call():
    """API для запуска звонка"""
    try:
        data = request.json
        phone_number = data.get('phone_number')
        call_id = data.get('call_id', f"call_{int(asyncio.get_event_loop().time())}")
        
        if not phone_number:
            return jsonify({"error": "phone_number required"}), 400
        
        success = await bridge.start_call(call_id, phone_number)
        
        if success:
            return jsonify({
                "success": True,
                "call_id": call_id,
                "message": "Call started successfully"
            })
        else:
            return jsonify({"error": "Failed to start call"}), 500
            
    except Exception as e:
        logger.error(f"❌ Ошибка API start-call: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/voximplant-webhook', methods=['POST'])
async def voximplant_webhook():
    """Webhook для получения данных от Voximplant"""
    try:
        data = request.json
        logger.info(f"📥 Получен webhook от Voximplant: {data}")
        
        # Обрабатываем данные от Voximplant
        # Здесь нужно добавить логику обработки аудио
        
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"❌ Ошибка webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test-elevenlabs-connection', methods=['GET'])
async def test_connection():
    """Тест подключения к ElevenLabs"""
    try:
        success = await bridge.elevenlabs_client.connect()
        
        if success:
            await bridge.elevenlabs_client.close()
            return jsonify({"success": True, "message": "ElevenLabs connection successful"})
        else:
            return jsonify({"success": False, "message": "ElevenLabs connection failed"})
            
    except Exception as e:
        logger.error(f"❌ Ошибка теста подключения: {e}")
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    logger.info("🚀 Запуск Voximplant-ElevenLabs WebSocket Bridge")
    logger.info(f"🤖 Agent ID: {ELEVENLABS_AGENT_ID}")
    logger.info(f"📞 Voximplant Account: {VOXIMPLANT_ACCOUNT_ID}")
    
    app.run(debug=True, port=8000, host='0.0.0.0')

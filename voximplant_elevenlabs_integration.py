#!/usr/bin/env python3
"""
Полная интеграция Voximplant + ElevenLabs WebSocket
"""

import asyncio
import websockets
import json
import base64
import logging
import time
from flask import Flask, request, jsonify, render_template
from config_elevenlabs import (
    ELEVENLABS_AGENT_API_KEY,
    VOXIMPLANT_ACCOUNT_ID,
    VOXIMPLANT_API_KEY,
    VOXIMPLANT_APPLICATION_ID,
    VOXIMPLANT_SCENARIO
)

# Новый Agent ID
ELEVENLABS_AGENT_ID = "agent_8701k4554cs1e69arzeae6vva5qz"
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
        self.conversation_id = None
        self.audio_format = "ulaw_8000"
        
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
                additional_headers=headers
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
    
    async def listen_for_responses(self, callback):
        """Прослушивание ответов от ElevenLabs"""
        if not self.websocket:
            return
            
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_elevenlabs_message(data, callback)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Ошибка парсинга JSON: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 Соединение с ElevenLabs закрыто")
        except Exception as e:
            logger.error(f"❌ Ошибка прослушивания: {e}")
    
    async def handle_elevenlabs_message(self, message, callback):
        """Обработка сообщений от ElevenLabs"""
        try:
            message_type = message.get("type")
            
            if message_type == "conversation_initiation_metadata":
                metadata = message.get("conversation_initiation_metadata_event", {})
                self.conversation_id = metadata.get("conversation_id")
                self.audio_format = metadata.get("agent_output_audio_format", "ulaw_8000")
                logger.info(f"🎭 Диалог инициализирован: {self.conversation_id}")
                
            elif message_type == "audio":
                # Получаем аудио ответ от агента
                audio_event = message.get("audio_event", {})
                audio_base64 = audio_event.get("audio_base_64")
                
                if audio_base64:
                    # Вызываем callback для отправки аудио в Voximplant
                    await callback(audio_base64, self.audio_format)
                    
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
    
    async def close(self):
        """Закрытие соединения"""
        if self.websocket:
            await self.websocket.close()
            logger.info("🔌 Соединение с ElevenLabs закрыто")

class VoximplantElevenLabsBridge:
    """Мост между Voximplant и ElevenLabs"""
    
    def __init__(self):
        self.active_calls = {}
    
    async def start_call(self, call_id, phone_number):
        """Запуск звонка через Voximplant"""
        try:
            logger.info(f"📞 Запуск звонка {call_id} на номер {phone_number}")
            
            # Создаем WebSocket клиент для ElevenLabs
            elevenlabs_client = ElevenLabsWebSocketClient(
                ELEVENLABS_AGENT_ID,
                ELEVENLABS_AGENT_API_KEY
            )
            
            # Подключаемся к ElevenLabs
            if await elevenlabs_client.connect():
                # Создаем callback для отправки аудио в Voximplant
                async def send_audio_to_voximplant(audio_base64, audio_format):
                    await self.send_audio_to_voximplant(call_id, audio_base64, audio_format)
                
                # Запускаем прослушивание ответов
                asyncio.create_task(elevenlabs_client.listen_for_responses(send_audio_to_voximplant))
                
                # Сохраняем информацию о звонке
                self.active_calls[call_id] = {
                    "phone_number": phone_number,
                    "elevenlabs_client": elevenlabs_client,
                    "webhook_url": f"http://localhost:8000/voximplant-webhook/{call_id}"
                }
                
                # Запускаем звонок через Voximplant API
                call_success = await self.initiate_voximplant_call(phone_number, call_id)
                
                if call_success:
                    return True
                else:
                    # Если звонок не удался, очищаем ресурсы
                    await elevenlabs_client.close()
                    if call_id in self.active_calls:
                        del self.active_calls[call_id]
                    return False
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
            
            # Параметры для звонка (используем params для POST)
            params = {
                'account_id': VOXIMPLANT_ACCOUNT_ID,
                'api_key': VOXIMPLANT_API_KEY,
                'application_id': VOXIMPLANT_APPLICATION_ID,
                'phone': phone_number.lstrip("+"),
                'scenario_name': VOXIMPLANT_SCENARIO,
                'script_custom_data': json.dumps({
                    'call_id': call_id,
                    'phone_number': phone_number,
                    'webhook_url': f'http://localhost:8000/voximplant-webhook/{call_id}',
                    'elevenlabs_agent_id': ELEVENLABS_AGENT_ID,
                    'elevenlabs_api_key': ELEVENLABS_AGENT_API_KEY
                })
            }
            
            # Добавляем rule_name если доступен (не используем rule_id)
            try:
                from config import VOXIMPLANT_RULE_NAME
                if VOXIMPLANT_RULE_NAME and VOXIMPLANT_RULE_NAME.strip():
                    params['rule_name'] = VOXIMPLANT_RULE_NAME
                    logger.info(f"📋 Используем rule_name: {VOXIMPLANT_RULE_NAME}")
                else:
                    logger.info("📋 rule_name не указан, используем только scenario_name")
            except ImportError:
                logger.info("📋 VOXIMPLANT_RULE_NAME не найден в config")
            
            headers = {
                'Host': 'api.voximplant.com',
                'User-Agent': 'Voximplant-ElevenLabs-Bridge/1.0'
            }
            
            logger.info(f"📤 Отправка запроса в Voximplant API:")
            logger.info(f"   URL: {url}")
            logger.info(f"   Параметры: {params}")
            
            response = requests.post(url, data=params, headers=headers, timeout=30)
            
            logger.info(f"📥 Ответ Voximplant API:")
            logger.info(f"   Статус: {response.status_code}")
            logger.info(f"   Заголовки: {dict(response.headers)}")
            logger.info(f"   Тело ответа: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('result'):
                        logger.info(f"✅ Звонок инициирован через Voximplant: {result['result']}")
                        return True
                    else:
                        logger.error(f"❌ Ошибка Voximplant API: {result}")
                        return False
                except json.JSONDecodeError:
                    logger.error(f"❌ Неверный JSON ответ: {response.text}")
                    return False
            else:
                logger.error(f"❌ Ошибка Voximplant API: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициации звонка: {e}")
            return False
    
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
    
    async def send_audio_to_voximplant(self, call_id, audio_base64, audio_format):
        """Отправка аудио ответа в Voximplant"""
        try:
            if call_id in self.active_calls:
                # Здесь нужно отправить аудио обратно в Voximplant
                # Это можно сделать через webhook или WebSocket
                
                # Конвертируем base64 обратно в аудио
                audio_data = base64.b64decode(audio_base64)
                
                # Отправляем в Voximplant через webhook
                webhook_url = self.active_calls[call_id]["webhook_url"]
                
                response_data = {
                    "call_id": call_id,
                    "audio_data": audio_base64,
                    "audio_format": audio_format,
                    "source": "elevenlabs"
                }
                
                # Отправляем POST запрос в Voximplant
                response = requests.post(webhook_url, json=response_data, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"🎵 Аудио ответ отправлен в Voximplant для звонка {call_id}")
                else:
                    logger.error(f"❌ Ошибка отправки в Voximplant: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в Voximplant: {e}")
    
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
    return jsonify({
        "status": "healthy", 
        "service": "Voximplant-ElevenLabs-Bridge",
        "active_calls": len(bridge.active_calls)
    })

@app.route('/form')
def call_form():
    """Форма для запуска звонка"""
    return render_template('call_form.html')

@app.route('/start-call', methods=['POST'])
def start_call():
    """API для запуска звонка"""
    try:
        data = request.json
        phone_number = data.get('phone_number')
        call_id = data.get('call_id', f"call_{int(time.time())}")
        
        if not phone_number:
            return jsonify({"error": "phone_number required"}), 400
        
        # Запускаем асинхронную функцию в новом event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success = loop.run_until_complete(bridge.start_call(call_id, phone_number))
        finally:
            loop.close()
        
        if success:
            return jsonify({
                "success": True,
                "call_id": call_id,
                "message": "Call started successfully",
                "webhook_url": f"http://localhost:8000/voximplant-webhook/{call_id}"
            })
        else:
            return jsonify({"error": "Failed to start call"}), 500
            
    except Exception as e:
        logger.error(f"❌ Ошибка API start-call: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/voximplant-webhook/<call_id>', methods=['POST'])
def voximplant_webhook(call_id):
    """Webhook для получения данных от Voximplant"""
    try:
        data = request.json
        logger.info(f"📥 Получен webhook от Voximplant для звонка {call_id}: {data}")
        
        # Запускаем асинхронную обработку
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Обрабатываем аудио от Voximplant
            if 'audio_data' in data:
                audio_base64 = data['audio_data']
                audio_data = base64.b64decode(audio_base64)
                loop.run_until_complete(bridge.handle_voximplant_audio(call_id, audio_data))
            
            # Обрабатываем завершение звонка
            if data.get('event') == 'call_ended':
                loop.run_until_complete(bridge.end_call(call_id))
        finally:
            loop.close()
        
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"❌ Ошибка webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test-elevenlabs-connection', methods=['GET'])
def test_connection():
    """Тест подключения к ElevenLabs"""
    try:
        elevenlabs_client = ElevenLabsWebSocketClient(
            ELEVENLABS_AGENT_ID,
            ELEVENLABS_AGENT_API_KEY
        )
        
        # Запускаем асинхронную функцию
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success = loop.run_until_complete(elevenlabs_client.connect())
            
            if success:
                loop.run_until_complete(elevenlabs_client.close())
                return jsonify({
                    "success": True, 
                    "message": "ElevenLabs connection successful",
                    "agent_id": ELEVENLABS_AGENT_ID
                })
            else:
                return jsonify({
                    "success": False, 
                    "message": "ElevenLabs connection failed"
                })
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"❌ Ошибка теста подключения: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/active-calls', methods=['GET'])
def get_active_calls():
    """Получение списка активных звонков"""
    calls = []
    for call_id, call_data in bridge.active_calls.items():
        calls.append({
            "call_id": call_id,
            "phone_number": call_data["phone_number"],
            "webhook_url": call_data["webhook_url"]
        })
    
    return jsonify({
        "active_calls": calls,
        "count": len(calls)
    })

if __name__ == '__main__':
    logger.info("🚀 Запуск Voximplant-ElevenLabs WebSocket Bridge")
    logger.info(f"🤖 Agent ID: {ELEVENLABS_AGENT_ID}")
    logger.info(f"📞 Voximplant Account: {VOXIMPLANT_ACCOUNT_ID}")
    logger.info(f"🎭 Сценарий: {VOXIMPLANT_SCENARIO}")
    
    app.run(debug=False, port=8000, host='0.0.0.0')

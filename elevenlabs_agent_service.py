import requests
import json
import logging
from typing import Dict, Optional, List
from config_elevenlabs import (
    ELEVENLABS_AGENT_API_KEY,
    ELEVENLABS_BASE_URL,
    ELEVENLABS_VOICE_ID
)

# Новый Agent ID
ELEVENLABS_AGENT_ID = "agent_8701k4554cs1e69arzeae6vva5qz"
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElevenLabsAgentService:
    """Сервис для работы с ElevenLabs AI Agent"""
    
    def __init__(self):
        self.api_key = ELEVENLABS_AGENT_API_KEY
        self.agent_id = ELEVENLABS_AGENT_ID
        self.base_url = ELEVENLABS_BASE_URL
        self.voice_id = ELEVENLABS_VOICE_ID
        
        logger.info(f"🤖 ElevenLabs Agent Service инициализирован")
        logger.info(f"   Agent ID: {self.agent_id}")
        logger.info(f"   API Key: {self.api_key[:20]}...")
        logger.info(f"   Voice ID: {self.voice_id}")
    
    def test_agent_connection(self) -> Dict:
        """Тестирует подключение к ElevenLabs Agent"""
        try:
            url = f"{self.base_url}/agent/{self.agent_id}"
            
            headers = {
                'Content-Type': 'application/json',
                'xi-api-key': self.api_key
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                agent_info = response.json()
                logger.info(f"✅ Подключение к ElevenLabs Agent успешно")
                logger.info(f"   Имя агента: {agent_info.get('name', 'Unknown')}")
                logger.info(f"   Статус: {agent_info.get('status', 'Unknown')}")
                
                return {
                    "success": True,
                    "agent_info": agent_info
                }
            else:
                logger.error(f"❌ Ошибка подключения к Agent: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования подключения: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_message_to_agent(self, message: str, session_id: str = None, message_type: str = "user_input") -> Dict:
        """Отправляет сообщение в ElevenLabs Agent"""
        try:
            if not session_id:
                session_id = f"test_session_{int(time.time())}"
            
            url = f"{self.base_url}/agent/{self.agent_id}/conversation"
            
            headers = {
                'Content-Type': 'application/json',
                'xi-api-key': self.api_key
            }
            
            data = {
                "session_id": session_id,
                "message_type": message_type,
                "message": message,
                "voice_id": self.voice_id
            }
            
            logger.info(f"🌐 Отправляем сообщение в Agent: '{message[:50]}...'")
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                agent_response = result.get('response') or result.get('message', 'Нет ответа')
                
                logger.info(f"✅ Ответ от Agent получен: '{agent_response[:50]}...'")
                
                return {
                    "success": True,
                    "response": agent_response,
                    "session_id": session_id,
                    "full_response": result
                }
            else:
                logger.error(f"❌ Ошибка API Agent: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_agent_conversation_history(self, session_id: str) -> Dict:
        """Получает историю диалога с агентом"""
        try:
            url = f"{self.base_url}/agent/{self.agent_id}/conversation/{session_id}"
            
            headers = {
                'Content-Type': 'application/json',
                'xi-api-key': self.api_key
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                history = response.json()
                logger.info(f"✅ История диалога получена для сессии {session_id}")
                
                return {
                    "success": True,
                    "history": history
                }
            else:
                logger.error(f"❌ Ошибка получения истории: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения истории: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_conversation_flow(self) -> Dict:
        """Тестирует полный поток диалога с агентом"""
        try:
            logger.info("🧪 Начинаем тестирование диалога с Agent")
            
            # Тест 1: Приветствие
            greeting_result = self.send_message_to_agent("", "greeting")
            if not greeting_result["success"]:
                return greeting_result
            
            session_id = greeting_result["session_id"]
            greeting = greeting_result["response"]
            
            logger.info(f"🤖 Приветствие: {greeting}")
            
            # Тест 2: Простой вопрос
            question_result = self.send_message_to_agent(
                "Привет! Расскажите о ваших услугах", 
                session_id, 
                "user_input"
            )
            
            if not question_result["success"]:
                return question_result
            
            answer = question_result["response"]
            logger.info(f"🤖 Ответ на вопрос: {answer}")
            
            # Тест 3: Получение истории
            history_result = self.get_agent_conversation_history(session_id)
            
            logger.info("✅ Тестирование диалога завершено успешно")
            
            return {
                "success": True,
                "session_id": session_id,
                "greeting": greeting,
                "answer": answer,
                "history": history_result.get("history", [])
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования диалога: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Глобальный экземпляр сервиса
elevenlabs_agent_service = ElevenLabsAgentService()

# Тестовые функции
def test_elevenlabs_agent():
    """Тестирует ElevenLabs Agent"""
    print("🧪 Тестирование ElevenLabs AI Agent")
    print("=" * 50)
    
    # Тест 1: Подключение
    print("1. Тестируем подключение к Agent...")
    connection_result = elevenlabs_agent_service.test_agent_connection()
    
    if connection_result["success"]:
        print("✅ Подключение успешно")
    else:
        print(f"❌ Ошибка подключения: {connection_result['error']}")
        return
    
    # Тест 2: Диалог
    print("\n2. Тестируем диалог...")
    dialog_result = elevenlabs_agent_service.test_conversation_flow()
    
    if dialog_result["success"]:
        print("✅ Диалог успешен")
        print(f"   Session ID: {dialog_result['session_id']}")
        print(f"   Приветствие: {dialog_result['greeting'][:100]}...")
        print(f"   Ответ: {dialog_result['answer'][:100]}...")
    else:
        print(f"❌ Ошибка диалога: {dialog_result['error']}")
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    test_elevenlabs_agent()

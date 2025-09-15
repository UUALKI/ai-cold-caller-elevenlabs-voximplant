import requests
import json
import logging
from typing import Dict, Optional
from config_elevenlabs import (
    VOXIMPLANT_ACCOUNT_ID,
    VOXIMPLANT_API_KEY,
    VOXIMPLANT_APPLICATION_ID,
    VOXIMPLANT_RULE_ID,
    VOXIMPLANT_SCENARIO,
    ELEVENLABS_AGENT_API_KEY,
    ELEVENLABS_VOICE_ID
)

# Новый Agent ID
ELEVENLABS_AGENT_ID = "agent_8701k4554cs1e69arzeae6vva5qz"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElevenLabsVoximplantService:
    """Сервис для интеграции ElevenLabs Agent с Voximplant"""
    
    def __init__(self):
        self.account_id = VOXIMPLANT_ACCOUNT_ID
        self.api_key = VOXIMPLANT_API_KEY
        self.application_id = VOXIMPLANT_APPLICATION_ID
        self.rule_id = VOXIMPLANT_RULE_ID
        self.scenario = VOXIMPLANT_SCENARIO
        
        # ElevenLabs Agent настройки
        self.agent_id = ELEVENLABS_AGENT_ID
        self.agent_api_key = ELEVENLABS_AGENT_API_KEY
        self.voice_id = ELEVENLABS_VOICE_ID
        
        logger.info(f"🤖 ElevenLabs Voximplant Service инициализирован")
        logger.info(f"   Voximplant Account: {self.account_id}")
        logger.info(f"   Application ID: {self.application_id}")
        logger.info(f"   Agent ID: {self.agent_id}")
    
    def start_elevenlabs_agent_call(self, phone_number: str, custom_config: Dict = None) -> Dict:
        """Запускает звонок с ElevenLabs AI Agent через Voximplant"""
        
        try:
            # Убираем плюс из номера для Voximplant
            phone = phone_number.lstrip("+")
            
            # URL Voximplant API
            url = 'https://api.voximplant.com/platform_api/StartScenarios/'
            
            # Подготавливаем данные для ElevenLabs Agent
            agent_config = {
                "agent_id": custom_config.get("agent_id", self.agent_id),
                "api_key": custom_config.get("api_key", self.agent_api_key),
                "voice_id": custom_config.get("voice_id", self.voice_id),
                "webhook_url": custom_config.get("webhook_url", "http://localhost:8000/api/call-results")
            }
            
            # Данные для Voximplant
            params = {
                'account_id': self.account_id,
                'api_key': self.api_key,
                'application_id': self.application_id,
                'phone': phone,
                'scenario_name': 'elevenlabs_agent_scenario',  # Новый сценарий
                'custom_data': json.dumps({
                    "phone": phone_number,
                    "agent_id": agent_config["agent_id"],
                    "api_key": agent_config["api_key"],
                    "voice_id": agent_config["voice_id"],
                    "webhook_url": agent_config["webhook_url"]
                })
            }
            
            logger.info(f"📞 Запускаем звонок ElevenLabs Agent на: {phone_number}")
            logger.info(f"   Agent ID: {agent_config['agent_id']}")
            logger.info(f"   Voice ID: {agent_config['voice_id']}")
            
            response = requests.post(url, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('result') == 0:
                    call_id = result.get('call_id', 'unknown')
                    logger.info(f"✅ Звонок ElevenLabs Agent запущен успешно! Call ID: {call_id}")
                    
                    return {
                        "success": True,
                        "call_id": call_id,
                        "phone_number": phone_number,
                        "agent_id": agent_config["agent_id"],
                        "message": "Звонок с ElevenLabs AI Agent запущен"
                    }
                else:
                    error_msg = result.get('error_msg', 'Unknown Voximplant error')
                    logger.error(f"❌ Voximplant error: {error_msg}")
                    
                    return {
                        "success": False,
                        "error": f"Voximplant error: {error_msg}"
                    }
            else:
                logger.error(f"❌ HTTP error: {response.status_code} - {response.text}")
                
                return {
                    "success": False,
                    "error": f"HTTP error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска звонка: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_voximplant_connection(self) -> Dict:
        """Тестирует подключение к Voximplant"""
        try:
            url = 'https://api.voximplant.com/platform_api/GetApplications/'
            
            params = {
                'account_id': self.account_id,
                'api_key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('result') == 0:
                    applications = result.get('applications', [])
                    logger.info(f"✅ Подключение к Voximplant успешно")
                    logger.info(f"   Найдено приложений: {len(applications)}")
                    
                    return {
                        "success": True,
                        "applications": applications
                    }
                else:
                    error_msg = result.get('error_msg', 'Unknown error')
                    logger.error(f"❌ Voximplant API error: {error_msg}")
                    
                    return {
                        "success": False,
                        "error": f"Voximplant API error: {error_msg}"
                    }
            else:
                logger.error(f"❌ HTTP error: {response.status_code}")
                
                return {
                    "success": False,
                    "error": f"HTTP error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования Voximplant: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_call_history(self, limit: int = 10) -> Dict:
        """Получает историю звонков"""
        try:
            url = 'https://api.voximplant.com/platform_api/GetCallHistory/'
            
            params = {
                'account_id': self.account_id,
                'api_key': self.api_key,
                'count': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('result') == 0:
                    calls = result.get('calls', [])
                    logger.info(f"✅ История звонков получена: {len(calls)} звонков")
                    
                    return {
                        "success": True,
                        "calls": calls
                    }
                else:
                    error_msg = result.get('error_msg', 'Unknown error')
                    logger.error(f"❌ Ошибка получения истории: {error_msg}")
                    
                    return {
                        "success": False,
                        "error": f"API error: {error_msg}"
                    }
            else:
                logger.error(f"❌ HTTP error: {response.status_code}")
                
                return {
                    "success": False,
                    "error": f"HTTP error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения истории: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Глобальный экземпляр сервиса
elevenlabs_voximplant_service = ElevenLabsVoximplantService()

# Тестовые функции
def test_elevenlabs_voximplant_integration():
    """Тестирует интеграцию ElevenLabs Agent с Voximplant"""
    print("🧪 Тестирование ElevenLabs Agent + Voximplant интеграции")
    print("=" * 60)
    
    # Тест 1: Подключение к Voximplant
    print("1. Тестируем подключение к Voximplant...")
    voximplant_result = elevenlabs_voximplant_service.test_voximplant_connection()
    
    if voximplant_result["success"]:
        print("✅ Подключение к Voximplant успешно")
        apps = voximplant_result.get("applications", [])
        print(f"   Найдено приложений: {len(apps)}")
    else:
        print(f"❌ Ошибка Voximplant: {voximplant_result['error']}")
        return
    
    # Тест 2: История звонков
    print("\n2. Получаем историю звонков...")
    history_result = elevenlabs_voximplant_service.get_call_history(5)
    
    if history_result["success"]:
        calls = history_result.get("calls", [])
        print(f"✅ История получена: {len(calls)} звонков")
        
        for i, call in enumerate(calls[:3]):
            print(f"   {i+1}. {call.get('phone_number', 'Unknown')} - {call.get('status', 'Unknown')}")
    else:
        print(f"❌ Ошибка истории: {history_result['error']}")
    
    # Тест 3: Запуск тестового звонка (опционально)
    print("\n3. Готов к запуску звонка с ElevenLabs Agent")
    print("   Для запуска используйте: start_elevenlabs_agent_call()")
    
    print("\n🎉 Тестирование интеграции завершено!")

def start_test_call():
    """Запускает тестовый звонок с ElevenLabs Agent"""
    print("📞 Запуск тестового звонка с ElevenLabs Agent")
    print("=" * 50)
    
    # Тестовый номер (замените на реальный)
    test_phone = "+79991234567"  # Замените на ваш номер для тестирования
    
    print(f"Тестовый номер: {test_phone}")
    
    # Конфигурация агента
    agent_config = {
        "agent_id": ELEVENLABS_AGENT_ID,
        "api_key": ELEVENLABS_AGENT_API_KEY,
        "voice_id": ELEVENLABS_VOICE_ID,
        "webhook_url": "http://localhost:8000/api/call-results"
    }
    
    # Запускаем звонок
    result = elevenlabs_voximplant_service.start_elevenlabs_agent_call(test_phone, agent_config)
    
    if result["success"]:
        print(f"✅ Звонок запущен успешно!")
        print(f"   Call ID: {result['call_id']}")
        print(f"   Phone: {result['phone_number']}")
        print(f"   Agent ID: {result['agent_id']}")
    else:
        print(f"❌ Ошибка запуска звонка: {result['error']}")

if __name__ == "__main__":
    test_elevenlabs_voximplant_integration()
    
    # Раскомментируйте для запуска тестового звонка
    # start_test_call()

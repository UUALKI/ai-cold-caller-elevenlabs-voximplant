import requests
import json
import urllib3
from typing import Dict, Optional

# Отключаем предупреждения о небезопасных SSL-соединениях
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from config import (
    VOXIMPLANT_ACCOUNT_ID, 
    VOXIMPLANT_API_KEY, 
    VOXIMPLANT_APPLICATION_ID, 
    VOXIMPLANT_RULE_ID,
    VOXIMPLANT_SCENARIO,
    VOXIMPLANT_RULE_NAME,
    ELEVENLABS_VOICE_ID,
    ELEVENLABS_CANDIDATE_VOICE_IDS,
    ELEVENLABS_API_KEY,
    OPENAI_API_KEY
)
from config import VOXIMPLANT_WEBHOOK_URL

class VoximplantService:
    def __init__(self):
        self.account_id = VOXIMPLANT_ACCOUNT_ID
        self.api_key = VOXIMPLANT_API_KEY
        self.application_id = VOXIMPLANT_APPLICATION_ID
        self.rule_id = VOXIMPLANT_RULE_ID
        self.scenario = VOXIMPLANT_SCENARIO
        self.rule_name = VOXIMPLANT_RULE_NAME
        
        # Выводим конфигурацию для отладки
        print(f"Voximplant config:")
        print(f"  Account ID: {self.account_id}")
        print(f"  API Key: {self.api_key[:10]}...")
        print(f"  Application ID: {self.application_id}")
        print(f"  Rule ID: {self.rule_id}")
        if self.rule_name:
            print(f"  Rule Name: {self.rule_name}")
        print(f"  Scenario: {self.scenario}")
    
    def start_call(self, phone_number: str) -> Dict:
        """Инициирует звонок через Voximplant (без передачи audio_url)"""
        
        # Убираем плюс из номера для Voximplant
        phone = phone_number.lstrip("+")
        
        # Используем правильный URL Voximplant API
        url = 'https://api.voximplant.com/platform_api/StartScenarios/'
        
        params = {
            'account_id': self.account_id,
            'api_key': self.api_key,
            'application_id': self.application_id,
            'phone': phone,
            'scenario_name': self.scenario,
        }
        
        candidate_list = []
        try:
            if ELEVENLABS_CANDIDATE_VOICE_IDS:
                candidate_list = [v.strip() for v in ELEVENLABS_CANDIDATE_VOICE_IDS.split(',') if len(v.strip()) >= 10]
        except Exception:
            candidate_list = []

        # Принудительно ставим приоритетный голос первым независимо от окружения
        preferred_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Molly
        if preferred_voice_id:
            # Убираем возможные дубликаты и ставим preferred первым
            candidate_list = [preferred_voice_id] + [v for v in candidate_list if v != preferred_voice_id]

        params['script_custom_data'] = json.dumps({
            'phone': phone,
            'tts_provider': 'elevenlabs',  # или 'openai' для OpenAI голосов
            'tts_language': 'ru-RU',
            'tts_voice': 'female_young_charming_ru',
            'voice_id': ELEVENLABS_VOICE_ID,
            'auto_pick_ru_female': True,
            'candidate_voice_ids': candidate_list,
            'ELEVEN_API_KEY': ELEVENLABS_API_KEY,
            'OPENAI_API_KEY': OPENAI_API_KEY,  # Добавляем OpenAI API ключ
            # Для Realtime API webhook не нужен, но оставляем для совместимости
            'webhook_url': VOXIMPLANT_WEBHOOK_URL,
            # Приветствие для AI - Алёна из ТранстИрекс
            'greeting': 'Добрый день! Меня зовут Алёна, я специалист по международным перевозкам компании ТранстИрекс. Подскажите, с кем я могу обсудить вопросы логистики из Китая в Россию?'
        })
        # Добавляем либо rule_name, либо корректный rule_id, если они заданы
        if self.rule_name:
            params['rule_name'] = self.rule_name
        else:
            try:
                if str(self.rule_id).isdigit() and int(self.rule_id) > 0:
                    params['rule_id'] = int(self.rule_id)
            except Exception:
                pass
        
        try:
            print(f"Отправляем запрос к Voximplant:")
            print(f"  URL: {url}")
            print(f"  Phone: {phone}")
            print(f"  Account ID: {self.account_id}")
            
            # Добавляем таймаут и обработку DNS
            headers = {
                'Host': 'api.voximplant.com',
                'User-Agent': 'AI-Call-Prototype/1.0'
            }
            response = requests.post(url, data=params, headers=headers, timeout=30, verify=False)
            
            print(f"Ответ от Voximplant:")
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result'):
                    print(f"✅ Звонок инициирован успешно! Call ID: {result['result']}")
                    return {
                        "success": True,
                        "call_id": result['result'],
                        "message": "Звонок инициирован успешно"
                    }
                else:
                    print(f"❌ Ошибка Voximplant: {result}")
                    return {
                        "success": False,
                        "error": f"Voximplant error: {result}"
                    }
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP error: {response.status_code} {response.text}"
                }
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Ошибка соединения с Voximplant: {str(e)}")
            if "NameResolutionError" in str(e) or "getaddrinfo failed" in str(e):
                return {
                    "success": False,
                    "error": "Ошибка DNS: не удается разрешить api.voximplant.com. Проверьте интернет-соединение и настройки DNS."
                }
            else:
                return {
                    "success": False,
                    "error": f"Ошибка соединения: {str(e)}"
                }
        except requests.exceptions.Timeout as e:
            print(f"❌ Таймаут при запросе к Voximplant: {str(e)}")
            return {
                "success": False,
                "error": "Таймаут соединения с Voximplant API"
            }
        except Exception as e:
            print(f"❌ Исключение при запросе к Voximplant: {str(e)}")
            return {
                "success": False,
                "error": f"Exception: {str(e)}"
            }
    
    def get_call_status(self, call_id: str) -> Dict:
        """Получает статус звонка"""
        # В реальной системе здесь был бы запрос к Voximplant API
        # Для прототипа возвращаем базовый статус
        return {
            "call_id": call_id,
            "status": "completed",  # или "in_progress", "failed"
            "duration": 120,  # в секундах
            "result": "answered"  # или "no_answer", "busy", "failed"
        }

# Глобальный экземпляр сервиса
voximplant_service = VoximplantService()

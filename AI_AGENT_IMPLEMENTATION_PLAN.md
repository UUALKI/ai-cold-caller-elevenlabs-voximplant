# План реализации продвинутого AI-агента для холодных звонков ТРАНСТИРЕКС

## Обзор проекта

Создание интеллектуального AI-агента для автоматических холодных звонков с естественным голосовым общением, способного:
- Вести естественные диалоги на русском языке
- Обрабатывать возражения и нестандартные ситуации
- Получать контакты ЛПР или запросы на расчет
- Интегрироваться с современными TTS/STT системами
- Анализировать результаты и обучаться на основе данных

## Архитектура системы

### 1. Компоненты системы

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Voximplant    │    │   FastAPI       │    │   OpenAI GPT    │
│   (Телефония)   │◄──►│   (Backend)     │◄──►│   (AI Logic)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ElevenLabs    │    │   SaluteSpeech  │    │   Analytics     │
│   (TTS)         │    │   (STT)         │    │   (Reports)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. Технологический стек

- **Телефония**: Voximplant (исходящие звонки)
- **TTS**: ElevenLabs (естественный голос)
- **STT**: SaluteSpeech API (распознавание речи)
- **AI**: OpenAI GPT-4/Claude (логика диалога)
- **Backend**: FastAPI (обработка webhook'ов)
- **База данных**: PostgreSQL (аналитика и результаты)
- **Аналитика**: Prometheus + Grafana (мониторинг)

## Этапы реализации

### Этап 1: Улучшение голосового движка (1-2 дня)

#### 1.1 Интеграция ElevenLabs TTS
```python
# voice_service.py - улучшенная версия
class ElevenLabsVoiceService:
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.voice_id = "AB9XsbSA4eLG12t2myjN"  # Женский русский голос
        self.model_id = "eleven_multilingual_v2"
    
    async def generate_speech(self, text: str, emotion: str = "neutral") -> bytes:
        """Генерирует речь с эмоциональной окраской"""
        # Реализация с поддержкой эмоций и пауз
```

#### 1.2 Настройка голосовых профилей
- **Основной голос**: Мария (дружелюбный, уверенный)
- **Эмоциональные состояния**: 
  - Уверенность (при презентации)
  - Понимание (при обработке возражений)
  - Энтузиазм (при получении контактов)

### Этап 2: Интеллектуальная система диалога (2-3 дня)

#### 2.1 Улучшенный AI-модуль
```python
# ai_dialog_system_advanced.py
class AdvancedDialogSystem:
    def __init__(self):
        self.conversation_stages = {
            'greeting': self._handle_greeting,
            'objection_handling': self._handle_objections,
            'value_presentation': self._handle_value,
            'contact_collection': self._handle_contacts,
            'closing': self._handle_closing
        }
        
    async def process_user_input(self, text: str, context: Dict) -> Dict:
        """Обрабатывает ввод пользователя с учетом контекста"""
        # Анализ намерений, эмоций, возражений
        # Генерация персонализированного ответа
```

#### 2.2 Система обработки возражений
```python
class ObjectionHandler:
    def __init__(self):
        self.objection_patterns = {
            'not_interested': [
                'не интересует', 'не интересно', 'не нужно'
            ],
            'has_carrier': [
                'есть перевозчик', 'работаем с', 'уже есть'
            ],
            'send_email': [
                'отправьте на почту', 'напишите email'
            ],
            'busy': [
                'занят', 'неудобно', 'позже'
            ]
        }
    
    def analyze_objection(self, text: str) -> Dict:
        """Анализирует возражения и возвращает стратегию ответа"""
```

### Этап 3: Интеграция с SaluteSpeech STT (1-2 дня)

#### 3.1 Улучшенное распознавание речи
```python
# salutespeech_service_advanced.py
class AdvancedSaluteSpeechService:
    def __init__(self):
        self.auth_token = None
        self.session_id = None
        
    async def start_recognition_session(self) -> str:
        """Создает сессию распознавания с улучшенными параметрами"""
        
    async def process_audio_chunk(self, audio_data: bytes) -> Dict:
        """Обрабатывает аудио чанк с контекстным распознаванием"""
```

#### 3.2 Обработка фоновых шумов
- Фильтрация шумов офиса
- Распознавание перебиваний
- Определение эмоционального тона

### Этап 4: Система аналитики и обучения (2-3 дня)

#### 4.1 База данных для аналитики
```sql
-- Создание таблиц для аналитики
CREATE TABLE call_sessions (
    id SERIAL PRIMARY KEY,
    call_id VARCHAR(50) UNIQUE,
    phone_number VARCHAR(20),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration INTEGER,
    outcome VARCHAR(50),
    contact_obtained BOOLEAN,
    calculation_requested BOOLEAN
);

CREATE TABLE conversation_turns (
    id SERIAL PRIMARY KEY,
    call_id VARCHAR(50),
    turn_number INTEGER,
    user_text TEXT,
    ai_response TEXT,
    confidence FLOAT,
    stage VARCHAR(50),
    objections_detected TEXT[],
    timestamp TIMESTAMP
);
```

#### 4.2 Система мониторинга KPI
```python
# analytics_service.py
class CallAnalytics:
    def __init__(self):
        self.metrics = {
            'conversion_rate': 0.0,
            'avg_call_duration': 0.0,
            'contact_obtained_rate': 0.0,
            'objection_handling_success': 0.0
        }
    
    async def track_call_metrics(self, call_data: Dict):
        """Отслеживает метрики звонка в реальном времени"""
    
    async def generate_report(self, date_range: Tuple) -> Dict:
        """Генерирует отчет по эффективности"""
```

### Этап 5: Улучшенный Voximplant сценарий (1 день)

#### 5.1 Продвинутый JavaScript сценарий
```javascript
// voximplant_scenario_advanced.js
const ADVANCED_CONFIG = {
    maxCallDuration: 300000, // 5 минут
    maxSilenceCount: 3,
    emotionDetection: true,
    realtimeAnalytics: true,
    adaptiveResponses: true
};

// Улучшенная обработка ASR
function createAdvancedRecognizer(call, onResult) {
    const recognizer = Voximplant.createASR('ru-RU', {
        interimResults: true,
        maxAlternatives: 3,
        profanityFilter: false,
        adaptation: {
            phraseHints: ['логистика', 'перевозки', 'Китай', 'Россия'],
            boost: 2.0
        }
    });
    
    // Обработка промежуточных результатов
    recognizer.addEventListener('InterimResult', function(e) {
        // Анализ промежуточных результатов для лучшего понимания
    });
}
```

### Этап 6: Система персонализации (1-2 дня)

#### 6.1 База знаний о клиентах
```python
# knowledge_base.py
class ClientKnowledgeBase:
    def __init__(self):
        self.client_profiles = {}
        self.industry_patterns = {}
        
    async def get_client_context(self, phone: str) -> Dict:
        """Получает контекст клиента из базы данных"""
        
    async def update_client_profile(self, phone: str, interaction_data: Dict):
        """Обновляет профиль клиента на основе взаимодействия"""
```

#### 6.2 Персонализация диалога
- Адаптация под отрасль клиента
- Учет предыдущих взаимодействий
- Персонализация предложений

### Этап 7: Система A/B тестирования (1 день)

#### 7.1 Фреймворк для тестирования
```python
# ab_testing.py
class ABTestingFramework:
    def __init__(self):
        self.experiments = {
            'greeting_style': ['formal', 'friendly', 'direct'],
            'objection_handling': ['soft', 'assertive', 'value_focused'],
            'closing_approach': ['direct_ask', 'value_reminder', 'urgency']
        }
    
    def get_variant(self, experiment_name: str, call_id: str) -> str:
        """Возвращает вариант для A/B теста"""
    
    async def track_experiment_result(self, experiment: str, variant: str, result: Dict):
        """Отслеживает результат эксперимента"""
```

## События и схема взаимодействия

### 1. События системы

#### 1.1 События Voximplant
```javascript
// Основные события звонка
CallEvents.Connected      // Звонок соединен
CallEvents.Disconnected   // Звонок завершен
CallEvents.Failed         // Ошибка звонка

// События ASR
ASREvents.Result          // Результат распознавания
ASREvents.InterimResult   // Промежуточный результат
ASREvents.Error           // Ошибка ASR
ASREvents.Canceled        // Отмена ASR

// События TTS
PlayerEvents.Started      // Начало воспроизведения
PlayerEvents.Finished     // Завершение воспроизведения
PlayerEvents.Error        // Ошибка TTS
```

#### 1.2 События Backend
```python
# Webhook события
WEBHOOK_EVENTS = {
    'call_started': 'Начало звонка',
    'asr_text': 'Распознанный текст',
    'tts_request': 'Запрос на генерацию речи',
    'call_ended': 'Завершение звонка',
    'error': 'Ошибка системы'
}
```

### 2. Схема взаимодействия

```
1. Инициация звонка
   Voximplant → Backend: call_started
   Backend → Voximplant: greeting_text
   Voximplant → ElevenLabs: TTS request
   ElevenLabs → Voximplant: audio_stream

2. Обработка речи пользователя
   Voximplant → SaluteSpeech: audio_chunk
   SaluteSpeech → Voximplant: recognized_text
   Voximplant → Backend: asr_text
   Backend → OpenAI: context + user_text
   OpenAI → Backend: ai_response
   Backend → Voximplant: response_text
   Voximplant → ElevenLabs: TTS request

3. Завершение звонка
   Voximplant → Backend: call_ended
   Backend → Database: analytics_data
   Backend → Analytics: kpi_update
```

## Современные библиотеки и интеграции

### 1. Обработка голоса

#### 1.1 TTS (Text-to-Speech)
```python
# elevenlabs_integration.py
import elevenlabs
from elevenlabs import generate, stream

class ElevenLabsService:
    def __init__(self):
        elevenlabs.set_api_key(ELEVENLABS_API_KEY)
        
    async def generate_speech_stream(self, text: str, voice_id: str) -> bytes:
        """Генерирует потоковую речь"""
        audio_stream = generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2",
            stream=True
        )
        return audio_stream
```

#### 1.2 STT (Speech-to-Text)
```python
# salutespeech_integration.py
import aiohttp
import asyncio

class SaluteSpeechService:
    def __init__(self):
        self.base_url = "https://smartspeech.sber.ru"
        self.auth_token = None
        
    async def recognize_speech(self, audio_data: bytes) -> Dict:
        """Распознает речь с помощью SaluteSpeech API"""
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'audio/wav'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/asr",
                data=audio_data,
                headers=headers
            ) as response:
                return await response.json()
```

### 2. Интеграция с телефонией

#### 2.1 Voximplant API
```python
# voximplant_integration.py
import requests
from typing import Dict

class VoximplantAPI:
    def __init__(self):
        self.account_id = VOXIMPLANT_ACCOUNT_ID
        self.api_key = VOXIMPLANT_API_KEY
        
    async def start_scenario(self, phone: str, custom_data: Dict) -> Dict:
        """Запускает сценарий звонка"""
        url = "https://api.voximplant.com/platform_api/StartScenarios/"
        
        params = {
            'account_id': self.account_id,
            'api_key': self.api_key,
            'phone': phone,
            'scenario_name': 'advanced_call_scenario',
            'script_custom_data': json.dumps(custom_data)
        }
        
        response = requests.post(url, params=params)
        return response.json()
```

### 3. Работа с LLM

#### 3.1 OpenAI GPT Integration
```python
# openai_integration.py
import openai
from openai import AsyncOpenAI

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
    async def generate_response(self, messages: List[Dict], context: Dict) -> str:
        """Генерирует ответ с учетом контекста диалога"""
        system_prompt = self._build_system_prompt(context)
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                *messages
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content
```

## План развертывания

### 1. Подготовка окружения
```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Заполнить API ключи в .env

# Инициализация базы данных
python scripts/init_db.py

# Запуск сервисов
docker-compose up -d
```

### 2. Тестирование
```bash
# Запуск тестов
python -m pytest tests/

# Тестирование интеграций
python test_integrations.py

# Нагрузочное тестирование
python load_test.py
```

### 3. Мониторинг
```bash
# Запуск мониторинга
docker-compose -f monitoring.yml up -d

# Просмотр метрик
open http://localhost:3000  # Grafana
open http://localhost:9090  # Prometheus
```

## Ожидаемые результаты

### 1. KPI метрики
- **Конверсия**: 15-25% (получение контактов ЛПР)
- **Длительность звонка**: 2-3 минуты
- **Качество диалога**: 85%+ естественности
- **Обработка возражений**: 70%+ успешности

### 2. Технические показатели
- **Время отклика**: < 500ms
- **Точность STT**: > 95%
- **Качество TTS**: Человекоподобный голос
- **Стабильность**: 99.9% uptime

### 3. Бизнес-результаты
- Автоматизация 80% холодных звонков
- Сокращение времени на поиск клиентов на 60%
- Увеличение количества квалифицированных лидов на 40%
- ROI: 300%+ в первый год

## Следующие шаги

1. **Немедленно**: Начать с Этапа 1 (улучшение TTS)
2. **Неделя 1**: Завершить Этапы 2-3 (AI диалог + STT)
3. **Неделя 2**: Этапы 4-5 (аналитика + сценарий)
4. **Неделя 3**: Этапы 6-7 (персонализация + A/B тесты)
5. **Неделя 4**: Тестирование и оптимизация

Этот план обеспечит создание продвинутого AI-агента, способного вести естественные диалоги и эффективно выполнять задачи холодных звонков для компании ТРАНСТИРЕКС.

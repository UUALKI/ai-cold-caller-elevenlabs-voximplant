# 🤖 AI Cold Caller - ElevenLabs WebSocket + Voximplant Integration

Система автоматических звонков с искусственным интеллектом, использующая ElevenLabs Conversational AI Agent и Voximplant для телефонии.

## 🚀 Основные возможности

- **ElevenLabs WebSocket интеграция** - реальное время диалога с AI агентом
- **Voximplant телефония** - исходящие звонки на российские номера
- **Автоматический диалог** - AI агент ведет разговор с клиентами
- **Веб-интерфейс** - удобное управление через браузер
- **Аналитика звонков** - статистика и результаты

## 📁 Структура проекта

### 🔧 Основные серверы:
- **`voximplant_elevenlabs_integration.py`** - главный Flask сервер (порт 8000)
- **`main.py`** - FastAPI сервер с веб-интерфейсом
- **`run.py`** - скрипт быстрого запуска

### ⚙️ Конфигурация:
- **`config_elevenlabs.py`** - настройки ElevenLabs Agent
- **`config.py`** - общие настройки и API ключи

### 📞 Сценарии Voximplant:
- **`voximplant_scenario_elevenlabs_agent.js`** - основной сценарий
- **`voximplant_scenario_elevenlabs_robust.js`** - улучшенная версия
- **`voximplant_scenario_elevenlabs_stream.js`** - потоковая версия

### 🧠 AI и сервисы:
- **`elevenlabs_agent_service.py`** - сервис ElevenLabs Agent
- **`elevenlabs_voximplant_service.py`** - интеграция сервисов
- **`gpt_service.py`** - GPT диалоги
- **`voice_service.py`** - синтез речи
- **`call_manager.py`** - управление звонками

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка API ключей
Отредактируйте `config_elevenlabs.py`:
```python
ELEVENLABS_AGENT_API_KEY = "ваш_ключ_elevenlabs"
ELEVENLABS_AGENT_ID = "ваш_agent_id"
```

### 3. Запуск сервера
```bash
python voximplant_elevenlabs_integration.py
```

### 4. Открытие веб-интерфейса
```
http://127.0.0.1:8000/form
```

## 🔧 Конфигурация

### ElevenLabs Agent:
- **Agent ID:** `agent_8701k4554cs1e69arzeae6vva5qz`
- **API Key:** настройте в `config_elevenlabs.py`
- **WebSocket:** `wss://api.elevenlabs.io/v1/convai/conversation`

### Voximplant:
- **Account ID:** 9768007
- **Сценарий:** `elevenlabs_official_module`
- **Rule Name:** `ai cold caller`

## 📊 API Endpoints

### Flask сервер (порт 8000):
- **`GET /form`** - форма запуска звонков
- **`POST /start-call`** - API запуска звонка
- **`POST /voximplant-webhook/<call_id>`** - webhook от Voximplant
- **`GET /test-elevenlabs-connection`** - тест подключения
- **`GET /active-calls`** - список активных звонков

## 🧪 Тестирование

### Веб-интерфейс:
1. Откройте `http://127.0.0.1:8000/form`
2. Введите номер телефона
3. Нажмите "Запустить звонок"

### Тестовые файлы:
- **`test_elevenlabs_api.js`** - тесты ElevenLabs API
- **`test_interface.html`** - веб-интерфейс для тестирования

## 🔄 Архитектура

```
📞 Voximplant (звонки)
    ↓ (аудио)
🔌 ElevenLabs WebSocket
    ↓ (AI обработка)
🎭 ElevenLabs Agent (диалог)
    ↓ (аудио ответ)
🔌 ElevenLabs WebSocket  
    ↓ (аудио)
📞 Voximplant (воспроизведение)
```

## 📝 Особенности

- **Реальное время** - WebSocket соединение для мгновенной обработки
- **Автоматическое переподключение** - восстановление соединения при сбоях
- **Обработка ошибок** - надежная работа в production
- **Масштабируемость** - поддержка множественных звонков

## 🔒 Безопасность

- API ключи хранятся в конфигурационных файлах
- `.gitignore` исключает чувствительные данные
- Webhook'и защищены проверкой call_id

## 📞 Поддержка

Для вопросов и поддержки создайте issue в репозитории.

## 📄 Лицензия

MIT License
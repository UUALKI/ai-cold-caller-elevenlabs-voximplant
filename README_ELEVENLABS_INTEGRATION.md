# 🤖 ElevenLabs AI Agent Integration

Интеграция ElevenLabs AI Agent Platform с Voximplant для совершения интеллектуальных звонков с российских номеров.

## 🎯 Что это такое

Система позволяет использовать **ElevenLabs AI Agent** (готовый бот с голосовым интерфейсом) в сочетании с **Voximplant** (российская телефония) для совершения реальных звонков.

### ✅ Преимущества

- **Качественный AI** - ElevenLabs Agent с естественным диалогом
- **Российские номера** - Voximplant для звонков в РФ
- **Быстрая настройка** - готовый агент из коробки
- **Умные ответы** - контекстная память и адаптация

## 🏗️ Архитектура

```
ElevenLabs AI Agent (логика бота)
    ↓ (REST API)
Voximplant (телефония)
    ↓ (российские номера)
Реальные звонки клиентам
    ↓ (webhook)
База данных (результаты)
```

## 📁 Структура файлов

```
elevenlabs-integration/
├── config_elevenlabs.py              # Конфигурация
├── elevenlabs_agent_service.py       # Сервис ElevenLabs Agent
├── elevenlabs_voximplant_service.py  # Интеграция с Voximplant
├── main_elevenlabs.py                # Веб-сервер
├── voximplant_scenario_elevenlabs_agent.js  # Voximplant сценарий
├── test_elevenlabs_integration.py    # Тестирование
└── README_ELEVENLABS_INTEGRATION.md  # Документация
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install fastapi uvicorn requests python-dotenv
```

### 2. Настройка конфигурации

Отредактируйте `config_elevenlabs.py`:

```python
# ElevenLabs AI Agent конфигурация
ELEVENLABS_AGENT_API_KEY = "sk_ff39c1d16620e8788133b568029a26401b92f1918cd89f40"
ELEVENLABS_AGENT_ID = "agent_01jxd1arjvfq9bd1ae6j92cs3t"
```

### 3. Настройка Voximplant

1. Создайте новый сценарий в Voximplant
2. Скопируйте код из `voximplant_scenario_elevenlabs_agent.js`
3. Настройте правило маршрутизации

### 4. Тестирование

```bash
# Запустите тесты
python test_elevenlabs_integration.py
```

### 5. Запуск сервера

```bash
# Запустите веб-сервер
python main_elevenlabs.py
```

### 6. Откройте интерфейс

```
http://localhost:8001
```

## 🎭 Использование

### Через веб-интерфейс

1. **Тестирование подключений**
   - Нажмите "🧪 Тестировать подключения"
   - Убедитесь, что все сервисы работают

2. **Тестирование Agent**
   - Нажмите "🧪 Тестировать Agent"
   - Проверьте, что агент отвечает

3. **Запуск звонка**
   - Введите номер телефона
   - Нажмите "📞 Запустить звонок"

### Через API

```bash
# Запуск звонка
curl -X POST "http://localhost:8001/api/call/elevenlabs-agent" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+79991234567",
    "agent_config": {
      "agent_id": "agent_01jxd1arjvfq9bd1ae6j92cs3t",
      "api_key": "sk_ff39c1d16620e8788133b568029a26401b92f1918cd89f40",
      "voice_id": "21m00Tcm4TlvDq8ikWAM"
    }
  }'
```

### Через Python

```python
from elevenlabs_voximplant_service import elevenlabs_voximplant_service

# Запуск звонка
result = elevenlabs_voximplant_service.start_elevenlabs_agent_call(
    "+79991234567",
    {
        "agent_id": "agent_01jxd1arjvfq9bd1ae6j92cs3t",
        "api_key": "sk_ff39c1d16620e8788133b568029a26401b92f1918cd89f40"
    }
)

print(result)
```

## 🔧 API Endpoints

### POST `/api/call/elevenlabs-agent`
Запускает звонок с ElevenLabs AI Agent

**Параметры:**
```json
{
  "phone_number": "+79991234567",
  "agent_config": {
    "agent_id": "agent_id",
    "api_key": "api_key",
    "voice_id": "voice_id"
  }
}
```

### GET `/api/test-connections`
Тестирует подключения к ElevenLabs Agent и Voximplant

### GET `/api/test-agent`
Тестирует ElevenLabs Agent

### GET `/api/calls`
Возвращает историю звонков

### POST `/api/call-results`
Webhook для сохранения результатов звонков

## 📊 Структура данных

### Данные звонка

```json
{
  "call_id": "session_1234567890_abc123",
  "phone_number": "+79991234567",
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "2024-01-15T10:32:45Z",
  "duration": 165,
  "status": "completed",
  "conversation": [
    {
      "role": "agent",
      "text": "Добрый день! Меня зовут Алёна...",
      "timestamp": "2024-01-15T10:30:05Z"
    },
    {
      "role": "client",
      "text": "Да, есть минутка",
      "timestamp": "2024-01-15T10:30:12Z",
      "confidence": 0.85
    }
  ],
  "outcome": "interested",
  "metrics": {
    "turns": 6,
    "client_turns": 3,
    "agent_turns": 3,
    "engagement": "high",
    "sentiment": "positive",
    "key_topics": ["pricing", "timing"]
  }
}
```

## 🧪 Тестирование

### Автоматические тесты

```bash
# Запуск всех тестов
python test_elevenlabs_integration.py
```

### Ручное тестирование

```bash
# Тест ElevenLabs Agent
python elevenlabs_agent_service.py

# Тест Voximplant
python elevenlabs_voximplant_service.py
```

## 🔍 Отладка

### Логи

Логи сохраняются в консоли и содержат:
- Подключения к API
- Результаты ASR
- Ошибки TTS
- Данные звонков

### Частые проблемы

1. **Ошибка подключения к ElevenLabs Agent**
   - Проверьте API ключ
   - Убедитесь, что агент активен

2. **Ошибка Voximplant**
   - Проверьте настройки аккаунта
   - Убедитесь, что сценарий создан

3. **Медленные ответы**
   - Проверьте интернет-соединение
   - Увеличьте таймауты в конфигурации

## 🎯 Настройка ElevenLabs Agent

### Создание агента

1. Зайдите на [ElevenLabs AI Agent Platform](https://elevenlabs.io/ai-agent)
2. Создайте нового агента
3. Настройте промпты и логику
4. Получите Agent ID и API ключ

### Настройка голоса

```python
# Доступные голоса
VOICES = {
    "molly": "21m00Tcm4TlvDq8ikWAM",  # Женский
    "bella": "EXAVITQu4vr4xnSDxMaL",  # Женский
    "josh": "VR6AewLTigWG4xSOukaG"    # Мужской
}
```

## 🔒 Безопасность

### API ключи

- Храните ключи в переменных окружения
- Не коммитьте ключи в репозиторий
- Используйте HTTPS в продакшене

### Валидация

- Проверяйте номера телефонов
- Валидируйте входные данные
- Ограничивайте частоту запросов

## 📈 Мониторинг

### Метрики

- Длительность звонков
- Успешность ASR
- Время ответа агента
- Конверсия звонков

### Алерты

- Ошибки подключения
- Высокая латентность
- Неудачные звонки

## 🚀 Развитие

### Возможные улучшения

1. **Интеграция с CRM**
   - Автоматическое создание лидов
   - Синхронизация контактов

2. **Аналитика**
   - Детальная статистика
   - A/B тестирование сценариев

3. **Автоматизация**
   - Планировщик звонков
   - Массовые кампании

4. **Мультиязычность**
   - Поддержка других языков
   - Локализация интерфейса

## 📞 Поддержка

### Документация

- [ElevenLabs API Docs](https://docs.elevenlabs.io/)
- [Voximplant API Docs](https://voximplant.com/docs/references/httpapi)

### Контакты

- ElevenLabs: [support@elevenlabs.io](mailto:support@elevenlabs.io)
- Voximplant: [support@voximplant.com](mailto:support@voximplant.com)

## 📄 Лицензия

Проект создан для демонстрации возможностей интеграции ElevenLabs AI Agent с Voximplant.

---

**🎉 Готово к использованию!** 

Система позволяет совершать интеллектуальные звонки с использованием лучшего AI от ElevenLabs и российской телефонии от Voximplant.

# 🚀 ИНТЕГРАЦИЯ С VOXIMPLANT API

## 📞 Запуск исходящих звонков от AI агента Алёны

### 🔧 Настройка Voximplant API

1. **Получение API ключа:**
   - Войдите в [Voximplant Console](https://console.voximplant.com/)
   - Перейдите в раздел "API Keys"
   - Создайте новый API ключ с правами на запуск сценариев

2. **Настройка сценария:**
   - Загрузите файл `voximplant_scenario_intelligent_alena.js` в Voximplant
   - Назовите сценарий: `intelligent_alena`
   - Убедитесь, что сценарий активен

### 🔗 API Endpoint для запуска звонков

```python
# В файле run_with_database.py добавьте:

import requests
import base64

VOXIMPLANT_API_KEY = "YOUR_API_KEY_HERE"
VOXIMPLANT_ACCOUNT_ID = "YOUR_ACCOUNT_ID"
VOXIMPLANT_SCENARIO_NAME = "intelligent_alena"

@app.route('/api/start-call', methods=['POST'])
def start_call():
    """API для запуска исходящего звонка от AI агента Алёны"""
    try:
        data = request.json
        
        if not data or 'phone' not in data:
            return jsonify({'error': 'Phone number is required'}), 400
        
        phone = data['phone']
        voice_id = data.get('voice_id', '21m00Tcm4TlvDq8ikWAM')
        greeting = data.get('greeting', '')
        webhook_url = data.get('webhook_url', 'http://localhost:8004/api/voxi/events')
        
        # Валидация номера телефона
        if not phone or len(phone) < 10:
            return jsonify({'error': 'Invalid phone number'}), 400
        
        # Подготовка данных для Voximplant
        custom_data = {
            'phone': phone,
            'voice_id': voice_id,
            'webhook_url': webhook_url
        }
        
        if greeting:
            custom_data['greeting'] = greeting
        
        # Кодирование данных в base64
        custom_data_encoded = base64.b64encode(json.dumps(custom_data).encode()).decode()
        
        # Запрос к Voximplant API
        voximplant_url = f"https://api.voximplant.com/platform_api/StartScenarios"
        
        headers = {
            'Authorization': f'Bearer {VOXIMPLANT_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'account_id': VOXIMPLANT_ACCOUNT_ID,
            'rule_id': VOXIMPLANT_SCENARIO_NAME,
            'script_custom_data': custom_data_encoded,
            'phone_number': phone
        }
        
        response = requests.post(voximplant_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"🚀 Звонок запущен! ID: {result.get('result', {}).get('scenario_id')}")
            
            return jsonify({
                'success': True,
                'message': f'Звонок запущен на номер {phone}',
                'scenario_id': result.get('result', {}).get('scenario_id'),
                'call_data': custom_data
            })
        else:
            print(f"❌ Ошибка Voximplant API: {response.status_code} - {response.text}")
            return jsonify({'error': 'Voximplant API error'}), 500
        
    except Exception as e:
        print(f"Ошибка запуска звонка: {e}")
        return jsonify({'error': 'Failed to start call'}), 500
```

### 🔐 Переменные окружения

Создайте файл `.env` в корне проекта:

```env
VOXIMPLANT_API_KEY=your_api_key_here
VOXIMPLANT_ACCOUNT_ID=your_account_id
VOXIMPLANT_SCENARIO_NAME=intelligent_alena
```

### 📋 Полная интеграция

1. **Установите зависимости:**
```bash
pip install python-dotenv requests
```

2. **Обновите run_with_database.py:**
```python
from dotenv import load_dotenv
load_dotenv()

VOXIMPLANT_API_KEY = os.getenv('VOXIMPLANT_API_KEY')
VOXIMPLANT_ACCOUNT_ID = os.getenv('VOXIMPLANT_ACCOUNT_ID')
VOXIMPLANT_SCENARIO_NAME = os.getenv('VOXIMPLANT_SCENARIO_NAME')
```

3. **Загрузите сценарий в Voximplant:**
   - Скопируйте содержимое `voximplant_scenario_intelligent_alena.js`
   - Вставьте в редактор сценариев Voximplant
   - Сохраните как `intelligent_alena`

### 🎯 Тестирование

1. **Запустите сервер:**
```bash
python run_with_database.py
```

2. **Откройте интерфейс:**
   - Перейдите на http://localhost:8004
   - Введите номер телефона
   - Нажмите "Запустить звонок от Алёны"

3. **Проверьте логи:**
   - В консоли сервера должны появиться сообщения о запуске звонка
   - В Voximplant Console можно отследить выполнение сценария

### 🔍 Мониторинг звонков

1. **Дашборд звонков:** http://localhost:8004/calls
2. **API звонков:** http://localhost:8004/api/calls
3. **Статистика:** http://localhost:8004/api/stats

### ⚠️ Важные моменты

1. **Номера телефонов:** Должны быть в международном формате (+7...)
2. **Webhook URL:** Должен быть доступен из интернета (используйте ngrok)
3. **API ключи:** Храните в безопасном месте
4. **Лимиты:** Следите за лимитами Voximplant API

### 🚀 Готово!

Теперь у вас есть полноценная система для запуска исходящих звонков от AI агента Алёны с:
- ✅ Интеллектуальным диалогом
- ✅ Динамическим TTS
- ✅ Системой прерывания речи
- ✅ Автоматическим сбором данных
- ✅ Дашбордом для мониторинга

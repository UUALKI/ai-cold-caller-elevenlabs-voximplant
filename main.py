#!/usr/bin/env python3
"""
Основной сервер для живого диалога в реальном времени
Обработка webhook'ов от Voximplant с SaluteSpeech API
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
# from fastapi.staticfiles import StaticFiles
import uvicorn

from ai_dialog_system import process_webhook_event, dialog_system
from ai_dialog_system_advanced import process_webhook_event_advanced, advanced_dialog_system
from call_manager import CallManager
from voximplant_service import VoximplantService
from salutespeech_service_advanced import salutespeech_service

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="Живая система диалога",
    description="API для обработки webhook'ов от Voximplant с SaluteSpeech API",
    version="2.0.0"
)

# Инициализируем сервисы
call_manager = CallManager()
voxi_service = VoximplantService()

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    logger.info("🚀 Живая система диалога запущена")
    logger.info("📡 Готов к приему webhook'ов от Voximplant")

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении"""
    logger.info("🛑 Живая система диалога остановлена")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Веб-интерфейс для запуска звонков"""
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Call Prototype</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #333;
            }
            
            .container {
                background: rgba(255, 255, 255, 0.95);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                width: 90%;
                max-width: 500px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .header h1 {
                font-size: 28px;
                color: #333;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            .header p {
                color: #666;
                font-size: 16px;
            }
            
            .form-group {
                margin-bottom: 30px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 10px;
                font-weight: 600;
                color: #333;
            }
            
            .form-group input {
                width: 100%;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 16px;
                transition: all 0.3s ease;
            }
            
            .form-group input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .call-button {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            .call-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .call-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .history {
                margin-top: 40px;
                padding-top: 30px;
                border-top: 2px solid #f0f0f0;
            }
            
            .history h2 {
                font-size: 20px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
                color: #333;
            }
            
            .call-item {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .call-number {
                font-weight: 600;
                color: #333;
            }
            
            .call-status {
                font-size: 14px;
                color: #28a745;
                font-weight: 500;
            }
            
            .call-date {
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }
            
            .loading {
                display: none;
                text-align: center;
                margin-top: 20px;
            }
            
            .spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI Call Prototype</h1>
                <p>Умные звонки с искусственным интеллектом</p>
            </div>
            
            <form id="callForm">
                <div class="form-group">
                    <label for="phoneNumber">Номер телефона клиента:</label>
                    <input type="tel" id="phoneNumber" name="phoneNumber" 
                           placeholder="+7 (999) 123-45-67" 
                           value="+7 (999) 123-45-67" required>
                </div>
                
                <button type="submit" class="call-button" id="callButton">
                    📞 Позвонить клиенту
                </button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Выполняется звонок...</p>
            </div>
            
            <div class="history">
                <h2>📋 История звонков</h2>
                <div id="callHistory">
                    <div class="call-item">
                        <div>
                            <div class="call-number">+79850889557</div>
                            <div class="call-date">25.08.2025, 18:37:40</div>
                        </div>
                        <div class="call-status">completed</div>
                    </div>
                    <div class="call-item">
                        <div>
                            <div class="call-number">+79850889557</div>
                            <div class="call-date">26.08.2025, 10:47:20</div>
                        </div>
                        <div class="call-status">completed</div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('callForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const phoneNumber = document.getElementById('phoneNumber').value;
                const callButton = document.getElementById('callButton');
                const loading = document.getElementById('loading');
                
                // Показываем индикатор загрузки
                callButton.disabled = true;
                callButton.innerHTML = '⏳ Звоним...';
                loading.style.display = 'block';
                
                try {
                    const response = await fetch('/api/call', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            phone_number: phoneNumber
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        // Добавляем в историю
                        addCallToHistory(phoneNumber, 'completed');
                        alert('Звонок успешно выполнен!');
                    } else {
                        alert('Ошибка при выполнении звонка: ' + (result.error || 'Неизвестная ошибка'));
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Ошибка соединения с сервером');
                } finally {
                    // Скрываем индикатор загрузки
                    callButton.disabled = false;
                    callButton.innerHTML = '📞 Позвонить клиенту';
                    loading.style.display = 'none';
                }
            });
            
            function addCallToHistory(phoneNumber, status) {
                const historyContainer = document.getElementById('callHistory');
                const callItem = document.createElement('div');
                callItem.className = 'call-item';
                
                const now = new Date();
                const dateString = now.toLocaleDateString('ru-RU') + ', ' + 
                                 now.toLocaleTimeString('ru-RU');
                
                callItem.innerHTML = `
                    <div>
                        <div class="call-number">${phoneNumber}</div>
                        <div class="call-date">${dateString}</div>
                    </div>
                    <div class="call-status">${status}</div>
                `;
                
                historyContainer.insertBefore(callItem, historyContainer.firstChild);
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "active_sessions": len(dialog_system.conversation_sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/voxi/events")
async def handle_voximplant_webhook(request: Request):
    """
    Обрабатывает webhook события от Voximplant
    Поддерживает потоковую обработку ASR от SaluteSpeech API
    """
    try:
        # Получаем данные запроса
        body = await request.body()
        data = json.loads(body) if body else {}
        
        logger.info(f"📥 Получен webhook: {data}")
        
        # Проверяем, это простой текстовый запрос от Yandex ASR
        if 'text' in data and 'turn' in data:
            # Простой обработчик для Yandex ASR
            return await handle_yandex_text_request(data)
        
        event_type = data.get('event', 'unknown')
        
        # Обрабатываем SaluteSpeech события
        if event_type in ['start_salutespeech_session', 'process_audio_chunk', 'end_salutespeech_session']:
            result = await handle_salutespeech_event(data)
        else:
            # Обрабатываем обычные события через продвинутую систему диалога
            result = await process_webhook_event_advanced(data)
        
        logger.info(f"📤 Отправлен ответ: {result.get('success', False)}")
        
        return JSONResponse(content=result)
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Ошибка парсинга JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def handle_salutespeech_event(data: dict) -> dict:
    """Обрабатывает события SaluteSpeech"""
    try:
        event_type = data.get('event')
        call_id = data.get('call_id', 'unknown')
        
        if event_type == 'start_salutespeech_session':
            # Создаем сессию SaluteSpeech
            session_id = await salutespeech_service.start_recognition_session(call_id)
            return {
                "success": True,
                "session_id": session_id,
                "message": "SaluteSpeech session created"
            }
            
        elif event_type == 'process_audio_chunk':
            # Обрабатываем аудио чанк
            session_id = data.get('session_id')
            audio_data = data.get('audio_data', '')
            
            if session_id and audio_data:
                # Декодируем base64 аудио данные
                import base64
                audio_bytes = base64.b64decode(audio_data)
                
                result = await salutespeech_service.process_audio_chunk(call_id, audio_bytes)
                return {
                    "success": True,
                    "result": result,
                    "message": "Audio chunk processed"
                }
            else:
                return {
                    "success": False,
                    "error": "Missing session_id or audio_data"
                }
                
        elif event_type == 'end_salutespeech_session':
            # Завершаем сессию SaluteSpeech
            session_id = data.get('session_id')
            if session_id:
                await salutespeech_service.end_recognition_session(call_id)
                return {
                    "success": True,
                    "message": "SaluteSpeech session ended"
                }
            else:
                return {
                    "success": False,
                    "error": "Missing session_id"
                }
        
        else:
            return {
                "success": False,
                "error": f"Unknown SaluteSpeech event: {event_type}"
            }
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки SaluteSpeech события: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def handle_yandex_text_request(data: dict) -> dict:
    """Обрабатывает простые текстовые запросы от Yandex ASR"""
    try:
        text = data.get('text', '')
        turn = data.get('turn', 1)
        yandex_mode = data.get('yandex_mode', False)
        fast_response = data.get('fast_response', False)
        
        logger.info(f"🇷🇺 Yandex ASR запрос: '{text}' (ход {turn})")
        
        if not text or text.strip() == '':
            return {
                "success": False,
                "error": "Пустой текст"
            }
        
        # Всегда используем GPT для естественного диалога
        response = await generate_gpt_response(text, turn)
        
        logger.info(f"🤖 Yandex ASR ответ: '{response}'")
        
        return {
            "success": True,
            "response": {
                "text": response,
                "turn": turn,
                "yandex_mode": yandex_mode
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки Yandex запроса: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def generate_simple_response(text: str, turn: int) -> str:
    """Генерирует ответы для TRANSTIREX холодных звонков"""
    text_lower = text.lower()
    
    # База знаний TRANSTIREX
    company_info = {
        "name": "TRANSTIREX",
        "services": "международные перевозки из Китая в Россию",
        "benefits": "сокращение сроков и рисков доставки на 20-30%",
        "specialization": "логистика, таможенное оформление, мультимодальные перевозки"
    }
    
    # Анализ возражений
    objections = {
        "not_interested": any(word in text_lower for word in ['не интересует', 'не интересно', 'не нужно', 'не подходит', 'не актуально']),
        "has_carrier": any(word in text_lower for word in ['есть перевозчик', 'работаем с', 'уже есть', 'сотрудничаем', 'партнер', 'договор']),
        "send_email": any(word in text_lower for word in ['отправьте на почту', 'напишите email', 'на общую почту', 'info@', 'общий@', 'отправьте предложение']),
        "busy": any(word in text_lower for word in ['занят', 'неудобно', 'позже', 'не сейчас', 'не время', 'сейчас не могу']),
        "secretary": any(word in text_lower for word in ['секретарь', 'помощник', 'ассистент', 'приемная', 'не принимаю решения', 'общий отдел'])
    }
    
    # Этап 1: Приветствие и представление
    if turn == 1:
        if objections["secretary"]:
            return "Понимаю! Тогда подскажите, пожалуйста, как зовут вашего руководителя отдела логистики? Мне нужно согласовать с ним детали по конкретному вопросу."
        elif objections["not_interested"]:
            return "Понимаю! Но у нас есть специальное предложение именно для вашей отрасли. Давайте я быстро расскажу, как мы помогаем компаниям экономить до 30% на логистике?"
        elif objections["has_carrier"]:
            return "Отлично! Значит, вы понимаете важность логистики. А что если я покажу, как можно сократить расходы на 20-30% при том же качестве?"
        else:
            return "Добрый день! Меня зовут Алёна, я специалист по международным перевозкам компании TRANSTIREX. Подскажите, с кем я могу обсудить вопросы логистики из Китая в Россию?"
    
    # Этап 2: Работа с возражениями
    elif turn == 2:
        if objections["send_email"]:
            return "Конечно, я отправлю на общую почту. Но чтобы наше предложение не затерялось среди сотни других, подскажите, пожалуйста, как зовут вашего логиста? Тогда я укажу его имя в теме письма."
        elif objections["busy"]:
            return "Понимаю, сейчас неудобно. Давайте я перезвоню в удобное время? Когда вам будет удобно?"
        elif objections["not_interested"]:
            return "Спасибо за честность! Может быть, стоит хотя бы узнать о наших условиях? Мы работаем с ведущими компаниями и гарантируем качество."
        else:
            return "Мы помогаем таким компаниям, как ваша, сокращать сроки и риски по доставке грузов из Китая. У нас есть точечное предложение по вашему направлению. Давайте я оперативно подготовлю для вас предварительный расчет?"
    
    # Этап 3: Презентация ценности
    elif turn == 3:
        if any(word in text_lower for word in ['расскажите', 'подробнее', 'что предлагаете', 'как работаете']):
            return "У нас есть специальное предложение по вашему направлению. Для расчета нужен город отправки и назначения. Куда вам удобнее получить результат?"
        elif objections["send_email"]:
            return "Обязательно отправлю! А для персонального предложения подскажите, кто у вас отвечает за логистику? Это стандартная практика."
        else:
            return "Спасибо! Я подготовлю для вас персональное предложение. Куда вам удобнее получить расчет: на email или в WhatsApp?"
    
    # Этап 4: Завершение
    elif turn == 4:
        if any(word in text_lower for word in ['email', 'почта', 'почту']):
            return "Отлично! Куда вам удобнее получить расчет: в WhatsApp или на email?"
        elif any(word in text_lower for word in ['whatsapp', 'вайбер', 'телеграм']):
            return "Спасибо за информацию! Я направлю персональное предложение. Хорошего дня!"
        else:
            return "Отлично! Я направлю вам детальное предложение. Хорошего дня!"
    
    # Дополнительные ходы
    else:
        if objections["not_interested"] or objections["has_carrier"]:
            return "Понимаю! Если ситуация изменится, мы всегда на связи. Всего доброго!"
        else:
            return "Спасибо за информацию! Я направлю персональное предложение. Хорошего дня!"

async def generate_gpt_response(text: str, turn: int) -> str:
    """Генерирует естественные ответы с помощью GPT для TRANSTIREX холодных звонков"""
    try:
        # Анализируем ответ собеседника
        text_lower = text.lower()
        
        # Проверяем на отказ или завершение разговора
        if any(word in text_lower for word in ['до свидания', 'пока', 'не нужно', 'не интересует', 'не интересно', 'не подходит', 'не актуально', 'не звоните', 'не беспокойте']):
            logger.info(f"🤖 Обнаружен отказ на ходе {turn}, завершаем звонок")
            return "Понимаю, спасибо за ваше время. Всего доброго!"
        
        # Ограничиваем количество ходов
        if turn >= 6:
            logger.info(f"🤖 Достигнут лимит ходов ({turn}), завершаем звонок")
            return "Спасибо за ваше время! Если у вас появятся вопросы по логистике из Китая, мы всегда на связи. Всего доброго!"
        
        # Системный промпт для GPT
        system_prompt = """Ты — настойчивый и дружелюбный AI-менеджер международной логистической компании TRANSTIREX. 

Твоя главная задача — совершить холодный звонок и, несмотря на вероятные возражения ("не интересует", "есть перевозчик", "отправьте коммерческое предложение на общую почту"), получить либо запрос на просчет перевозки из Китая в Россию, либо прямой контакт (email или мобильный телефон) лица, принимающего решения (ЛПР) по логистике.

ВНИМАНИЕ: Ключевая сложность — тебя будет фильтровать секретарь или помощник. Их задача — не соединять с ЛПР и отфутболить на общую почту, что нам не подходит. Твоя цель в разговоре с ними — мягко, но настойчиво, минуя общие реквизиты, выяснить прямое имя и контакты ЛПР, аргументируя это необходимостью оперативно согласовать детали по конкретному вопросу.

Будь готов гибко парировать стандартные отписки, переводя разговор в конструктивное русло и оставляя инициативу у себя.

ПЛАН ДИАЛОГА:
1. Приветствие и представление (ход 1): Энергично представься как Алёна из TRANSTIREX
2. Работа с возражениями секретаря (ход 2-3): Мягко, но настойчиво выясни имя ЛПР
3. Презентация ценности (ход 4-5): Коротко расскажи о преимуществах
4. Завершение (ход 6+): Получи контакт или запрос на расчет

ВАЖНО: 
- Будь естественной, не скриптовой
- Адаптируйся к ответам собеседника
- НЕ завершай разговор раньше времени
- Главная цель — контакты ЛПР или запрос на расчет
- Компания называется TRANSTIREX (ударение на "И")
- Твое имя — Алёна
- Давай РАЗНЫЕ ответы на разные вопросы
- Не повторяй один и тот же ответ

СТРАТЕГИЯ ОТВЕТОВ:
- На приветствие (ход 1): "Спасибо! Я звоню по поводу логистики из Китая в Россию. Подскажите, с кем я могу обсудить вопросы перевозок?"
- На повторное приветствие (ход 2): "Спасибо! Мы помогаем компаниям сокращать сроки и риски по доставке грузов из Китая. У нас есть точечное предложение по вашему направлению. Давайте я оперативно подготовлю для вас предварительный расчет?"
- На "нет": "Понимаю. Может быть, у вас есть коллеги, которые занимаются логистикой? Или подскажите, кто принимает решения по перевозкам?"
- На отказ: "Понимаю, спасибо за ваше время. Всего доброго!"

Отвечай кратко, естественно, как живой человек. Максимум 2-3 предложения. НЕ говори "спасибо за время" и НЕ завершай разговор, если собеседник не отказался явно."""

        # Контекст диалога
        context = f"""
Ход диалога: {turn}
Ответ собеседника: "{text}"

Сгенерируй естественный ответ, который:
1. Соответствует текущему ходу диалога
2. Адаптируется к ответу собеседника
3. Продвигает к цели (контакты ЛПР или расчет)
4. Звучит естественно, не как скрипт
5. НЕ завершает разговор, если собеседник не отказался явно
"""

        # Используем OpenAI для генерации ответа
        from ai_dialog_system import dialog_system
        
        # Создаем временную сессию для диалога
        temp_session = {
            'call_id': f'temp_{turn}',
            'history': [],
            'turn_count': turn,
            'created_at': time.time(),
            'last_activity': time.time()
        }
        
        # Добавляем системный промпт в историю
        temp_session['history'].append({
            'role': 'system',
            'content': system_prompt,
            'timestamp': datetime.now().isoformat()
        })
        
        # Добавляем текущий запрос
        temp_session['history'].append({
            'role': 'user',
            'content': context,
            'timestamp': datetime.now().isoformat()
        })
        
        # Получаем ответ от GPT через существующую систему
        response = dialog_system._generate_ai_response(temp_session, text, {})
        
        if response and response.strip():
            # Проверяем, что ответ не завершает разговор
            response_lower = response.lower()
            if any(word in response_lower for word in ['спасибо за время', 'всего доброго', 'до свидания', 'пока']):
                logger.warning(f"⚠️ GPT пытается завершить разговор на ходе {turn}, генерируем альтернативный ответ")
                return generate_fallback_response(text, turn)
            return response.strip()
        else:
            # Fallback ответ
            logger.warning(f"⚠️ GPT не смог сгенерировать ответ на ходе {turn}, используем fallback")
            return generate_fallback_response(text, turn)
            
    except Exception as e:
        logger.error(f"❌ Ошибка GPT генерации: {e}")
        # Fallback ответ при ошибке
        return generate_fallback_response(text, turn)

def generate_fallback_response(text: str, turn: int) -> str:
    """Генерирует fallback ответы для продолжения диалога"""
    text_lower = text.lower()
    
    # Проверяем на отказ
    if any(word in text_lower for word in ['не нужно', 'не интересует', 'не интересно', 'не подходит', 'не актуально', 'нет не нужно']):
        return "Понимаю, спасибо за ваше время. Всего доброго!"
    
    # Проверяем на завершение разговора
    if any(word in text_lower for word in ['до свидания', 'пока', 'прощайте']):
        return "Понимаю, спасибо за ваше время. Всего доброго!"
    
    # Проверяем на запрос информации
    if any(word in text_lower for word in ['расскажите', 'подробнее', 'что предлагаете', 'как работаете', 'что это']):
        return "Мы специализируемся на доставке грузов из Китая в Россию. Сокращаем сроки на 20-30% и снижаем риски. Для расчета нужен город отправки и назначения. Куда вам удобнее получить результат?"
    
    # Проверяем на запрос email
    if any(word in text_lower for word in ['email', 'почта', 'почту', 'отправьте', 'напишите']):
        return "Обязательно отправлю! А для персонального предложения подскажите, кто у вас отвечает за логистику? Это стандартная практика."
    
    # Проверяем на приветствие
    if any(word in text_lower for word in ['добрый день', 'здравствуйте', 'привет', 'добрый день со мной']):
        if turn == 1:
            return "Спасибо! Я звоню по поводу логистики из Китая в Россию. Подскажите, с кем я могу обсудить вопросы перевозок?"
        elif turn == 2:
            return "Спасибо! Мы помогаем компаниям сокращать сроки и риски по доставке грузов из Китая. У нас есть точечное предложение по вашему направлению. Давайте я оперативно подготовлю для вас предварительный расчет?"
        else:
            return "Спасибо! Для расчета нужен город отправки и назначения. Куда вам удобнее получить результат?"
    
    # Проверяем на короткие ответы
    if text_lower in ['нет', 'не', 'неа']:
        if turn <= 3:
            return "Понимаю. Может быть, у вас есть коллеги, которые занимаются логистикой? Или подскажите, кто принимает решения по перевозкам?"
        else:
            return "Понимаю, спасибо за ваше время. Всего доброго!"
    
    # Общий fallback в зависимости от хода
    if turn <= 2:
        return "Спасибо! Мы помогаем компаниям сокращать сроки и риски по доставке грузов из Китая. У нас есть точечное предложение по вашему направлению. Давайте я оперативно подготовлю для вас предварительный расчет?"
    elif turn <= 4:
        return "Для расчета нужен город отправки и назначения. Куда вам удобнее получить результат?"
    else:
        return "Понимаю, спасибо за ваше время. Всего доброго!"

@app.get("/api/sessions")
async def get_active_sessions():
    """Получает информацию об активных сессиях диалога"""
    sessions_info = []
    
    for call_id, session in dialog_system.conversation_sessions.items():
        sessions_info.append({
            "call_id": call_id,
            "turn_count": session["turn_count"],
            "created_at": datetime.fromtimestamp(session["created_at"]).isoformat(),
            "last_activity": datetime.fromtimestamp(session["last_activity"]).isoformat(),
            "history_length": len(session["history"])
        })
    
    return {
        "active_sessions": len(sessions_info),
        "sessions": sessions_info
    }

@app.delete("/api/sessions/{call_id}")
async def cleanup_session(call_id: str):
    """Очищает конкретную сессию диалога"""
    try:
        dialog_system.cleanup_session(call_id)
        return {"success": True, "message": f"Session {call_id} cleaned up"}
    except Exception as e:
        logger.error(f"❌ Ошибка очистки сессии {call_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup session")

@app.post("/api/cleanup")
async def cleanup_old_sessions():
    """Очищает старые сессии диалога"""
    try:
        dialog_system.cleanup_old_sessions()
        return {"success": True, "message": "Old sessions cleaned up"}
    except Exception as e:
        logger.error(f"❌ Ошибка очистки старых сессий: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup old sessions")

@app.post("/api/test/dialog")
async def test_dialog_system(request: Request):
    """
    Тестовый endpoint для проверки системы диалога
    """
    try:
        body = await request.json()
        test_text = body.get("text", "Привет, как дела?")
        test_call_id = body.get("call_id", "test_call_123")
        
        # Создаем тестовое событие
        test_event = {
            "event": "asr_text",
            "call_id": test_call_id,
            "text": test_text,
            "custom_data": {
                "test": True,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Обрабатываем через систему диалога
        result = process_webhook_event(test_event)
        
        return {
            "test": True,
            "input": test_text,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования: {e}")
        raise HTTPException(status_code=500, detail="Test failed")

@app.post("/api/voxi/events")
async def handle_voxi_events(request: Request):
    """
    Обработчик событий от Voximplant
    """
    try:
        body = await request.json()
        logger.info(f"📥 Получено событие от Voximplant: {body}")
        
        # Проверяем заголовки для простого режима
        simple_mode = request.headers.get("X-Simple-Mode") == "true"
        
        # Обработка данных о завершенном звонке
        if body.get('type') == 'call_data':
            call_data = body.get('callData')
            logger.info(f"📊 Данные звонка: {call_data}")
            
            # Здесь можно сохранить в базу данных
            return {
                "success": True,
                "message": "Call data received"
            }
        
        # Обработка простых текстовых запросов
        elif 'text' in body:
            text = body.get('text', '')
            turn = body.get('turn', 1)
            
            logger.info(f"🤖 AI запрос: '{text}' (ход {turn})")
            
            if simple_mode:
                # Простой режим - используем базовые ответы
                response = await generate_simple_response(text, turn)
            else:
                # Полный режим - используем GPT
                response = await generate_gpt_response(text, turn)
            
            logger.info(f"🤖 AI ответ: '{response}'")
            
            return {
                "success": True,
                "response": {
                    "text": response,
                    "turn": turn
                }
            }
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки события: {e}")
        return {"error": "Internal server error"}, 500

@app.post("/api/call")
async def make_call(request: Request):
    """
    Запускает звонок через Voximplant
    """
    try:
        body = await request.json()
        phone_number = body.get("phone_number")
        
        if not phone_number:
            raise HTTPException(status_code=400, detail="Phone number is required")
        
        logger.info(f"📞 Запуск звонка на номер: {phone_number}")
        
        # Запускаем звонок через Voximplant
        result = voxi_service.start_call(phone_number)
        
        if result.get("success"):
            logger.info(f"✅ Звонок успешно запущен: {result}")
            return {
                "success": True,
                "message": "Звонок успешно запущен",
                "call_id": result.get("call_id"),
                "phone_number": phone_number
            }
        else:
            logger.error(f"❌ Ошибка запуска звонка: {result}")
            return {
                "success": False,
                "error": result.get("error", "Неизвестная ошибка")
            }
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске звонка: {e}")
        raise HTTPException(status_code=500, detail=f"Call failed: {str(e)}")

if __name__ == "__main__":
    # Запускаем сервер
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )

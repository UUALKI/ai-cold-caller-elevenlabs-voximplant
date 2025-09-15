#!/usr/bin/env python3
"""
Живая система диалога в реальном времени
Поддержка SaluteSpeech API + GPT для естественного общения
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from config import OPENAI_API_KEY, ELEVENLABS_API_KEY, OPENROUTER_API_KEY

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveDialogSystem:
    """
    Живая система диалога в реальном времени
    Обрабатывает потоковые запросы от Voximplant с SaluteSpeech API
    """
    
    def __init__(self):
        self.openai_client = None
        self.conversation_sessions = {}
        self.max_turns = 50
        self.max_session_time = 3600  # 1 час
        
        # Инициализация OpenRouter
        if OPENROUTER_API_KEY:
            try:
                self.openai_client = {
                    'api_key': OPENROUTER_API_KEY,
                    'base_url': "https://openrouter.ai/api/v1"
                }
                logger.info("✅ OpenRouter клиент инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации OpenRouter: {e}")
        else:
            logger.warning("⚠️ OPENROUTER_API_KEY не настроен")
    
    def process_asr_text(self, call_id: str, text: str, custom_data: Dict = None) -> Dict:
        """
        Обрабатывает распознанный текст от SaluteSpeech API
        """
        try:
            logger.info(f"🎤 Обработка ASR текста: '{text}' для звонка {call_id}")
            
            # Получаем или создаем сессию диалога
            session = self._get_or_create_session(call_id)
            
            # Добавляем сообщение пользователя в историю
            session['history'].append({
                'role': 'user',
                'content': text,
                'timestamp': datetime.now().isoformat()
            })
            
            # Проверяем лимиты
            if self._check_limits(session):
                return self._create_response("Спасибо за разговор! Я подготовлю коммерческое предложение и перезвоню в удобное время.", success=True)
            
            # Генерируем ответ через GPT
            ai_response = self._generate_ai_response(session, text, custom_data)
            
            if ai_response:
                # Добавляем ответ AI в историю
                session['history'].append({
                    'role': 'assistant', 
                    'content': ai_response,
                    'timestamp': datetime.now().isoformat()
                })
                
                session['turn_count'] += 1
                session['last_activity'] = time.time()
                
                logger.info(f"🤖 AI ответ: '{ai_response}'")
                return self._create_response(ai_response, success=True)
            else:
                logger.error("❌ Не удалось сгенерировать ответ AI")
                return self._create_response("", success=False, error="GPT не смог сгенерировать ответ")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки ASR текста: {e}")
            return self._create_response("", success=False, error=str(e))
    
    def _get_or_create_session(self, call_id: str) -> Dict:
        """Получает или создает сессию диалога"""
        if call_id not in self.conversation_sessions:
            self.conversation_sessions[call_id] = {
                'call_id': call_id,
                'history': [],
                'turn_count': 0,
                'created_at': time.time(),
                'last_activity': time.time(),
                'context': {
                    'company': 'ТранстИрекс',
                    'service': 'Международные перевозки из Китая в Россию',
                    'goal': 'Получить контакт ответственного лица для коммерческого предложения'
                }
            }
            logger.info(f"🆕 Создана новая сессия диалога: {call_id}")
        
        return self.conversation_sessions[call_id]
    
    def _check_limits(self, session: Dict) -> bool:
        """Проверяет лимиты диалога"""
        # Лимит ходов
        if session['turn_count'] >= self.max_turns:
            logger.info(f"🛑 Достигнут лимит ходов для звонка {session['call_id']}")
            return True
        
        # Лимит времени
        if time.time() - session['created_at'] > self.max_session_time:
            logger.info(f"🛑 Достигнут лимит времени для звонка {session['call_id']}")
            return True
        
        return False
    
    def _generate_ai_response(self, session: Dict, user_text: str, custom_data: Dict = None) -> Optional[str]:
        """Генерирует ответ через GPT с анализом эмоций и контекста"""
        try:
            # Используем глобальный клиент
            if not self.openai_client:
                logger.error("❌ OpenAI клиент не инициализирован")
                return None
            
            # Анализируем эмоции и контекст
            emotion_analysis = self._analyze_emotion(user_text)
            context_info = self._build_dialog_context(session, user_text, custom_data)
            
            # Системный промпт для живого диалога с анализом эмоций
            system_prompt = """Ты - Алёна, специалист по международным перевозкам компании ТранстИрекс. 
Твоя задача - вести естественный, живой диалог с клиентом и получить контакт ответственного лица для отправки коммерческого предложения.

ПРАВИЛА ДИАЛОГА:
1. Будь естественной и дружелюбной, как живой человек
2. Адаптируйся под эмоциональное состояние клиента
3. Задавай уточняющие вопросы на основе его ответов
4. Собирай информацию о потребностях клиента
5. В конце попроси контакт ответственного лица
6. Отвечай кратко и по делу (максимум 2-3 предложения)
7. НИКОГДА не используй скриптовые фразы
8. Если клиент негативно настроен - прояви понимание и предложи альтернативы
9. Если клиент заинтересован - развивай тему и собирай детали
10. Всегда подтверждай понимание: "Понятно, значит..." или "Правильно ли я понимаю..."
11. Используй естественные переходы и связки между фразами
12. Реагируй на эмоции клиента: если он взволнован - успокой, если сомневается - убеди

Цель: Получить имя, должность и контактные данные ответственного лица.

Анализ эмоций клиента: {emotion_analysis}
Контекст диалога: {context_info}"""

            # Формируем сообщения для GPT
            messages = [{"role": "system", "content": system_prompt}]
            
            # Добавляем историю диалога (последние 10 сообщений)
            recent_history = session['history'][-10:] if len(session['history']) > 10 else session['history']
            for msg in recent_history:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # Добавляем текущее сообщение пользователя
            messages.append({"role": "user", "content": user_text})
            
            logger.info(f"🧠 Отправка запроса к GPT (сообщений: {len(messages)}, эмоция: {emotion_analysis})")
            
            # Отправляем запрос к GPT через OpenRouter (новая версия API)
            from openai import OpenAI
            
            # Создаем клиент OpenRouter с правильными заголовками
            client = OpenAI(
                api_key=self.openai_client['api_key'],
                base_url=self.openai_client['base_url'],
                default_headers={
                    "HTTP-Referer": "https://ai-call-prototype.com",
                    "X-Title": "AI Call Prototype",
                    "Authorization": f"Bearer {self.openai_client['api_key']}"
                }
            )
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Используем доступную модель
                messages=messages,
                max_tokens=150,  # Уменьшаем для более кратких ответов
                temperature=0.9,  # Увеличиваем креативность
                presence_penalty=0.3,
                frequency_penalty=0.3
            )
            ai_response = response.choices[0].message.content.strip()
            
            if ai_response and len(ai_response.strip()) > 0:
                return ai_response
            else:
                logger.warning("⚠️ GPT вернул пустой ответ")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации ответа GPT: {e}")
            return None
    
    def _analyze_emotion(self, text: str) -> str:
        """Анализирует эмоциональное состояние клиента"""
        text_lower = text.lower()
        
        # Позитивные эмоции
        positive_words = ['да', 'конечно', 'интересно', 'хорошо', 'отлично', 'давайте', 'расскажите', 'подробнее', 'спасибо', 'понятно']
        # Негативные эмоции
        negative_words = ['нет', 'неинтересно', 'не нужно', 'не хочу', 'занят', 'неудобно', 'не подходит', 'дорого', 'не подходит']
        # Нейтральные/вопросительные
        neutral_words = ['что', 'как', 'когда', 'где', 'почему', 'сколько', 'можно', 'возможно', 'а', 'но']
        # Эмоциональные слова
        emotional_words = ['волнуюсь', 'беспокоюсь', 'сомневаюсь', 'не уверен', 'думаю', 'решаю', 'обдумываю']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        neutral_count = sum(1 for word in neutral_words if word in text_lower)
        emotional_count = sum(1 for word in emotional_words if word in text_lower)
        
        # Анализируем длину ответа и пунктуацию
        if len(text) < 5:
            emotion = "краткий/неопределенный"
        elif len(text) > 50:
            emotion = "подробный/заинтересованный"
        elif '!' in text:
            emotion = "эмоциональный/активный"
        elif '?' in text:
            emotion = "вопрошающий/сомневающийся"
        elif positive_count > negative_count:
            emotion = "позитивный/заинтересованный"
        elif negative_count > positive_count:
            emotion = "негативный/отрицающий"
        elif emotional_count > 0:
            emotion = "эмоциональный/сомневающийся"
        elif neutral_count > 0:
            emotion = "нейтральный/вопрошающий"
        else:
            emotion = "нейтральный"
        
        logger.info(f"🎭 Анализ эмоций: '{text}' -> {emotion}")
        return emotion
    
    def _build_dialog_context(self, session: Dict, user_text: str, custom_data: Dict = None) -> Dict:
        """Строит контекст диалога"""
        context = {
            'company': session['context']['company'],
            'service': session['context']['service'],
            'goal': session['context']['goal'],
            'turn_count': session['turn_count'],
            'session_duration': time.time() - session['created_at'],
            'conversation_flow': custom_data.get('conversation_flow', 'greeting') if custom_data else 'greeting',
            'user_engagement': custom_data.get('user_engagement', 0) if custom_data else 0,
            'confidence': custom_data.get('confidence', 0) if custom_data else 0
        }
        
        if custom_data:
            context.update(custom_data)
        
        # Добавляем информацию о последних ответах клиента
        if len(session['history']) > 0:
            recent_user_messages = [msg['content'] for msg in session['history'] if msg['role'] == 'user'][-3:]
            context['recent_user_responses'] = recent_user_messages
        
        # Определяем этап диалога
        if session['turn_count'] == 0:
            context['stage'] = 'greeting'
        elif session['turn_count'] <= 2:
            context['stage'] = 'needs_analysis'
        elif session['turn_count'] <= 4:
            context['stage'] = 'service_details'
        elif session['turn_count'] <= 6:
            context['stage'] = 'contact_request'
        else:
            context['stage'] = 'closing'
        
        logger.info(f"📋 Контекст диалога: этап={context['stage']}, вовлеченность={context['user_engagement']}, confidence={context['confidence']}")
        
        return context
    

    
    def _create_response(self, response_text: str, success: bool = True, error: str = None) -> Dict:
        """Создает стандартный ответ"""
        return {
            "success": success,
            "response": response_text,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    
    def cleanup_session(self, call_id: str) -> None:
        """Очищает сессию диалога"""
        if call_id in self.conversation_sessions:
            session = self.conversation_sessions.pop(call_id)
            logger.info(f"🧹 Очищена сессия диалога: {call_id} (ходов: {session['turn_count']})")
    
    def cleanup_old_sessions(self) -> None:
        """Очищает старые сессии"""
        current_time = time.time()
        expired_sessions = []
        
        for call_id, session in self.conversation_sessions.items():
            if current_time - session['last_activity'] > self.max_session_time:
                expired_sessions.append(call_id)
        
        for call_id in expired_sessions:
            self.cleanup_session(call_id)
        
        if expired_sessions:
            logger.info(f"🧹 Очищено {len(expired_sessions)} старых сессий")

# Глобальный экземпляр системы диалога
dialog_system = LiveDialogSystem()

def process_webhook_event(event_data: Dict) -> Dict:
    """
    Обрабатывает webhook события от Voximplant
    """
    try:
        event_type = event_data.get('event')
        call_id = event_data.get('call_id', 'unknown')
        
        logger.info(f"📥 Получено событие: {event_type} для звонка {call_id}")
        
        if event_type == 'asr_text':
            # Обработка распознанного текста от SaluteSpeech API
            text = event_data.get('text', '')
            custom_data = event_data.get('custom_data', {})
            
            if text:
                return dialog_system.process_asr_text(call_id, text, custom_data)
            else:
                logger.warning("⚠️ Получен пустой текст ASR")
                return dialog_system._create_response("", success=False, error="Пустой текст ASR")
        
        elif event_type == 'call_ended':
            # Завершение звонка
            dialog_system.cleanup_session(call_id)
            return dialog_system._create_response("Звонок завершен", success=True)
        
        else:
            logger.warning(f"⚠️ Неизвестный тип события: {event_type}")
            return dialog_system._create_response("Неизвестное событие", success=False, error="Unknown event type")
    
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook события: {e}")
        return dialog_system._create_response("Ошибка обработки", success=False, error=str(e))

# Периодическая очистка старых сессий
def cleanup_old_sessions_task():
    """Задача для периодической очистки старых сессий"""
    dialog_system.cleanup_old_sessions()

#!/usr/bin/env python3
"""
Продвинутая система диалога для AI-агента ТРАНСТИРЕКС
Обработка возражений, персонализация, аналитика
"""

import json
import logging
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import openai
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENROUTER_API_KEY

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObjectionHandler:
    """Обработчик возражений с продвинутыми стратегиями"""
    
    def __init__(self):
        self.objection_patterns = {
            'not_interested': [
                r'не интересует', r'не интересно', r'не нужно', r'не подходит',
                r'не актуально', r'не требуется', r'не ищем'
            ],
            'has_carrier': [
                r'есть перевозчик', r'работаем с', r'уже есть', r'сотрудничаем',
                r'поставщик услуг', r'партнер', r'договор'
            ],
            'send_email': [
                r'отправьте на почту', r'напишите email', r'на общую почту',
                r'info@', r'общий@', r'отправьте предложение'
            ],
            'busy': [
                r'занят', r'неудобно', r'позже', r'не сейчас', r'не время',
                r'сейчас не могу', r'перезвоните'
            ],
            'expensive': [
                r'дорого', r'стоимость', r'цена', r'бюджет', r'не по карману'
            ],
            'secretary': [
                r'секретарь', r'помощник', r'ассистент', r'приемная',
                r'общий отдел', r'не принимаю решения'
            ]
        }
        
        self.response_strategies = {
            'not_interested': [
                "Понимаю! Но у нас есть специальное предложение именно для вашей отрасли. Давайте я быстро расскажу, как мы помогаем компаниям экономить до 30% на логистике?",
                "Спасибо за честность! Может быть, стоит хотя бы узнать о наших условиях? Мы работаем с ведущими компаниями и гарантируем качество."
            ],
            'has_carrier': [
                "Отлично! Значит, вы понимаете важность логистики. А что если я покажу, как можно сократить расходы на 20-30% при том же качестве?",
                "Понимаю! Но у нас есть уникальные условия для новых клиентов. Давайте сравним? Это займет всего минуту."
            ],
            'send_email': [
                "Конечно, я отправлю на общую почту. Но чтобы наше предложение не затерялось среди сотни других, подскажите, пожалуйста, как зовут вашего логиста? Тогда я укажу его имя в теме письма.",
                "Обязательно отправлю! А для персонального предложения подскажите, кто у вас отвечает за логистику? Это стандартная практика."
            ],
            'busy': [
                "Понимаю, сейчас неудобно. Давайте я перезвоню в удобное время? Когда вам будет удобно?",
                "Конечно! Я перезвоню позже. Подскажите, пожалуйста, как зовут вашего логиста, чтобы я мог обратиться к нему лично?"
            ],
            'expensive': [
                "Понимаю ваши опасения! Но у нас есть гибкие тарифы и специальные условия для новых клиентов. Давайте я покажу конкретные цифры?",
                "Согласен, цена важна! Но мы предлагаем не просто перевозку, а комплексное решение, которое окупается за 2-3 месяца."
            ],
            'secretary': [
                "Понимаю! Тогда подскажите, пожалуйста, как зовут вашего руководителя отдела логистики? Я подготовлю для него персональное предложение.",
                "Спасибо! А кто у вас принимает решения по логистике? Мне нужно согласовать с ним детали по конкретному вопросу."
            ]
        }
    
    def analyze_objection(self, text: str) -> Dict:
        """Анализирует возражения и возвращает стратегию ответа"""
        text_lower = text.lower()
        detected_objections = []
        
        for objection_type, patterns in self.objection_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected_objections.append(objection_type)
                    break
        
        if detected_objections:
            primary_objection = detected_objections[0]
            responses = self.response_strategies.get(primary_objection, [])
            selected_response = responses[0] if responses else "Понимаю! Давайте я подготовлю для вас персональное предложение."
            
            return {
                'objection_type': primary_objection,
                'all_objections': detected_objections,
                'response': selected_response,
                'confidence': 0.9
            }
        
        return {
            'objection_type': None,
            'all_objections': [],
            'response': None,
            'confidence': 0.0
        }

class ContactExtractor:
    """Извлекает контактную информацию из текста"""
    
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+7|8)[\s\-\(]?(\d{3})[\s\-\)]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})'
        self.name_patterns = [
            r'зовут\s+([А-Я][а-я]+)',
            r'меня\s+([А-Я][а-я]+)',
            r'это\s+([А-Я][а-я]+)',
            r'([А-Я][а-я]+)\s+отвечает'
        ]
    
    def extract_contacts(self, text: str) -> Dict:
        """Извлекает контакты из текста"""
        result = {
            'emails': [],
            'phones': [],
            'names': [],
            'has_decision_maker': False
        }
        
        # Поиск email
        emails = re.findall(self.email_pattern, text)
        result['emails'] = emails
        
        # Поиск телефонов
        phones = re.findall(self.phone_pattern, text)
        result['phones'] = [''.join(phone) for phone in phones]
        
        # Поиск имен
        for pattern in self.name_patterns:
            names = re.findall(pattern, text)
            result['names'].extend(names)
        
        # Определение ЛПР
        decision_maker_indicators = [
            'руководитель', 'директор', 'начальник', 'менеджер',
            'отвечает за', 'принимаю решения', 'логист'
        ]
        
        text_lower = text.lower()
        for indicator in decision_maker_indicators:
            if indicator in text_lower:
                result['has_decision_maker'] = True
                break
        
        return result

class AdvancedDialogSystem:
    """Продвинутая система диалога для AI-агента"""
    
    def __init__(self):
        self.openai_client = None
        self.conversation_sessions = {}
        self.objection_handler = ObjectionHandler()
        self.contact_extractor = ContactExtractor()
        
        # Инициализация OpenAI
        if OPENAI_API_KEY or OPENROUTER_API_KEY:
            try:
                # Для обычных запросов используем OpenRouter (обходит блокировку)
                api_key = OPENROUTER_API_KEY if OPENROUTER_API_KEY else OPENAI_API_KEY
                
                # Если используем OpenRouter, устанавливаем правильный base_url
                if api_key.startswith("sk-or-"):
                    self.openai_client = AsyncOpenAI(
                        api_key=api_key,
                        base_url="https://openrouter.ai/api/v1"
                    )
                else:
                    self.openai_client = AsyncOpenAI(api_key=api_key)
                
                logger.info("✅ OpenAI клиент инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации OpenAI: {e}")
    
    def _get_or_create_session(self, call_id: str) -> Dict:
        """Получает или создает сессию диалога"""
        if call_id not in self.conversation_sessions:
            self.conversation_sessions[call_id] = {
                'call_id': call_id,
                'history': [],
                'turn_count': 0,
                'created_at': time.time(),
                'last_activity': time.time(),
                'stage': 'greeting',
                'objections_handled': [],
                'contacts_found': [],
                'user_engagement': 0,
                'conversation_flow': []
            }
        return self.conversation_sessions[call_id]
    
    def _build_system_prompt(self, context: Dict) -> str:
        """Строит системный промпт для GPT"""
        base_prompt = """Ты — настойчивый и дружелюбный AI-менеджер международной логистической компании TRANSTIREX. 
Твоя главная задача — совершить холодный звонок и получить либо запрос на просчет перевозки из Китая в Россию, 
либо прямой контакт лица, принимающего решения по логистике.

КЛЮЧЕВЫЕ ПРИНЦИПЫ:
1. Будь естественным, дружелюбным, но настойчивым
2. Обрабатывай возражения мягко, но уверенно
3. Цель - получить контакт ЛПР или запрос на расчет
4. Не сжигай контакты, будь вежлив при отказах
5. Используй разговорный стиль, избегай скриптовости
6. ОТВЕЧАЙ КРАТКО, МАКСИМУМ 1-2 ПРЕДЛОЖЕНИЯ

СТРАТЕГИЯ ДИАЛОГА:
1. Приветствие и представление (10-15 сек)
2. Работа с возражениями секретаря (30-60 сек)
3. Презентация ценности и запрос (30 сек)
4. Завершение и фиксация результата (15-30 сек)

ТЕКУЩАЯ СТАДИЯ: {stage}
ОБРАБОТАННЫЕ ВОЗРАЖЕНИЯ: {objections}
НАЙДЕННЫЕ КОНТАКТЫ: {contacts}"""

        return base_prompt.format(
            stage=context.get('stage', 'greeting'),
            objections=', '.join(context.get('objections_handled', [])),
            contacts=', '.join(context.get('contacts_found', []))
        )
    
    async def process_user_input(self, call_id: str, text: str, confidence: float = 1.0) -> Dict:
        """Обрабатывает ввод пользователя и генерирует ответ"""
        try:
            logger.info(f"🎤 Обработка ввода: '{text}' для звонка {call_id}")
            
            # Получаем сессию
            session = self._get_or_create_session(call_id)
            session['last_activity'] = time.time()
            
            # Анализируем возражения
            objection_analysis = self.objection_handler.analyze_objection(text)
            if objection_analysis['objection_type']:
                session['objections_handled'].append(objection_analysis['objection_type'])
            
            # Извлекаем контакты
            contacts = self.contact_extractor.extract_contacts(text)
            if contacts['emails'] or contacts['phones'] or contacts['names']:
                session['contacts_found'].extend(contacts['emails'] + contacts['phones'] + contacts['names'])
            
            # Определяем стадию диалога
            self._update_conversation_stage(session, text, objection_analysis)
            
            # Добавляем в историю
            session['history'].append({
                'role': 'user',
                'content': text,
                'timestamp': datetime.now().isoformat(),
                'objections': objection_analysis['all_objections'],
                'contacts': contacts
            })
            
            # Генерируем ответ
            ai_response = await self._generate_ai_response(session, text, objection_analysis)
            
            if ai_response:
                session['history'].append({
                    'role': 'assistant',
                    'content': ai_response,
                    'timestamp': datetime.now().isoformat()
                })
                
                session['turn_count'] += 1
                session['conversation_flow'].append({
                    'turn': session['turn_count'],
                    'stage': session['stage'],
                    'user_input': text,
                    'ai_response': ai_response,
                    'objections': objection_analysis['all_objections'],
                    'contacts_found': contacts
                })
                
                logger.info(f"🤖 AI ответ: '{ai_response}'")
                return self._create_response(ai_response, success=True, session=session)
            else:
                logger.error("❌ Не удалось сгенерировать ответ AI")
                return self._create_response("", success=False, error="GPT не смог сгенерировать ответ")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки ввода: {e}")
            return self._create_response("", success=False, error=str(e))
    
    def _update_conversation_stage(self, session: Dict, text: str, objection_analysis: Dict):
        """Обновляет стадию диалога"""
        current_stage = session['stage']
        
        # Логика перехода между стадиями
        if current_stage == 'greeting':
            if objection_analysis['objection_type']:
                session['stage'] = 'objection_handling'
            else:
                session['stage'] = 'value_presentation'
        
        elif current_stage == 'objection_handling':
            if objection_analysis['objection_type']:
                # Продолжаем обработку возражений
                pass
            else:
                session['stage'] = 'value_presentation'
        
        elif current_stage == 'value_presentation':
            # Проверяем, получили ли мы контакты или запрос на расчет
            contacts = self.contact_extractor.extract_contacts(text)
            if contacts['emails'] or contacts['phones'] or 'расчет' in text.lower():
                session['stage'] = 'closing'
        
        elif current_stage == 'closing':
            # Остаемся в стадии закрытия
            pass
    
    async def _generate_ai_response(self, session: Dict, user_text: str, objection_analysis: Dict) -> str:
        """Генерирует ответ через GPT"""
        if not self.openai_client:
            # Fallback ответы
            return self._get_fallback_response(session['stage'], objection_analysis)
        
        try:
            # Строим контекст
            context = {
                'stage': session['stage'],
                'objections_handled': session['objections_handled'],
                'contacts_found': session['contacts_found'],
                'turn_count': session['turn_count']
            }
            
            system_prompt = self._build_system_prompt(context)
            
            # Формируем сообщения для GPT
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Добавляем последние 5 сообщений из истории
            recent_history = session['history'][-5:] if len(session['history']) > 5 else session['history']
            for msg in recent_history:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # Добавляем текущее сообщение пользователя
            messages.append({"role": "user", "content": user_text})
            
            # Если есть возражение, добавляем контекст
            if objection_analysis['objection_type']:
                messages.append({
                    "role": "system", 
                    "content": f"Пользователь выразил возражение типа: {objection_analysis['objection_type']}. Используй соответствующую стратегию ответа."
                })
            
            # Генерируем ответ
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации ответа GPT: {e}")
            return self._get_fallback_response(session['stage'], objection_analysis)
    
    def _get_fallback_response(self, stage: str, objection_analysis: Dict) -> str:
        """Возвращает fallback ответы"""
        if objection_analysis['objection_type'] and objection_analysis['response']:
            return objection_analysis['response']
        
        fallback_responses = {
            'greeting': [
                'Добрый день! Меня зовут Мария, я специалист по международным перевозкам компании TRANSTIREX. Подскажите, с кем я могу обсудить вопросы логистики из Китая в Россию?',
                'Здравствуйте! Мария из TRANSTIREX. Кто у вас отвечает за логистику из Китая?'
            ],
            'objection_handling': [
                'Понимаю! Речь идет не о массовой рассылке, а об оперативном согласовании деталей по конкретным поставкам. Подскажите, пожалуйста, как зовут вашего руководителя отдела логистики?',
                'Спасибо! Чтобы не отвлекать руководителя лишний раз, подскажите, как зовут вашего логиста и на какую почту ему направить персональное предложение?'
            ],
            'value_presentation': [
                'Мы помогаем таким компаниям, как ваша, сокращать сроки и риски по доставке грузов из Китая. У нас есть точечное предложение по вашему направлению. Давайте я оперативно подготовлю для вас предварительный расчет?',
                'У нас есть специальное предложение по вашему направлению. Для расчета нужен город отправки и назначения. Куда вам удобнее получить результат?'
            ],
            'closing': [
                'Отлично! Куда вам удобнее получить расчет: в WhatsApp или на email?',
                'Спасибо за информацию! Я направлю персональное предложение. Хорошего дня!'
            ]
        }
        
        responses = fallback_responses.get(stage, fallback_responses['greeting'])
        return responses[0]
    
    def _create_response(self, text: str, success: bool = True, error: str = None, session: Dict = None) -> Dict:
        """Создает структурированный ответ"""
        response = {
            'success': success,
            'response': {
                'text': text,
                'stage': session['stage'] if session else 'unknown',
                'turn_count': session['turn_count'] if session else 0,
                'objections_handled': session['objections_handled'] if session else [],
                'contacts_found': session['contacts_found'] if session else []
            }
        }
        
        if error:
            response['error'] = error
        
        return response
    
    def get_session_analytics(self, call_id: str) -> Dict:
        """Возвращает аналитику сессии"""
        if call_id not in self.conversation_sessions:
            return {}
        
        session = self.conversation_sessions[call_id]
        
        return {
            'call_id': call_id,
            'duration': time.time() - session['created_at'],
            'turn_count': session['turn_count'],
            'stage': session['stage'],
            'objections_handled': session['objections_handled'],
            'contacts_found': session['contacts_found'],
            'user_engagement': session['user_engagement'],
            'conversation_flow': session['conversation_flow']
        }
    
    def cleanup_session(self, call_id: str):
        """Очищает сессию диалога"""
        if call_id in self.conversation_sessions:
            del self.conversation_sessions[call_id]
            logger.info(f"🧹 Сессия {call_id} очищена")

# Глобальный экземпляр системы диалога
advanced_dialog_system = AdvancedDialogSystem()

async def process_webhook_event_advanced(event_data: Dict) -> Dict:
    """Обрабатывает webhook события для продвинутой системы"""
    try:
        event_type = event_data.get('event')
        call_id = event_data.get('call_id', 'unknown')
        
        if event_type == 'asr_text':
            text = event_data.get('text', '')
            confidence = event_data.get('custom_data', {}).get('confidence', 1.0)
            
            # Обрабатываем через продвинутую систему
            result = advanced_dialog_system.process_user_input(call_id, text, confidence)
            return result
        
        elif event_type == 'call_ended':
            # Получаем аналитику и очищаем сессию
            analytics = advanced_dialog_system.get_session_analytics(call_id)
            advanced_dialog_system.cleanup_session(call_id)
            
            return {
                'success': True,
                'analytics': analytics,
                'message': 'Call session ended and cleaned up'
            }
        
        else:
            return {
                'success': False,
                'error': f'Unknown event type: {event_type}'
            }
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook события: {e}")
        return {
            'success': False,
            'error': str(e)
        }

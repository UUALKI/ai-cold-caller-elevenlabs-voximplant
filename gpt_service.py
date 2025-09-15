import requests
import json
from typing import Dict, List, Optional
from knowledge.loader import get_or_build_index
from config import OPENROUTER_API_KEY, KNOWLEDGE_DIR
import os
from typing import Tuple
from pypdf import PdfReader

class GPTService:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        # Используем доступную модель через OpenRouter
        self.model = "anthropic/claude-3-haiku"  # Используем модель, доступную в регионе
        # Простая заглушка RAG: читаем короткие txt/резюме если есть
        self.knowledge_snippets = self._load_local_snippets()
        
        # Системный промпт для агента (тонкая настройка под TRANSTIREX)
        self.system_prompt = """Ты — настойчивый и дружелюбный AI-менеджер международной логистической компании TRANSTIREX. 
Твоя главная задача — совершить холодный звонок и, несмотря на вероятные возражения ("не интересует", "есть перевозчик", "отправьте коммерческое предложение на общую почту"), получить либо запрос на просчёт перевозки из Китая в Россию, либо прямой контакт (email или мобильный телефон) лица, принимающего решения (ЛПР) по логистике.

ВНИМАНИЕ: Ключевая сложность — тебя будет фильтровать секретарь или помощник. Их задача — не соединять с ЛПР и отфутболить на общую почту, что нам не подходит. Твоя цель в разговоре с ними — мягко, но настойчиво, минуя общие реквизиты, выяснить прямое имя и контакты ЛПР, аргументируя это необходимостью оперативно согласовать детали по конкретному вопросу.

Будь готов гибко парировать стандартные отписки, переводя разговор в конструктивное русло и оставляя инициативу у себя.

Стиль общения: энергичный, уверенный, но уважительный; кратко (2–3 предложения), без канцелярита. 
Специализация: международная логистика из Китая в Россию, таможенное оформление, мультимодальные перевозки.

Краткий план диалога (1.5–2.5 минуты):
1) Приветствие и представление (10–15 сек). Пример: «Добрый день! Меня зовут Алёна, я специалист по международным перевозкам компании TRANSTIREX. Подскажите, с кем я могу обсудить вопросы логистики из Китая в Россию?»
2) Работа с возражениями секретаря (30–60 сек):
   - Если просят инфо/общую почту: «Спасибо! Понимаю. Речь не о массовой рассылке, а об оперативном согласовании деталей по конкретным поставкам. Чтобы не отвлекать руководителя лишний раз, подскажите, пожалуйста, как зовут вашего руководителя логистики и на какую почту ему направить персональное предложение?»
   - Если упираются в общую почту: «На общую я продублирую, конечно. Но чтобы письмо не потерялось среди сотни других, важно указать в теме имя ответственного лица. Подскажите, как зовут вашего логиста?»
3) Короткая ценность и запрос (до 30 сек), когда получен контакт ЛПР или соединение: 
   Пример: «[Имя], здравствуйте! Мы помогаем таким компаниям, как ваша, сокращать сроки и риски при доставке из Китая. У меня есть точечное предложение под ваше направление. Давайте быстро подготовлю предварительный расчёт: нужен город отправки/назначения и тип груза.»
4) Завершение и фиксация результата (15–30 сек):
   - Цель 1 (идеально): получить данные для расчёта: «Отлично! Куда удобнее отправить расчёт — WhatsApp или email?»
   - Цель 2 (минимум): получить прямой контакт ЛПР: «Спасибо! Я направлю персональное предложение [Имя ЛПР] на его почту [email] и продублирую в мессенджер по номеру [номер]. Хорошего дня!»

Правила поведения:
- Отвечай кратко; задавай уточняющие вопросы (объёмы/частота, направления, тип груза, сроки, Инкотермс, текущие ставки).
- Отрабатывай возражения мягко и профессионально; сохраняй инициативу.
- Если собеседник не ЛПР — аккуратно и аргументированно спроси контакты ЛПР (ФИО, должность, email/телефон), согласуй удобное время связи.
- Всегда предлагай конкретный следующий шаг (просчёт/связь).
- Если категорический отказ — вежливо завершай, не сжигай контакт.

Всегда анализируй ответ клиента и указывай в скрытом служебном блоке:
- Настроение клиента (positive/neutral/negative)
- Уровень заинтересованности (high/medium/low)
- Следующее действие (continue/close/objection_handling)
"""

    def generate_response(self, conversation_history: List[Dict], client_message: str = None) -> Dict:
        """Генерирует ответ агента на основе истории диалога"""
        
        # Формируем сообщения для GPT
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Добавляем историю диалога
        for msg in conversation_history:
            if msg["role"] == "agent":
                messages.append({"role": "assistant", "content": msg["content"]})
            elif msg["role"] == "client":
                messages.append({"role": "user", "content": msg["content"]})
        
        # Подмешиваем RAG-контекст (если доступен)
        rag_context = self._retrieve_context(client_message or "")
        # Дополнительно — запрос по эмбеддинговому индексу, если он готов
        try:
            kb = get_or_build_index()
            rag_hits = kb.query(client_message or "логистика Китай Россия", top_k=3)
            if rag_hits:
                rag_context = (rag_context + "\n---\n" + "\n---\n".join(rag_hits)).strip()
        except Exception:
            pass
        if rag_context:
            messages.append({"role": "system", "content": f"Контекст компании TRANSTIREX:\n{rag_context}"})

        # Добавляем текущее сообщение клиента, если есть
        if client_message:
            messages.append({"role": "user", "content": client_message})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AI Call Prototype"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                agent_response = result["choices"][0]["message"]["content"]
                
                # Анализируем ответ для определения настроения и действий
                analysis = self._analyze_response(agent_response, client_message)
                
                return {
                    "response": agent_response,
                    "analysis": analysis
                }
            else:
                raise Exception(f"GPT API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Ошибка генерации ответа: {e}")
            return {
                "response": "Извините, произошла техническая ошибка. Давайте продолжим наш разговор.",
                "analysis": {
                    "mood": "neutral",
                    "engagement": "medium",
                    "action": "continue"
                }
            }
    
    def _analyze_response(self, agent_response: str, client_message: str = None) -> Dict:
        """Анализирует ответ агента и определяет следующие действия"""
        
        # Простой анализ на основе ключевых слов
        response_lower = agent_response.lower()
        
        # Определяем настроение
        mood = "neutral"
        if any(word in response_lower for word in ["отлично", "прекрасно", "замечательно", "рад"]):
            mood = "positive"
        elif any(word in response_lower for word in ["понимаю", "согласен", "конечно"]):
            mood = "positive"
        elif any(word in response_lower for word in ["извините", "жаль", "к сожалению"]):
            mood = "negative"
        
        # Определяем уровень вовлеченности
        engagement = "medium"
        if any(word in response_lower for word in ["вопрос", "расскажите", "как", "что"]):
            engagement = "high"
        elif any(word in response_lower for word in ["спасибо", "до свидания", "всего доброго"]):
            engagement = "low"
        
        # Определяем следующее действие
        action = "continue"
        if any(word in response_lower for word in ["до свидания", "всего доброго", "спасибо за время"]):
            action = "close"
        elif any(word in response_lower for word in ["понимаю ваши", "согласен", "но давайте"]):
            action = "objection_handling"
        
        return {
            "mood": mood,
            "engagement": engagement,
            "action": action
        }

    def _load_local_snippets(self) -> List[str]:
        snippets: List[str] = []
        try:
            # Берём короткие .txt в knowledge/ как быстрые подсказки
            if os.path.isdir(KNOWLEDGE_DIR):
                for name in os.listdir(KNOWLEDGE_DIR):
                    path = os.path.join(KNOWLEDGE_DIR, name)
                    lower = name.lower()
                    if lower.endswith('.txt') and os.path.getsize(path) < 200_000:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            snippets.append(f.read()[:4000])
                    elif lower.endswith('.pdf') and os.path.getsize(path) < 5_000_000:
                        try:
                            reader = PdfReader(path)
                            pages = []
                            for p in reader.pages[:10]:
                                pages.append((p.extract_text() or ''))
                            text = "\n".join(pages)
                            if text:
                                snippets.append(text[:4000])
                        except Exception:
                            pass
        except Exception:
            pass
        return snippets

    def _retrieve_context(self, query: str) -> str:
        # Простой эвристический отбор из snippets, пока без полноценного эмбеддингового поиска
        query_l = (query or '').lower()
        if not self.knowledge_snippets:
            return ""
        scored = []
        for s in self.knowledge_snippets:
            score = 0
            for kw in ["китай", "логист", "жд", "море", "авиа", "инкотермс", "срок", "ставк", "транстирекс", "trans tirex", "transtirex"]:
                if kw in s.lower():
                    score += 1
                if query_l and kw in query_l:
                    score += 1
            scored.append((score, s))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = [s for sc, s in scored[:2] if sc > 0]
        return "\n---\n".join(top)

# Глобальный экземпляр сервиса
gpt_service = GPTService()


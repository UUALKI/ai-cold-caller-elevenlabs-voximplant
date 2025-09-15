import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import os

from voice_service import voice_service
from gpt_service import gpt_service
from voximplant_service import voximplant_service

@dataclass
class CallSession:
    call_id: str
    phone_number: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: int = 0
    conversation_history: List[Dict] = None
    audio_file: Optional[str] = None
    analysis: Dict = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.analysis is None:
            self.analysis = {}

class CallManager:
    def __init__(self):
        self.active_calls: Dict[str, CallSession] = {}
        self.call_history: List[Dict] = []
        
    async def start_call(self, phone_number: str) -> Dict:
        """Запускает полный цикл звонка"""
        
        call_id = str(uuid.uuid4())
        call_session = CallSession(
            call_id=call_id,
            phone_number=phone_number,
            status="initiated",
            start_time=datetime.now()
        )
        
        self.active_calls[call_id] = call_session
        
        try:
            print(f"Начинаем звонок на номер: {phone_number}")
            
            # Проверяем, включен ли режим симуляции
            simulation_mode = os.getenv("SIMULATION_MODE", "false").lower() == "true"
            
            if simulation_mode:
                print("🔧 Режим симуляции включен - пропускаем Voximplant")
                # Симулируем успешный звонок
                call_session.status = "in_progress"
                call_session.analysis = {
                    "success": True,
                    "duration": 45,
                    "engagement": "medium",
                    "sentiment": "positive",
                    "result": "interested"
                }
                
                # Имитируем задержку звонка
                await asyncio.sleep(2)
                
                return {
                    "success": True,
                    "call_id": call_id,
                    "message": "Звонок симулирован успешно (режим тестирования)"
                }
            
            # 1. Реплика приветствия (синтез выполнит ElevenLabs на стороне Voximplant)
            greeting = "Здравствуйте! Меня зовут Дмитрий, звоню из компании ЛогистикПро. Извините за беспокойство, у вас есть минутка?"

            # 2. Инициируем звонок через Voximplant (без локального аудиофайла)
            try:
                call_result = voximplant_service.start_call(phone_number)
                print(f"Результат инициирования звонка: {call_result}")
                
                # Если Voximplant вернул ошибку, выбрасываем исключение
                if not call_result.get("success"):
                    raise Exception(f"Voximplant error: {call_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"Ошибка инициирования звонка: {e}")
                # Для реальных звонков не используем симуляцию
                raise Exception(f"Не удалось инициировать звонок: {str(e)}")
            
            # 3. Обновляем статус
            call_session.status = "in_progress"
            
            # 4. Добавляем приветствие в историю
            call_session.conversation_history.append({
                "role": "agent",
                "content": greeting,
                "timestamp": datetime.now().isoformat()
            })
            
            # 5. Симулируем диалог (в реальной системе здесь был бы WebSocket для получения ответов клиента)
            await self._simulate_conversation(call_session)
            
            # 6. Завершаем звонок
            call_session.status = "completed"
            call_session.end_time = datetime.now()
            call_session.duration = int((call_session.end_time - call_session.start_time).total_seconds())
            
            # 7. Анализируем результат
            call_session.analysis = self._analyze_call_result(call_session)
            
            # 8. Сохраняем в историю
            self.call_history.append(asdict(call_session))
            del self.active_calls[call_id]
            
            print(f"Звонок завершен успешно: {call_id}")
            
            return {
                "success": True,
                "call_id": call_id,
                "result": asdict(call_session)
            }
            
        except Exception as e:
            print(f"Ошибка в процессе звонка: {e}")
            call_session.status = "failed"
            call_session.end_time = datetime.now()
            call_session.analysis = {"error": str(e)}
            
            return {
                "success": False,
                "call_id": call_id,
                "error": str(e)
            }
    
    async def _simulate_conversation(self, call_session: CallSession):
        """Симулирует диалог с клиентом (для прототипа)"""
        
        # Симулируем несколько обменов репликами
        simulated_responses = [
            "Да, есть минутка. Что вы предлагаете?",
            "Интересно, расскажите подробнее о ваших услугах",
            "А какие у вас цены на доставку из Китая?",
            "Спасибо за информацию, я подумаю и перезвоню"
        ]
        
        for i, client_response in enumerate(simulated_responses):
            # Добавляем ответ клиента в историю
            call_session.conversation_history.append({
                "role": "client",
                "content": client_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Генерируем ответ агента через GPT
            gpt_result = gpt_service.generate_response(
                call_session.conversation_history,
                client_response
            )
            
            agent_response = gpt_result["response"]
            
            # Добавляем ответ агента в историю
            call_session.conversation_history.append({
                "role": "agent",
                "content": agent_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Синтезируем речь для ответа агента
            emotion = gpt_result["analysis"]["mood"]
            audio_path = voice_service.synthesize_speech(agent_response, "dmitriy", emotion)
            
            # Обновляем аудиофайл
            if audio_path:
                call_session.audio_file = audio_path
            
            # Небольшая пауза между репликами
            await asyncio.sleep(1)
            
            # Если это последний ответ клиента, завершаем
            if i == len(simulated_responses) - 1:
                break
    
    def _analyze_call_result(self, call_session: CallSession) -> Dict:
        """Анализирует результат звонка"""
        
        # Подсчитываем статистику
        agent_messages = [msg for msg in call_session.conversation_history if msg["role"] == "agent"]
        client_messages = [msg for msg in call_session.conversation_history if msg["role"] == "client"]
        
        # Определяем успешность на основе количества обменов
        success_rate = min(len(client_messages) / 4 * 100, 100)  # Максимум 4 обмена
        
        # Определяем вовлеченность
        engagement = "medium"
        if len(client_messages) >= 3:
            engagement = "high"
        elif len(client_messages) <= 1:
            engagement = "low"
        
        return {
            "success_rate": success_rate,
            "engagement": engagement,
            "total_exchanges": len(client_messages),
            "call_duration": call_session.duration,
            "summary": f"Звонок длился {call_session.duration} секунд. Клиент проявил {engagement} уровень заинтересованности. Успешность: {success_rate:.1f}%"
        }
    
    def get_call_history(self) -> List[Dict]:
        """Возвращает историю звонков"""
        return self.call_history
    
    def get_call_by_id(self, call_id: str) -> Optional[Dict]:
        """Возвращает информацию о конкретном звонке"""
        # Ищем в активных звонках
        if call_id in self.active_calls:
            return asdict(self.active_calls[call_id])
        
        # Ищем в истории
        for call in self.call_history:
            if call["call_id"] == call_id:
                return call
        
        return None

# Глобальный экземпляр менеджера
call_manager = CallManager()

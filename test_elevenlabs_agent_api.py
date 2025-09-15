#!/usr/bin/env python3
"""
Тест ElevenLabs Agent API - проверяем правильные endpoints
"""

import requests
import json

# Ваши данные
API_KEY = "sk_bccc3b4272958d60c4c6e7cc003460f7d2d6d0f8724159af"
AGENT_ID = "agent_8701k4554cs1e69arzeae6vva5qz"

def test_agent_endpoints():
    """Тестирует различные endpoints для Agent API"""
    
    headers = {
        'Content-Type': 'application/json',
        'xi-api-key': API_KEY
    }
    
    # Тест 1: Получение информации об агенте
    print("1. Тестируем получение информации об агенте...")
    
    # Попробуем разные варианты URL
    urls_to_test = [
        f"https://api.elevenlabs.io/v1/agent/{AGENT_ID}",
        f"https://api.elevenlabs.io/v1/agents/{AGENT_ID}",
        f"https://api.elevenlabs.io/v1/agent/{AGENT_ID}/info",
        f"https://api.elevenlabs.io/v1/agents/{AGENT_ID}/info"
    ]
    
    for url in urls_to_test:
        try:
            print(f"   Пробуем: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   Статус: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Успешно! Ответ: {response.json()}")
                return url
            else:
                print(f"   ❌ Ошибка: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
    
    return None

def test_conversation_endpoint():
    """Тестирует endpoint для диалога"""
    print("\n2. Тестируем endpoint для диалога...")
    
    headers = {
        'Content-Type': 'application/json',
        'xi-api-key': API_KEY
    }
    
    # Попробуем разные варианты URL для диалога
    urls_to_test = [
        f"https://api.elevenlabs.io/v1/agent/{AGENT_ID}/conversation",
        f"https://api.elevenlabs.io/v1/agents/{AGENT_ID}/conversation",
        f"https://api.elevenlabs.io/v1/agent/{AGENT_ID}/chat",
        f"https://api.elevenlabs.io/v1/agents/{AGENT_ID}/chat"
    ]
    
    data = {
        "session_id": "test_session_123",
        "message_type": "user_input",
        "message": "Привет! Как дела?",
        "voice_id": "21m00Tcm4TlvDq8ikWAM"
    }
    
    for url in urls_to_test:
        try:
            print(f"   Пробуем: {url}")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            print(f"   Статус: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Успешно! Ответ: {result.get('response', 'Нет ответа')}")
                return url
            else:
                print(f"   ❌ Ошибка: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
    
    return None

def test_available_endpoints():
    """Тестирует доступные endpoints"""
    print("\n3. Проверяем доступные endpoints...")
    
    headers = {
        'Content-Type': 'application/json',
        'xi-api-key': API_KEY
    }
    
    # Попробуем получить список агентов
    try:
        url = "https://api.elevenlabs.io/v1/agents"
        print(f"   Пробуем: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            agents = response.json()
            print(f"   ✅ Найдено агентов: {len(agents.get('agents', []))}")
            for agent in agents.get('agents', []):
                print(f"      - {agent.get('name', 'Unknown')} (ID: {agent.get('agent_id', 'Unknown')})")
        else:
            print(f"   ❌ Ошибка: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Исключение: {e}")

def main():
    print("🧪 Тестирование ElevenLabs Agent API endpoints")
    print("=" * 60)
    
    # Тест 1: Информация об агенте
    agent_url = test_agent_endpoints()
    
    # Тест 2: Диалог
    conversation_url = test_conversation_endpoint()
    
    # Тест 3: Доступные endpoints
    test_available_endpoints()
    
    print("\n" + "=" * 60)
    print("📋 Результаты:")
    
    if agent_url:
        print(f"✅ Agent info URL: {agent_url}")
    else:
        print("❌ Agent info URL не найден")
    
    if conversation_url:
        print(f"✅ Conversation URL: {conversation_url}")
    else:
        print("❌ Conversation URL не найден")

if __name__ == "__main__":
    main()

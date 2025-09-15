#!/usr/bin/env python3
"""
Скрипт для быстрого запуска AI Call Prototype
"""

import os
import sys
import subprocess

def check_dependencies():
    """Проверяет установленные зависимости"""
    try:
        import fastapi
        import uvicorn
        import requests
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return False

def check_config():
    """Проверяет конфигурацию"""
    try:
        from config import OPENROUTER_API_KEY, YANDEX_API_KEY, VOXIMPLANT_API_KEY
        
        if OPENROUTER_API_KEY == "your_openrouter_api_key":
            print("⚠️  Внимание: Не настроен OPENROUTER_API_KEY")
            return False
        
        if YANDEX_API_KEY == "your_yandex_speechkit_key":
            print("⚠️  Внимание: Не настроен YANDEX_API_KEY")
            return False
        
        if VOXIMPLANT_API_KEY == "your_voximplant_api_key":
            print("⚠️  Внимание: Не настроен VOXIMPLANT_API_KEY")
            return False
        
        print("✅ Конфигурация проверена")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def main():
    """Основная функция запуска"""
    print("🤖 AI Call Prototype - Запуск системы")
    print("=" * 50)
    
    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)
    
    # Проверяем конфигурацию
    if not check_config():
        print("\n📝 Для настройки API ключей отредактируйте файл config.py")
        print("Подробности в README.md")
    
    print("\n🚀 Запуск сервера...")
    print("📱 Откройте браузер: http://localhost:8004")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Запускаем сервер
    try:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == "__main__":
    main()

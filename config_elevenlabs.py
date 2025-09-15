import os
from dotenv import load_dotenv

load_dotenv()

# ElevenLabs AI Agent конфигурация
ELEVENLABS_AGENT_API_KEY = "sk_bccc3b4272958d60c4c6e7cc003460f7d2d6d0f8724159af"
ELEVENLABS_AGENT_ID = "agent_8701k4554cs1e69arzeae6vva5qz"

# ElevenLabs API настройки
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Molly voice

# Voximplant настройки (используем существующие из config.py)
from config import (
    VOXIMPLANT_ACCOUNT_ID,
    VOXIMPLANT_API_KEY,
    VOXIMPLANT_APPLICATION_ID,
    VOXIMPLANT_RULE_ID,
    VOXIMPLANT_RULE_NAME
)

# Обновляем название сценария
VOXIMPLANT_SCENARIO = "elevenlabs_official_module"

# Webhook настройки
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://localhost:8000/api/call-results")

# Настройки звонков
CALLER_ID = "74951183993"  # Номер для исходящих звонков
CONFIDENCE_THRESHOLD = 0.6
RECOGNITION_TIMEOUT = 8000

# Логирование
LOG_LEVEL = "INFO"
LOG_FILE = "logs/elevenlabs_agent.log"

print("✅ ElevenLabs Agent конфигурация загружена:")
print(f"   Agent ID: {ELEVENLABS_AGENT_ID}")
print(f"   API Key: {ELEVENLABS_AGENT_API_KEY[:20]}...")
print(f"   Voice ID: {ELEVENLABS_VOICE_ID}")
print(f"   Voximplant Account: {VOXIMPLANT_ACCOUNT_ID}")

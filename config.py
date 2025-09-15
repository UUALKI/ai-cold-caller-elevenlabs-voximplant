import os
from dotenv import load_dotenv

load_dotenv()

# API Keys

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "AQVN3FLZ6YlKQp553aTzZQ-AJBUCQVnO35phLwZW")
# Автоматически используем указанный ключ ElevenLabs, если переменная окружения не задана
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_bccc3b4272958d60c4c6e7cc003460f7d2d6d0f8724159af")
# Настоящий OpenAI API ключ для Realtime API (работает через VPN)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")

# SaluteSpeech API (Сбер) для распознавания речи
SALUTESPEECH_AUTH_KEY = os.getenv("SALUTESPEECH_AUTH_KEY", "ODFhMDdjYWQtZWExYS00NzE0LTk0ZWYtMGRhNDg2ODg5MGRhOjRiMzBkNTEzLWEyYTEtNDVhMS1hMmMxLTZiNjVhY2IzN2JmMQ==")
SALUTESPEECH_CLIENT_ID = os.getenv("SALUTESPEECH_CLIENT_ID", "81a07cad-ea1a-4714-94ef-0da4868890da")
SALUTESPEECH_SCOPE = os.getenv("SALUTESPEECH_SCOPE", "SALUTE_SPEECH_PERS")
SALUTESPEECH_OAUTH_URL = os.getenv("SALUTESPEECH_OAUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
SALUTESPEECH_API_URL = os.getenv("SALUTESPEECH_API_URL", "https://smartspeech.sber.ru")

# Проверяем, что API ключи загружены
if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "":
    print("WARNING: OPENROUTER_API_KEY not found, using default")
    OPENROUTER_API_KEY = "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"

# ElevenLabs Voice (default for realtime TTS)
# Пустое значение по умолчанию, чтобы сценарий сам подбирал подходящий публичный RU женский голос
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")

# Список кандидатов голосов ElevenLabs (через запятую), например: "id1,id2,id3"
# Предпочтительные женские голоса с лучшим качеством для русского языка
ELEVENLABS_CANDIDATE_VOICE_IDS = os.getenv(
    "ELEVENLABS_CANDIDATE_VOICE_IDS",
    "21m00Tcm4TlvDq8ikWAM,EXAVITQu4vr4xnSDxMaL,VR6AewLTigWG4xSOukaG"
)

# Voximplant Settings
VOXIMPLANT_ACCOUNT_ID = os.getenv("VOXIMPLANT_ACCOUNT_ID", "9768007")
VOXIMPLANT_API_KEY = os.getenv("VOXIMPLANT_API_KEY", "fbe15287-6a3f-4fe2-a51f-fe26b96e8c6f")
VOXIMPLANT_APPLICATION_ID = int(os.getenv("VOXIMPLANT_APPLICATION_ID", "45686923"))
VOXIMPLANT_RULE_ID = os.getenv("VOXIMPLANT_RULE_ID", "7944221")
VOXIMPLANT_SCENARIO = os.getenv("VOXIMPLANT_SCENARIO", "elevenlabs_official_module")
VOXIMPLANT_USER = os.getenv("VOXIMPLANT_USER", "kichkina@tt.kichkina.n3.voximplant.com")
VOXIMPLANT_RULE_NAME = os.getenv("VOXIMPLANT_RULE_NAME", "ai cold caller")

# Voice Settings
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "dmitriy")
DEFAULT_AGENT_ID = int(os.getenv("DEFAULT_AGENT_ID", "3"))

# System Settings
MAX_CALL_DURATION = 300  # 5 минут
RING_TIMEOUT = 30  # 30 секунд
AUDIO_CACHE_DIR = "audio_cache"
TTS_AUDIO_DIR = "tts_audio"
LOGS_DIR = "logs"
KNOWLEDGE_DIR = "knowledge"

# Webhook URL for Voximplant ASR/Dialogue callbacks
# Используем ngrok URL для внешнего доступа
VOXIMPLANT_WEBHOOK_URL = os.getenv("VOXIMPLANT_WEBHOOK_URL", "https://57f1e64a1533.ngrok-free.app/api/voxi/events")

# Создаем необходимые директории
for directory in [AUDIO_CACHE_DIR, TTS_AUDIO_DIR, LOGS_DIR, KNOWLEDGE_DIR]:
    os.makedirs(directory, exist_ok=True)

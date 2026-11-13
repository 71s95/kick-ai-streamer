"""Environment-backed configuration for the local co-streamer."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    root_dir: Path = ROOT_DIR
    kick_client_id: str = os.getenv("KICK_CLIENT_ID", "")
    kick_client_secret: str = os.getenv("KICK_CLIENT_SECRET", "")
    kick_redirect_uri: str = os.getenv("KICK_REDIRECT_URI", "http://localhost:8000/kick/callback")
    kick_webhook_public_url: str = os.getenv("KICK_WEBHOOK_PUBLIC_URL", "")
    kick_webhook_path: str = os.getenv("KICK_WEBHOOK_PATH", "/kick/webhook")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    assistant_name: str = os.getenv("ASSISTANT_NAME", "Mira")
    bind_host: str = os.getenv("DASHBOARD_HOST", "localhost")
    port: int = _int("DASHBOARD_PORT", 8000)
    webhook_bind_host: str = os.getenv("WEBHOOK_BIND_HOST", "0.0.0.0")
    webhook_port: int = _int("WEBHOOK_PORT", 8001)
    max_message_length: int = _int("MAX_MESSAGE_LENGTH", 350)
    max_context_messages: int = _int("MAX_CONTEXT_MESSAGES", 24)
    max_chat_items: int = _int("MAX_DASHBOARD_MESSAGES", 120)
    user_cooldown_seconds: int = _int("USER_COOLDOWN_SECONDS", 90)
    response_cooldown_seconds: int = _int("RESPONSE_COOLDOWN_SECONDS", 18)
    max_responses_per_minute: int = _int("MAX_RESPONSES_PER_MINUTE", 3)
    message_batch_seconds: float = _float("MESSAGE_BATCH_SECONDS", 2.5)
    spontaneous_min_interval_seconds: int = _int("SPONTANEOUS_MIN_INTERVAL_SECONDS", 240)
    spontaneous_min_messages: int = _int("SPONTANEOUS_MIN_MESSAGES", 10)
    min_importance_score: int = _int("MIN_IMPORTANCE_SCORE", 24)
    max_speech_chars: int = _int("MAX_SPEECH_CHARS", 700)
    blocked_terms: tuple[str, ...] = tuple(
        term.strip().casefold()
        for term in os.getenv(
            "BLOCKED_TERMS",
            "amk,aq,orospu,piç,sik,yarrak,göt,ananı,avradını,gerizekalı",
        ).split(",")
        if term.strip()
    )
    azure_speech_key: str = os.getenv("AZURE_SPEECH_KEY", "")
    azure_speech_region: str = os.getenv("AZURE_SPEECH_REGION", "")
    tts_voice: str = os.getenv("TTS_VOICE", "tr-TR-EmelNeural")
    tts_rate_percent: int = _int("TTS_RATE_PERCENT", 0)
    tts_volume: int = max(0, min(100, _int("TTS_VOLUME", 85)))
    audio_device_name: str = os.getenv("AUDIO_DEVICE_NAME", "")
    webhook_max_age_seconds: int = _int("WEBHOOK_MAX_AGE_SECONDS", 300)


def get_settings() -> Settings:
    return Settings()

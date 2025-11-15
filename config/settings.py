"""
CONFIG/SETTINGS.PY
==================
Configurações centralizadas do projeto.

Carrega variáveis de ambiente e fornece acesso tipado.

Autor: Claude Code
Versão: 1.0
Data: Janeiro 2025
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurações do projeto."""

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    CONFIG_DIR: Path = BASE_DIR / "config"

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL_CHAT: str = "gpt-4o-mini"
    OPENAI_MODEL_TRANSCRIBE: str = "gpt-4o-transcribe"
    OPENAI_MODEL_EMBEDDING: str = "text-embedding-3-small"

    # ElevenLabs
    ELEVENLABS_API_KEY: str
    ELEVENLABS_MODEL: str = "eleven_multilingual_v2"
    ELEVENLABS_VOICE_ID: str

    # WhatsApp
    WHATSAPP_ACCESS_TOKEN: str
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str  # Corrigido: adicionado WEBHOOK no nome
    WHATSAPP_WEBHOOK_SECRET: str
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = None

    # Google Calendar
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/oauth/callback"
    GOOGLE_CREDENTIALS_PATH: Path = Field(default=Path("config/google_credentials.json"))
    GOOGLE_TOKEN_PATH: Path = Field(default=Path("config/google_token.json"))
    GOOGLE_CALENDAR_ID: Optional[str] = None

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_QUEUE: str = "mensagens_whatsapp"

    # Configurações Gerais
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    MAX_CONCURRENT_MESSAGES: int = 10

    # Configurações do Agente
    COMPANY_NAME: str = "Vertical Partners"
    PRODUCT_NAME: str = "Agentes de IA"
    AGENT_NAME: str = "Iara"
    MESSAGE_BUFFER_SECONDS: int = 30
    MAX_FRAGMENT_WORDS: int = 30
    FOLLOWUP_CHECK_INTERVAL: int = 5

    # URLs
    VIDEO_BOAS_VINDAS_URL: Optional[str] = None  # Tornado opcional para não quebrar se não configurada

    # Servidor Web
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instância global de configurações
settings = Settings()

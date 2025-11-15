"""
MAIN.PY
=======
Entry point da aplicação - Agente SDR WhatsApp

Inicializa:
- FastAPI (webhooks)
- Agente SDR
- Sistema de follow-up
- RabbitMQ consumer
- Redis
- Todos os clientes

Autor: Claude Code
Versão: 1.0
Data: Janeiro 2025
"""

import asyncio
from contextlib import asynccontextmanager

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from loguru import logger

from config.settings import settings
from core.integrations import (
    WhatsAppClient,
    GoogleCalendarClient,
    SupabaseClient,
    ElevenLabsClient,
    RabbitMQClient
)
from core.memory import (
    RedisMemoryManager,
    MessageBuffer,
    SessionStateManager,
    HybridRetriever
)
from core.agent import AgenteSDR
from core.followup import FollowUpManager, FollowUpScheduler


# ==============================================================================
# INICIALIZAÇÃO
# ==============================================================================

# Variáveis globais
whatsapp_client = None
google_calendar_client = None
supabase_client = None
elevenlabs_client = None
rabbitmq_client = None
redis_client = None
memory_manager = None
message_buffer = None
session_state = None
hybrid_retriever = None
agente_sdr = None
followup_manager = None
followup_scheduler = None


async def init_clients():
    """Inicializa todos os clientes e serviços."""
    global whatsapp_client, google_calendar_client, supabase_client
    global elevenlabs_client, rabbitmq_client, redis_client
    global memory_manager, message_buffer, session_state, hybrid_retriever
    global agente_sdr, followup_manager, followup_scheduler

    logger.info("Inicializando clientes...")

    # WhatsApp
    whatsapp_client = WhatsAppClient(
        access_token=settings.WHATSAPP_ACCESS_TOKEN,
        phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID,
        verify_token=settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN
    )

    # Google Calendar
    google_calendar_client = GoogleCalendarClient(
        credentials_path=str(settings.GOOGLE_CREDENTIALS_PATH),
        token_path=str(settings.GOOGLE_TOKEN_PATH)
    )

    # Supabase
    supabase_client = SupabaseClient(
        url=settings.SUPABASE_URL,
        key=settings.SUPABASE_KEY
    )

    # ElevenLabs
    elevenlabs_client = ElevenLabsClient(
        api_key=settings.ELEVENLABS_API_KEY,
        voice_id=settings.ELEVENLABS_VOICE_ID
    )

    # RabbitMQ
    rabbitmq_client = RabbitMQClient(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        username=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD,
        queue_name=settings.RABBITMQ_QUEUE
    )

    # Redis
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=False
    )

    # Memory Manager
    memory_manager = RedisMemoryManager(redis_client)

    # Session State
    session_state = SessionStateManager(redis_client)

    # Embeddings (OpenAI)
    embeddings = OpenAIEmbeddings(
        model=settings.OPENAI_MODEL_EMBEDDING,
        api_key=settings.OPENAI_API_KEY
    )

    # Hybrid Retriever (RAG)
    hybrid_retriever = HybridRetriever(
        supabase_client=supabase_client,
        embeddings=embeddings
    )

    # Message Buffer (callback será definido depois)
    message_buffer = MessageBuffer(
        redis_client=redis_client,
        process_callback=process_buffered_messages
    )

    # Agente SDR
    agente_sdr = AgenteSDR(
        whatsapp_client=whatsapp_client,
        google_calendar_client=google_calendar_client,
        supabase_client=supabase_client,
        elevenlabs_client=elevenlabs_client,
        redis_memory=memory_manager,
        hybrid_retriever=hybrid_retriever,
        session_state=session_state,
        openai_api_key=settings.OPENAI_API_KEY
    )

    # LLM para follow-up
    llm_followup = ChatOpenAI(
        model=settings.OPENAI_MODEL_CHAT,
        temperature=0.7,
        api_key=settings.OPENAI_API_KEY
    )

    # Follow-up Manager
    followup_manager = FollowUpManager(
        whatsapp_client=whatsapp_client,
        supabase_client=supabase_client,
        memory=memory_manager,
        llm=llm_followup
    )

    # Follow-up Scheduler
    followup_scheduler = FollowUpScheduler(followup_manager)
    followup_scheduler.start()

    logger.info("✅ Todos os clientes inicializados com sucesso!")


async def cleanup():
    """Cleanup ao finalizar aplicação."""
    logger.info("Finalizando aplicação...")

    if followup_scheduler:
        followup_scheduler.stop()

    if whatsapp_client:
        await whatsapp_client.close()

    if elevenlabs_client:
        await elevenlabs_client.close()

    if rabbitmq_client:
        rabbitmq_client.close()

    if redis_client:
        await redis_client.close()

    logger.info("✅ Cleanup concluído")


# ==============================================================================
# FASTAPI APP
# ==============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia lifecycle da aplicação."""
    # Startup
    await init_clients()
    yield
    # Shutdown
    await cleanup()


app = FastAPI(
    title="Agente SDR WhatsApp",
    description="Agente de IA para WhatsApp com LangChain",
    version="1.0.0",
    lifespan=lifespan
)


# ==============================================================================
# WEBHOOKS
# ==============================================================================

@app.get("/webhook/whatsapp")
async def whatsapp_webhook_verify(request: Request):
    """
    Verificação do webhook do WhatsApp.

    Meta envia GET request para verificar o webhook.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verificado com sucesso")
        return PlainTextResponse(challenge)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/webhook/whatsapp")
async def whatsapp_webhook_receive(request: Request):
    """
    Recebe mensagens do WhatsApp.

    Processa:
    - Mensagens de texto
    - Mídias (imagem, vídeo, áudio, documento)
    - Status de entrega
    """
    try:
        # Validar signature
        signature = request.headers.get("X-Hub-Signature-256", "")
        body = await request.body()

        if not whatsapp_client.verify_webhook_signature(
            body,
            signature,
            settings.WHATSAPP_WEBHOOK_SECRET
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse data
        data = await request.json()

        # Processar entries
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                # Processar mensagens
                if "messages" in value:
                    for message in value["messages"]:
                        # Publicar no RabbitMQ para processamento assíncrono
                        rabbitmq_client.publish({
                            "type": "message",
                            "data": message
                        })

        return JSONResponse({"status": "ok"})

    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# PROCESSAMENTO DE MENSAGENS
# ==============================================================================

async def process_buffered_messages(
    phone: str,
    combined_content: str,
    original_messages: list
):
    """
    Callback para processar mensagens após buffer de 30s.

    Args:
        phone: Telefone do lead
        combined_content: Conteúdo combinado das mensagens
        original_messages: Mensagens originais
    """
    try:
        logger.info(f"Processando mensagens buffered de {phone}")

        # Processar com agente
        response = await agente_sdr.process_message(
            phone=phone,
            message=combined_content,
            metadata={"buffered_messages": original_messages}
        )

        logger.info(f"Resposta enviada para {phone}")

        # Agendar primeiro follow-up (se ainda não tiver)
        lead = await supabase_client.get_lead(phone)
        if lead and lead.get('fup_enviado', 0) == 0:
            await followup_manager.agendar_primeiro_followup(phone)

    except Exception as e:
        logger.error(f"Erro ao processar mensagens de {phone}: {e}")


def message_consumer_callback(ch, method, properties, body):
    """
    Callback do RabbitMQ consumer.

    Processa mensagens da fila.
    """
    import json

    try:
        data = json.loads(body)
        message_data = data.get("data", {})

        # Extrair informações
        phone = message_data.get("from")
        message_id = message_data.get("id")
        message_type = message_data.get("type")

        # Marcar como lida
        asyncio.create_task(whatsapp_client.mark_as_read(message_id))

        # Processar baseado no tipo
        if message_type == "text":
            content = message_data.get("text", {}).get("body", "")
            media_url = None
            media_type = None

        elif message_type in ["image", "video", "audio", "document"]:
            media_id = message_data.get(message_type, {}).get("id")
            # TODO: Buscar URL da mídia
            media_url = f"media://{media_id}"
            content = message_data.get(message_type, {}).get("caption", "")
            media_type = message_type

        else:
            # Tipo não suportado
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Adicionar ao buffer
        asyncio.create_task(message_buffer.add_message(phone, {
            "message_id": message_id,
            "content": content,
            "timestamp": message_data.get("timestamp"),
            "media_url": media_url,
            "media_type": media_type
        }))

        # Confirmar processamento
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Erro no consumer: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)


# ==============================================================================
# HEALTH CHECK
# ==============================================================================

@app.get("/health")
async def health_check():
    """Health check da aplicação."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    # Configurar logging
    logger.add(
        "logs/app.log",
        rotation="1 day",
        retention="7 days",
        level=settings.LOG_LEVEL
    )

    logger.info(f"🚀 Iniciando Agente SDR WhatsApp - Ambiente: {settings.ENVIRONMENT}")

    # Iniciar RabbitMQ consumer em thread separada
    import threading

    def start_consumer():
        rabbitmq_client.consume(message_consumer_callback)

    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()

    # Iniciar FastAPI
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )

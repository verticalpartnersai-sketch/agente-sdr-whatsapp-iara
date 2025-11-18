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
from pathlib import Path

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from loguru import logger
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

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

    # Google Calendar (opcional - não crasha se não autenticado)
    try:
        google_calendar_client = GoogleCalendarClient(
            credentials_path=str(settings.GOOGLE_CREDENTIALS_PATH),
            token_path=str(settings.GOOGLE_TOKEN_PATH)
        )
        logger.info("✅ Google Calendar inicializado")
    except Exception as e:
        logger.warning(f"⚠️ Google Calendar não disponível: {e}")
        google_calendar_client = None

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

    # RabbitMQ (async)
    rabbitmq_client = RabbitMQClient(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        username=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD,
        queue_name=settings.RABBITMQ_QUEUE
    )
    await rabbitmq_client.connect()  # Conexão async

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
        try:
            await rabbitmq_client.close()
        except Exception as e:
            logger.warning(f"Erro ao fechar RabbitMQ (ignorado): {e}")

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

    # Iniciar RabbitMQ consumer (async task em background)
    consumer_task = None
    if rabbitmq_client:
        logger.info("Iniciando RabbitMQ consumer (async)...")
        consumer_task = asyncio.create_task(
            rabbitmq_client.consume(message_consumer_callback)
        )

    yield

    # Shutdown
    if consumer_task and not consumer_task.done():
        logger.info("Cancelando consumer RabbitMQ...")
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Consumer RabbitMQ cancelado com sucesso")

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
                        await rabbitmq_client.publish({
                            "type": "message",
                            "data": message
                        })

        return JSONResponse({"status": "ok"})

    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# OAUTH ENDPOINTS - GOOGLE CALENDAR
# ==============================================================================

@app.get("/oauth/google/authorize")
async def google_oauth_authorize():
    """
    Gera URL de autorização do Google Calendar.

    Fluxo:
    1. Usuário acessa este endpoint
    2. Recebe URL de autorização
    3. Acessa a URL no navegador
    4. Autoriza o aplicativo
    5. É redirecionado para /oauth/google/callback
    """
    try:
        # Criar Flow OAuth
        flow = Flow.from_client_secrets_file(
            str(settings.GOOGLE_CREDENTIALS_PATH),
            scopes=[
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.events'
            ],
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        # Gerar URL de autorização
        authorization_url, state = flow.authorization_url(
            access_type='offline',  # IMPORTANTE: Para obter refresh_token
            include_granted_scopes='true',
            prompt='consent'  # Força consentimento para garantir refresh_token
        )

        logger.info(f"URL de autorização gerada: {authorization_url}")

        return {
            "authorization_url": authorization_url,
            "message": "Acesse esta URL no navegador para autorizar o aplicativo",
            "instructions": [
                "1. Copie a URL abaixo",
                "2. Cole no seu navegador",
                "3. Faça login com sua conta Google",
                "4. Autorize o acesso ao Google Calendar",
                "5. Aguarde o redirecionamento automático"
            ]
        }

    except Exception as e:
        logger.error(f"Erro ao gerar URL de autorização: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar URL: {str(e)}")


@app.get("/oauth/google/callback")
async def google_oauth_callback(code: str = None, error: str = None):
    """
    Callback do Google OAuth.

    Recebe o código de autorização e troca por tokens.
    Salva o refresh_token para uso futuro.
    """
    global google_calendar_client

    # Verificar se houve erro
    if error:
        logger.error(f"Erro na autorização: {error}")
        raise HTTPException(status_code=400, detail=f"Erro na autorização: {error}")

    # Verificar se recebeu código
    if not code:
        raise HTTPException(status_code=400, detail="Código de autorização não fornecido")

    try:
        # Criar Flow OAuth
        flow = Flow.from_client_secrets_file(
            str(settings.GOOGLE_CREDENTIALS_PATH),
            scopes=[
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.events'
            ],
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        # Trocar código por tokens
        flow.fetch_token(code=code)

        # Obter credenciais
        credentials = flow.credentials

        # Salvar token
        token_path = Path(settings.GOOGLE_TOKEN_PATH)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(credentials.to_json())

        logger.info(f"✅ Token do Google Calendar salvo em: {token_path}")

        # Reinicializar GoogleCalendarClient
        try:
            from core.integrations import GoogleCalendarClient
            google_calendar_client = GoogleCalendarClient(
                credentials_path=str(settings.GOOGLE_CREDENTIALS_PATH),
                token_path=str(settings.GOOGLE_TOKEN_PATH)
            )
            logger.info("✅ Google Calendar Client reinicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao reinicializar Google Calendar Client: {e}")

        return {
            "status": "success",
            "message": "Autenticação realizada com sucesso!",
            "token_saved": str(token_path),
            "instructions": [
                "O Google Calendar está agora autenticado",
                "O token será renovado automaticamente quando expirar",
                "Você pode fechar esta página"
            ]
        }

    except Exception as e:
        logger.error(f"Erro no callback OAuth: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar callback: {str(e)}")


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

        # CAMADA DE SEGURANÇA: Se agente não usou a tool, enviar manualmente
        # (fallback para garantir que mensagem SEMPRE seja enviada)
        if response and not response.startswith("Mensagem enviada com sucesso"):
            logger.warning(
                f"⚠️ Agente não usou tool enviar_mensagem - "
                f"Ativando fallback para {phone}"
            )

            # VALIDAÇÃO: Não enviar se resposta for JSON/código/formato ReAct
            is_safe_to_send = True

            # Verificar se contém padrões problemáticos
            problematic_patterns = [
                "Pensamento:",
                "Ação:",
                "Entrada da Ação:",
                '"telefone":',
                '"texto":',
                'Invoking:',
                '```json',
                '```python'
            ]

            for pattern in problematic_patterns:
                if pattern in response:
                    logger.error(
                        f"🚨 RESPOSTA PERIGOSA BLOQUEADA para {phone}: "
                        f"contém '{pattern}'"
                    )
                    is_safe_to_send = False
                    break

            # Se começar com { ou contiver apenas JSON
            if response.strip().startswith("{") or response.strip().startswith("["):
                logger.error(f"🚨 RESPOSTA PERIGOSA BLOQUEADA para {phone}: JSON bruto")
                is_safe_to_send = False

            if is_safe_to_send and len(response.strip()) > 5:
                # Importar MessageFormatter
                from core.agent import MessageFormatter

                # Enviar resposta manualmente
                await MessageFormatter.enviar_fragmentado(
                    whatsapp_client=whatsapp_client,
                    telefone=phone,
                    texto=response
                )

                # Salvar na memória
                await memory_manager.add_message(phone, "ai", response)

                logger.info(f"✅ Resposta enviada via fallback para {phone}")
            else:
                logger.error(
                    f"🚨 Resposta não enviada (bloqueada por segurança) para {phone}"
                )
        else:
            logger.info(f"✅ Resposta enviada via tool para {phone}")

        # Agendar primeiro follow-up (se ainda não tiver)
        lead = await supabase_client.get_lead(phone)
        if lead and lead.get('fup_enviado', 0) == 0:
            await followup_manager.agendar_primeiro_followup(phone)

    except Exception as e:
        logger.error(f"Erro ao processar mensagens de {phone}: {e}")


async def message_consumer_callback(data: dict):
    """
    Callback async do RabbitMQ consumer.

    Processa mensagens da fila (async nativo).

    Args:
        data: Dicionário com dados completos da mensagem
    """
    try:
        message_data = data.get("data", {})

        # Extrair informações
        phone = message_data.get("from")
        message_id = message_data.get("id")
        message_type = message_data.get("type")

        # Marcar como lida (async direto)
        if whatsapp_client:
            await whatsapp_client.mark_as_read(message_id)

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
            # Tipo não suportado - callback aio-pika já faz ack/nack
            return

        # Adicionar ao buffer (async direto)
        if message_buffer:
            await message_buffer.add_message(phone, {
                "message_id": message_id,
                "content": content,
                "timestamp": message_data.get("timestamp"),
                "media_url": media_url,
                "media_type": media_type
            })

    except Exception as e:
        logger.error(f"Erro no consumer: {e}")
        raise  # Re-raise para aio-pika fazer nack


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

    # Iniciar FastAPI
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )

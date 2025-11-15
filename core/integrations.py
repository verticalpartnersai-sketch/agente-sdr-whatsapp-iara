"""
CORE/INTEGRATIONS.PY
====================
Integrações com APIs externas:
- WhatsApp Business API (Meta)
- Google Calendar API
- Supabase
- ElevenLabs
- RabbitMQ
"""

import asyncio
import hmac
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path

import httpx
import pika
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from supabase import create_client, Client
from loguru import logger

# ==============================================================================
# WHATSAPP CLIENT
# ==============================================================================

class WhatsAppClient:
    """
    Cliente para WhatsApp Business API Oficial (Meta).

    Funcionalidades:
    - Enviar mensagens de texto
    - Enviar mídias (imagem, vídeo, áudio, documento)
    - Enviar templates
    - Marcar mensagens como lidas
    """

    def __init__(self, access_token: str, phone_number_id: str, verify_token: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.verify_token = verify_token
        self.base_url = f"https://graph.facebook.com/v18.0/{phone_number_id}"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def send_text(
        self,
        to: str,
        message: str,
        preview_url: bool = True
    ) -> Dict:
        """
        Envia mensagem de texto.

        Args:
            to: Número de telefone do destinatário (ex: 5511999999999)
            message: Texto da mensagem
            preview_url: Se True, mostra preview de links

        Returns:
            Resposta da API com message_id
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": message
            }
        }

        try:
            response = await self._request("POST", "/messages", json=payload)
            logger.info(f"Mensagem enviada para {to}: {message[:50]}...")
            return response
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {to}: {e}")
            raise

    async def send_media(
        self,
        to: str,
        media_type: str,
        media_url: str,
        caption: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Dict:
        """
        Envia mídia (imagem, vídeo, áudio, documento).

        Args:
            to: Número do destinatário
            media_type: Tipo (image, video, audio, document)
            media_url: URL pública da mídia
            caption: Legenda (apenas para image, video, document)
            filename: Nome do arquivo (apenas para document)

        Returns:
            Resposta da API
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": media_type,
            media_type: {
                "link": media_url
            }
        }

        # Adicionar caption
        if caption and media_type in ["image", "video", "document"]:
            payload[media_type]["caption"] = caption

        # Adicionar filename
        if filename and media_type == "document":
            payload[media_type]["filename"] = filename

        try:
            response = await self._request("POST", "/messages", json=payload)
            logger.info(f"{media_type.upper()} enviado para {to}")
            return response
        except Exception as e:
            logger.error(f"Erro ao enviar {media_type} para {to}: {e}")
            raise

    async def send_audio(self, to: str, audio_url: str) -> Dict:
        """Envia mensagem de áudio."""
        return await self.send_media(to, "audio", audio_url)

    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "pt_BR",
        components: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Envia template pré-aprovado.

        Args:
            to: Número do destinatário
            template_name: Nome do template
            language_code: Código do idioma (pt_BR, en_US, etc)
            components: Componentes do template (variáveis)

        Returns:
            Resposta da API
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": components or []
            }
        }

        try:
            response = await self._request("POST", "/messages", json=payload)
            logger.info(f"Template '{template_name}' enviado para {to}")
            return response
        except Exception as e:
            logger.error(f"Erro ao enviar template para {to}: {e}")
            raise

    async def mark_as_read(self, message_id: str) -> Dict:
        """Marca mensagem como lida."""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }

        return await self._request("POST", "/messages", json=payload)

    async def get_media_url(self, media_id: str) -> str:
        """
        Obtém URL de mídia pelo ID.

        Args:
            media_id: ID da mídia retornado no webhook

        Returns:
            URL pública da mídia
        """
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with self.client as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["url"]

    async def download_media(self, media_url: str) -> bytes:
        """
        Baixa mídia do WhatsApp.

        Args:
            media_url: URL da mídia

        Returns:
            Bytes da mídia
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with self.client as client:
            response = await client.get(media_url, headers=headers)
            response.raise_for_status()
            return response.content

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Faz requisição HTTP com retry logic."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        url = f"{self.base_url}{endpoint}"

        # Retry logic simples (3 tentativas)
        for attempt in range(3):
            try:
                async with self.client as client:
                    response = await client.request(
                        method,
                        url,
                        headers=headers,
                        **kwargs
                    )
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPError as e:
                if attempt == 2:  # última tentativa
                    raise
                await asyncio.sleep(2 ** attempt)  # exponential backoff

    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Verifica assinatura do webhook (segurança).

        Args:
            payload: Body da requisição em bytes
            signature: Valor do header X-Hub-Signature-256
            secret: Secret do webhook

        Returns:
            True se válido, False caso contrário
        """
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Remove prefixo "sha256=" se existir
        if signature.startswith("sha256="):
            signature = signature[7:]

        return hmac.compare_digest(signature, expected_signature)

    async def close(self):
        """Fecha conexão HTTP."""
        await self.client.aclose()


# ==============================================================================
# GOOGLE CALENDAR CLIENT
# ==============================================================================

class GoogleCalendarClient:
    """
    Cliente para Google Calendar API.

    Funcionalidades:
    - Listar horários disponíveis (FreeBusy)
    - Agendar reuniões com Google Meet
    - Cancelar reuniões
    - Reagendar reuniões
    - Atualizar participantes
    - Consultar eventos
    """

    # Scopes necessários
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]

    def _create_credentials_file(self, credentials_path: str):
        """
        Cria o arquivo google_credentials.json a partir das variáveis de ambiente
        se o arquivo não existir.

        Args:
            credentials_path: Caminho onde o arquivo será criado
        """
        from config.settings import settings

        credentials_file = Path(credentials_path)

        # Se o arquivo já existe, não fazer nada
        if credentials_file.exists():
            logger.info(f"Arquivo de credenciais já existe: {credentials_path}")
            return

        logger.info(f"Criando arquivo de credenciais a partir das variáveis de ambiente: {credentials_path}")

        # Criar estrutura do arquivo credentials.json
        credentials_data = {
            "installed": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
            }
        }

        # Criar diretório se não existir
        credentials_file.parent.mkdir(parents=True, exist_ok=True)

        # Salvar arquivo
        credentials_file.write_text(json.dumps(credentials_data, indent=2))
        logger.info(f"Arquivo de credenciais criado com sucesso: {credentials_path}")

    def __init__(self, credentials_path: str, token_path: str = "token.json"):
        """
        Inicializa cliente do Google Calendar.

        Args:
            credentials_path: Caminho para credentials.json do Google Cloud
            token_path: Caminho para salvar token de acesso
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        self.service = None
        self.calendar_id = 'primary'

        # Criar arquivo de credenciais se não existir
        self._create_credentials_file(credentials_path)

        self._authenticate()

    def _authenticate(self):
        """
        Autentica usando OAuth 2.0.

        Comportamento em produção (sem navegador):
        - Se já tem token salvo: carrega e usa (renova automaticamente se expirado)
        - Se NÃO tem token: não crasha, apenas loga aviso
        """
        # Carregar token se existir
        if Path(self.token_path).exists():
            try:
                self.creds = Credentials.from_authorized_user_file(
                    self.token_path,
                    self.SCOPES
                )

                # Se expirou, fazer refresh automaticamente
                if self.creds.expired and self.creds.refresh_token:
                    logger.info("Token do Google Calendar expirado, renovando...")
                    self.creds.refresh(Request())
                    # Salvar token atualizado
                    Path(self.token_path).write_text(self.creds.to_json())
                    logger.info("Token do Google Calendar renovado com sucesso")

                # Criar serviço
                self.service = build('calendar', 'v3', credentials=self.creds)
                logger.info("✅ Google Calendar autenticado com sucesso")
                return

            except Exception as e:
                logger.error(f"Erro ao carregar token do Google Calendar: {e}")
                # Continuar para tentar autenticar novamente

        # Se chegou aqui, não tem token válido
        # NÃO TENTAR AUTENTICAR (sem navegador em produção)
        logger.warning(
            "⚠️ Google Calendar não autenticado. "
            "Acesse GET /oauth/google/authorize para obter URL de autorização."
        )
        self.service = None

    def _check_service_available(self):
        """Verifica se o serviço do Google Calendar está disponível."""
        if self.service is None:
            raise RuntimeError(
                "Google Calendar não autenticado. "
                "Acesse GET /oauth/google/authorize para autenticar."
            )

    async def listar_horarios_disponiveis(
        self,
        data_inicio: datetime,
        data_fim: datetime,
        duracao_minutos: int = 60,
        horario_comercial: bool = True
    ) -> List[Dict]:
        """
        Lista horários disponíveis em um período.

        Args:
            data_inicio: Data/hora de início do período
            data_fim: Data/hora de fim do período
            duracao_minutos: Duração da reunião em minutos
            horario_comercial: Se True, apenas horários entre 9h-18h

        Returns:
            Lista de slots disponíveis: [{"inicio": datetime, "fim": datetime}]
        """
        self._check_service_available()

        # Buscar eventos ocupados
        freebusy_query = {
            "timeMin": data_inicio.isoformat(),
            "timeMax": data_fim.isoformat(),
            "items": [{"id": self.calendar_id}]
        }

        freebusy_result = self.service.freebusy().query(
            body=freebusy_query
        ).execute()

        busy_slots = freebusy_result['calendars'][self.calendar_id].get('busy', [])

        # Calcular slots livres
        slots_livres = self._calcular_slots_livres(
            data_inicio,
            data_fim,
            busy_slots,
            duracao_minutos,
            horario_comercial
        )

        return slots_livres

    def _calcular_slots_livres(
        self,
        data_inicio: datetime,
        data_fim: datetime,
        busy_slots: List[Dict],
        duracao_minutos: int,
        horario_comercial: bool
    ) -> List[Dict]:
        """Calcula slots de tempo livres."""
        slots_livres = []
        current_time = data_inicio
        duracao = timedelta(minutes=duracao_minutos)

        while current_time + duracao <= data_fim:
            # Verificar se está em horário comercial
            if horario_comercial:
                if current_time.hour < 9 or current_time.hour >= 18:
                    current_time += timedelta(hours=1)
                    continue

            # Verificar se slot está livre
            slot_fim = current_time + duracao
            is_free = True

            for busy in busy_slots:
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))

                # Verificar sobreposição
                if not (slot_fim <= busy_start or current_time >= busy_end):
                    is_free = False
                    break

            if is_free:
                slots_livres.append({
                    "inicio": current_time,
                    "fim": slot_fim
                })

            # Avançar 30 minutos
            current_time += timedelta(minutes=30)

        return slots_livres

    async def agendar_reuniao(
        self,
        titulo: str,
        data_inicio: datetime,
        data_fim: datetime,
        participantes: List[str],
        descricao: Optional[str] = None,
        localizacao: Optional[str] = None
    ) -> Dict:
        """
        Agenda nova reunião com Google Meet.

        Args:
            titulo: Título da reunião
            data_inicio: Data/hora de início
            data_fim: Data/hora de fim
            participantes: Lista de emails dos participantes
            descricao: Descrição da reunião
            localizacao: Localização

        Returns:
            Dados do evento criado (inclui link do Meet)
        """
        self._check_service_available()

        event = {
            'summary': titulo,
            'description': descricao,
            'location': localizacao,
            'start': {
                'dateTime': data_inicio.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': data_fim.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'attendees': [{'email': email} for email in participantes],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 24h
                    {'method': 'popup', 'minutes': 120},      # 2h
                ],
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{uuid.uuid4()}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        created_event = self.service.events().insert(
            calendarId=self.calendar_id,
            body=event,
            conferenceDataVersion=1,
            sendUpdates='all'  # Envia convites
        ).execute()

        logger.info(f"Reunião '{titulo}' agendada para {data_inicio}")
        return created_event

    async def cancelar_reuniao(self, event_id: str) -> bool:
        """
        Cancela reunião.

        Args:
            event_id: ID do evento no Google Calendar

        Returns:
            True se cancelado com sucesso
        """
        self._check_service_available()

        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id,
                sendUpdates='all'  # Notifica participantes
            ).execute()

            logger.info(f"Reunião {event_id} cancelada")
            return True
        except Exception as e:
            logger.error(f"Erro ao cancelar reunião {event_id}: {e}")
            return False

    async def reagendar_reuniao(
        self,
        event_id: str,
        nova_data_inicio: datetime,
        nova_data_fim: datetime
    ) -> Dict:
        """
        Reagenda reunião existente.

        Args:
            event_id: ID do evento
            nova_data_inicio: Nova data/hora de início
            nova_data_fim: Nova data/hora de fim

        Returns:
            Evento atualizado
        """
        self._check_service_available()

        # Buscar evento existente
        event = self.service.events().get(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()

        # Atualizar datas
        event['start'] = {
            'dateTime': nova_data_inicio.isoformat(),
            'timeZone': 'America/Sao_Paulo'
        }
        event['end'] = {
            'dateTime': nova_data_fim.isoformat(),
            'timeZone': 'America/Sao_Paulo'
        }

        # Atualizar
        updated_event = self.service.events().update(
            calendarId=self.calendar_id,
            eventId=event_id,
            body=event,
            sendUpdates='all'  # Notifica participantes
        ).execute()

        logger.info(f"Reunião {event_id} reagendada para {nova_data_inicio}")
        return updated_event

    async def atualizar_participantes(
        self,
        event_id: str,
        participantes: List[str]
    ) -> Dict:
        """
        Atualiza lista de participantes de uma reunião.

        Args:
            event_id: ID do evento
            participantes: Nova lista de emails

        Returns:
            Evento atualizado
        """
        self._check_service_available()

        # Buscar evento
        event = self.service.events().get(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()

        # Atualizar participantes
        event['attendees'] = [{'email': email} for email in participantes]

        # Atualizar
        updated_event = self.service.events().update(
            calendarId=self.calendar_id,
            eventId=event_id,
            body=event,
            sendUpdates='all'
        ).execute()

        logger.info(f"Participantes da reunião {event_id} atualizados")
        return updated_event

    async def consultar_reuniao(self, event_id: str) -> Optional[Dict]:
        """
        Consulta detalhes de uma reunião.

        Args:
            event_id: ID do evento

        Returns:
            Dados do evento ou None se não encontrado
        """
        self._check_service_available()

        try:
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            return event
        except Exception as e:
            logger.error(f"Erro ao consultar reunião {event_id}: {e}")
            return None

    async def listar_reunioes_lead(
        self,
        email_lead: str,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Lista todas as reuniões de um lead específico.

        Args:
            email_lead: Email do lead
            data_inicio: Filtro de data inicial (opcional)
            data_fim: Filtro de data final (opcional)

        Returns:
            Lista de eventos
        """
        self._check_service_available()

        query_params = {
            'calendarId': self.calendar_id,
            'singleEvents': True,
            'orderBy': 'startTime'
        }

        if data_inicio:
            query_params['timeMin'] = data_inicio.isoformat()
        if data_fim:
            query_params['timeMax'] = data_fim.isoformat()

        events_result = self.service.events().list(**query_params).execute()
        all_events = events_result.get('items', [])

        # Filtrar por participante
        lead_events = [
            event for event in all_events
            if 'attendees' in event and
            any(att['email'] == email_lead for att in event['attendees'])
        ]

        return lead_events


# ==============================================================================
# SUPABASE CLIENT
# ==============================================================================

class SupabaseClient:
    """
    Cliente para Supabase (PostgreSQL + pgvector).

    Gerencia:
    - CRUD de leads
    - Base de conhecimento (RAG)
    - Reuniões
    - Storage de mídias
    """

    def __init__(self, url: str, key: str):
        """
        Inicializa cliente Supabase.

        Args:
            url: URL do projeto Supabase
            key: API key do Supabase
        """
        self.client: Client = create_client(url, key)
        logger.info("Supabase conectado")

    # === LEADS ===

    async def get_lead(self, telefone: str) -> Optional[Dict]:
        """Busca lead por telefone."""
        result = self.client.table('leads_wpp').select('*').eq('telefone', telefone).execute()
        return result.data[0] if result.data else None

    async def create_lead(self, lead_data: Dict) -> Dict:
        """Cria novo lead."""
        result = self.client.table('leads_wpp').insert(lead_data).execute()
        return result.data[0]

    async def update_lead(self, telefone: str, updates: Dict) -> Dict:
        """Atualiza lead existente."""
        result = self.client.table('leads_wpp').update(updates).eq('telefone', telefone).execute()
        return result.data[0]

    async def add_tag(self, telefone: str, tag: str) -> Dict:
        """Adiciona tag a um lead."""
        lead = await self.get_lead(telefone)
        if not lead:
            raise ValueError(f"Lead {telefone} não encontrado")

        tags_atuais = lead.get('tags', [])
        if tag not in tags_atuais:
            tags_atuais.append(tag)
            return await self.update_lead(telefone, {'tags': tags_atuais})
        return lead

    async def remove_tag(self, telefone: str, tag: str) -> Dict:
        """Remove tag de um lead."""
        lead = await self.get_lead(telefone)
        if not lead:
            raise ValueError(f"Lead {telefone} não encontrado")

        tags_atuais = lead.get('tags', [])
        if tag in tags_atuais:
            tags_atuais.remove(tag)
            return await self.update_lead(telefone, {'tags': tags_atuais})
        return lead

    # === KNOWLEDGE BASE ===

    async def add_knowledge(
        self,
        assunto: str,
        conteudo: str,
        embedding: List[float],
        perguntas: Optional[List[str]] = None,
        respostas: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        categoria: Optional[str] = None
    ) -> Dict:
        """Adiciona conhecimento à base."""
        data = {
            'assunto': assunto,
            'conteudo': conteudo,
            'embedding': embedding,
            'perguntas': perguntas or [],
            'respostas': respostas or [],
            'tags': tags or [],
            'categoria': categoria
        }

        result = self.client.table('knowledge').insert(data).execute()
        return result.data[0]

    async def hybrid_search(
        self,
        query_embedding: List[float],
        query_text: str,
        match_count: int = 5,
        semantic_weight: float = 0.6
    ) -> List[Dict]:
        """
        Busca híbrida (semântica + BM25).

        Args:
            query_embedding: Embedding da query
            query_text: Texto da query
            match_count: Quantidade de resultados
            semantic_weight: Peso da busca semântica (0.6 = 60%)

        Returns:
            Lista de documentos relevantes
        """
        result = self.client.rpc('hybrid_search', {
            'query_embedding': query_embedding,
            'query_text': query_text,
            'match_count': match_count,
            'semantic_weight': semantic_weight
        }).execute()

        return result.data

    # === REUNIÕES ===

    async def create_reuniao(self, reuniao_data: Dict) -> Dict:
        """Cria registro de reunião."""
        result = self.client.table('reunioes').insert(reuniao_data).execute()
        return result.data[0]

    async def get_reuniao_by_google_id(self, google_event_id: str) -> Optional[Dict]:
        """Busca reunião por ID do Google Calendar."""
        result = self.client.table('reunioes').select('*').eq('google_event_id', google_event_id).execute()
        return result.data[0] if result.data else None

    async def update_reuniao(self, reuniao_id: str, updates: Dict) -> Dict:
        """Atualiza reunião."""
        result = self.client.table('reunioes').update(updates).eq('id', reuniao_id).execute()
        return result.data[0]

    async def get_reunioes_proximas(self, horas: int = 24) -> List[Dict]:
        """
        Busca reuniões que acontecerão nas próximas X horas.

        Args:
            horas: Número de horas à frente

        Returns:
            Lista de reuniões
        """
        agora = datetime.utcnow()
        limite = agora + timedelta(hours=horas)

        result = self.client.table('reunioes')\
            .select('*')\
            .gte('data_inicio', agora.isoformat())\
            .lte('data_inicio', limite.isoformat())\
            .eq('status', 'agendada')\
            .execute()

        return result.data

    # === STORAGE ===

    async def upload_file(
        self,
        bucket: str,
        file_path: str,
        file_data: bytes,
        content_type: str
    ) -> str:
        """
        Faz upload de arquivo para Supabase Storage.

        Args:
            bucket: Nome do bucket
            file_path: Caminho do arquivo (ex: audios/123/audio.mp3)
            file_data: Bytes do arquivo
            content_type: MIME type

        Returns:
            URL pública do arquivo
        """
        self.client.storage.from_(bucket).upload(
            file_path,
            file_data,
            {"content-type": content_type}
        )

        # Obter URL pública
        url = self.client.storage.from_(bucket).get_public_url(file_path)
        return url


# ==============================================================================
# ELEVENLABS CLIENT
# ==============================================================================

class ElevenLabsClient:
    """
    Cliente para ElevenLabs Text-to-Speech API.

    Modelo: Eleven Multilingual v2
    """

    def __init__(self, api_key: str, voice_id: str):
        """
        Inicializa cliente ElevenLabs.

        Args:
            api_key: API key da ElevenLabs
            voice_id: ID da voz escolhida
        """
        self.api_key = api_key
        self.voice_id = voice_id
        self.base_url = "https://api.elevenlabs.io/v1"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def text_to_speech(
        self,
        text: str,
        model_id: str = "eleven_multilingual_v2",
        stability: float = 0.6,
        similarity_boost: float = 0.8,
        style: float = 0.2
    ) -> bytes:
        """
        Converte texto em áudio.

        Args:
            text: Texto para converter
            model_id: ID do modelo (eleven_multilingual_v2)
            stability: Estabilidade da voz (0-1)
            similarity_boost: Similaridade com voz original (0-1)
            style: Estilo/expressividade (0-1)

        Returns:
            Bytes do áudio (MP3)
        """
        url = f"{self.base_url}/text-to-speech/{self.voice_id}/stream"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": True
            }
        }

        try:
            async with self.client as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()

                logger.info(f"Áudio gerado: {text[:50]}...")
                return response.content
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}")
            raise

    async def close(self):
        """Fecha conexão HTTP."""
        await self.client.aclose()


# ==============================================================================
# RABBITMQ CLIENT
# ==============================================================================

class RabbitMQClient:
    """
    Cliente para RabbitMQ (fila de mensagens).

    Implementa pattern de Work Queue com confirmações.
    """

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 5672,
        username: str = 'guest',
        password: str = 'guest',
        queue_name: str = 'mensagens_whatsapp'
    ):
        """Inicializa cliente RabbitMQ."""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.connection = None
        self.channel = None

        self._connect()

    def _connect(self):
        """Estabelece conexão com RabbitMQ."""
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Declarar fila (idempotente)
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True  # Sobrevive a reinicialização
        )

        logger.info(f"RabbitMQ conectado na fila '{self.queue_name}'")

    def publish(self, message: Dict):
        """
        Publica mensagem na fila.

        Args:
            message: Dicionário com dados da mensagem
        """
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Mensagem persistente
            )
        )

        logger.info(f"Mensagem publicada na fila: {message.get('phone', 'N/A')}")

    def consume(self, callback):
        """
        Consome mensagens da fila.

        Args:
            callback: Função callback(ch, method, properties, body)
        """
        self.channel.basic_qos(prefetch_count=10)  # Max 10 mensagens simultâneas
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback,
            auto_ack=False  # Confirmação manual
        )

        logger.info("Aguardando mensagens...")
        self.channel.start_consuming()

    def close(self):
        """Fecha conexão."""
        if self.connection:
            self.connection.close()
            logger.info("RabbitMQ desconectado")


# ==============================================================================
# EXPORTAÇÕES
# ==============================================================================

__all__ = [
    'WhatsAppClient',
    'GoogleCalendarClient',
    'SupabaseClient',
    'ElevenLabsClient',
    'RabbitMQClient'
]

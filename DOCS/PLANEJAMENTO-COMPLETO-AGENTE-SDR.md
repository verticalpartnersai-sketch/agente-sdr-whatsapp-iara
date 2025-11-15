# 🤖 PLANEJAMENTO COMPLETO - AGENTE IA SDR WHATSAPP

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Arquitetura Modular Ultra-Eficiente](#arquitetura-modular)
3. [Estrutura de Banco de Dados](#estrutura-banco-dados)
4. [Sistema de RAG Híbrido](#rag-hibrido)
5. [Sistema de Memória e Buffer](#memoria-buffer)
6. [Integrações Externas](#integracoes)
7. [Sistema de Follow-Up Inteligente](#follow-up)
8. [Tools Customizadas](#tools)
9. [Processamento Multimodal](#multimodal)
10. [Credenciais Necessárias](#credenciais)
11. [Fluxo de Execução](#fluxo-execucao)
12. [Roadmap de Implementação](#roadmap)

---

## 🎯 VISÃO GERAL {#visao-geral}

### Objetivo
Criar um Agente IA SDR (Sales Development Representative) para WhatsApp 100% em Python + LangChain, com arquitetura modular ultra-eficiente (máximo 3 arquivos principais).

### Características Principais
- ✅ **Modular**: 3 arquivos Python principais
- ✅ **RAG Híbrido**: Semântico (60%) + BM25 (40%)
- ✅ **Memória Redis**: Buffer de mensagens + histórico conversacional
- ✅ **Multimodal**: Imagens, vídeos, áudios e documentos
- ✅ **Follow-Up Inteligente**: Sistema automatizado com regras de negócio
- ✅ **Integrações**: WhatsApp API, Google Calendar, Supabase, ElevenLabs, RabbitMQ
- ✅ **Humanizado**: Mensagens fragmentadas (20-30 palavras) com delay natural

### Stack Tecnológica
```yaml
linguagem: Python 3.11+
framework_ia: LangChain 0.1.0+
llm: OpenAI GPT-4o-mini
embeddings: text-embedding-3-small
banco_dados: Supabase (PostgreSQL + pgvector)
cache_memoria: Redis 7.0+
fila_mensagens: RabbitMQ
apis:
  - WhatsApp Business API (Oficial)
  - Google Calendar API
  - ElevenLabs API (Text-to-Speech)
```

---

## 🏗️ ARQUITETURA MODULAR ULTRA-EFICIENTE {#arquitetura-modular}

### Estrutura de Arquivos (3 Arquivos Principais)

```
agente-sdr-whatsapp/
│
├── 📁 config/
│   ├── .env                          # Variáveis de ambiente
│   ├── prompt.md                     # Prompt principal do agente
│   └── settings.py                   # Configurações centralizadas
│
├── 📁 core/
│   ├── agent.py                      # 🔥 ARQUIVO 1: Agente Principal + Tools
│   ├── memory.py                     # 🔥 ARQUIVO 2: Memória, Buffer e RAG
│   └── integrations.py               # 🔥 ARQUIVO 3: Integrações Externas
│
├── 📁 utils/
│   └── helpers.py                    # Funções auxiliares
│
├── main.py                           # Entry point da aplicação
├── requirements.txt                  # Dependências
└── README.md                         # Documentação
```

### Descrição dos 3 Arquivos Principais

#### 📄 ARQUIVO 1: `core/agent.py` (Agente + Tools)
**Responsabilidades:**
- Inicialização do agente LangChain
- Definição de todas as tools customizadas
- Lógica de execução e orquestração
- Classificação de intenção
- Formatação de respostas humanizadas

**Componentes:**
```python
# Tools
- WhatsAppTool (enviar mensagens, mídias)
- GoogleCalendarTools (agendar, cancelar, reagendar, consultar)
- SupabaseTools (CRUD leads, tags, follow-ups)
- ElevenLabsTool (gerar áudios)
- MediaAnalysisTool (processar imagens/vídeos/áudios/docs)

# Agente
- AgenteSDR (orquestrador principal)
- AgenteClassifica (classificar intenção do lead)
- FormatoResposta (humanizar e fragmentar mensagens)
```

#### 📄 ARQUIVO 2: `core/memory.py` (Memória + Buffer + RAG)
**Responsabilidades:**
- Gerenciamento de memória conversacional (Redis)
- Buffer de mensagens (30s de espera)
- RAG híbrido (semântico + BM25)
- Retrieval de conhecimento
- Embeddings e vector store

**Componentes:**
```python
# Memória
- RedisMemoryManager (histórico conversacional)
- MessageBuffer (buffer 30s)
- ConversationSummary (sumarização automática)

# RAG
- HybridRetriever (semântico 60% + BM25 40%)
- SupabaseVectorStore (pgvector)
- EmbeddingManager (text-embedding-3-small)
- KnowledgeBase (gerenciar base de conhecimento)
```

#### 📄 ARQUIVO 3: `core/integrations.py` (Integrações)
**Responsabilidades:**
- Clientes de APIs externas
- Webhooks (WhatsApp, RabbitMQ)
- Conexões com bancos de dados
- Rate limiting e retry logic
- Logging e monitoramento

**Componentes:**
```python
# Clientes
- WhatsAppClient (API oficial)
- GoogleCalendarClient (OAuth + CRUD eventos)
- SupabaseClient (banco de dados)
- ElevenLabsClient (TTS)
- RabbitMQClient (fila de mensagens)

# Webhooks
- WhatsAppWebhook (receber mensagens)
- CalendarWebhook (notificações de eventos)

# Managers
- ConnectionManager (gerenciar conexões)
- RateLimiter (controlar rate limits)
```

---

## 🗄️ ESTRUTURA DE BANCO DE DADOS {#estrutura-banco-dados}

### Supabase (PostgreSQL + pgvector)

#### Tabela: `leads_wpp`
```sql
CREATE TABLE leads_wpp (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),

    -- Controle de interações
    ultima_interacao_lead TIMESTAMPTZ,
    ultima_interacao_agente TIMESTAMPTZ,
    agendar_conversa TIMESTAMPTZ,

    -- Sistema de follow-up
    fup_enviado INTEGER DEFAULT 0,
    fup_ultima_data TIMESTAMPTZ,
    fup_proximo_horario TIMESTAMPTZ,

    -- Tags e status
    tags TEXT[] DEFAULT ARRAY['IA'],
    status VARCHAR(50) DEFAULT 'ativo',

    -- Metadados
    origem VARCHAR(100),
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_leads_telefone ON leads_wpp(telefone);
CREATE INDEX idx_leads_tags ON leads_wpp USING GIN(tags);
CREATE INDEX idx_leads_fup_proximo ON leads_wpp(fup_proximo_horario);
```

**Valores possíveis para `tags`:**
- `IA`: Permitido fazer follow-up automático
- `BREAK`: Interromper follow-up (desinteresse detectado)
- `reuniao_agendada`: Reunião confirmada
- `reuniao_cancelada`: Reunião cancelada
- `reuniao_reagendada`: Reunião remarcada
- `nao_interessado`: Lead explicitamente não interessado
- `atendimento_humano`: Transferir para atendente humano
- `alta_intencao`: Lead com alta intenção de compra
- `em_negociacao`: Em processo de negociação

#### Tabela: `knowledge` (Base de Conhecimento RAG)
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Conteúdo
    assunto VARCHAR(255) NOT NULL,
    conteudo TEXT NOT NULL,

    -- Q&A
    perguntas TEXT[],
    respostas TEXT[],

    -- RAG
    embedding vector(1536),  -- OpenAI text-embedding-3-small

    -- Metadados
    tags TEXT[],
    categoria VARCHAR(100),
    prioridade INTEGER DEFAULT 1,
    ativo BOOLEAN DEFAULT TRUE,

    -- Controle
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para similaridade semântica
CREATE INDEX idx_knowledge_embedding ON knowledge
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Índice full-text search (BM25)
CREATE INDEX idx_knowledge_conteudo_fts ON knowledge
USING gin(to_tsvector('portuguese', conteudo));

-- Índices adicionais
CREATE INDEX idx_knowledge_tags ON knowledge USING GIN(tags);
CREATE INDEX idx_knowledge_categoria ON knowledge(categoria);
```

**Função de busca híbrida:**
```sql
CREATE OR REPLACE FUNCTION hybrid_search(
    query_embedding vector(1536),
    query_text TEXT,
    match_count INT DEFAULT 5,
    semantic_weight FLOAT DEFAULT 0.6
)
RETURNS TABLE (
    id UUID,
    assunto VARCHAR,
    conteudo TEXT,
    similarity_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    WITH semantic_search AS (
        SELECT
            k.id,
            k.assunto,
            k.conteudo,
            1 - (k.embedding <=> query_embedding) as score
        FROM knowledge k
        WHERE k.ativo = TRUE
        ORDER BY k.embedding <=> query_embedding
        LIMIT match_count * 2
    ),
    keyword_search AS (
        SELECT
            k.id,
            k.assunto,
            k.conteudo,
            ts_rank(to_tsvector('portuguese', k.conteudo),
                    plainto_tsquery('portuguese', query_text)) as score
        FROM knowledge k
        WHERE
            k.ativo = TRUE
            AND to_tsvector('portuguese', k.conteudo) @@
                plainto_tsquery('portuguese', query_text)
        ORDER BY score DESC
        LIMIT match_count * 2
    )
    SELECT
        COALESCE(s.id, k.id) as id,
        COALESCE(s.assunto, k.assunto) as assunto,
        COALESCE(s.conteudo, k.conteudo) as conteudo,
        (COALESCE(s.score, 0) * semantic_weight +
         COALESCE(k.score, 0) * (1 - semantic_weight)) as similarity_score
    FROM semantic_search s
    FULL OUTER JOIN keyword_search k ON s.id = k.id
    ORDER BY similarity_score DESC
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

#### Tabela: `reunioes` (Eventos Google Calendar)
```sql
CREATE TABLE reunioes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads_wpp(id),

    -- Dados da reunião
    google_event_id VARCHAR(255) UNIQUE,
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,

    -- Horários
    data_inicio TIMESTAMPTZ NOT NULL,
    data_fim TIMESTAMPTZ NOT NULL,

    -- Participantes
    participantes JSONB,  -- [{email, nome, confirmado}]

    -- Status
    status VARCHAR(50) DEFAULT 'agendada',  -- agendada, confirmada, cancelada, concluida

    -- Lembretes
    lembrete_24h_enviado BOOLEAN DEFAULT FALSE,
    lembrete_2h_enviado BOOLEAN DEFAULT FALSE,

    -- Controle
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reunioes_lead ON reunioes(lead_id);
CREATE INDEX idx_reunioes_google_id ON reunioes(google_event_id);
CREATE INDEX idx_reunioes_data_inicio ON reunioes(data_inicio);
```

### Redis (Memória e Buffer)

#### Estrutura de Dados

**1. Histórico de Conversação**
```python
# Key pattern: chat_history:{telefone}
# Type: List
# TTL: 168 horas (7 dias)
# Estrutura:
{
    "role": "human" | "ai",
    "content": "mensagem",
    "timestamp": "2025-01-15T10:30:00Z",
    "metadata": {
        "message_id": "wamid.xxx",
        "type": "text" | "image" | "audio" | "video" | "document"
    }
}
```

**2. Buffer de Mensagens**
```python
# Key pattern: buffer:{telefone}
# Type: List
# TTL: 60 segundos
# Estrutura:
{
    "message_id": "wamid.xxx",
    "content": "mensagem",
    "timestamp": "2025-01-15T10:30:00Z",
    "media_url": "https://...",  # opcional
    "media_type": "image"  # opcional
}
```

**3. Session State**
```python
# Key pattern: session:{telefone}
# Type: Hash
# TTL: 24 horas
# Campos:
{
    "intent": "agendar_reuniao" | "duvida_produto" | "objecao",
    "context": {...},  # contexto da conversa
    "last_tool_used": "google_calendar",
    "awaiting_confirmation": true | false,
    "temp_data": {...}  # dados temporários
}
```

**4. Rate Limiting**
```python
# Key pattern: rate_limit:{telefone}
# Type: String (contador)
# TTL: 60 segundos
# Valor: número de mensagens enviadas no último minuto
```

---

## 🧠 SISTEMA DE RAG HÍBRIDO {#rag-hibrido}

### Estratégia Híbrida (60% Semântico + 40% BM25)

```python
# Implementação em core/memory.py

class HybridRetriever:
    """
    RAG Híbrido combinando:
    - 60% Busca Semântica (embeddings)
    - 40% Busca por Palavras-chave (BM25)
    """

    def __init__(self, supabase_client, embeddings):
        self.supabase = supabase_client
        self.embeddings = embeddings

        # Vector store para busca semântica
        self.vector_store = SupabaseVectorStore(
            client=supabase_client,
            embedding=embeddings,
            table_name="knowledge",
            query_name="hybrid_search"
        )

    async def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Busca híbrida com pesos ajustados.

        Retorna top-k documentos mais relevantes.
        """

        # 1. Gerar embedding da query
        query_embedding = await self.embeddings.aembed_query(query)

        # 2. Executar busca híbrida no Supabase
        results = self.supabase.rpc(
            'hybrid_search',
            {
                'query_embedding': query_embedding,
                'query_text': query,
                'match_count': k,
                'semantic_weight': 0.6  # 60% semântico, 40% BM25
            }
        ).execute()

        # 3. Converter para Documents
        documents = [
            Document(
                page_content=r['conteudo'],
                metadata={
                    'id': r['id'],
                    'assunto': r['assunto'],
                    'score': r['similarity_score']
                }
            )
            for r in results.data
        ]

        return documents
```

### Pipeline de Processamento de Conhecimento

```python
class KnowledgeManager:
    """Gerencia base de conhecimento e embeddings."""

    async def add_knowledge(
        self,
        assunto: str,
        conteudo: str,
        perguntas: List[str] = None,
        respostas: List[str] = None,
        tags: List[str] = None,
        categoria: str = None
    ):
        """Adiciona novo conhecimento com embedding."""

        # 1. Gerar embedding
        embedding = await self.embeddings.aembed_query(conteudo)

        # 2. Inserir no Supabase
        result = self.supabase.table('knowledge').insert({
            'assunto': assunto,
            'conteudo': conteudo,
            'perguntas': perguntas or [],
            'respostas': respostas or [],
            'tags': tags or [],
            'categoria': categoria,
            'embedding': embedding
        }).execute()

        return result.data[0]['id']

    async def bulk_import(self, file_path: str):
        """Importa conhecimento em massa de arquivo JSON/CSV."""
        # Implementação para importação em lote
        pass

    async def update_embeddings(self):
        """Atualiza embeddings de todos os documentos."""
        # Útil quando mudar modelo de embedding
        pass
```

---

## 💾 SISTEMA DE MEMÓRIA E BUFFER {#memoria-buffer}

### Arquitetura de Memória

```python
# core/memory.py

class RedisMemoryManager:
    """
    Gerencia memória conversacional com Redis.

    Features:
    - Histórico persistente (168h)
    - Sumarização automática (>1000 tokens)
    - Contexto deslizante (últimas 100 mensagens)
    """

    def __init__(self, redis_client):
        self.redis = redis_client
        self.max_messages = 100
        self.ttl_hours = 168

    async def add_message(
        self,
        phone: str,
        role: str,
        content: str,
        metadata: dict = None
    ):
        """Adiciona mensagem ao histórico."""

        key = f"chat_history:{phone}"

        message = {
            "role": role,  # "human" ou "ai"
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        # Adicionar à lista
        await self.redis.lpush(key, json.dumps(message))

        # Limitar tamanho
        await self.redis.ltrim(key, 0, self.max_messages - 1)

        # Definir TTL
        await self.redis.expire(key, self.ttl_hours * 3600)

    async def get_history(
        self,
        phone: str,
        limit: int = None
    ) -> List[dict]:
        """Recupera histórico de conversação."""

        key = f"chat_history:{phone}"
        limit = limit or self.max_messages

        messages = await self.redis.lrange(key, 0, limit - 1)

        return [json.loads(msg) for msg in messages]

    async def clear_history(self, phone: str):
        """Limpa histórico (útil para reset)."""
        await self.redis.delete(f"chat_history:{phone}")
```

### Sistema de Buffer de Mensagens (30 segundos)

```python
class MessageBuffer:
    """
    Agrupa mensagens enviadas rapidamente pelo lead.

    Aguarda 30 segundos desde a última mensagem antes de processar.
    Evita múltiplas respostas fragmentadas.
    """

    def __init__(self, redis_client):
        self.redis = redis_client
        self.window_seconds = 30
        self.tasks = {}  # {phone: Task}

    async def add_message(self, phone: str, message: dict):
        """
        Adiciona mensagem ao buffer.

        Se já existe timer, cancela e reinicia.
        """

        # Cancelar timer existente
        if phone in self.tasks:
            self.tasks[phone].cancel()

        # Adicionar mensagem ao buffer Redis
        key = f"buffer:{phone}"
        await self.redis.lpush(key, json.dumps(message))
        await self.redis.expire(key, 60)  # TTL 60s

        # Criar novo timer
        self.tasks[phone] = asyncio.create_task(
            self._process_after_delay(phone)
        )

    async def _process_after_delay(self, phone: str):
        """Aguarda 30s e processa buffer."""

        try:
            await asyncio.sleep(self.window_seconds)

            # Recuperar todas as mensagens do buffer
            key = f"buffer:{phone}"
            messages = await self.redis.lrange(key, 0, -1)

            if not messages:
                return

            # Limpar buffer
            await self.redis.delete(key)

            # Processar mensagens agrupadas
            parsed_messages = [json.loads(msg) for msg in reversed(messages)]

            # Combinar conteúdo
            combined_content = self._combine_messages(parsed_messages)

            # Enviar para agente processar
            await self._process_with_agent(phone, combined_content, parsed_messages)

        except asyncio.CancelledError:
            # Timer cancelado, nova mensagem chegou
            pass
        finally:
            # Remover task
            if phone in self.tasks:
                del self.tasks[phone]

    def _combine_messages(self, messages: List[dict]) -> str:
        """Combina múltiplas mensagens em uma única entrada."""

        text_parts = []
        media_items = []

        for msg in messages:
            if msg.get('content'):
                text_parts.append(msg['content'])

            if msg.get('media_url'):
                media_items.append({
                    'url': msg['media_url'],
                    'type': msg['media_type']
                })

        combined = "\n".join(text_parts)

        # Adicionar referências de mídia
        if media_items:
            media_desc = "\n".join([
                f"[{item['type'].upper()}]: {item['url']}"
                for item in media_items
            ])
            combined += f"\n\nMídias anexadas:\n{media_desc}"

        return combined

    async def _process_with_agent(
        self,
        phone: str,
        content: str,
        original_messages: List[dict]
    ):
        """Envia mensagens combinadas para o agente processar."""

        # Importar agente (evitar import circular)
        from core.agent import sdr_agent

        # Processar com agente
        response = await sdr_agent.process_message(
            phone=phone,
            message=content,
            metadata={'buffered_messages': original_messages}
        )

        return response
```

---

## 🔌 INTEGRAÇÕES EXTERNAS {#integracoes}

### 1. WhatsApp Business API (Oficial)

```python
# core/integrations.py

class WhatsAppClient:
    """
    Cliente para WhatsApp Business API Oficial.

    Suporta:
    - Envio de mensagens de texto
    - Envio de mídia (imagem, vídeo, áudio, documento)
    - Templates de mensagem
    - Mensagens interativas (botões, listas)
    """

    def __init__(self, access_token: str, phone_number_id: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/v18.0/{phone_number_id}"

    async def send_text(
        self,
        to: str,
        message: str,
        preview_url: bool = True
    ) -> dict:
        """Envia mensagem de texto."""

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

        return await self._request("POST", "/messages", json=payload)

    async def send_media(
        self,
        to: str,
        media_type: str,  # image, video, audio, document
        media_url: str,
        caption: str = None,
        filename: str = None
    ) -> dict:
        """Envia mídia (imagem, vídeo, áudio, documento)."""

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": media_type,
            media_type: {
                "link": media_url
            }
        }

        # Adicionar caption (apenas para image, video, document)
        if caption and media_type in ["image", "video", "document"]:
            payload[media_type]["caption"] = caption

        # Adicionar filename (apenas para document)
        if filename and media_type == "document":
            payload[media_type]["filename"] = filename

        return await self._request("POST", "/messages", json=payload)

    async def send_audio(self, to: str, audio_url: str) -> dict:
        """Envia mensagem de áudio."""
        return await self.send_media(to, "audio", audio_url)

    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "pt_BR",
        components: List[dict] = None
    ) -> dict:
        """Envia template pré-aprovado."""

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

        return await self._request("POST", "/messages", json=payload)

    async def mark_as_read(self, message_id: str) -> dict:
        """Marca mensagem como lida."""

        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }

        return await self._request("POST", "/messages", json=payload)

    async def _request(self, method: str, endpoint: str, **kwargs):
        """Faz requisição HTTP com retry e rate limiting."""

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        url = f"{self.base_url}{endpoint}"

        # Implementar retry logic e rate limiting
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                url,
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
```

**Webhook Handler:**
```python
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Recebe mensagens do WhatsApp.

    Processa:
    - Mensagens de texto
    - Mídias (imagem, vídeo, áudio, documento)
    - Status de entrega
    """

    data = await request.json()

    # Validar signature (segurança)
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_webhook_signature(signature, await request.body()):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Processar entrada
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            # Mensagens
            if "messages" in value:
                for message in value["messages"]:
                    await process_incoming_message(message)

            # Status de entrega
            if "statuses" in value:
                for status in value["statuses"]:
                    await process_message_status(status)

    return {"status": "ok"}

async def process_incoming_message(message: dict):
    """Processa mensagem recebida."""

    phone = message["from"]
    message_id = message["id"]
    message_type = message["type"]

    # Marcar como lida
    await whatsapp_client.mark_as_read(message_id)

    # Extrair conteúdo baseado no tipo
    if message_type == "text":
        content = message["text"]["body"]
        media_url = None
        media_type = None

    elif message_type in ["image", "video", "audio", "document"]:
        media_id = message[message_type]["id"]
        media_url = await whatsapp_client.get_media_url(media_id)
        content = message[message_type].get("caption", "")
        media_type = message_type

    else:
        # Tipo não suportado
        return

    # Adicionar ao buffer
    await message_buffer.add_message(phone, {
        "message_id": message_id,
        "content": content,
        "timestamp": message["timestamp"],
        "media_url": media_url,
        "media_type": media_type
    })
```

### 2. Google Calendar API

```python
class GoogleCalendarClient:
    """
    Cliente para Google Calendar API.

    Funcionalidades:
    - Listar horários disponíveis
    - Agendar reuniões
    - Cancelar reuniões
    - Reagendar reuniões
    - Atualizar participantes
    - Consultar eventos
    """

    def __init__(self, credentials_path: str):
        self.credentials = self._load_credentials(credentials_path)
        self.service = build('calendar', 'v3', credentials=self.credentials)
        self.calendar_id = 'primary'

    async def listar_horarios_disponiveis(
        self,
        data_inicio: datetime,
        data_fim: datetime,
        duracao_minutos: int = 60
    ) -> List[dict]:
        """
        Lista horários disponíveis em um período.

        Retorna slots de tempo livres.
        """

        # Buscar eventos existentes
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=data_inicio.isoformat(),
            timeMax=data_fim.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        eventos = events_result.get('items', [])

        # Calcular slots livres
        slots_disponiveis = self._calcular_slots_livres(
            data_inicio,
            data_fim,
            eventos,
            duracao_minutos
        )

        return slots_disponiveis

    async def agendar_reuniao(
        self,
        titulo: str,
        data_inicio: datetime,
        data_fim: datetime,
        participantes: List[str],
        descricao: str = None,
        localizacao: str = None
    ) -> dict:
        """Cria novo evento no calendário."""

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
                    {'method': 'email', 'minutes': 24 * 60},  # 24h antes
                    {'method': 'popup', 'minutes': 120},       # 2h antes
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
            sendUpdates='all'  # Enviar convites
        ).execute()

        return created_event

    async def cancelar_reuniao(
        self,
        event_id: str,
        notificar: bool = True
    ) -> dict:
        """Cancela evento."""

        send_updates = 'all' if notificar else 'none'

        self.service.events().delete(
            calendarId=self.calendar_id,
            eventId=event_id,
            sendUpdates=send_updates
        ).execute()

        return {"status": "cancelled", "event_id": event_id}

    async def reagendar_reuniao(
        self,
        event_id: str,
        nova_data_inicio: datetime,
        nova_data_fim: datetime,
        notificar: bool = True
    ) -> dict:
        """Reagenda evento existente."""

        # Buscar evento
        event = self.service.events().get(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()

        # Atualizar horários
        event['start']['dateTime'] = nova_data_inicio.isoformat()
        event['end']['dateTime'] = nova_data_fim.isoformat()

        # Salvar alterações
        updated_event = self.service.events().update(
            calendarId=self.calendar_id,
            eventId=event_id,
            body=event,
            sendUpdates='all' if notificar else 'none'
        ).execute()

        return updated_event

    async def atualizar_participantes(
        self,
        event_id: str,
        adicionar: List[str] = None,
        remover: List[str] = None
    ) -> dict:
        """Adiciona ou remove participantes."""

        # Buscar evento
        event = self.service.events().get(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()

        attendees = event.get('attendees', [])
        emails_atuais = {a['email'] for a in attendees}

        # Adicionar novos
        if adicionar:
            for email in adicionar:
                if email not in emails_atuais:
                    attendees.append({'email': email})

        # Remover
        if remover:
            attendees = [a for a in attendees if a['email'] not in remover]

        event['attendees'] = attendees

        # Salvar
        updated_event = self.service.events().update(
            calendarId=self.calendar_id,
            eventId=event_id,
            body=event,
            sendUpdates='all'
        ).execute()

        return updated_event

    async def consultar_reuniao(self, event_id: str) -> dict:
        """Busca detalhes de um evento."""

        event = self.service.events().get(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()

        return event

    def _calcular_slots_livres(
        self,
        inicio: datetime,
        fim: datetime,
        eventos: List[dict],
        duracao_minutos: int
    ) -> List[dict]:
        """Calcula intervalos de tempo livres."""

        # Horário comercial: 9h - 18h
        slots = []
        current = inicio

        while current < fim:
            # Verificar se está em horário comercial
            if current.hour < 9 or current.hour >= 18:
                current += timedelta(hours=1)
                continue

            slot_end = current + timedelta(minutes=duracao_minutos)

            # Verificar se slot está livre
            livre = True
            for event in eventos:
                event_start = datetime.fromisoformat(
                    event['start'].get('dateTime', event['start'].get('date'))
                )
                event_end = datetime.fromisoformat(
                    event['end'].get('dateTime', event['end'].get('date'))
                )

                # Verificar sobreposição
                if (current < event_end and slot_end > event_start):
                    livre = False
                    break

            if livre:
                slots.append({
                    'inicio': current.isoformat(),
                    'fim': slot_end.isoformat(),
                    'disponivel': True
                })

            current += timedelta(minutes=30)  # Incremento de 30min

        return slots[:10]  # Retornar até 10 slots
```

### 3. ElevenLabs (Text-to-Speech)

```python
class ElevenLabsClient:
    """Cliente para ElevenLabs TTS API."""

    def __init__(self, api_key: str, voice_id: str = None):
        self.api_key = api_key
        self.voice_id = voice_id or "21m00Tcm4TlvDq8ikWAM"  # Voz padrão (este ID da voz deve buscar do .env)
        self.base_url = "https://api.elevenlabs.io/v1"

    async def text_to_speech(
        self,
        text: str,
        output_path: str = None,
        voice_settings: dict = None
    ) -> bytes:
        """
        Converte texto em áudio.

        Retorna bytes do arquivo de áudio ou salva em arquivo.
        """

        url = f"{self.base_url}/text-to-speech/{self.voice_id}"

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": voice_settings or {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            audio_bytes = response.content

            # Salvar em arquivo se especificado
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(audio_bytes)

            return audio_bytes

    async def upload_to_whatsapp(self, audio_bytes: bytes) -> str:
        """
        Upload de áudio para WhatsApp e retorna URL.

        Usa API de mídia do WhatsApp.
        """

        # Salvar temporariamente
        temp_path = f"/tmp/audio_{uuid.uuid4()}.mp3"
        with open(temp_path, 'wb') as f:
            f.write(audio_bytes)

        # Upload para WhatsApp
        # (implementar upload de mídia)
        media_url = await whatsapp_client.upload_media(temp_path)

        # Limpar arquivo temporário
        os.remove(temp_path)

        return media_url
```

### 4. RabbitMQ (Fila de Mensagens)

```python
class RabbitMQClient:
    """
    Cliente RabbitMQ para processamento em fila.

    Features:
    - Fila de mensagens (max 10 por batch)
    - Retry com backoff exponencial
    - Dead letter queue
    """

    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.connection = None
        self.channel = None

    async def connect(self):
        """Estabelece conexão com RabbitMQ."""

        self.connection = await aio_pika.connect_robust(
            self.connection_url,
            heartbeat=60
        )

        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)  # Max 10 mensagens

        # Declarar queues
        await self.channel.declare_queue(
            'whatsapp_messages',
            durable=True,
            arguments={
                'x-dead-letter-exchange': 'dlx',
                'x-message-ttl': 86400000  # 24h
            }
        )

        # Dead letter queue
        await self.channel.declare_queue(
            'whatsapp_messages_dlq',
            durable=True
        )

    async def publish_message(self, phone: str, message: dict):
        """Publica mensagem na fila."""

        payload = {
            'phone': phone,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'retry_count': 0
        }

        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key='whatsapp_messages'
        )

    async def consume_messages(self, callback):
        """Consome mensagens da fila."""

        queue = await self.channel.get_queue('whatsapp_messages')

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    payload = json.loads(message.body.decode())

                    try:
                        # Processar mensagem
                        await callback(payload)

                    except Exception as e:
                        # Retry logic
                        if payload['retry_count'] < 3:
                            payload['retry_count'] += 1
                            await asyncio.sleep(2 ** payload['retry_count'])
                            await self.publish_message(
                                payload['phone'],
                                payload['message']
                            )
                        else:
                            # Mover para DLQ
                            logger.error(f"Failed after 3 retries: {e}")
```

---

## ⏰ SISTEMA DE FOLLOW-UP INTELIGENTE {#follow-up}

### Regras de Follow-Up

```yaml
janela_total: 72 horas (3 dias)
horario_permitido: 07:00 - 21:00
max_tentativas: 3

timeline:
  follow_up_1: 30 minutos após última mensagem do agente
  follow_up_2: 4 horas após follow_up_1
  follow_up_3: 12 horas após follow_up_2

tags_bloqueadas:
  - reuniao_agendada
  - reuniao_cancelada
  - reuniao_reagendada
  - nao_interessado
  - atendimento_humano
  - BREAK

reset_contador:
  - Lead responde à qualquer mensagem
  - Lead agenda reunião
  - Lead solicita nova conversa
```

### Implementação

```python
# core/agent.py - Follow-Up Manager

class FollowUpManager:
    """
    Gerencia follow-ups automáticos.

    Sistema inteligente que:
    - Respeita janela de 72h
    - Opera apenas 7h-21h
    - Analisa contexto antes de enviar
    - Detecta desinteresse
    """

    def __init__(self, supabase_client, whatsapp_client):
        self.supabase = supabase_client
        self.whatsapp = whatsapp_client

        # Timeline de follow-ups (em minutos)
        self.follow_up_timeline = [30, 240, 720]  # 30min, 4h, 12h

        # Horário permitido
        self.hora_inicio = 7
        self.hora_fim = 21

        # Tags que bloqueiam follow-up
        self.tags_bloqueadas = {
            'reuniao_agendada',
            'reuniao_cancelada',
            'reuniao_reagendada',
            'nao_interessado',
            'atendimento_humano',
            'BREAK'
        }

    async def agendar_follow_up(self, lead_id: str, phone: str):
        """
        Agenda próximo follow-up para um lead.

        Verifica:
        1. Tags bloqueadas
        2. Contador de follow-ups
        3. Janela de 72h
        4. Horário comercial
        """

        # Buscar lead
        lead = await self._get_lead(lead_id)

        # Verificar se pode fazer follow-up
        if not await self._pode_fazer_followup(lead):
            return None

        # Calcular próximo horário
        proximo_horario = await self._calcular_proximo_horario(lead)

        if not proximo_horario:
            return None

        # Atualizar no banco
        await self.supabase.table('leads_wpp').update({
            'fup_proximo_horario': proximo_horario.isoformat()
        }).eq('id', lead_id).execute()

        return proximo_horario

    async def executar_follow_ups_pendentes(self):
        """
        Executa follow-ups agendados.

        Chamado por cron job a cada 5 minutos.
        """

        # Buscar leads com follow-up pendente
        now = datetime.utcnow()

        result = await self.supabase.table('leads_wpp').select('*').lte(
            'fup_proximo_horario',
            now.isoformat()
        ).is_('fup_proximo_horario', 'not.null').execute()

        leads = result.data

        for lead in leads:
            try:
                await self._processar_follow_up(lead)
            except Exception as e:
                logger.error(f"Erro no follow-up {lead['id']}: {e}")

    async def _processar_follow_up(self, lead: dict):
        """Processa follow-up individual."""

        # Verificar novamente se pode enviar
        if not await self._pode_fazer_followup(lead):
            await self._limpar_follow_up(lead['id'])
            return

        # Analisar contexto da conversa
        tags = await self._analisar_contexto_conversa(lead['telefone'])

        # Se detectou desinteresse, adicionar tag BREAK
        if 'BREAK' in tags:
            await self._adicionar_tag(lead['id'], 'BREAK')
            await self._limpar_follow_up(lead['id'])
            return

        # Gerar mensagem de follow-up personalizada
        mensagem = await self._gerar_mensagem_followup(
            lead,
            tentativa=lead['fup_enviado'] + 1
        )

        # Enviar mensagem
        await self.whatsapp.send_text(lead['telefone'], mensagem)

        # Atualizar contador
        novo_contador = lead['fup_enviado'] + 1

        await self.supabase.table('leads_wpp').update({
            'fup_enviado': novo_contador,
            'fup_ultima_data': datetime.utcnow().isoformat(),
            'fup_proximo_horario': None,
            'ultima_interacao_agente': datetime.utcnow().isoformat()
        }).eq('id', lead['id']).execute()

        # Se não atingiu o máximo, agendar próximo
        if novo_contador < 3:
            await self.agendar_follow_up(lead['id'], lead['telefone'])

    async def _pode_fazer_followup(self, lead: dict) -> bool:
        """Verifica se pode fazer follow-up."""

        # Verificar tags bloqueadas
        tags = set(lead.get('tags', []))
        if tags & self.tags_bloqueadas:
            return False

        # Verificar contador
        if lead.get('fup_enviado', 0) >= 3:
            return False

        # Verificar janela de 72h
        ultima_interacao = lead.get('ultima_interacao_agente')
        if ultima_interacao:
            ultima = datetime.fromisoformat(ultima_interacao)
            if datetime.utcnow() - ultima > timedelta(hours=72):
                return False

        return True

    async def _calcular_proximo_horario(self, lead: dict) -> datetime:
        """Calcula próximo horário de follow-up."""

        tentativa = lead.get('fup_enviado', 0)

        if tentativa >= len(self.follow_up_timeline):
            return None

        # Minutos até próximo follow-up
        minutos = self.follow_up_timeline[tentativa]

        # Calcular horário base
        base = datetime.utcnow() + timedelta(minutes=minutos)

        # Ajustar para horário comercial
        horario_ajustado = await self._ajustar_horario_comercial(base)

        return horario_ajustado

    async def _ajustar_horario_comercial(self, dt: datetime) -> datetime:
        """Ajusta horário para janela 7h-21h."""

        # Converter para timezone local (America/Sao_Paulo)
        local_tz = pytz.timezone('America/Sao_Paulo')
        dt_local = dt.astimezone(local_tz)

        # Se antes das 7h, agendar para 7h do mesmo dia
        if dt_local.hour < self.hora_inicio:
            dt_local = dt_local.replace(
                hour=self.hora_inicio,
                minute=0,
                second=0
            )

        # Se depois das 21h, agendar para 7h do próximo dia
        elif dt_local.hour >= self.hora_fim:
            dt_local = (dt_local + timedelta(days=1)).replace(
                hour=self.hora_inicio,
                minute=0,
                second=0
            )

        return dt_local.astimezone(pytz.utc)

    async def _analisar_contexto_conversa(self, phone: str) -> Set[str]:
        """
        Analisa histórico da conversa para detectar desinteresse.

        Retorna tags identificadas (ex: BREAK se desinteressado).
        """

        # Buscar histórico de mensagens
        from core.memory import redis_memory
        history = await redis_memory.get_history(phone, limit=10)

        if not history:
            return set()

        # Montar contexto
        contexto = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in reversed(history)
        ])

        # Usar LLM para análise de sentimento/intenção
        prompt = f"""
Analise a conversa abaixo e identifique se o lead demonstra:
1. Desinteresse explícito
2. Sinais de irritação
3. Pedidos para parar contato

Conversa:
{contexto}

Responda apenas com uma das opções:
- CONTINUAR (se lead está engajado ou neutro)
- BREAK (se detectar desinteresse/irritação)
"""

        from core.agent import llm
        response = await llm.ainvoke(prompt)

        tags = set()
        if 'BREAK' in response.content:
            tags.add('BREAK')

        return tags

    async def _gerar_mensagem_followup(
        self,
        lead: dict,
        tentativa: int
    ) -> str:
        """Gera mensagem personalizada de follow-up."""

        # Templates baseados na tentativa (LEMBRE-SE: As mensagens de Follow-up DEVEM ser extraidas do PROMPT do Agente.)
        templates = {
            1: """Oi {nome}! 👋

Notei que não conseguimos finalizar nossa conversa.

Você ainda tem interesse em conhecer nossa solução?""",

            2: """Oi {nome}!

Entendo que você deve estar com a agenda cheia.

Que tal marcarmos um horário que funcione melhor para você?

Tenho alguns horários disponíveis nos próximos dias.""",

            3: """Oi {nome},

Essa é minha última tentativa de contato.

Se você ainda tiver interesse, estou à disposição para ajudar.

Caso contrário, respeito totalmente sua decisão! 🙂"""
        }

        template = templates.get(tentativa, templates[3])

        return template.format(nome=lead.get('nome', 'Olá'))

    async def resetar_contador(self, lead_id: str):
        """Reseta contador de follow-up quando lead responde."""

        await self.supabase.table('leads_wpp').update({
            'fup_enviado': 0,
            'fup_ultima_data': None,
            'fup_proximo_horario': None
        }).eq('id', lead_id).execute()
```

### Cron Job para Follow-Ups

```python
# main.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', minute='*/5')  # A cada 5 minutos
async def executar_followups():
    """Job que executa follow-ups pendentes."""

    try:
        await follow_up_manager.executar_follow_ups_pendentes()
        logger.info("Follow-ups executados com sucesso")
    except Exception as e:
        logger.error(f"Erro ao executar follow-ups: {e}")

# Lembrete de reuniões
@scheduler.scheduled_job('cron', hour='*')  # A cada hora
async def verificar_lembretes_reunioes():
    """Verifica reuniões que precisam de lembrete."""

    try:
        await enviar_lembretes_reunioes()
        logger.info("Lembretes verificados")
    except Exception as e:
        logger.error(f"Erro ao verificar lembretes: {e}")

# Iniciar scheduler
scheduler.start()
```

---

## 🛠️ TOOLS CUSTOMIZADAS {#tools}

### Definição de Todas as Tools

```python
# core/agent.py - Tools Definition

from langchain_core.tools import tool
from pydantic import BaseModel, Field

# ==================== WHATSAPP TOOLS ====================

class WhatsAppSendInput(BaseModel):
    phone: str = Field(description="Número de telefone no formato internacional")
    message: str = Field(description="Mensagem a ser enviada")

@tool("send_whatsapp_message", args_schema=WhatsAppSendInput)
async def send_whatsapp_message(phone: str, message: str) -> str:
    """
    Envia mensagem de texto via WhatsApp.

    Use quando precisar enviar mensagem de texto para o lead.
    """
    try:
        result = await whatsapp_client.send_text(phone, message)
        return f"Mensagem enviada com sucesso. ID: {result['messages'][0]['id']}"
    except Exception as e:
        return f"Erro ao enviar mensagem: {str(e)}"


class WhatsAppMediaInput(BaseModel):
    phone: str = Field(description="Número de telefone")
    media_url: str = Field(description="URL da mídia")
    media_type: str = Field(description="Tipo: image, video, audio, document")
    caption: str = Field(None, description="Legenda opcional")

@tool("send_whatsapp_media", args_schema=WhatsAppMediaInput)
async def send_whatsapp_media(
    phone: str,
    media_url: str,
    media_type: str,
    caption: str = None
) -> str:
    """
    Envia mídia (imagem, vídeo, áudio, documento) via WhatsApp.

    Use quando precisar enviar arquivos de mídia para o lead.
    """
    try:
        result = await whatsapp_client.send_media(
            phone, media_type, media_url, caption
        )
        return f"Mídia enviada com sucesso. ID: {result['messages'][0]['id']}"
    except Exception as e:
        return f"Erro ao enviar mídia: {str(e)}"


# ==================== GOOGLE CALENDAR TOOLS ====================

class CalendarListSlotsInput(BaseModel):
    data_inicio: str = Field(description="Data início (ISO 8601)")
    data_fim: str = Field(description="Data fim (ISO 8601)")
    duracao_minutos: int = Field(60, description="Duração em minutos")

@tool("consulta_horarios", args_schema=CalendarListSlotsInput)
async def consulta_horarios(
    data_inicio: str,
    data_fim: str,
    duracao_minutos: int = 60
) -> str:
    """
    Lista horários disponíveis no Google Calendar.

    Use quando lead perguntar sobre disponibilidade ou
    quiser agendar reunião.
    """
    try:
        inicio = datetime.fromisoformat(data_inicio)
        fim = datetime.fromisoformat(data_fim)

        slots = await calendar_client.listar_horarios_disponiveis(
            inicio, fim, duracao_minutos
        )

        # Formatar resposta
        if not slots:
            return "Não há horários disponíveis neste período."

        horarios_formatados = []
        for slot in slots:
            dt = datetime.fromisoformat(slot['inicio'])
            horarios_formatados.append(
                dt.strftime("%d/%m/%Y às %H:%M")
            )

        return "Horários disponíveis:\n" + "\n".join(
            f"- {h}" for h in horarios_formatados
        )

    except Exception as e:
        return f"Erro ao consultar horários: {str(e)}"


class CalendarScheduleInput(BaseModel):
    titulo: str = Field(description="Título da reunião")
    data_inicio: str = Field(description="Data/hora início (ISO 8601)")
    data_fim: str = Field(description="Data/hora fim (ISO 8601)")
    participantes: list[str] = Field(description="Lista de emails")
    descricao: str = Field(None, description="Descrição opcional")

@tool("agenda_reunioes", args_schema=CalendarScheduleInput)
async def agenda_reunioes(
    titulo: str,
    data_inicio: str,
    data_fim: str,
    participantes: list[str],
    descricao: str = None
) -> str:
    """
    Agenda nova reunião no Google Calendar.

    Use quando lead confirmar horário para reunião.
    SEMPRE consulte horários disponíveis antes de agendar.
    """
    try:
        inicio = datetime.fromisoformat(data_inicio)
        fim = datetime.fromisoformat(data_fim)

        event = await calendar_client.agendar_reuniao(
            titulo, inicio, fim, participantes, descricao
        )

        # Registrar no banco
        await supabase_client.table('reunioes').insert({
            'lead_id': '<lead_id>',  # Pegar do contexto
            'google_event_id': event['id'],
            'titulo': titulo,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'participantes': participantes,
            'status': 'agendada'
        }).execute()

        # Atualizar tag do lead
        # (implementar lógica para pegar lead_id do contexto)

        meet_link = event.get('hangoutLink', 'N/A')

        return f"""Reunião agendada com sucesso! ✅

Título: {titulo}
Data: {inicio.strftime('%d/%m/%Y às %H:%M')}
Link Google Meet: {meet_link}

Convites enviados para: {', '.join(participantes)}"""

    except Exception as e:
        return f"Erro ao agendar reunião: {str(e)}"


class CalendarCancelInput(BaseModel):
    event_id: str = Field(description="ID do evento no Google Calendar")

@tool("cancela_reunioes", args_schema=CalendarCancelInput)
async def cancela_reunioes(event_id: str) -> str:
    """
    Cancela reunião agendada.

    Use quando lead solicitar cancelamento.
    """
    try:
        await calendar_client.cancelar_reuniao(event_id, notificar=True)

        # Atualizar no banco
        await supabase_client.table('reunioes').update({
            'status': 'cancelada'
        }).eq('google_event_id', event_id).execute()

        return "Reunião cancelada com sucesso. Notificações enviadas aos participantes."

    except Exception as e:
        return f"Erro ao cancelar reunião: {str(e)}"


class CalendarRescheduleInput(BaseModel):
    event_id: str = Field(description="ID do evento")
    nova_data_inicio: str = Field(description="Nova data/hora início")
    nova_data_fim: str = Field(description="Nova data/hora fim")

@tool("reagenda_reunioes", args_schema=CalendarRescheduleInput)
async def reagenda_reunioes(
    event_id: str,
    nova_data_inicio: str,
    nova_data_fim: str
) -> str:
    """
    Reagenda reunião existente.

    Use quando lead quiser mudar horário da reunião.
    """
    try:
        inicio = datetime.fromisoformat(nova_data_inicio)
        fim = datetime.fromisoformat(nova_data_fim)

        event = await calendar_client.reagendar_reuniao(
            event_id, inicio, fim, notificar=True
        )

        # Atualizar no banco
        await supabase_client.table('reunioes').update({
            'data_inicio': nova_data_inicio,
            'data_fim': nova_data_fim,
            'status': 'reagendada'
        }).eq('google_event_id', event_id).execute()

        return f"Reunião reagendada para {inicio.strftime('%d/%m/%Y às %H:%M')}. Notificações enviadas."

    except Exception as e:
        return f"Erro ao reagendar reunião: {str(e)}"


class CalendarUpdateInput(BaseModel):
    event_id: str = Field(description="ID do evento")
    adicionar_emails: list[str] = Field(None, description="Emails para adicionar")
    remover_emails: list[str] = Field(None, description="Emails para remover")

@tool("atualiza_informacoes", args_schema=CalendarUpdateInput)
async def atualiza_informacoes(
    event_id: str,
    adicionar_emails: list[str] = None,
    remover_emails: list[str] = None
) -> str:
    """
    Atualiza participantes da reunião.

    Use quando lead quiser adicionar ou remover participantes.
    """
    try:
        event = await calendar_client.atualizar_participantes(
            event_id,
            adicionar=adicionar_emails,
            remover=remover_emails
        )

        return "Participantes atualizados com sucesso. Notificações enviadas."

    except Exception as e:
        return f"Erro ao atualizar participantes: {str(e)}"


class CalendarQueryInput(BaseModel):
    event_id: str = Field(description="ID do evento")

@tool("consulta_reunioes", args_schema=CalendarQueryInput)
async def consulta_reunioes(event_id: str) -> str:
    """
    Consulta detalhes de uma reunião.

    Use quando lead perguntar sobre reunião agendada.
    """
    try:
        event = await calendar_client.consultar_reuniao(event_id)

        inicio = datetime.fromisoformat(event['start']['dateTime'])

        participantes = [a['email'] for a in event.get('attendees', [])]

        return f"""Detalhes da reunião:

Título: {event['summary']}
Data: {inicio.strftime('%d/%m/%Y às %H:%M')}
Duração: {event.get('duration', 'N/A')}
Participantes: {', '.join(participantes)}
Link: {event.get('hangoutLink', 'N/A')}"""

    except Exception as e:
        return f"Erro ao consultar reunião: {str(e)}"


# ==================== SUPABASE TOOLS ====================

class LeadUpdateInput(BaseModel):
    phone: str = Field(description="Telefone do lead")
    campo: str = Field(description="Campo a atualizar")
    valor: str = Field(description="Novo valor")

@tool("atualizar_lead", args_schema=LeadUpdateInput)
async def atualizar_lead(phone: str, campo: str, valor: str) -> str:
    """
    Atualiza informações do lead no banco de dados.

    Use para atualizar nome, email, tags, etc.
    """
    try:
        await supabase_client.table('leads_wpp').update({
            campo: valor,
            'atualizado_em': datetime.utcnow().isoformat()
        }).eq('telefone', phone).execute()

        return f"Campo '{campo}' atualizado com sucesso."

    except Exception as e:
        return f"Erro ao atualizar lead: {str(e)}"


class LeadTagInput(BaseModel):
    phone: str = Field(description="Telefone do lead")
    tag: str = Field(description="Tag a adicionar")

@tool("adicionar_tag", args_schema=LeadTagInput)
async def adicionar_tag(phone: str, tag: str) -> str:
    """
    Adiciona tag ao lead.

    Use para marcar leads com status especiais:
    - reuniao_agendada
    - nao_interessado
    - atendimento_humano
    - BREAK
    """
    try:
        # Buscar tags atuais
        result = await supabase_client.table('leads_wpp').select(
            'tags'
        ).eq('telefone', phone).execute()

        tags_atuais = result.data[0].get('tags', [])

        if tag not in tags_atuais:
            tags_atuais.append(tag)

        # Atualizar
        await supabase_client.table('leads_wpp').update({
            'tags': tags_atuais
        }).eq('telefone', phone).execute()

        return f"Tag '{tag}' adicionada ao lead."

    except Exception as e:
        return f"Erro ao adicionar tag: {str(e)}"


# ==================== ELEVENLABS TOOLS ====================

class AudioGenerateInput(BaseModel):
    text: str = Field(description="Texto para converter em áudio")
    phone: str = Field(description="Telefone para enviar o áudio")

@tool("enviar_audio", args_schema=AudioGenerateInput)
async def enviar_audio(text: str, phone: str) -> str:
    """
    Gera áudio com ElevenLabs e envia via WhatsApp.

    Use quando lead solicitar áudio ou preferir comunicação por voz.
    """
    try:
        # Gerar áudio
        audio_bytes = await elevenlabs_client.text_to_speech(text)

        # Upload para WhatsApp
        audio_url = await elevenlabs_client.upload_to_whatsapp(audio_bytes)

        # Enviar
        await whatsapp_client.send_audio(phone, audio_url)

        return "Áudio enviado com sucesso."

    except Exception as e:
        return f"Erro ao enviar áudio: {str(e)}"


# ==================== MULTIMODAL TOOLS ====================

class MediaAnalysisInput(BaseModel):
    media_url: str = Field(description="URL da mídia")
    media_type: str = Field(description="Tipo: image, video, audio, document")
    question: str = Field(description="Pergunta sobre a mídia")

@tool("analisar_midia", args_schema=MediaAnalysisInput)
async def analisar_midia(
    media_url: str,
    media_type: str,
    question: str
) -> str:
    """
    Analisa mídia enviada pelo lead.

    Suporta: imagens, vídeos, áudios e documentos.
    Use quando lead enviar arquivo e você precisar entender o conteúdo.
    """
    try:
        # Implementar processamento multimodal
        # (ver seção de Processamento Multimodal)

        if media_type == "image":
            result = await process_image(media_url, question)
        elif media_type == "audio":
            result = await process_audio(media_url)
        elif media_type == "document":
            result = await process_document(media_url)
        elif media_type == "video":
            result = await process_video(media_url, question)
        else:
            return "Tipo de mídia não suportado."

        return result

    except Exception as e:
        return f"Erro ao analisar mídia: {str(e)}"


# ==================== KNOWLEDGE BASE TOOL ====================

class KnowledgeQueryInput(BaseModel):
    query: str = Field(description="Pergunta sobre produtos/serviços")

@tool("consultar_conhecimento", args_schema=KnowledgeQueryInput)
async def consultar_conhecimento(query: str) -> str:
    """
    Consulta base de conhecimento sobre produtos e serviços.

    Use quando lead fizer perguntas sobre:
    - Produtos
    - Preços
    - Funcionalidades
    - Casos de uso
    """
    try:
        # Buscar no RAG híbrido
        from core.memory import hybrid_retriever

        docs = await hybrid_retriever.retrieve(query, k=3)

        if not docs:
            return "Não encontrei informações sobre isso na base de conhecimento."

        # Montar contexto
        context = "\n\n".join([
            f"{doc.metadata['assunto']}:\n{doc.page_content}"
            for doc in docs
        ])

        return context

    except Exception as e:
        return f"Erro ao consultar conhecimento: {str(e)}"
```

---

## 🎨 PROCESSAMENTO MULTIMODAL {#multimodal}

### Implementação de Processamento de Mídias

```python
# core/agent.py - Multimodal Processing

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import base64

# LLM Multimodal
multimodal_llm = ChatOpenAI(
    model="gpt-4-vision-preview",
    max_tokens=1024
)

async def process_image(image_url: str, question: str) -> str:
    """Processa e analisa imagem usando GPT-4 Vision."""

    try:
        # Download da imagem
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            image_data = base64.b64encode(response.content).decode()

        # Criar mensagem com imagem
        message = HumanMessage(
            content=[
                {"type": "text", "text": question},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}",
                        "detail": "high"
                    }
                }
            ]
        )

        # Processar com GPT-4 Vision
        response = await multimodal_llm.ainvoke([message])

        return response.content

    except Exception as e:
        logger.error(f"Erro ao processar imagem: {e}")
        return "Não consegui analisar esta imagem. Pode descrever o que precisa?"


async def process_audio(audio_url: str) -> str:
    """Transcreve áudio usando Whisper."""

    try:
        # Download do áudio
        async with httpx.AsyncClient() as client:
            response = await client.get(audio_url)

        # Salvar temporariamente
        temp_path = f"/tmp/audio_{uuid.uuid4()}.ogg"
        with open(temp_path, 'wb') as f:
            f.write(response.content)

        # Transcrever com Whisper
        import openai

        with open(temp_path, 'rb') as audio_file:
            transcript = await openai.Audio.atranscribe(
                model="whisper-1",
                file=audio_file,
                language="pt"
            )

        # Limpar arquivo temp
        os.remove(temp_path)

        return transcript['text']

    except Exception as e:
        logger.error(f"Erro ao processar áudio: {e}")
        return "Não consegui transcrever este áudio. Pode me enviar por texto?"


async def process_document(doc_url: str) -> str:
    """Extrai texto de documentos (PDF, DOCX, etc)."""

    try:
        # Download do documento
        async with httpx.AsyncClient() as client:
            response = await client.get(doc_url)

        # Detectar tipo
        content_type = response.headers.get('content-type', '')

        temp_path = f"/tmp/doc_{uuid.uuid4()}"
        with open(temp_path, 'wb') as f:
            f.write(response.content)

        # Processar baseado no tipo
        if 'pdf' in content_type:
            from PyPDF2 import PdfReader

            reader = PdfReader(temp_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

        elif 'word' in content_type or 'docx' in content_type:
            from docx import Document

            doc = Document(temp_path)
            text = "\n".join([p.text for p in doc.paragraphs])

        else:
            # Tentar como texto puro
            with open(temp_path, 'r', encoding='utf-8') as f:
                text = f.read()

        # Limpar arquivo temp
        os.remove(temp_path)

        # Limitar tamanho
        if len(text) > 2000:
            text = text[:2000] + "..."

        return f"Conteúdo do documento:\n\n{text}"

    except Exception as e:
        logger.error(f"Erro ao processar documento: {e}")
        return "Não consegui ler este documento. Pode me enviar as informações por texto?"


async def process_video(video_url: str, question: str) -> str:
    """Processa vídeo extraindo frames chave."""

    try:
        import cv2

        # Download do vídeo
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(video_url)

        temp_video = f"/tmp/video_{uuid.uuid4()}.mp4"
        with open(temp_video, 'wb') as f:
            f.write(response.content)

        # Extrair frames (1 frame a cada 2 segundos)
        cap = cv2.VideoCapture(temp_video)
        fps = cap.get(cv2.CAP_PROP_FPS)

        frames = []
        frame_count = 0

        while cap.isOpened() and len(frames) < 5:  # Max 5 frames
            ret, frame = cap.read()
            if not ret:
                break

            # Pegar 1 frame a cada 2 segundos
            if frame_count % int(fps * 2) == 0:
                # Salvar frame
                frame_path = f"/tmp/frame_{uuid.uuid4()}.jpg"
                cv2.imwrite(frame_path, frame)
                frames.append(frame_path)

            frame_count += 1

        cap.release()

        # Analisar frames
        analyses = []
        for frame_path in frames:
            with open(frame_path, 'rb') as f:
                frame_data = base64.b64encode(f.read()).decode()

            analysis = await process_image(
                f"data:image/jpeg;base64,{frame_data}",
                question
            )
            analyses.append(analysis)

            # Limpar frame
            os.remove(frame_path)

        # Limpar vídeo
        os.remove(temp_video)

        # Combinar análises
        result = "Análise do vídeo:\n\n" + "\n\n".join([
            f"Frame {i+1}: {a}" for i, a in enumerate(analyses)
        ])

        return result

    except Exception as e:
        logger.error(f"Erro ao processar vídeo: {e}")
        return "Não consegui analisar este vídeo. Pode me descrever o conteúdo?"
```

---

## 🔑 CREDENCIAIS NECESSÁRIAS {#credenciais}

### Arquivo `.env`

```bash
# ==================== OPENAI ====================
OPENAI_API_KEY=sk-...

# ==================== WHATSAPP API ====================
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789
WHATSAPP_BUSINESS_ACCOUNT_ID=987654321
WHATSAPP_WEBHOOK_VERIFY_TOKEN=meu_token_secreto_123
WHATSAPP_WEBHOOK_SECRET=sha256_secret_key

# ==================== GOOGLE CALENDAR ====================
GOOGLE_CALENDAR_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CALENDAR_CLIENT_SECRET=GOCSPX-xxxxx
GOOGLE_CALENDAR_REDIRECT_URI=http://localhost:8000/oauth/callback
GOOGLE_CALENDAR_REFRESH_TOKEN=1//xxxxx
# OU usar Service Account:
GOOGLE_SERVICE_ACCOUNT_FILE=./config/google-service-account.json
GOOGLE_CALENDAR_ID=primary

# ==================== SUPABASE ====================
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx

# ==================== REDIS ====================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
# OU URL completa:
REDIS_URL=redis://localhost:6379/0

# ==================== RABBITMQ ====================
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
# OU URL completa:
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# ==================== ELEVENLABS ====================
ELEVENLABS_API_KEY=sk_xxxxx
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# ==================== OUTRAS CONFIGURAÇÕES ====================
VIDEO_REUNIAO_URL=https://xxxxx.supabase.co/storage/v1/object/public/videos/video-gessyan.mp4

# Ambiente
ENVIRONMENT=development  # development, staging, production
LOG_LEVEL=INFO

# Configurações do Agente
AGENT_NAME=SDR WhatsApp Bot
AGENT_TEMPERATURE=0.7
MAX_TOKENS=1000
```

### Instruções para Obter Credenciais

#### 1. WhatsApp Business API

**Passo a passo:**
1. Acesse [Meta for Developers](https://developers.facebook.com/)
2. Crie um App e ative WhatsApp Business API
3. Configure o número de telefone
4. Gere o `Access Token` permanente
5. Anote `Phone Number ID` e `Business Account ID`
6. Configure webhook apontando para seu servidor

**Credenciais necessárias:**
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_BUSINESS_ACCOUNT_ID`
- `WHATSAPP_WEBHOOK_VERIFY_TOKEN` (você define)
- `WHATSAPP_WEBHOOK_SECRET` (gerado pelo Meta)

#### 2. Google Calendar API

**Opção A: OAuth (usuário):**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie novo projeto
3. Ative Google Calendar API
4. Crie credenciais OAuth 2.0
5. Configure redirect URI
6. Gere refresh token

**Opção B: Service Account (recomendado):**
1. Crie Service Account no Google Cloud
2. Baixe arquivo JSON de credenciais
3. Compartilhe calendário com email do service account
4. Conceda permissão de "Make changes to events"

**Credenciais necessárias:**
- `GOOGLE_SERVICE_ACCOUNT_FILE` (caminho do arquivo JSON)
- OU `GOOGLE_CALENDAR_CLIENT_ID`, `CLIENT_SECRET`, `REFRESH_TOKEN`

#### 3. Supabase

1. Acesse [Supabase Dashboard](https://app.supabase.com/)
2. Crie novo projeto
3. Vá em Settings → API
4. Copie `URL` e `anon/public key`
5. Para operações admin, copie `service_role key`

**Credenciais necessárias:**
- `SUPABASE_URL`
- `SUPABASE_KEY` (anon key)
- `SUPABASE_SERVICE_KEY` (service role key)

#### 4. ElevenLabs

1. Acesse [ElevenLabs](https://elevenlabs.io/)
2. Crie conta e vá em Profile
3. Gere API Key
4. Escolha ou crie voz e copie Voice ID

**Credenciais necessárias:**
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID`

---

## 🔄 FLUXO DE EXECUÇÃO {#fluxo-execucao}

### Diagrama de Fluxo Principal

```mermaid
graph TD
    A[Lead envia mensagem] --> B[Webhook WhatsApp]
    B --> C{Tipo de mensagem?}

    C -->|Texto| D[Buffer 30s]
    C -->|Mídia| E[Download mídia]

    E --> F[Processar com GPT-4V/Whisper]
    F --> D

    D --> G[Combinar mensagens buffer]
    G --> H[Buscar histórico Redis]

    H --> I[Classificar Intenção]

    I --> J{Qual intenção?}

    J -->|Agendar| K[Tool: consulta_horarios]
    J -->|Dúvida| L[Tool: consultar_conhecimento]
    J -->|Objeção| M[Chain de objeções]
    J -->|Cancelar| N[Tool: cancela_reunioes]

    K --> O[RAG Híbrido]
    L --> O
    M --> O
    N --> P[Google Calendar]

    O --> Q[Gerar Resposta LLM]
    P --> Q

    Q --> R[Fragmentar mensagem]
    R --> S[Enviar via WhatsApp]

    S --> T[Salvar histórico Redis]
    T --> U[Atualizar Supabase]

    U --> V{Lead respondeu?}
    V -->|Sim| W[Resetar contador follow-up]
    V -->|Não| X[Agendar follow-up]

    W --> Z[Fim]
    X --> Z
```

### Fluxo de Follow-Up

```mermaid
graph TD
    A[Cron Job a cada 5min] --> B[Buscar follow-ups pendentes]

    B --> C{Há pendentes?}

    C -->|Não| D[Aguardar próximo cron]
    C -->|Sim| E[Para cada lead]

    E --> F{Verificar tags}

    F -->|Tag bloqueada| G[Cancelar follow-up]
    F -->|Tag OK| H{Horário 7h-21h?}

    H -->|Não| I[Reagendar para 7h]
    H -->|Sim| J[Analisar contexto conversa]

    J --> K{Detectou desinteresse?}

    K -->|Sim| L[Adicionar tag BREAK]
    K -->|Não| M[Gerar mensagem personalizada]

    L --> G
    M --> N[Enviar mensagem]

    N --> O[Incrementar contador]
    O --> P{Contador < 3?}

    P -->|Sim| Q[Agendar próximo follow-up]
    P -->|Não| R[Marcar como finalizado]

    Q --> S[Fim]
    R --> S
    G --> S
    I --> S
```

### Fluxo de Agendamento

```mermaid
graph TD
    A[Lead: quero agendar] --> B[Intent: agendar_reuniao]

    B --> C[Tool: consulta_horarios]
    C --> D[Google Calendar API]

    D --> E[Retornar slots disponíveis]
    E --> F[Apresentar opções ao lead]

    F --> G{Lead confirma horário?}

    G -->|Sim| H[Tool: agenda_reunioes]
    G -->|Sugere outro| I[Verificar disponibilidade]

    I --> J{Disponível?}
    J -->|Sim| H
    J -->|Não| F

    H --> K[Criar evento Google Calendar]
    K --> L[Inserir em tabela reunioes]
    L --> M[Adicionar tag reuniao_agendada]

    M --> N[Enviar confirmação com Meet link]
    N --> O[Enviar vídeo Gessyan Lion]

    O --> P[Agendar lembretes 24h e 2h]
    P --> Q[Fim]
```

---

## 📅 ROADMAP DE IMPLEMENTAÇÃO {#roadmap}

### Fase 1: Fundação (Semana 1)

**Prioridade: CRÍTICA**

#### 1.1 Setup Inicial
- [ ] Criar estrutura de diretórios
- [ ] Configurar ambiente virtual Python
- [ ] Instalar dependências (`requirements.txt`)
- [ ] Configurar `.env` com credenciais
- [ ] Setup Supabase (criar tabelas)
- [ ] Setup Redis local
- [ ] Setup RabbitMQ local

#### 1.2 Banco de Dados
- [ ] Criar tabela `leads_wpp` no Supabase
- [ ] Criar tabela `knowledge` com pgvector
- [ ] Criar tabela `reunioes`
- [ ] Implementar função `hybrid_search`
- [ ] Criar índices otimizados
- [ ] Inserir dados iniciais de conhecimento

#### 1.3 Integrações Básicas
- [ ] Implementar `SupabaseClient` (`core/integrations.py`)
- [ ] Implementar `RedisMemoryManager` (`core/memory.py`)
- [ ] Testar conexões com banco de dados

**Entregável:** Infraestrutura de dados funcional

---

### Fase 2: Agente Básico (Semana 2)

**Prioridade: ALTA**

#### 2.1 Agente Core
- [ ] Implementar `SDRAgent` base (`core/agent.py`)
- [ ] Configurar LangChain com OpenAI
- [ ] Criar prompt principal (`config/prompt.md`)
- [ ] Implementar `IntentClassifier`
- [ ] Implementar `ResponseFormatter` (fragmentação de mensagens)

#### 2.2 RAG Híbrido
- [ ] Implementar `HybridRetriever` (`core/memory.py`)
- [ ] Configurar embeddings OpenAI
- [ ] Integrar com Supabase vector store
- [ ] Testar busca semântica + BM25
- [ ] Implementar `KnowledgeManager`

#### 2.3 Memória e Buffer
- [ ] Implementar `MessageBuffer` (`core/memory.py`)
- [ ] Configurar buffer de 30 segundos
- [ ] Integrar memória Redis com agente
- [ ] Implementar histórico conversacional
- [ ] Testar persistência de contexto

**Entregável:** Agente conversacional básico funcional

---

### Fase 3: Integrações WhatsApp e Calendar (Semana 3)

**Prioridade: ALTA**

#### 3.1 WhatsApp Integration
- [ ] Implementar `WhatsAppClient` (`core/integrations.py`)
- [ ] Criar webhook handler
- [ ] Implementar envio de mensagens de texto
- [ ] Implementar envio de mídias
- [ ] Implementar rate limiting
- [ ] Configurar webhook no Meta

#### 3.2 Google Calendar
- [ ] Implementar `GoogleCalendarClient` (`core/integrations.py`)
- [ ] Configurar OAuth/Service Account
- [ ] Implementar listagem de horários
- [ ] Implementar agendamento
- [ ] Implementar cancelamento
- [ ] Implementar reagendamento
- [ ] Testar criação de eventos com Google Meet

#### 3.3 Tools Customizadas
- [ ] Criar tool `send_whatsapp_message`
- [ ] Criar tool `consulta_horarios`
- [ ] Criar tool `agenda_reunioes`
- [ ] Criar tool `cancela_reunioes`
- [ ] Criar tool `reagenda_reunioes`
- [ ] Criar tool `atualiza_informacoes`
- [ ] Criar tool `consultar_reunioes`
- [ ] Integrar tools com agente

**Entregável:** Agente pode enviar mensagens e agendar reuniões

---

### Fase 4: Follow-Up e Automação (Semana 4)

**Prioridade: MÉDIA-ALTA**

#### 4.1 Sistema de Follow-Up
- [ ] Implementar `FollowUpManager` (`core/agent.py`)
- [ ] Implementar lógica de agendamento (30min, 4h, 12h)
- [ ] Implementar verificação de horário comercial (7h-21h)
- [ ] Implementar análise de contexto para detectar desinteresse
- [ ] Implementar reset de contador quando lead responde
- [ ] Implementar verificação de tags bloqueadas

#### 4.2 Cron Jobs
- [ ] Configurar APScheduler
- [ ] Criar job de follow-ups (a cada 5 minutos)
- [ ] Criar job de lembretes de reunião (horário)
- [ ] Implementar envio de lembrete 24h antes
- [ ] Implementar envio de lembrete 2h antes
- [ ] Testar execução de jobs

#### 4.3 RabbitMQ
- [ ] Implementar `RabbitMQClient` (`core/integrations.py`)
- [ ] Configurar fila de mensagens (max 10)
- [ ] Implementar publisher
- [ ] Implementar consumer
- [ ] Implementar retry logic
- [ ] Configurar dead letter queue

**Entregável:** Sistema de follow-up automático funcionando

---

### Fase 5: Multimodal e TTS (Semana 5)

**Prioridade: MÉDIA**

#### 5.1 Processamento Multimodal
- [ ] Implementar `process_image` (GPT-4 Vision)
- [ ] Implementar `process_audio` (Whisper)
- [ ] Implementar `process_document` (PyPDF2/python-docx)
- [ ] Implementar `process_video` (extração de frames)
- [ ] Criar tool `analisar_midia`
- [ ] Testar com diferentes tipos de arquivo

#### 5.2 ElevenLabs TTS
- [ ] Implementar `ElevenLabsClient` (`core/integrations.py`)
- [ ] Configurar API ElevenLabs
- [ ] Implementar conversão text-to-speech
- [ ] Implementar upload de áudio para WhatsApp
- [ ] Criar tool `enviar_audio`
- [ ] Testar geração e envio de áudio

#### 5.3 Envio de Vídeo
- [ ] Fazer upload do vídeo do Gessyan para Supabase Storage
- [ ] Configurar URL pública
- [ ] Implementar envio automático após agendamento
- [ ] Testar envio de vídeo via WhatsApp

**Entregável:** Agente pode processar e enviar mídias

---

### Fase 6: Refinamento e Testes (Semana 6)

**Prioridade: ALTA**

#### 6.1 Otimizações
- [ ] Otimizar fragmentação de mensagens
- [ ] Melhorar prompts para respostas mais naturais
- [ ] Ajustar pesos do RAG híbrido
- [ ] Implementar caching estratégico
- [ ] Otimizar tempo de resposta (<5s)

#### 6.2 Testes
- [ ] Testar fluxo completo de agendamento
- [ ] Testar sistema de follow-up (simular 72h)
- [ ] Testar processamento de mídias
- [ ] Testar detecção de desinteresse
- [ ] Testar cancelamento e reagendamento
- [ ] Testar lembretes de reunião

#### 6.3 Logging e Monitoring
- [ ] Implementar logging estruturado
- [ ] Configurar alertas de erro
- [ ] Criar dashboard de métricas
- [ ] Implementar health checks
- [ ] Configurar retry e fallback strategies

**Entregável:** Sistema robusto e testado

---

### Fase 7: Deploy e Produção (Semana 7)

**Prioridade: CRÍTICA**

#### 7.1 Preparação para Produção
- [ ] Configurar variáveis de ambiente produção
- [ ] Migrar Redis para Redis Cloud
- [ ] Migrar RabbitMQ para CloudAMQP
- [ ] Configurar SSL/TLS
- [ ] Implementar secrets management

#### 7.2 Deploy
- [ ] Dockerizar aplicação
- [ ] Configurar Docker Compose
- [ ] Deploy em servidor (AWS/GCP/Azure)
- [ ] Configurar domínio e HTTPS
- [ ] Configurar webhook WhatsApp para produção
- [ ] Configurar OAuth Google Calendar

#### 7.3 Monitoramento
- [ ] Configurar APM (Application Performance Monitoring)
- [ ] Configurar alertas de uptime
- [ ] Configurar logs centralizados
- [ ] Criar runbook de incidentes
- [ ] Treinar equipe de operações

**Entregável:** Sistema em produção funcionando 24/7

---

### Métricas de Sucesso

**KPIs Técnicos:**
- ✅ Tempo de resposta médio: <3 segundos
- ✅ Uptime: >99.5%
- ✅ Taxa de erro: <0.5%
- ✅ Accuracy de classificação de intenção: >90%
- ✅ Taxa de conclusão de agendamentos: >70%

**KPIs de Negócio:**
- ✅ Taxa de conversão lead → reunião agendada: >15%
- ✅ Taxa de comparecimento em reuniões: >60%
- ✅ NPS (Net Promoter Score): >7
- ✅ Tempo médio até primeira reunião: <48h
- ✅ Volume de leads processados: >100/dia

---

## 📦 DEPENDÊNCIAS (requirements.txt)

```txt
# ==================== LANGCHAIN ====================
langchain==0.1.0
langchain-openai==0.0.5
langchain-community==0.0.13
langchain-core==0.1.10

# ==================== OPENAI ====================
openai==1.10.0

# ==================== BANCO DE DADOS ====================
supabase==2.3.0
redis==5.0.1
psycopg2-binary==2.9.9

# ==================== FILA DE MENSAGENS ====================
aio-pika==9.3.1
pika==1.3.2

# ==================== HTTP CLIENT ====================
httpx==0.26.0
requests==2.31.0

# ==================== WEB FRAMEWORK ====================
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# ==================== VALIDAÇÃO ====================
pydantic==2.5.3
pydantic-settings==2.1.0

# ==================== AGENDAMENTO ====================
apscheduler==3.10.4

# ==================== PROCESSAMENTO DE ARQUIVOS ====================
PyPDF2==3.0.1
python-docx==1.1.0
opencv-python==4.9.0.80
Pillow==10.2.0

# ==================== GOOGLE APIS ====================
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-api-python-client==2.116.0

# ==================== UTILIDADES ====================
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
pytz==2024.1
uuid==1.30

# ==================== LOGGING ====================
loguru==0.7.2
sentry-sdk==1.40.0

# ==================== DESENVOLVIMENTO ====================
pytest==8.0.0
pytest-asyncio==0.23.3
black==24.1.1
ruff==0.1.15
```

---

## 🎯 CONCLUSÃO

Este planejamento fornece uma arquitetura **modular, eficiente e escalável** para o Agente IA SDR WhatsApp utilizando **Python + LangChain**.

### Principais Diferenciais:

1. **Ultra-Modular**: Apenas 3 arquivos principais (`agent.py`, `memory.py`, `integrations.py`)
2. **RAG Híbrido Avançado**: Combina busca semântica (60%) + BM25 (40%) para máxima precisão
3. **Buffer Inteligente**: Aguarda 30s para agrupar mensagens fragmentadas do lead
4. **Follow-Up Automatizado**: Sistema completo com análise de contexto e detecção de desinteresse
5. **Multimodal Completo**: Processa imagens, vídeos, áudios e documentos
6. **Google Calendar Integrado**: Agendamento, cancelamento, reagendamento e lembretes automáticos
7. **Humanização Total**: Mensagens fragmentadas (20-30 palavras) com delays naturais
8. **Production-Ready**: RabbitMQ para filas, Redis para memória, Supabase para persistência

### Próximos Passos:

1. **Validar credenciais** necessárias
2. **Iniciar Fase 1** (Setup Inicial)
3. **Seguir roadmap** de 7 semanas
4. **Iterar e otimizar** baseado em feedback real

---

**Está pronto para começar a implementação! 🚀**

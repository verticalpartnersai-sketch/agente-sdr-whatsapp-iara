# 🤖 Agente IA SDR - WhatsApp

> Agente de inteligência artificial para Sales Development Representative (SDR) integrado com WhatsApp, Google Calendar, Supabase e ElevenLabs.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.20-green.svg)](https://python.langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📋 Índice

1. [Sobre o Projeto](#sobre-o-projeto)
2. [Funcionalidades](#funcionalidades)
3. [Arquitetura](#arquitetura)
4. [Tecnologias](#tecnologias)
5. [Instalação](#instalação)
6. [Configuração](#configuração)
7. [Uso](#uso)
8. [Estrutura do Projeto](#estrutura-do-projeto)
9. [API Reference](#api-reference)
10. [Contribuindo](#contribuindo)
11. [Licença](#licença)

---

## 🎯 Sobre o Projeto

Este é um agente de IA completo e profissional para atuar como SDR (Sales Development Representative) via WhatsApp. O agente é capaz de:

- 💬 **Conversar naturalmente** com leads via WhatsApp
- 📅 **Agendar reuniões** automaticamente no Google Calendar
- 🔄 **Fazer follow-ups inteligentes** (30min → 4h → 12h → 24h)
- 🧠 **RAG Híbrido** (60% semântico + 40% BM25) para busca de conhecimento
- 🎤 **Gerar áudios** via ElevenLabs quando necessário
- 📸 **Processar mídias** (imagens, vídeos, áudios, documentos)
- 🤝 **Humanização** com mensagens fragmentadas (20-30 palavras)

---

## ✨ Funcionalidades

### 🤖 Agente Conversacional

- Conversas naturais e humanizadas via LangChain
- Mensagens fragmentadas (20-30 palavras por mensagem)
- Delay natural entre mensagens (1-3 segundos)
- Classificação de intenções em tempo real
- Suporte a múltiplos idiomas (foco pt-BR)

### 📅 Integração Google Calendar

- ✅ Consulta de horários disponíveis
- ✅ Agendamento automático de reuniões com Google Meet
- ✅ Cancelamento de reuniões
- ✅ Reagendamento de reuniões
- ✅ Atualização de participantes
- ✅ Lembretes automáticos (24h e 2h antes)

### 🔄 Sistema de Follow-up Inteligente

- **Timeline automático**: 30min → 4h → 12h → 24h
- **Análise de desinteresse** antes de cada follow-up
- **Horário comercial**: Apenas 7h-21h
- **Janela de 72 horas** (3 dias)
- **Máximo 4 follow-ups** por lead

### 🧠 RAG Híbrido

- **60% Busca Semântica** (embeddings OpenAI)
- **40% BM25** (busca por palavras-chave)
- **pgvector** no Supabase para vetores
- **Full-text search** PostgreSQL

### 🎤 Geração de Áudios

- **ElevenLabs Multilingual v2**
- Conversão text-to-speech em tempo real
- Upload automático no Supabase Storage
- Envio via WhatsApp

### 📸 Processamento Multimodal

- **Imagens**: Análise via GPT-4o-mini (visão)
- **Vídeos**: Extração de frames + análise
- **Áudios**: Transcrição via gpt-4o-transcribe
- **Documentos**: Extração de texto (PDF, DOCX)

### 💾 Memória Conversacional

- **Redis** para histórico (7 dias, 100 mensagens)
- **Buffer de mensagens** (30s para agrupar múltiplas)
- **Estado de sessão** (contexto temporário)
- **Sumarização automática** para contextos longos

---

## 🏗️ Arquitetura

### Arquitetura Modular Ultra-Eficiente

```
┌─────────────────────────────────────────────────────────────┐
│                      WhatsApp Lead                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │   Webhook     │
         │   (FastAPI)   │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │   RabbitMQ    │  (Fila, max 10 req)
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ Message Buffer│  (Aguarda 30s)
         │    (Redis)    │
         └───────┬───────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │   AGENTE SDR (LangChain)   │
    │  ┌──────────────────────┐  │
    │  │  15+ Tools           │  │
    │  │  - WhatsApp          │  │
    │  │  - Google Calendar   │  │
    │  │  - Supabase          │  │
    │  │  - Knowledge Base    │  │
    │  │  - Media Analysis    │  │
    │  └──────────────────────┘  │
    └────────┬──────────┬────────┘
             │          │
             ▼          ▼
    ┌────────────┐  ┌────────────┐
    │   Redis    │  │  Supabase  │
    │  (Memória) │  │ (Database) │
    └────────────┘  └────────────┘
```

### 3 Arquivos Principais

1. **`core/agent.py`**: Agente SDR + 15 Tools customizadas
2. **`core/memory.py`**: Memória Redis + Buffer + RAG híbrido
3. **`core/integrations.py`**: Clientes de APIs externas

---

## 🛠️ Tecnologias

### Core

- **Python 3.11+**
- **LangChain 0.1.20** - Framework de IA
- **OpenAI GPT-4o-mini** - LLM principal
- **FastAPI** - Webhooks e API

### Banco de Dados

- **Supabase** (PostgreSQL + pgvector)
- **Redis** - Cache e memória
- **RabbitMQ** - Fila de mensagens

### APIs Externas

- **WhatsApp Business API** (Meta)
- **Google Calendar API**
- **ElevenLabs API** (TTS)
- **OpenAI API**

---

## 📦 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- Redis server
- RabbitMQ server
- Conta Supabase
- Credenciais das APIs (WhatsApp, Google Calendar, ElevenLabs, OpenAI)

### Passo 1: Clonar o repositório

```bash
git clone <seu-repositorio>
cd agente-sdr-whatsapp
```

### Passo 2: Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### Passo 3: Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Iniciar serviços

```bash
# Redis
redis-server

# RabbitMQ (Docker)
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

---

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Copie o arquivo de exemplo e preencha as credenciais:

```bash
cp config/.env.example .env
```

Edite `.env` com suas credenciais:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# ElevenLabs
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...

# WhatsApp
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_VERIFY_TOKEN=...

# Google Calendar
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=...

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
```

### 2. Supabase - Criar Tabelas

Execute o schema SQL no Supabase:

```bash
# Acesse o Supabase SQL Editor e execute
database/schema.sql
```

### 3. Google Calendar - Autenticação

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto
3. Ative a API do Google Calendar
4. Crie credenciais OAuth 2.0
5. Baixe `credentials.json` e salve em `config/google_credentials.json`

### 4. WhatsApp - Configurar Webhook

1. Acesse o [Meta Developers](https://developers.facebook.com/)
2. Configure o webhook apontando para: `https://seu-dominio.com/webhook/whatsapp`
3. Use o `WHATSAPP_VERIFY_TOKEN` configurado no `.env`

---

## 🚀 Uso

### Iniciar Aplicação

```bash
python main.py
```

A aplicação estará disponível em:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### Adicionar Conhecimento

```python
from core.memory import KnowledgeManager
from core.integrations import SupabaseClient
from langchain_openai import OpenAIEmbeddings

# Inicializar
supabase = SupabaseClient(url="...", key="...")
embeddings = OpenAIEmbeddings(api_key="...")
knowledge_mgr = KnowledgeManager(supabase, embeddings)

# Adicionar conhecimento
await knowledge_mgr.add_knowledge(
    assunto="Sobre a Vertical Partners",
    conteudo="A Vertical Partners é uma empresa especializada em...",
    tags=["empresa", "institucional"],
    categoria="institucional"
)
```

### Importação em Massa

```bash
# Prepare um arquivo JSON
# conhecimento.json:
[
  {
    "assunto": "Produto X",
    "conteudo": "Descrição do produto...",
    "perguntas": ["O que é o produto X?"],
    "respostas": ["É um produto que..."],
    "tags": ["produto"],
    "categoria": "produtos"
  }
]

# Importe
python -c "
from core.memory import KnowledgeManager
import asyncio

async def main():
    # ... inicializar managers
    await knowledge_mgr.bulk_import_from_json('conhecimento.json')

asyncio.run(main())
"
```

---

## 📂 Estrutura do Projeto

```
agente-sdr-whatsapp/
│
├── 📁 config/
│   ├── .env.example              # Exemplo de variáveis de ambiente
│   ├── settings.py               # Configurações centralizadas
│   ├── prompt.md                 # Prompt principal do agente
│   ├── prompt-followup.md        # Prompt de follow-ups
│   └── prompt-lembretes.md       # Prompt de lembretes
│
├── 📁 core/
│   ├── agent.py                  # 🔥 Agente SDR + Tools
│   ├── memory.py                 # 🔥 Memória, Buffer, RAG
│   ├── integrations.py           # 🔥 Clientes de APIs
│   └── followup.py               # Sistema de follow-up
│
├── 📁 database/
│   └── schema.sql                # Schema do Supabase
│
├── 📁 DOCS/
│   ├── ESTRUTURA-DO-AGENTE-SDR-WPP.md
│   ├── DOCUMENTACAO-COMPLETA-TECNOLOGIAS-2025.md
│   └── PLANEJAMENTO-COMPLETO-AGENTE-SDR.md
│
├── main.py                       # Entry point da aplicação
├── requirements.txt              # Dependências
└── README.md                     # Este arquivo
```

---

## 📚 API Reference

### Endpoints FastAPI

#### GET `/health`
Health check da aplicação.

**Response:**
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

#### GET `/webhook/whatsapp`
Verificação do webhook do WhatsApp (Meta).

**Query Params:**
- `hub.mode`: "subscribe"
- `hub.verify_token`: Token de verificação
- `hub.challenge`: Challenge do Meta

#### POST `/webhook/whatsapp`
Recebe mensagens do WhatsApp.

**Headers:**
- `X-Hub-Signature-256`: Assinatura do webhook

**Body:** Payload do WhatsApp (ver [docs oficiais](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks))

---

## 🧪 Testes

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=core --cov-report=html
```

---

## 📊 Monitoramento

### Logs

Logs são salvos em `logs/app.log` com rotação diária.

```bash
# Ver logs em tempo real
tail -f logs/app.log
```

### Métricas

TODO: Implementar dashboard de métricas (Prometheus + Grafana)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👥 Autores

- **Vertical Partners** - Desenvolvimento inicial
- **Claude Code** - Implementação técnica

---

## 🙏 Agradecimentos

- [LangChain](https://python.langchain.com/)
- [OpenAI](https://openai.com/)
- [Supabase](https://supabase.com/)
- [ElevenLabs](https://elevenlabs.io/)
- [Meta WhatsApp Business](https://developers.facebook.com/docs/whatsapp/)

---

## 📞 Suporte

Para suporte, abra uma issue no GitHub ou entre em contato via email.

---

**Desenvolvido com ❤️ pela Vertical Partners**

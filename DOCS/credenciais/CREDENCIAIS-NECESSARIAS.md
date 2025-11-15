# 🔐 CREDENCIAIS NECESSÁRIAS

Este documento lista todas as credenciais que você precisa fornecer para o Agente SDR funcionar.

---

## 📋 Checklist de Credenciais

### ✅ 1. WhatsApp Business API (Meta)

**O que você precisa:**

1. **Access Token** (`WHATSAPP_ACCESS_TOKEN`)
   - Obtido no Meta Developers Console
   - Token de longa duração recomendado

2. **Phone Number ID** (`WHATSAPP_PHONE_NUMBER_ID`)
   - ID do número de telefone business
   - Encontrado no console do WhatsApp Business

3. **Verify Token** (`WHATSAPP_VERIFY_TOKEN`)
   - Token customizado que você cria
   - Usado para verificar o webhook
   - Pode ser qualquer string segura (ex: `meu_token_secreto_123`)

4. **Webhook Secret** (`WHATSAPP_WEBHOOK_SECRET`)
   - Secret para validar assinatura do webhook
   - Encontrado nas configurações do app

**Como obter:**
1. Acesse: https://developers.facebook.com/
2. Crie um app WhatsApp Business
3. Configure o WhatsApp Business API
4. Anote as credenciais acima

---

### ✅ 2. Google Calendar API

**O que você precisa:**

1. **Client ID** (`GOOGLE_CLIENT_ID`)
2. **Client Secret** (`GOOGLE_CLIENT_SECRET`)
3. **Arquivo credentials.json**
   - Salvar em: `config/google_credentials.json`

**Como obter:**
1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto (ou use existente)
3. Ative a **Google Calendar API**
4. Vá em "Credenciais" → "Criar credenciais" → "ID do cliente OAuth 2.0"
5. Tipo de aplicativo: **Aplicativo para computador**
6. Configure URIs de redirecionamento:
   - `http://localhost:8000/oauth/callback`
7. Baixe o arquivo JSON e salve como `config/google_credentials.json`

**Scopes necessários:**
- `https://www.googleapis.com/auth/calendar`
- `https://www.googleapis.com/auth/calendar.events`

---

### ✅ 3. ElevenLabs API (Text-to-Speech)

**O que você precisa:**

1. **API Key** (`ELEVENLABS_API_KEY`)
   - Chave de API da ElevenLabs

2. **Voice ID** (`ELEVENLABS_VOICE_ID`)
   - ID da voz escolhida
   - Recomendado: Uma voz em português

**Como obter:**
1. Acesse: https://elevenlabs.io/
2. Crie uma conta
3. Vá em "Profile" → "API Keys"
4. Gere uma nova API Key
5. Em "Voices", escolha uma voz e copie o Voice ID

**Modelo a usar:** `eleven_multilingual_v2` (já configurado)

---

### ✅ 4. OpenAI API

**O que você precisa:**

1. **API Key** (`OPENAI_API_KEY`)
   - Chave de API da OpenAI

**Como obter:**
1. Acesse: https://platform.openai.com/
2. Crie uma conta
3. Vá em "API Keys"
4. Crie uma nova Secret Key
5. **IMPORTANTE**: Copie imediatamente (não será mostrada novamente)

**Modelos usados:**
- `gpt-4o-mini` - Conversação (configurado)
- `gpt-4o-transcribe` - Transcrição de áudio (configurado)
- `text-embedding-3-small` - Embeddings (configurado)

---

### ✅ 5. Supabase

**O que você precisa:**

1. **Project URL** (`SUPABASE_URL`)
   - URL do seu projeto Supabase
   - Formato: `https://xxxxx.supabase.co`

2. **Anon/Public Key** (`SUPABASE_KEY`)
   - Chave pública do projeto

3. **Service Role Key** (`SUPABASE_SERVICE_KEY`)
   - Chave de serviço (opcional, mas recomendado)

**Como obter:**
1. Acesse: https://supabase.com/
2. Crie uma conta e um novo projeto
3. Aguarde o projeto ser criado (~2 minutos)
4. Vá em "Settings" → "API"
5. Copie:
   - **URL**
   - **anon/public key**
   - **service_role key**

**Importante:** Execute o schema SQL:
```bash
# Acesse o Supabase SQL Editor
# Cole e execute o conteúdo de: database/schema.sql
```

---

### ✅ 6. Redis (Memória e Cache)

**O que você precisa:**

1. **Host** (`REDIS_HOST`)
   - Padrão: `localhost` (se rodando localmente)

2. **Port** (`REDIS_PORT`)
   - Padrão: `6379`

3. **Password** (`REDIS_PASSWORD`)
   - Opcional (deixe vazio se sem senha)

**Instalação local:**
```bash
# macOS
brew install redis
redis-server

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Docker
docker run -d --name redis -p 6379:6379 redis:latest
```

---

### ✅ 7. RabbitMQ (Fila de Mensagens)

**O que você precisa:**

1. **Host** (`RABBITMQ_HOST`)
   - Padrão: `localhost`

2. **Port** (`RABBITMQ_PORT`)
   - Padrão: `5672`

3. **User** (`RABBITMQ_USER`)
   - Padrão: `guest`

4. **Password** (`RABBITMQ_PASSWORD`)
   - Padrão: `guest`

**Instalação:**
```bash
# Docker (recomendado)
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management

# Acesse o dashboard: http://localhost:15672
# Usuário: guest / Senha: guest
```

---

## 📝 Resumo do .env

Após obter todas as credenciais, seu arquivo `.env` deve ficar assim:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# ElevenLabs
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...

# WhatsApp
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_VERIFY_TOKEN=meu_token_secreto_123
WHATSAPP_WEBHOOK_SECRET=...

# Google Calendar
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/oauth/callback
GOOGLE_CREDENTIALS_PATH=./config/google_credentials.json

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=...
SUPABASE_SERVICE_KEY=...

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Config
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## ✅ Checklist de Configuração

- [ ] OpenAI API Key obtida
- [ ] ElevenLabs API Key e Voice ID obtidos
- [ ] WhatsApp Business API configurado
- [ ] Google Calendar credentials.json baixado
- [ ] Supabase projeto criado e schema executado
- [ ] Redis rodando localmente
- [ ] RabbitMQ rodando localmente
- [ ] Arquivo `.env` criado e preenchido
- [ ] Dependências instaladas (`pip install -r requirements.txt`)

---

## 🚀 Próximos Passos

Após ter todas as credenciais:

1. **Configure o .env**
   ```bash
   cp config/.env.example .env
   # Edite .env com suas credenciais
   ```

2. **Execute o schema SQL no Supabase**
   - Acesse o SQL Editor do Supabase
   - Execute `database/schema.sql`

3. **Inicie os serviços**
   ```bash
   redis-server  # Terminal 1
   # RabbitMQ já está rodando via Docker
   ```

4. **Inicie a aplicação**
   ```bash
   python main.py
   ```

5. **Configure o webhook do WhatsApp**
   - Use ngrok para expor localhost: `ngrok http 8000`
   - Configure webhook: `https://seu-ngrok.io/webhook/whatsapp`

---

## ❓ Dúvidas?

Se tiver dificuldades para obter alguma credencial, consulte:
- **WhatsApp**: https://developers.facebook.com/docs/whatsapp/
- **Google Calendar**: https://developers.google.com/calendar/api/guides/overview
- **ElevenLabs**: https://elevenlabs.io/docs
- **OpenAI**: https://platform.openai.com/docs
- **Supabase**: https://supabase.com/docs

---

**Boa sorte com seu Agente SDR! 🚀**

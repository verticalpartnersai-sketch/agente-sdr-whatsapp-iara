# ⚡ Quick Start - Deploy no Easypanel

Guia rápido para colocar o Agente SDR WhatsApp em produção usando Easypanel (Hostinger).

---

## 📦 O que você precisa

### 1. Credenciais (obtenha todas antes de começar)

- ✅ OpenAI API Key
- ✅ ElevenLabs API Key + Voice ID
- ✅ WhatsApp Business API Token + Phone Number ID
- ✅ Google Calendar Credentials (JSON)
- ✅ Supabase URL + Key

**Veja o guia completo:** `CREDENCIAIS-NECESSARIAS.md`

### 2. Easypanel configurado

- ✅ Acesso ao painel Easypanel na Hostinger
- ✅ Domínio ou subdomínio configurado

---

## 🚀 Deploy em 5 passos

### Passo 1: Criar projeto no Easypanel

1. Acesse Easypanel
2. **"+ Create Project"** → **"Docker Compose"**
3. Nome: `agente-sdr-whatsapp`

### Passo 2: Conectar repositório

1. Conecte ao seu repositório Git (GitHub/GitLab)
2. Easypanel detectará automaticamente o `docker-compose.yml`

**OU** Cole manualmente o conteúdo de `docker-compose.yml`

### Passo 3: Configurar variáveis de ambiente

No Easypanel, adicione **TODAS** estas variáveis:

```bash
# === OPENAI ===
OPENAI_API_KEY=sk-...
OPENAI_MODEL_CHAT=gpt-4o-mini
OPENAI_MODEL_TRANSCRIBE=gpt-4o-transcribe
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# === ELEVENLABS ===
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...
ELEVENLABS_MODEL=eleven_multilingual_v2

# === WHATSAPP ===
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_BUSINESS_ACCOUNT_ID=...
WHATSAPP_WEBHOOK_VERIFY_TOKEN=MEU_TOKEN_SECRETO_123
WHATSAPP_WEBHOOK_SECRET=...

# === GOOGLE CALENDAR ===
GOOGLE_CALENDAR_ID=...
GOOGLE_CREDENTIALS_FILE=/app/config/google_credentials.json
GOOGLE_TOKEN_FILE=/app/config/google_token.json

# === SUPABASE ===
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=...

# === REDIS (INTERNO) ===
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=SUA_SENHA_REDIS_SEGURA
REDIS_DB=0

# === RABBITMQ (INTERNO) ===
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=SUA_SENHA_RABBITMQ_SEGURA
RABBITMQ_QUEUE_NAME=whatsapp_messages

# === AGENTE ===
COMPANY_NAME=Vertical Partners
PRODUCT_NAME=Agentes de IA
AGENT_NAME=Isabella
MESSAGE_BUFFER_SECONDS=30
MAX_FRAGMENT_WORDS=30
FOLLOWUP_CHECK_INTERVAL=5
```

⚠️ **IMPORTANTE:** Troque `SUA_SENHA_REDIS_SEGURA` e `SUA_SENHA_RABBITMQ_SEGURA` por senhas fortes!

### Passo 4: Configurar domínio

1. No Easypanel: **"Domains"**
2. Adicione: `whatsapp-agent.seudominio.com`
3. SSL configurado automaticamente ✅

### Passo 5: Deploy!

1. Clique em **"Deploy"**
2. Aguarde 3-5 minutos
3. Verifique logs: deve aparecer `Application startup complete`

---

## 🔗 Configurar Webhook WhatsApp

Agora configure o webhook no Meta Developers:

### URL do Webhook

```
https://whatsapp-agent.seudominio.com/webhook/whatsapp
```

### Token de Verificação

```
MEU_TOKEN_SECRETO_123
```

(Use o **mesmo** valor que você colocou em `WHATSAPP_WEBHOOK_VERIFY_TOKEN`)

### Passo a passo

1. Acesse: https://developers.facebook.com/
2. Seu App → WhatsApp → Configuration
3. **"Edit"** na seção Webhook
4. Cole a URL e o token
5. **"Verificar e salvar"**
6. Marque as subscriptions:
   - ✅ `messages`
   - ✅ `message_status` (opcional)

---

## ✅ Testar

### 1. Health Check

Abra no navegador:
```
https://whatsapp-agent.seudominio.com/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0"
}
```

### 2. Enviar mensagem teste

Envie uma mensagem pelo WhatsApp para o número configurado.

**O agente deve:**
- ✅ Receber a mensagem
- ✅ Processar com IA
- ✅ Responder automaticamente

### 3. Verificar logs

No Easypanel:
- Vá em **"Logs"** do serviço `agente-sdr`
- Deve ver: `INFO: Processando mensagens buffered de +55...`

---

## 🎉 Pronto!

Seu Agente IA SDR está funcionando em produção!

**Webhook configurado:** ✅
**SSL ativo:** ✅
**Agente respondendo:** ✅

---

## 🆘 Problemas?

### Webhook não verifica

1. Confirme que a URL está correta
2. Verifique se `WHATSAPP_WEBHOOK_VERIFY_TOKEN` está igual ao token do Meta
3. Teste manualmente:
   ```bash
   curl "https://whatsapp-agent.seudominio.com/webhook/whatsapp?hub.mode=subscribe&hub.challenge=1234&hub.verify_token=MEU_TOKEN_SECRETO_123"
   ```

### Agente não responde

1. Verifique logs no Easypanel
2. Confirme que Redis e RabbitMQ estão rodando
3. Teste o health check
4. Verifique todas as credenciais

### Mais ajuda

Veja o guia completo: **`DEPLOY-EASYPANEL.md`**

---

**Deploy feito com ❤️ usando Easypanel**

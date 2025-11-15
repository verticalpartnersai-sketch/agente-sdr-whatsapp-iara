# ⚙️ Configurar Variáveis de Ambiente no Easypanel

## 🚨 Erro Atual

Você está vendo este erro porque as variáveis de ambiente não foram configuradas:

```
The "OPENAI_API_KEY" variable is not set. Defaulting to a blank string.
The "ELEVENLABS_API_KEY" variable is not set. Defaulting to a blank string.
...
```

## ✅ Solução: Adicionar Variáveis no Easypanel

### Passo 1: Acessar Configuração de Variáveis

1. Acesse seu painel Easypanel
2. Vá até o projeto: **agente-sdr-whatsapp**
3. Clique na aba **"Environment"** (ou "Variables" / "Config")

### Passo 2: Adicionar Todas as Variáveis

Copie e cole **TODAS** as variáveis abaixo, substituindo os valores pelos seus reais:

```bash
# ============================================================================
# OPENAI
# ============================================================================
OPENAI_API_KEY=sk-proj-XXXXXXXXXX
OPENAI_MODEL_CHAT=gpt-4o-mini
OPENAI_MODEL_TRANSCRIBE=gpt-4o-transcribe
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# ============================================================================
# ELEVENLABS
# ============================================================================
ELEVENLABS_API_KEY=sk_XXXXXXXXXX
ELEVENLABS_VOICE_ID=XXXXXXXXXX
ELEVENLABS_MODEL=eleven_multilingual_v2

# ============================================================================
# WHATSAPP
# ============================================================================
WHATSAPP_ACCESS_TOKEN=EAXXXXXXXXXX
WHATSAPP_PHONE_NUMBER_ID=XXXXXXXXXX
WHATSAPP_BUSINESS_ACCOUNT_ID=XXXXXXXXXX
WHATSAPP_WEBHOOK_VERIFY_TOKEN=XcJxjhDKrwq78QL1FbDBT6IX9Dkamiks
WHATSAPP_WEBHOOK_SECRET=XXXXXXXXXX

# ============================================================================
# GOOGLE CALENDAR
# ============================================================================
GOOGLE_CALENDAR_ID=XXXXXXXXXX@group.calendar.google.com
GOOGLE_CREDENTIALS_FILE=/app/config/google_credentials.json
GOOGLE_TOKEN_FILE=/app/config/google_token.json

# ============================================================================
# SUPABASE
# ============================================================================
SUPABASE_URL=https://XXXXXXXXXX.supabase.co
SUPABASE_KEY=eyJhbGciOiXXXXXXXXXX

# ============================================================================
# REDIS (INTERNO)
# ============================================================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=XVusgNTTR+6oSFXsAnKp&CLm
REDIS_DB=0

# ============================================================================
# RABBITMQ (INTERNO)
# ============================================================================
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=8CgO3*TGIjcQ45pzs&P8V9Td
RABBITMQ_QUEUE_NAME=whatsapp_messages

# ============================================================================
# CONFIGURAÇÕES DO AGENTE
# ============================================================================
COMPANY_NAME=Vertical Partners
PRODUCT_NAME=Agentes de IA
AGENT_NAME=Iara
MESSAGE_BUFFER_SECONDS=30
MAX_FRAGMENT_WORDS=30
FOLLOWUP_CHECK_INTERVAL=5
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Passo 3: Substituir Valores

#### ⚠️ Variáveis que você PRECISA substituir:

**OpenAI:**
- `OPENAI_API_KEY` → Sua chave da OpenAI (começa com `sk-proj-`)

**ElevenLabs:**
- `ELEVENLABS_API_KEY` → Sua chave ElevenLabs (começa com `sk_`)
- `ELEVENLABS_VOICE_ID` → ID da voz escolhida

**WhatsApp:**
- `WHATSAPP_ACCESS_TOKEN` → Token do Meta Developers (começa com `EAA`)
- `WHATSAPP_PHONE_NUMBER_ID` → ID do número WhatsApp
- `WHATSAPP_BUSINESS_ACCOUNT_ID` → ID da conta business
- `WHATSAPP_WEBHOOK_SECRET` → App Secret do Meta Developers

**Google Calendar:**
- `GOOGLE_CALENDAR_ID` → ID do calendário Google

**Supabase:**
- `SUPABASE_URL` → URL do projeto Supabase
- `SUPABASE_KEY` → Chave anon/public do Supabase

#### ✅ Variáveis que já estão corretas:

**Tokens gerados automaticamente (não mudar):**
- `WHATSAPP_WEBHOOK_VERIFY_TOKEN=XcJxjhDKrwq78QL1FbDBT6IX9Dkamiks`
- `REDIS_PASSWORD=XVusgNTTR+6oSFXsAnKp&CLm`
- `RABBITMQ_PASSWORD=8CgO3*TGIjcQ45pzs&P8V9Td`

**Configurações internas (não mudar):**
- `REDIS_HOST=redis`
- `RABBITMQ_HOST=rabbitmq`
- Todas as configurações do agente

### Passo 4: Salvar e Rebuild

1. **Salve** as variáveis de ambiente no Easypanel
2. Clique em **"Rebuild"** ou **"Redeploy"**
3. Aguarde 2-3 minutos

### Passo 5: Verificar

Após rebuild, verifique os logs. Você **NÃO** deve mais ver:

```
❌ The "OPENAI_API_KEY" variable is not set
```

Deve ver:

```
✅ INFO: Application startup complete
✅ INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## 📋 Checklist de Variáveis

Use este checklist para garantir que todas as variáveis foram configuradas:

### Obrigatórias para Funcionamento Básico

- [ ] `OPENAI_API_KEY`
- [ ] `WHATSAPP_ACCESS_TOKEN`
- [ ] `WHATSAPP_PHONE_NUMBER_ID`
- [ ] `WHATSAPP_WEBHOOK_VERIFY_TOKEN`
- [ ] `WHATSAPP_WEBHOOK_SECRET`
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_KEY`
- [ ] `REDIS_PASSWORD`
- [ ] `RABBITMQ_PASSWORD`

### Opcionais (mas recomendadas)

- [ ] `ELEVENLABS_API_KEY` (para respostas em áudio)
- [ ] `ELEVENLABS_VOICE_ID` (para respostas em áudio)
- [ ] `GOOGLE_CALENDAR_ID` (para agendamento)

---

## 🔍 Como Obter Cada Credencial

### OpenAI API Key

1. Acesse: https://platform.openai.com/api-keys
2. Clique em **"Create new secret key"**
3. Copie a chave (começa com `sk-proj-`)

### ElevenLabs

1. Acesse: https://elevenlabs.io/
2. **API Key:** Settings → API Keys
3. **Voice ID:** Voices → Escolha uma voz → Copie o ID

### WhatsApp Business API

1. Acesse: https://developers.facebook.com/
2. Seu App → WhatsApp
3. **Access Token:** Configuration → Temporary access token
4. **Phone Number ID:** Configuration → Phone number ID
5. **Business Account ID:** Settings → WhatsApp Business Account ID
6. **Webhook Secret:** Settings → Basic → App Secret

### Google Calendar

1. Acesse: https://console.cloud.google.com/
2. APIs & Services → Credentials
3. Baixe o arquivo JSON de credenciais
4. **Calendar ID:** Google Calendar → Settings → Integrations

### Supabase

1. Acesse: https://app.supabase.com/
2. Seu projeto → Settings → API
3. **URL:** Project URL
4. **Key:** anon public key

---

## ⚠️ Aviso sobre docker-compose.yml version

O warning sobre `version` no docker-compose.yml é **apenas um aviso**, não um erro:

```
the attribute `version` is obsolete, it will be ignored
```

Isso não afeta o funcionamento. Se quiser remover o aviso, posso atualizar o arquivo.

---

## 🆘 Problemas Comuns

### "Variable is not set" após adicionar

**Solução:**
1. Verifique se salvou as variáveis
2. Faça **Rebuild** (não apenas Restart)
3. Aguarde o build completo

### Variáveis com caracteres especiais

**Problema:** Senhas com `&`, `$`, `!` podem causar problemas

**Solução:**
- Use as senhas geradas (`REDIS_PASSWORD`, `RABBITMQ_PASSWORD`)
- Se criar suas próprias, evite caracteres especiais no shell

### Como testar se variáveis estão corretas

**Health Check:**
```bash
curl https://agente-sdr-whatsapp-agente-sdr-whatsapp.zqco7k.easypanel.host/health
```

Deve retornar:
```json
{"status": "healthy", "environment": "production", "version": "1.0.0"}
```

---

## ✅ Próximo Passo

Após configurar todas as variáveis:

1. ✅ Rebuild no Easypanel
2. ✅ Verificar logs (sem erros de variáveis)
3. ✅ Testar health check
4. ✅ Configurar webhook no Meta Developers

**Veja:** `DOCS/MEU-DEPLOY.md` para próximos passos

---

**Última atualização:** Janeiro 2025

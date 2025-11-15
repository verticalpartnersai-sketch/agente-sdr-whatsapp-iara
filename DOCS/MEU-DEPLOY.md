# 🚀 Meu Deploy - Configuração Específica

## 🔗 URLs do Projeto

### Domínio Easypanel
```
https://agente-sdr-whatsapp-agente-sdr-whatsapp.zqco7k.easypanel.host/
```

### Endpoints

#### Health Check
```
https://agente-sdr-whatsapp-agente-sdr-whatsapp.zqco7k.easypanel.host/health
```

**Teste agora:**
```bash
curl https://agente-sdr-whatsapp-agente-sdr-whatsapp.zqco7k.easypanel.host/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0"
}
```

#### Webhook WhatsApp
```
https://agente-sdr-whatsapp-agente-sdr-whatsapp.zqco7k.easypanel.host/webhook/whatsapp
```

---

## 🔐 Configuração do Webhook no Meta Developers

### Passo 1: Acessar Meta Developers
1. Acesse: https://developers.facebook.com/
2. Vá até seu App WhatsApp
3. Menu lateral: **WhatsApp** → **Configuration**

### Passo 2: Configurar Webhook

Clique em **"Edit"** na seção Webhook e configure:

**URL de callback (Callback URL):**
```
https://agente-sdr-whatsapp-agente-sdr-whatsapp.zqco7k.easypanel.host/webhook/whatsapp
```

**Verificar token (Verify token):**
```
(Use o mesmo valor que você definiu em WHATSAPP_WEBHOOK_VERIFY_TOKEN)
```

**Exemplo de token:**
```
meu_token_secreto_2025
```

### Passo 3: Verificar

1. Clique em **"Verificar e salvar"** (Verify and Save)
2. Meta vai fazer uma requisição GET para validar
3. Se tudo estiver correto, aparecerá ✅ "Verificado"

### Passo 4: Ativar Subscriptions

Marque os seguintes campos:

- ✅ **messages** (obrigatório)
- ✅ **message_status** (opcional - para status de entrega)

---

## 🧪 Testes de Validação

### 1. Health Check

**Comando:**
```bash
curl https://agente-sdr-whatsapp-agente-sdr-whatsapp.zqco7k.easypanel.host/health
```

**Resultado esperado:**
```json
{"status": "healthy", "environment": "production", "version": "1.0.0"}
```

### 2. Webhook Verification (Manual)

**Comando:**
```bash
curl "https://agente-sdr-whatsapp-agente-sdr-whatsapp.zqco7k.easypanel.host/webhook/whatsapp?hub.mode=subscribe&hub.challenge=1234&hub.verify_token=SEU_TOKEN_AQUI"
```

**Substitua `SEU_TOKEN_AQUI`** pelo valor da sua variável `WHATSAPP_WEBHOOK_VERIFY_TOKEN`

**Resultado esperado:**
```
1234
```

### 3. Teste Real WhatsApp

1. Envie uma mensagem para o número WhatsApp configurado
2. Verifique os logs no Easypanel:
   - Dashboard → Projeto `agente-sdr-whatsapp` → **Logs**
3. Deve aparecer:
   ```
   INFO: Processando mensagens buffered de +55...
   ```
4. Agente deve responder automaticamente

---

## 📊 Monitoramento

### Logs da Aplicação

**Acessar:**
```
Easypanel Dashboard → agente-sdr-whatsapp → Logs (tab superior)
```

**O que procurar:**
- ✅ `Application startup complete`
- ✅ `Webhook verificado com sucesso`
- ✅ `Processando mensagens buffered de...`
- ❌ Qualquer linha com `ERROR`

### RabbitMQ Management

**URL:**
```
https://agente-sdr-whatsapp-agente-sdr-whatsapp.zqco7k.easypanel.host:15672
```

**Credenciais:**
- User: `admin` (ou valor de `RABBITMQ_USER`)
- Password: valor de `RABBITMQ_PASSWORD`

**Verificar:**
- Queues → `whatsapp_messages`
- Overview → Message rates

### Redis (Interno)

Redis não tem interface web, mas você pode verificar logs:
```
Easypanel → Serviço redis → Logs
```

---

## 🔧 Variáveis de Ambiente Configuradas

### ✅ Checklist de Variáveis

Verifique se **TODAS** estas variáveis estão configuradas no Easypanel:

#### OpenAI
- [ ] `OPENAI_API_KEY`
- [ ] `OPENAI_MODEL_CHAT=gpt-4o-mini`
- [ ] `OPENAI_MODEL_TRANSCRIBE=gpt-4o-transcribe`
- [ ] `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`

#### ElevenLabs
- [ ] `ELEVENLABS_API_KEY`
- [ ] `ELEVENLABS_VOICE_ID`
- [ ] `ELEVENLABS_MODEL=eleven_multilingual_v2`

#### WhatsApp
- [ ] `WHATSAPP_ACCESS_TOKEN`
- [ ] `WHATSAPP_PHONE_NUMBER_ID`
- [ ] `WHATSAPP_BUSINESS_ACCOUNT_ID`
- [ ] `WHATSAPP_WEBHOOK_VERIFY_TOKEN` ⚠️ **Mesmo token do Meta!**
- [ ] `WHATSAPP_WEBHOOK_SECRET`

#### Google Calendar
- [ ] `GOOGLE_CALENDAR_ID`
- [ ] `GOOGLE_CREDENTIALS_FILE=/app/config/google_credentials.json`
- [ ] `GOOGLE_TOKEN_FILE=/app/config/google_token.json`

#### Supabase
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_KEY`

#### Redis (Interno)
- [ ] `REDIS_HOST=redis`
- [ ] `REDIS_PORT=6379`
- [ ] `REDIS_PASSWORD` (senha forte)
- [ ] `REDIS_DB=0`

#### RabbitMQ (Interno)
- [ ] `RABBITMQ_HOST=rabbitmq`
- [ ] `RABBITMQ_PORT=5672`
- [ ] `RABBITMQ_USER=admin`
- [ ] `RABBITMQ_PASSWORD` (senha forte)
- [ ] `RABBITMQ_QUEUE_NAME=whatsapp_messages`

#### Agente
- [ ] `COMPANY_NAME=Vertical Partners`
- [ ] `PRODUCT_NAME=Agentes de IA`
- [ ] `AGENT_NAME=Iara`
- [ ] `MESSAGE_BUFFER_SECONDS=30`
- [ ] `MAX_FRAGMENT_WORDS=30`
- [ ] `FOLLOWUP_CHECK_INTERVAL=5`

---

## 🚨 Troubleshooting

### Problema: Webhook não verifica no Meta

**Possíveis causas:**
1. URL incorreta
2. Token diferente entre Easypanel e Meta
3. Aplicação não está rodando
4. HTTPS não configurado

**Soluções:**
1. Confirme URL exata:
   ```
   https://agente-sdr-whatsapp-agente-sdr-whatsapp.zqco7k.easypanel.host/webhook/whatsapp
   ```
2. Confirme que `WHATSAPP_WEBHOOK_VERIFY_TOKEN` no Easypanel é **EXATAMENTE** igual ao token no Meta
3. Teste health check primeiro
4. Veja logs no Easypanel

### Problema: Health check retorna erro

**Soluções:**
1. Verifique se aplicação está rodando:
   - Easypanel → Status do serviço `agente-sdr`
2. Veja logs para erros de inicialização
3. Confirme que porta 8000 está exposta
4. Tente rebuild: Easypanel → Rebuild

### Problema: Agente não responde mensagens

**Soluções:**
1. Verifique webhook está subscrito (`messages` marcado)
2. Veja logs: deve aparecer recebimento da mensagem
3. Confirme Redis está rodando
4. Confirme RabbitMQ está rodando
5. Verifique credenciais OpenAI

---

## 📝 Anotações

### Token de Verificação WhatsApp
```
Token usado: _______________________

(Anote aqui para referência futura)
```

### Senhas Geradas

**Redis:**
```
Password: _______________________
```

**RabbitMQ:**
```
Password: _______________________
```

---

## ✅ Status do Deploy

### Serviços

- [ ] Aplicação `agente-sdr` rodando
- [ ] Redis rodando
- [ ] RabbitMQ rodando
- [ ] Health check passando
- [ ] Webhook verificado no Meta
- [ ] Teste real funcionando

### Próximos Passos

1. [ ] Configurar webhook no Meta Developers
2. [ ] Testar health check
3. [ ] Enviar mensagem teste
4. [ ] Popular base de conhecimento
5. [ ] Ajustar prompts
6. [ ] Monitorar primeiras conversas

---

## 🔗 Links Úteis

**Easypanel Dashboard:**
```
https://panel.zqco7k.easypanel.host/
```

**Meta Developers:**
```
https://developers.facebook.com/
```

**Supabase Dashboard:**
```
https://app.supabase.com/
```

---

**Última atualização:** Janeiro 2025
**Status:** Pronto para configuração webhook ✅

# ✅ Checklist de Deploy - Easypanel

Use este checklist para garantir que tudo está configurado corretamente antes do deploy.

---

## 📋 Pré-Deploy

### 1. Credenciais Obtidas

- [ ] **OpenAI API Key** - https://platform.openai.com/api-keys
- [ ] **ElevenLabs API Key** - https://elevenlabs.io/
- [ ] **ElevenLabs Voice ID** - https://elevenlabs.io/voices
- [ ] **WhatsApp Access Token** - https://developers.facebook.com/
- [ ] **WhatsApp Phone Number ID** - Meta Developers Console
- [ ] **WhatsApp Business Account ID** - Meta Developers Console
- [ ] **Google Calendar Credentials JSON** - Google Cloud Console
- [ ] **Google Calendar ID** - Google Calendar Settings
- [ ] **Supabase URL** - https://app.supabase.com/
- [ ] **Supabase Key (anon/public)** - Supabase Dashboard

### 2. Banco de Dados Configurado

- [ ] Supabase project criado
- [ ] Schema SQL executado (`database/schema.sql`)
- [ ] Tabelas criadas: `leads_wpp`, `knowledge`, `reunioes`
- [ ] Extensão `pgvector` habilitada
- [ ] Dados iniciais da base de conhecimento inseridos

### 3. Webhook Token Definido

- [ ] Token de verificação criado (ex: `MEU_TOKEN_SECRETO_123`)
- [ ] Token anotado para configuração no Meta Developers

### 4. Senhas Seguras Geradas

- [ ] Senha Redis (ex: `Redis2025!Secure`)
- [ ] Senha RabbitMQ (ex: `Rabbit2025!Secure`)

---

## 🚀 Durante o Deploy

### 1. Projeto no Easypanel

- [ ] Conta Easypanel ativa
- [ ] Projeto criado: `agente-sdr-whatsapp`
- [ ] Tipo: Docker Compose
- [ ] Repositório Git conectado OU `docker-compose.yml` colado

### 2. Variáveis de Ambiente Configuradas

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
- [ ] `WHATSAPP_WEBHOOK_VERIFY_TOKEN` (seu token secreto)
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
- [ ] `REDIS_PASSWORD` (senha segura gerada)
- [ ] `REDIS_DB=0`

#### RabbitMQ (Interno)
- [ ] `RABBITMQ_HOST=rabbitmq`
- [ ] `RABBITMQ_PORT=5672`
- [ ] `RABBITMQ_USER=admin`
- [ ] `RABBITMQ_PASSWORD` (senha segura gerada)
- [ ] `RABBITMQ_QUEUE_NAME=whatsapp_messages`

#### Agente
- [ ] `COMPANY_NAME=Vertical Partners`
- [ ] `PRODUCT_NAME=Agentes de IA`
- [ ] `AGENT_NAME=Isabella`
- [ ] `MESSAGE_BUFFER_SECONDS=30`
- [ ] `MAX_FRAGMENT_WORDS=30`
- [ ] `FOLLOWUP_CHECK_INTERVAL=5`

### 3. Domínio Configurado

- [ ] Domínio/subdomínio adicionado no Easypanel
- [ ] SSL/HTTPS configurado automaticamente
- [ ] URL anotada (ex: `https://whatsapp-agent.seudominio.com`)

### 4. Deploy Realizado

- [ ] Deploy iniciado
- [ ] Build concluído (3-5 minutos)
- [ ] Logs verificados - sem erros críticos
- [ ] Mensagem `Application startup complete` visível

---

## 🔗 Pós-Deploy

### 1. Webhook Configurado no Meta

- [ ] Acesso a https://developers.facebook.com/
- [ ] App → WhatsApp → Configuration
- [ ] Webhook editado
- [ ] URL: `https://whatsapp-agent.seudominio.com/webhook/whatsapp`
- [ ] Token: mesmo valor de `WHATSAPP_WEBHOOK_VERIFY_TOKEN`
- [ ] Verificação bem-sucedida ✅
- [ ] Subscriptions marcadas:
  - [ ] `messages`
  - [ ] `message_status` (opcional)

### 2. Testes de Funcionamento

#### Health Check
- [ ] URL testada: `https://whatsapp-agent.seudominio.com/health`
- [ ] Resposta recebida:
  ```json
  {
    "status": "healthy",
    "environment": "production",
    "version": "1.0.0"
  }
  ```

#### Teste Webhook Manual
- [ ] Comando executado:
  ```bash
  curl "https://whatsapp-agent.seudominio.com/webhook/whatsapp?hub.mode=subscribe&hub.challenge=1234&hub.verify_token=SEU_TOKEN"
  ```
- [ ] Retornou: `1234`

#### Teste via WhatsApp
- [ ] Mensagem enviada para o número WhatsApp
- [ ] Mensagem recebida (logs confirmam)
- [ ] Agente processou (logs confirmam)
- [ ] Resposta enviada automaticamente
- [ ] Conversação funcionando corretamente

### 3. Monitoramento Configurado

#### Logs
- [ ] Acesso aos logs no Easypanel funcionando
- [ ] Nível de log apropriado (INFO em produção)
- [ ] Sem erros críticos nos logs

#### Serviços
- [ ] Serviço `agente-sdr` rodando
- [ ] Serviço `redis` rodando
- [ ] Serviço `rabbitmq` rodando
- [ ] Health checks passando

#### RabbitMQ Management (Opcional)
- [ ] Acesso a `https://whatsapp-agent.seudominio.com:15672`
- [ ] Login com credenciais RabbitMQ
- [ ] Fila `whatsapp_messages` visível
- [ ] Mensagens sendo processadas

---

## 🎯 Validação Final

### Fluxo Completo
- [ ] Lead envia mensagem via WhatsApp
- [ ] Sistema recebe e armazena no Redis
- [ ] Buffer aguarda 30s antes de processar
- [ ] Agente processa com IA (GPT-4o-mini)
- [ ] Busca conhecimento no Supabase (RAG)
- [ ] Responde fragmentado (20-30 palavras)
- [ ] Histórico salvo no Redis
- [ ] Lead atualizado no Supabase
- [ ] Follow-up agendado (se necessário)

### Funcionalidades Específicas

#### Agendamento
- [ ] Lead solicita agendamento
- [ ] Agente busca horários no Google Calendar
- [ ] Lead escolhe horário
- [ ] Reunião criada no Google Calendar
- [ ] Confirmação enviada ao lead

#### Áudio
- [ ] Lead envia mensagem de áudio
- [ ] Sistema transcreve com GPT-4o-transcribe
- [ ] Agente responde com texto
- [ ] (Opcional) Resposta em áudio via ElevenLabs

#### Follow-up
- [ ] Sistema verifica follow-ups pendentes
- [ ] Envia FUP1 após 30 minutos
- [ ] Respeita horário comercial (7h-21h)
- [ ] Analisa desinteresse antes de enviar
- [ ] Timeline funciona: 30min → 4h → 12h → 24h

---

## 🚨 Troubleshooting Comum

### ❌ Webhook não verifica
**Checklist:**
- [ ] URL correta e acessível
- [ ] Token idêntico no Easypanel e Meta
- [ ] HTTPS funcionando
- [ ] Endpoint GET implementado

### ❌ Agente não responde
**Checklist:**
- [ ] Logs verificados (Easypanel)
- [ ] Redis conectado
- [ ] RabbitMQ conectado
- [ ] Credenciais OpenAI corretas
- [ ] Supabase acessível
- [ ] Webhook subscrito a `messages`

### ❌ Erro 500 no webhook
**Checklist:**
- [ ] Todas as variáveis de ambiente configuradas
- [ ] Formato das variáveis correto
- [ ] Senhas sem caracteres especiais problemáticos
- [ ] Logs detalhados verificados

### ❌ Follow-up não envia
**Checklist:**
- [ ] Scheduler iniciado (logs confirmam)
- [ ] Horário dentro de 7h-21h
- [ ] Lead tem `fup_enviado < 4`
- [ ] Última interação dentro de 72h
- [ ] Sem desinteresse detectado

---

## ✅ Deploy Concluído

Se todos os itens acima estão marcados, seu Agente IA SDR WhatsApp está **100% funcional em produção**! 🎉

**Última atualização:** Janeiro 2025

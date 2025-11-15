# 🚀 Deploy no Easypanel (Hostinger)

Este guia mostra como fazer deploy do Agente IA SDR WhatsApp no Easypanel da Hostinger.

## 📋 Pré-requisitos

- Conta Hostinger com Easypanel configurado
- Acesso ao painel Easypanel
- Todas as credenciais configuradas (veja `CREDENCIAIS-NECESSARIAS.md`)
- Projeto em um repositório Git (GitHub, GitLab, etc.)

---

## 🎯 Passo a Passo

### 1. Acessar Easypanel

1. Acesse seu painel Hostinger
2. Navegue até VPS → Easypanel
3. Abra o painel Easypanel

### 2. Criar Novo Projeto

1. No Easypanel, clique em **"+ Create Project"**
2. Escolha **"Docker Compose"**
3. Dê um nome ao projeto: `agente-sdr-whatsapp`

### 3. Configurar Docker Compose

1. No editor do Easypanel, cole o conteúdo do arquivo `docker-compose.yml`
2. Ou conecte ao seu repositório Git e o Easypanel detectará automaticamente

### 4. Configurar Variáveis de Ambiente

No Easypanel, adicione todas as variáveis de ambiente necessárias:

#### OpenAI
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL_CHAT=gpt-4o-mini
OPENAI_MODEL_TRANSCRIBE=gpt-4o-transcribe
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

#### ElevenLabs
```
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...
ELEVENLABS_MODEL=eleven_multilingual_v2
```

#### WhatsApp
```
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_BUSINESS_ACCOUNT_ID=...
WHATSAPP_WEBHOOK_VERIFY_TOKEN=meu_token_secreto_123
WHATSAPP_WEBHOOK_SECRET=...
```

#### Google Calendar
```
GOOGLE_CALENDAR_ID=...
GOOGLE_CREDENTIALS_FILE=/app/config/google_credentials.json
GOOGLE_TOKEN_FILE=/app/config/google_token.json
```

#### Supabase
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=...
```

#### Redis (Interno)
```
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=sua_senha_redis_segura
REDIS_DB=0
```

#### RabbitMQ (Interno)
```
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=sua_senha_rabbitmq_segura
RABBITMQ_QUEUE_NAME=whatsapp_messages
```

#### Configurações do Agente
```
COMPANY_NAME=Vertical Partners
PRODUCT_NAME=Agentes de IA
AGENT_NAME=Isabella
MESSAGE_BUFFER_SECONDS=30
MAX_FRAGMENT_WORDS=30
FOLLOWUP_CHECK_INTERVAL=5
```

### 5. Configurar Domínio/Subdomínio

1. No Easypanel, vá em **"Domains"**
2. Adicione um domínio ou subdomínio (ex: `whatsapp-agent.seudominio.com`)
3. Easypanel configurará automaticamente SSL/HTTPS

### 6. Deploy

1. Clique em **"Deploy"**
2. Aguarde o build e deploy (3-5 minutos)
3. Verifique os logs para confirmar que está rodando

### 7. Obter URL do Webhook

Após o deploy, sua URL do webhook será:

```
https://whatsapp-agent.seudominio.com/webhook/whatsapp
```

---

## 🔗 Configurar Webhook no WhatsApp Business API

### Passo a Passo

1. Acesse [Meta Developers](https://developers.facebook.com/)
2. Vá até seu App → WhatsApp → Configuration
3. Clique em **"Edit"** na seção Webhook
4. Configure:

   **URL de callback:**
   ```
   https://whatsapp-agent.seudominio.com/webhook/whatsapp
   ```

   **Verificar token:**
   ```
   meu_token_secreto_123
   ```
   (O mesmo valor que você definiu em `WHATSAPP_WEBHOOK_VERIFY_TOKEN`)

5. Clique em **"Verificar e salvar"**

6. **Importante:** Marque os campos de assinatura (subscriptions):
   - ✅ messages
   - ✅ message_status (opcional)

---

## ✅ Verificação de Funcionamento

### 1. Health Check

Acesse no navegador:
```
https://whatsapp-agent.seudominio.com/health
```

Deve retornar:
```json
{"status": "healthy"}
```

### 2. Verificar Logs

No Easypanel:
1. Vá em **"Logs"** do serviço `agente-sdr`
2. Verifique se não há erros
3. Deve ver mensagens como:
   ```
   INFO: Application startup complete
   INFO: Uvicorn running on http://0.0.0.0:8000
   ```

### 3. Testar Webhook

Envie uma mensagem pelo WhatsApp para o número configurado e verifique:
- Logs mostram recebimento da mensagem
- Agente responde corretamente
- Redis armazena o histórico
- RabbitMQ processa a fila

---

## 📊 Monitoramento

### Acessar RabbitMQ Management

URL: `https://whatsapp-agent.seudominio.com:15672`

Login:
- User: `admin` (ou o que você configurou em `RABBITMQ_USER`)
- Password: valor de `RABBITMQ_PASSWORD`

### Verificar Filas
- Acesse **"Queues"**
- Veja a fila `whatsapp_messages`
- Monitore mensagens processadas

---

## 🔧 Troubleshooting

### Webhook não verifica

**Problema:** Meta retorna erro ao verificar webhook

**Soluções:**
1. Verifique se a URL está acessível publicamente
2. Confirme que `WHATSAPP_WEBHOOK_VERIFY_TOKEN` está correto
3. Veja os logs do Easypanel para erros
4. Teste o endpoint manualmente:
   ```bash
   curl "https://whatsapp-agent.seudominio.com/webhook/whatsapp?hub.mode=subscribe&hub.challenge=1234&hub.verify_token=meu_token_secreto_123"
   ```
   Deve retornar: `1234`

### Agente não responde

**Problema:** Mensagens são recebidas mas agente não responde

**Soluções:**
1. Verifique logs no Easypanel
2. Confirme que Redis está rodando: veja serviço `redis`
3. Confirme que RabbitMQ está rodando: veja serviço `rabbitmq`
4. Verifique credenciais OpenAI e outras APIs
5. Teste conexão Supabase

### Redis/RabbitMQ não conectam

**Problema:** Erro ao conectar aos serviços internos

**Soluções:**
1. Verifique se os serviços estão rodando no Easypanel
2. Confirme que `REDIS_HOST=redis` e `RABBITMQ_HOST=rabbitmq`
3. Verifique as senhas configuradas
4. Reinicie o stack completo

---

## 🔄 Atualizar Deployment

Para atualizar o código após mudanças:

1. Faça push das mudanças para o repositório Git
2. No Easypanel, clique em **"Rebuild"**
3. Ou configure **Auto-Deploy** para atualizar automaticamente

---

## 📈 Escalabilidade

### Aumentar Recursos

Se o tráfego aumentar:

1. No Easypanel, ajuste recursos do container `agente-sdr`:
   - CPU: 2+ cores
   - RAM: 2+ GB

2. Configure réplicas para alta disponibilidade:
   ```yaml
   deploy:
     replicas: 2
   ```

### Redis Externo (Opcional)

Para melhor performance, use Redis externo:

1. Crie instância Redis gerenciada (Upstash, Redis Cloud, etc.)
2. Atualize variáveis:
   ```
   REDIS_HOST=seu-redis-externo.cloud
   REDIS_PORT=6379
   REDIS_PASSWORD=...
   ```
3. Remova serviço `redis` do docker-compose.yml

---

## 🛡️ Segurança

### SSL/TLS

- Easypanel configura automaticamente SSL via Let's Encrypt
- Certificados renovam automaticamente

### Variáveis Sensíveis

- ✅ Use variáveis de ambiente no Easypanel
- ❌ Nunca commite arquivos `.env` no Git
- ✅ Use secrets do Easypanel para credenciais

### Firewall

- Easypanel gerencia firewall automaticamente
- Apenas portas necessárias ficam expostas (80, 443)

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique logs detalhados no Easypanel
2. Consulte documentação oficial: https://easypanel.io/docs
3. Suporte Hostinger: https://www.hostinger.com.br/suporte

---

## ✨ Pronto!

Seu Agente IA SDR WhatsApp está rodando em produção! 🎉

**URL Webhook:** `https://whatsapp-agent.seudominio.com/webhook/whatsapp`
**Status:** `https://whatsapp-agent.seudominio.com/health`

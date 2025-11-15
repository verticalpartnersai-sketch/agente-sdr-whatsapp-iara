# 🚀 Deploy em Produção - Easypanel (Hostinger)

Este projeto está **100% pronto** para deploy em produção usando **Easypanel da Hostinger**.

---

## 📚 Documentação Disponível

### Guias de Deploy

1. **QUICKSTART-EASYPANEL.md** - Deploy rápido em 5 passos
2. **DEPLOY-EASYPANEL.md** - Guia completo com troubleshooting
3. **CHECKLIST-DEPLOY.md** - Checklist interativo para validação

### Outros Documentos

- **CREDENCIAIS-NECESSARIAS.md** - Como obter todas as credenciais
- **README.md** - Documentação geral do projeto

---

## ⚡ Deploy Rápido (5 minutos)

### 1. Preparar Credenciais

Obtenha todas as credenciais necessárias:
- OpenAI API Key
- ElevenLabs API Key + Voice ID
- WhatsApp Business API Token
- Google Calendar Credentials
- Supabase URL + Key

**Veja:** `DOCS/CREDENCIAIS-NECESSARIAS.md`

### 2. Criar Projeto no Easypanel

```
Easypanel → "+ Create Project" → "Docker Compose"
Nome: agente-sdr-whatsapp
```

### 3. Configurar

1. Conecte seu repositório Git **OU** cole `docker-compose.yml`
2. Adicione **todas** as variáveis de ambiente (veja `.env.example`)
3. Configure domínio/subdomínio
4. Clique em **"Deploy"**

### 4. Configurar Webhook WhatsApp

```
URL: https://whatsapp-agent.seudominio.com/webhook/whatsapp
Token: SEU_TOKEN_SECRETO (mesmo de WHATSAPP_WEBHOOK_VERIFY_TOKEN)
```

No Meta Developers:
```
App → WhatsApp → Configuration → Webhook → Edit
```

### 5. Testar

```bash
# Health check
curl https://whatsapp-agent.seudominio.com/health

# Enviar mensagem teste via WhatsApp
```

---

## 📦 Arquivos de Deploy Incluídos

- ✅ `Dockerfile` - Imagem Docker otimizada
- ✅ `docker-compose.yml` - Stack completo (app + Redis + RabbitMQ)
- ✅ `.dockerignore` - Otimização de build
- ✅ `.gitignore` - Segurança (não commita .env)

---

## 🔧 Tecnologias

### Stack Principal
- **FastAPI** - API webhooks
- **LangChain 0.1.20** - Agente IA
- **OpenAI GPT-4o-mini** - LLM
- **ElevenLabs** - Text-to-Speech
- **Supabase** - Banco de dados PostgreSQL + pgvector

### Infraestrutura
- **Redis** - Cache e memória
- **RabbitMQ** - Fila de mensagens
- **Docker** - Containerização
- **Easypanel** - Plataforma de deploy

---

## 🎯 Recursos Implementados

### ✅ Agente IA Conversacional
- Processamento de linguagem natural
- Base de conhecimento com RAG híbrido (60% semântico + 40% BM25)
- Fragmentação inteligente de mensagens (20-30 palavras)
- Buffer de 30 segundos para agregação de mensagens

### ✅ Multimodal
- Transcrição de áudio (OpenAI Whisper)
- Análise de imagens (GPT-4o Vision)
- Suporte a documentos e vídeos
- Text-to-Speech (ElevenLabs)

### ✅ Agendamento Inteligente
- Integração Google Calendar
- Verificação de disponibilidade
- Confirmações automáticas
- Lembretes 24h e 2h antes

### ✅ Sistema de Follow-up
- Timeline automático: 30min → 4h → 12h → 24h
- Análise de desinteresse
- Respeita horário comercial (7h-21h)
- Personalização com IA

### ✅ Gerenciamento de Leads
- Histórico completo de conversas
- Tagging automático
- Estados de conversação
- Métricas de engajamento

---

## 🛡️ Segurança

- ✅ Validação de assinatura do webhook WhatsApp
- ✅ HTTPS/SSL automático (Let's Encrypt)
- ✅ Variáveis de ambiente para credenciais
- ✅ Senhas fortes para Redis/RabbitMQ
- ✅ Validação de entrada de dados

---

## 📊 Monitoramento

### Health Check
```
GET https://whatsapp-agent.seudominio.com/health
```

### Logs
Acesse via Easypanel Dashboard → Logs

### RabbitMQ Management
```
https://whatsapp-agent.seudominio.com:15672
User: admin
Password: (valor de RABBITMQ_PASSWORD)
```

---

## 🔄 Atualização do Deploy

### Via Git (Recomendado)
1. Push mudanças para repositório
2. Easypanel → Rebuild

### Manual
1. Editar código no Easypanel
2. Deploy novamente

---

## 💡 Próximos Passos Após Deploy

1. ✅ Validar webhook funcionando
2. ✅ Testar conversação completa
3. ✅ Popular base de conhecimento
4. ✅ Ajustar prompts conforme necessário
5. ✅ Monitorar logs iniciais
6. ✅ Configurar alertas (opcional)

---

## 🆘 Suporte

### Problemas Comuns

**Webhook não verifica:**
- Verifique URL e token
- Confirme HTTPS funcionando
- Veja logs no Easypanel

**Agente não responde:**
- Verifique logs
- Confirme credenciais OpenAI
- Teste health check

**Follow-up não envia:**
- Verifique horário (7h-21h)
- Confirme scheduler nos logs
- Valide dados do lead

### Documentação Detalhada

Veja `DOCS/DEPLOY-EASYPANEL.md` para troubleshooting completo.

---

## ✨ Status do Projeto

- ✅ **Código:** 100% implementado
- ✅ **Testes:** Validado localmente
- ✅ **Deploy:** Pronto para produção
- ✅ **Documentação:** Completa
- ✅ **Easypanel:** Totalmente compatível

---

## 📞 Arquitetura

```
WhatsApp Business API
        ↓
    Webhook (FastAPI)
        ↓
    RabbitMQ (fila)
        ↓
   Message Buffer (30s)
        ↓
    Agente SDR (LangChain)
        ↓
    ├─→ OpenAI (GPT-4o-mini)
    ├─→ Supabase (RAG + Leads)
    ├─→ Google Calendar
    ├─→ ElevenLabs (TTS)
    └─→ Redis (memória)
        ↓
    Follow-up System
```

---

**Desenvolvido com ❤️ usando Claude Code**
**Deploy com 🚀 Easypanel (Hostinger)**

**Versão:** 1.0.0
**Última atualização:** Janeiro 2025

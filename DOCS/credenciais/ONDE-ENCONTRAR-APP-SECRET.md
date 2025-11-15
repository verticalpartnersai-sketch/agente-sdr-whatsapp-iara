# 🔐 Onde Encontrar o App Secret (WHATSAPP_WEBHOOK_SECRET)

## O que é o App Secret?

O `WHATSAPP_WEBHOOK_SECRET` é o **App Secret** do seu aplicativo Meta/Facebook. É usado para validar que as mensagens realmente vêm do WhatsApp.

---

## 📍 Como Encontrar

### Passo 1: Acessar Configurações do App

1. No Meta Developers (onde você está agora)
2. Menu lateral esquerdo → **"Configurações do app"** (ou **"App settings"**)
3. Clique em **"Básico"** (ou **"Basic"**)

### Passo 2: Localizar App Secret

Na página de configurações básicas, você verá:

```
ID do aplicativo: 116540208883350
Chave secreta do app: ••••••••••••••••••••••••••••
```

### Passo 3: Revelar o Secret

1. Ao lado de **"Chave secreta do app"** (App Secret), clique em **"Mostrar"** (Show)
2. O Meta pode pedir sua senha do Facebook
3. Digite sua senha
4. O App Secret será revelado (exemplo: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)

### Passo 4: Copiar

Copie o valor completo do App Secret.

---

## ✅ Usar o App Secret

### No arquivo .env (local)

```bash
WHATSAPP_WEBHOOK_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### No Easypanel

Adicione a variável de ambiente:

```
Nome: WHATSAPP_WEBHOOK_SECRET
Valor: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

---

## 🎯 Configurar Webhook no Meta

Agora que você está na tela de Webhook, configure:

### URL de callback

```
https://agente-sdr-whatsapp-agente-sdr-whatsapp.zqco7k.easypanel.host/webhook/whatsapp
```

### Verificar token

```
XcJxjhDKrwq78QL1FbDBT6IX9Dkamiks
```

(Este é o token que geramos - está no seu .env como `WHATSAPP_WEBHOOK_VERIFY_TOKEN`)

### Importante

⚠️ **Antes de configurar o webhook**, você DEVE:

1. ✅ Adicionar TODAS as variáveis no Easypanel
2. ✅ Fazer Rebuild no Easypanel
3. ✅ Verificar que aplicação está rodando
4. ✅ Testar health check primeiro

Caso contrário, a verificação do webhook vai falhar!

---

## 🔍 Resumo Visual

```
Meta Developers
    ↓
Menu lateral → "Configurações do app" → "Básico"
    ↓
Chave secreta do app: ••••••••••
    ↓
Clique em "Mostrar" → Digite senha Facebook
    ↓
Copie o App Secret
    ↓
Cole no .env e no Easypanel como WHATSAPP_WEBHOOK_SECRET
```

---

## ⚠️ Problema: Variáveis Ainda Faltando no Easypanel

Você configurou o `.env` **local**, mas o Easypanel não lê esse arquivo!

### Solução

Você precisa adicionar as variáveis **manualmente no Easypanel**:

1. Easypanel → Projeto `agente-sdr-whatsapp`
2. Aba **"Environment"** (ou "Variables")
3. Adicionar **UMA POR UMA** cada variável

**Exemplo:**

```
Nome: WHATSAPP_BUSINESS_ACCOUNT_ID
Valor: 175678977168823

Nome: WHATSAPP_WEBHOOK_VERIFY_TOKEN
Valor: XcJxjhDKrwq78QL1FbDBT6IX9Dkamiks

Nome: GOOGLE_CALENDAR_ID
Valor: seu_email@group.calendar.google.com
```

### Variáveis que ainda faltam (baseado no erro):

```
WHATSAPP_BUSINESS_ACCOUNT_ID
WHATSAPP_WEBHOOK_VERIFY_TOKEN
GOOGLE_CALENDAR_ID
```

---

## 📋 Checklist Completo

- [ ] Obter App Secret no Meta Developers (Configurações → Básico)
- [ ] Adicionar `WHATSAPP_WEBHOOK_SECRET` no Easypanel
- [ ] Adicionar `WHATSAPP_BUSINESS_ACCOUNT_ID` no Easypanel
- [ ] Adicionar `WHATSAPP_WEBHOOK_VERIFY_TOKEN` no Easypanel
- [ ] Adicionar `GOOGLE_CALENDAR_ID` no Easypanel (ou deixar vazio se não usar agendamento)
- [ ] Fazer **Rebuild** no Easypanel
- [ ] Verificar logs (sem warnings)
- [ ] Testar health check
- [ ] Configurar webhook no Meta

---

**Última atualização:** Janeiro 2025

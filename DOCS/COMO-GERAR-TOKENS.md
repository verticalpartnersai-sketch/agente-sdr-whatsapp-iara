# 🔐 Como Gerar Tokens e Senhas

## WHATSAPP_WEBHOOK_VERIFY_TOKEN

### O que é?

O `WHATSAPP_WEBHOOK_VERIFY_TOKEN` é uma **senha secreta que VOCÊ cria**.

Não é gerado pelo WhatsApp ou Meta. É apenas uma string aleatória que você inventa para validar que o webhook é legítimo.

### Como criar?

#### Opção 1: Criar manualmente (simples)

Escolha uma string aleatória forte, por exemplo:

```
meu_token_secreto_2025_whatsapp
```

```
verticalpartners_webhook_token_2025
```

```
agente_sdr_verify_abc123xyz
```

**Regras:**
- ✅ Letras, números, underscore (`_`), hífen (`-`)
- ✅ Mínimo 16 caracteres
- ✅ Difícil de adivinhar
- ❌ Sem espaços
- ❌ Sem caracteres especiais (@, #, $, etc.)

#### Opção 2: Gerar aleatoriamente (recomendado)

**No terminal (Mac/Linux):**
```bash
# Gera token de 32 caracteres
openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32
```

**Exemplo de output:**
```
Kj8mN2vR4tY6wE9qS1xC5zF7hL3pU0aB
```

**Online:**
- Acesse: https://www.random.org/strings/
- Configure:
  - Number of strings: `1`
  - Length: `32`
  - Characters: `Alphanumeric`
- Clique em `Get Strings`

#### Opção 3: Python (se preferir)

```python
import secrets
import string

# Gera token de 32 caracteres
alphabet = string.ascii_letters + string.digits
token = ''.join(secrets.choice(alphabet) for i in range(32))
print(token)
```

---

## Como usar?

### 1. Criar o token

Escolha uma das opções acima e gere seu token. Exemplo:

```
verticalpartners_webhook_2025_abc123
```

### 2. Configurar no Easypanel

Adicione a variável de ambiente:

```
WHATSAPP_WEBHOOK_VERIFY_TOKEN=verticalpartners_webhook_2025_abc123
```

### 3. Usar no Meta Developers

Quando configurar o webhook no Meta Developers, use o **MESMO token**:

**Campo "Verificar token":**
```
verticalpartners_webhook_2025_abc123
```

⚠️ **IMPORTANTE:** O token deve ser **EXATAMENTE IGUAL** nos dois lugares!

---

## WHATSAPP_WEBHOOK_SECRET

### O que é?

O `WHATSAPP_WEBHOOK_SECRET` é **gerado automaticamente pelo Meta** quando você configura o App WhatsApp.

### Onde encontrar?

1. Acesse: https://developers.facebook.com/
2. Seu App → **Settings** → **Basic**
3. Procure por **"App Secret"** ou **"App Secret Key"**
4. Clique em **"Show"** (pode pedir sua senha do Facebook)
5. Copie o valor

**Exemplo:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### Como usar?

Adicione ao Easypanel:

```
WHATSAPP_WEBHOOK_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

---

## REDIS_PASSWORD

### Como criar?

Use um gerador de senhas forte:

#### Opção 1: Terminal
```bash
openssl rand -base64 24
```

**Exemplo:**
```
Kj8mN2vR4tY6wE9qS1xC5zF7hL==
```

#### Opção 2: Online
- https://www.lastpass.com/pt/features/password-generator
- Configure: 24+ caracteres, letras, números, símbolos

#### Opção 3: Manual
```
Redis@2025!SecurePassword#ABC
```

### Como usar?

```
REDIS_PASSWORD=Redis@2025!SecurePassword#ABC
```

---

## RABBITMQ_PASSWORD

### Como criar?

Mesma lógica do Redis. Use um gerador:

```bash
openssl rand -base64 24
```

**Exemplo:**
```
RabbitMQ@2025!Secure#XYZ789
```

### Como usar?

```
RABBITMQ_PASSWORD=RabbitMQ@2025!Secure#XYZ789
```

---

## 📋 Resumo Completo

### Tokens que VOCÊ cria

| Variável | Como criar | Exemplo |
|----------|------------|---------|
| `WHATSAPP_WEBHOOK_VERIFY_TOKEN` | String aleatória (16-32 chars) | `webhook_verify_2025_abc123` |
| `REDIS_PASSWORD` | Senha forte (24+ chars) | `Redis@2025!Secure#ABC` |
| `RABBITMQ_PASSWORD` | Senha forte (24+ chars) | `RabbitMQ@2025!Secure#XYZ` |

### Tokens que você obtém de serviços

| Variável | Onde obter | Documentação |
|----------|------------|--------------|
| `WHATSAPP_WEBHOOK_SECRET` | Meta Developers → App Secret | [Meta Docs](https://developers.facebook.com/) |
| `WHATSAPP_ACCESS_TOKEN` | Meta Developers → WhatsApp → Token | `CREDENCIAIS-NECESSARIAS.md` |
| `OPENAI_API_KEY` | OpenAI Platform | `CREDENCIAIS-NECESSARIAS.md` |
| `ELEVENLABS_API_KEY` | ElevenLabs Dashboard | `CREDENCIAIS-NECESSARIAS.md` |
| `SUPABASE_KEY` | Supabase Dashboard | `CREDENCIAIS-NECESSARIAS.md` |

---

## 🛡️ Boas Práticas

### ✅ Fazer

- Usar tokens longos (32+ caracteres)
- Combinar letras maiúsculas, minúsculas, números
- Tokens diferentes para cada serviço
- Armazenar em gerenciador de senhas
- Nunca commitar no Git
- Trocar tokens periodicamente (a cada 6 meses)

### ❌ Não Fazer

- Usar senhas simples (`123456`, `password`)
- Reutilizar tokens entre projetos
- Compartilhar tokens publicamente
- Commitar `.env` no Git
- Usar tokens legíveis (`webhook_token_123`)

---

## 🔄 Regenerar Tokens

### Quando regenerar?

- Token comprometido ou vazado
- Mudança de ambiente (dev → prod)
- Rotação de segurança (6 meses)
- Suspeita de acesso não autorizado

### Como regenerar?

1. **Gere novo token**
2. **Atualize Easypanel** (variável de ambiente)
3. **Atualize Meta Developers** (se `WEBHOOK_VERIFY_TOKEN`)
4. **Rebuild** aplicação
5. **Teste** funcionamento

---

## 📝 Template Completo

Use este template como referência:

```bash
# === WHATSAPP ===
# Você cria este token (16-32 chars aleatórios)
WHATSAPP_WEBHOOK_VERIFY_TOKEN=verticalpartners_webhook_2025_abc123

# Você obtém do Meta Developers → App Secret
WHATSAPP_WEBHOOK_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# === REDIS ===
# Você cria esta senha (24+ chars forte)
REDIS_PASSWORD=Redis@2025!SecurePassword#ABC

# === RABBITMQ ===
# Você cria esta senha (24+ chars forte)
RABBITMQ_PASSWORD=RabbitMQ@2025!Secure#XYZ789
```

---

## 🎯 Comando Rápido - Gerar Todos

Execute este script Python para gerar todos os tokens de uma vez:

```python
import secrets
import string

def gerar_token(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def gerar_senha(length=24):
    alphabet = string.ascii_letters + string.digits + '!@#$%&*'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

print("=== TOKENS GERADOS ===")
print(f"WHATSAPP_WEBHOOK_VERIFY_TOKEN={gerar_token(32)}")
print(f"REDIS_PASSWORD={gerar_senha(24)}")
print(f"RABBITMQ_PASSWORD={gerar_senha(24)}")
print("\n⚠️ COPIE E SALVE ESTES TOKENS COM SEGURANÇA!")
```

**Salve como:** `gerar_tokens.py`

**Execute:**
```bash
python gerar_tokens.py
```

---

**Última atualização:** Janeiro 2025

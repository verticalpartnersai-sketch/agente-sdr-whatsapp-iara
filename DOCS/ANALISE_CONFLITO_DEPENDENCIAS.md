# Análise de Conflito de Dependências - Docker Build

## Data da Análise
2025-11-15

## Problema Identificado

Erro durante build do Docker:
```
ERROR: Cannot install -r requirements.txt (line 20), -r requirements.txt (line 25) and httpx==0.27.0
because these package versions have conflicting dependencies.
```

## Análise Detalhada do Conflito

### 1. Requisitos de httpx por Pacote

| Pacote | Versão Atual | Requisito httpx | Compatível com 0.27.0? |
|--------|--------------|-----------------|------------------------|
| **openai** | 1.14.0 | `httpx<1,>=0.23.0` | ✅ SIM (0.23.0 - 0.99.x) |
| **supabase** | 2.4.0 | `httpx>=0.24,<0.26` | ❌ NÃO (apenas 0.24.x - 0.25.x) |
| **httpx fixo** | 0.27.0 | - | ❌ Conflita com supabase |

### 2. Causa Raiz do Conflito

O **supabase 2.4.0** requer `httpx>=0.24,<0.26`, ou seja:
- ✅ Aceita: 0.24.0, 0.24.1, 0.25.0, 0.25.1, etc.
- ❌ Rejeita: 0.26.x, 0.27.x, 0.28.x

O requirements.txt fixa `httpx==0.27.0` (linha 42), que está **fora do range** aceito pelo supabase 2.4.0.

### 3. Evolução das Dependências do Supabase

| Versão Supabase | Requisito httpx | Status |
|-----------------|-----------------|--------|
| 2.4.0 | `>=0.24,<0.26` | ❌ Incompatível com httpx 0.27.0 |
| 2.10.0 | `>=0.26,<0.28` | ✅ Compatível com httpx 0.27.0 |
| 2.15.0 | `>=0.26,<0.29` | ✅ Compatível com httpx 0.27.0 |
| 2.24.0 (latest) | `>=0.26,<0.29` | ✅ Compatível com httpx 0.27.0 |

## Soluções Recomendadas

### ✅ Solução 1: Atualizar Supabase (RECOMENDADA)

**Ação**: Atualizar `supabase` de 2.4.0 para 2.15.0 ou superior

**Vantagens**:
- Resolve conflito mantendo httpx 0.27.0
- Supabase 2.15.0 é estável e com mais features
- Compatível com httpx>=0.26,<0.29
- Mantém todas as funcionalidades atuais

**Mudanças no requirements.txt**:
```diff
- supabase==2.4.0
+ supabase==2.15.0  # ou 2.24.0 (latest)
  httpx==0.27.0
```

**Testes Necessários**:
1. Validar que não há breaking changes entre 2.4.0 → 2.15.0
2. Testar autenticação e queries do Supabase
3. Verificar integração com vecs (vector store)

---

### ✅ Solução 2: Remover httpx Fixo

**Ação**: Remover linha 42 (`httpx==0.27.0`) e deixar pip resolver automaticamente

**Vantagens**:
- Pip instalará versão compatível com todos os pacotes
- Sem necessidade de atualizar supabase
- Manutenção mais simples

**Mudanças no requirements.txt**:
```diff
- httpx==0.27.0
+ # httpx será instalado automaticamente pelos pacotes que dependem dele
```

**Versão que será instalada**: 0.25.x (compatível com todos)

**Desvantagens**:
- Versão de httpx não está explicitamente controlada
- Pode variar entre ambientes se não usar lock file

---

### ❌ Solução 3: Downgrade httpx (NÃO RECOMENDADA)

**Ação**: Alterar httpx para versão 0.25.x

**Por que NÃO é recomendada**:
- Perde features e fixes de segurança mais recentes
- Limita atualizações futuras
- Supabase 2.4.0 já tem versões mais novas disponíveis

---

## Recomendação Final

### 🎯 SOLUÇÃO RECOMENDADA: Solução 1 + Solução 2 Combinadas

**Ação**:
1. Atualizar `supabase` para 2.15.0 (ou 2.24.0)
2. Remover fixação de `httpx` (deixar gerenciado automaticamente)

**Mudanças no requirements.txt**:
```diff
  # ------------------------------------------------------------------------------
  # Vector Store
  # ------------------------------------------------------------------------------
- supabase==2.4.0
+ supabase==2.15.0
  vecs==0.4.0

  # ------------------------------------------------------------------------------
  # APIs Externas
  # ------------------------------------------------------------------------------
- httpx==0.27.0
+ # httpx gerenciado automaticamente pelas dependências
  google-auth==2.29.0
```

**Benefícios**:
- ✅ Resolve conflito completamente
- ✅ Usa versões mais recentes e seguras
- ✅ Mantém compatibilidade com todos os pacotes
- ✅ Facilita manutenção futura
- ✅ httpx 0.27.x será instalado automaticamente (compatível com todos)

## Verificação de Compatibilidade

### Pacotes que dependem de httpx:
- openai==1.14.0: `httpx<1,>=0.23.0` ✅
- supabase==2.15.0: `httpx>=0.26,<0.29` ✅
- elevenlabs==0.2.27: (verificar se usa httpx)
- fastapi/uvicorn: (usam httpx indiretamente)

### Range compatível com TODOS:
- httpx >= 0.26.0 AND httpx < 0.29.0
- Versões: 0.26.x, 0.27.x, 0.28.x

## Próximos Passos

1. ✅ Atualizar requirements.txt conforme Solução 1+2
2. 🧪 Testar build do Docker
3. 🧪 Validar funcionalidades do Supabase
4. 🧪 Testar integração com OpenAI
5. 📝 Documentar mudanças no changelog

## Comandos para Teste Local

```bash
# Limpar ambiente
docker-compose down -v

# Rebuild com novas dependências
docker-compose build --no-cache

# Testar instalação
docker-compose run --rm app pip list | grep -E "openai|supabase|httpx"
```

## Referências

- OpenAI SDK: https://pypi.org/project/openai/1.14.0/
- Supabase Python: https://pypi.org/project/supabase/
- HTTPX: https://pypi.org/project/httpx/

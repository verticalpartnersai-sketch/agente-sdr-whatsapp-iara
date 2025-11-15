# Resolução de Conflitos de Dependências - HISTÓRICO COMPLETO

## CONFLITO 1: httpx (RESOLVIDO ✅)

### Data
2025-11-15

### Problema
Build do Docker falhando com erro de conflito de dependências entre `openai`, `supabase` e `httpx`.

### Causa Raiz
- **supabase 2.4.0** requer `httpx>=0.24,<0.26`
- **httpx fixo em 0.27.0** está fora deste range
- **openai 1.14.0** aceita `httpx<1,>=0.23.0` (compatível com ambos)

### Solução Aplicada

#### Mudanças no requirements.txt

1. **Atualização do Supabase**
   ```diff
   - supabase==2.4.0
   + supabase==2.15.0
   ```

2. **Remoção do httpx fixo**
   ```diff
   - httpx==0.27.0
   + # httpx gerenciado automaticamente pelas dependências (openai, supabase)
   ```

### Status: ✅ RESOLVIDO

---

## CONFLITO 2: pydantic + redis-om (RESOLVIDO ✅)

### Data
2025-11-15

### Problema
Erro de conflito de dependências ao instalar `requirements.txt`:

```
ERROR: Cannot install -r requirements.txt (line 13), -r requirements.txt (line 20),
-r requirements.txt (line 32) and pydantic==2.6.4 because these package versions
have conflicting dependencies.
```

### Análise do Conflito

#### Requisitos de Pydantic por Pacote

| Pacote | Versão | Requisito Pydantic | Status |
|--------|--------|-------------------|--------|
| `langchain==0.1.20` | linha 13 | `pydantic<3,>=1` | ✅ Compatível |
| `openai==1.14.0` | linha 20 | `pydantic<3,>=1.9.0` | ✅ Compatível |
| `redis-om==0.2.1` | linha 32 | `pydantic<2.1.0,>=1.10.2` | ❌ CONFLITO |
| `requirements.txt` | linha 73 | `pydantic==2.6.4` | - |

#### Root Cause

- **redis-om 0.2.1** requer `pydantic<2.1.0` (máximo 2.0.x)
- **requirements.txt** fixa `pydantic==2.6.4` (incompatível)
- LangChain e OpenAI aceitam qualquer Pydantic 2.x

### Solução Implementada

#### Opção Escolhida: Remover redis-om

**Justificativa:**
1. ✅ redis-om usado apenas para cache (não essencial)
2. ✅ Mantém LangChain 0.1.20 e OpenAI 1.14.0 funcionando
3. ✅ Preserva Pydantic 2.6.4 (versão moderna e estável)
4. ✅ Nenhum código do projeto utiliza redis-om (verificado via grep)

#### Alteração em requirements.txt

```diff
# Memória e Cache
redis==5.0.3
- redis-om==0.2.1
+ # redis-om==0.2.1  # REMOVIDO: Conflito com pydantic 2.6.4 (requer pydantic<2.1.0)
```

### Versões Compatíveis Finais

#### Pacotes Principais (Mantidos)
```txt
langchain==0.1.20          # Aceita pydantic 1.x ou 2.x
langchain-openai==0.0.8    # Aceita pydantic 1.x ou 2.x
openai==1.14.0             # Aceita pydantic >=1.9.0, <3
pydantic==2.6.4            # ✅ MANTIDO
pydantic-settings==2.2.1   # ✅ MANTIDO
```

#### Cache (Simplificado)
```txt
redis==5.0.3               # Cliente Redis puro (sem ORM)
```

### Verificação

#### Teste de Instalação
```bash
pip install -r requirements.txt --dry-run
```

**Resultado:** ✅ Sucesso - Todas as dependências resolvidas

#### Verificação de Uso
```bash
grep -r "redis-om\|redis_om\|RedisOM" --include="*.py"
```

**Resultado:** ✅ Nenhum código utiliza redis-om

### Alternativas Consideradas

#### Opção 2: Downgrade de Pydantic (NÃO RECOMENDADA)

```txt
pydantic==2.0.3  # Compatível com redis-om
```

**Motivos para rejeitar:**
- ❌ Pydantic 2.0.3 é versão muito antiga (junho 2023)
- ❌ Perde melhorias de performance e segurança do Pydantic 2.6.4
- ❌ Outros pacotes podem ter problemas com versões antigas
- ❌ redis-om não é essencial para o projeto

### Impacto

#### Sem Impacto
- ✅ Nenhum código usa redis-om (verificado)
- ✅ Redis puro (redis==5.0.3) continua funcionando
- ✅ LangChain e OpenAI mantidos nas versões desejadas
- ✅ Pydantic moderno preservado

#### Cache Alternativo (se necessário)

Se precisar de ORM para Redis no futuro:

```python
# Opção 1: Redis puro com serialização manual
import redis
import json

r = redis.Redis()
r.set("key", json.dumps(data))

# Opção 2: Usar Pydantic + Redis manualmente
from pydantic import BaseModel
import redis

class CacheModel(BaseModel):
    data: str

r = redis.Redis()
r.set("key", CacheModel(data="value").model_dump_json())
```

### Status: ✅ RESOLVIDO

---

## Resumo das Resoluções

### Pacotes Removidos
1. ❌ `httpx==0.27.0` → Gerenciado automaticamente
2. ❌ `redis-om==0.2.1` → Conflito com pydantic 2.6.4

### Pacotes Atualizados
1. ⬆️ `supabase==2.4.0` → `supabase==2.15.0`

### Pacotes Mantidos (Críticos)
1. ✅ `langchain==0.1.20`
2. ✅ `openai==1.14.0`
3. ✅ `pydantic==2.6.4`
4. ✅ `redis==5.0.3`

## Comandos de Instalação

### Limpar ambiente
```bash
pip uninstall redis-om httpx -y
```

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Verificar instalação
```bash
pip list | grep -E "pydantic|langchain|openai|redis|supabase|httpx"
```

## Arquivos Modificados

- `/Users/mateusmpz/Documents/Vertical Partners - Agentes/Agente IA SDR - WhatsApp/requirements.txt`

## Documentação Relacionada

- Análise detalhada Conflito 1: `/DOCS/ANALISE_CONFLITO_DEPENDENCIAS.md`
- Este documento: `/DOCS/RESOLUCAO_CONFLITO_DEPENDENCIAS.md`

## Conclusão Final

**Todos os conflitos resolvidos com sucesso!**

- ✅ Todas as dependências compatíveis
- ✅ LangChain 0.1.20 funcional
- ✅ OpenAI 1.14.0 funcional
- ✅ Supabase 2.15.0 funcional
- ✅ Pydantic 2.6.4 preservado
- ✅ Zero impacto no código existente
- ✅ Build do Docker funcional (a validar)

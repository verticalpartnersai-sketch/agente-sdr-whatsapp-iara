# 📚 Documentação do Agente IA SDR WhatsApp

Documentação completa organizada por categorias.

---

## 📁 Estrutura de Pastas

### 🚀 `/deploy` - Guias de Deploy e Configuração
Tudo relacionado ao deploy em produção no Easypanel.

- **QUICKSTART-EASYPANEL.md** - ⚡ Deploy rápido em 5 passos (5 minutos)
- **DEPLOY-EASYPANEL.md** - 📖 Guia completo de deploy com troubleshooting
- **MEU-DEPLOY.md** - 🎯 Configuração específica do seu projeto
- **RESUMO-DEPLOY.md** - 📋 Resumo executivo do deploy
- **CHECKLIST-DEPLOY.md** - ✅ Checklist interativo de validação
- **CONFIGURAR-VARIAVEIS-EASYPANEL.md** - ⚙️ Como configurar variáveis de ambiente

**Comece por aqui:** `QUICKSTART-EASYPANEL.md`

---

### 🔑 `/credenciais` - Credenciais e Tokens
Guias para obter e configurar todas as credenciais necessárias.

- **COMO-GERAR-TOKENS.md** - 🔐 Como gerar tokens de segurança
- **DIFERENCA-IDS-WHATSAPP.md** - 🆔 Diferença entre App ID, Business ID e Phone ID
- **ONDE-ENCONTRAR-APP-SECRET.md** - 🔍 Como encontrar o App Secret do Meta

**Complementa:** `CREDENCIAIS-NECESSARIAS.md` (na raiz do projeto)

---

### 📐 `/planejamento` - Arquitetura e Planejamento
Documentação técnica sobre arquitetura e decisões de design.

- **PLANEJAMENTO-COMPLETO-AGENTE-SDR.md** - 📋 Planejamento inicial completo
- **ESTRUTURA-DO-AGENTE-SDR-WPP.md** - 🏗️ Estrutura do agente
- **DOCUMENTACAO-COMPLETA-TECNOLOGIAS-2025.md** - 🔧 Tecnologias utilizadas

**Para desenvolvedores:** Entender a arquitetura do sistema

---

### 🗄️ `/legacy` - Arquivos Legados
Arquivos antigos mantidos para referência histórica.

- **Agentes em JSON do N8N/** - JSON e prompts do N8N (versão anterior)

**Nota:** Estes arquivos são mantidos apenas para referência, não são usados na versão atual.

---

## 📖 Documentos na Raiz do Projeto

### Principais

- **README.md** - Documentação geral do projeto
- **DEPLOY.md** - Overview de deploy (entrada para guias detalhados)
- **CREDENCIAIS-NECESSARIAS.md** - Como obter todas as credenciais
- **CLAUDE.md** - Instruções específicas para Claude Code

---

## 🎯 Guias Rápidos por Objetivo

### Quero fazer deploy agora!
1. `deploy/QUICKSTART-EASYPANEL.md` ← Comece aqui
2. `credenciais/COMO-GERAR-TOKENS.md` ← Gere tokens
3. `CREDENCIAIS-NECESSARIAS.md` ← Obtenha credenciais

### Preciso configurar credenciais
1. `CREDENCIAIS-NECESSARIAS.md` ← Guia completo
2. `credenciais/DIFERENCA-IDS-WHATSAPP.md` ← IDs do WhatsApp
3. `credenciais/ONDE-ENCONTRAR-APP-SECRET.md` ← App Secret
4. `credenciais/COMO-GERAR-TOKENS.md` ← Tokens de segurança

### Quero entender a arquitetura
1. `planejamento/ESTRUTURA-DO-AGENTE-SDR-WPP.md` ← Estrutura
2. `planejamento/DOCUMENTACAO-COMPLETA-TECNOLOGIAS-2025.md` ← Tecnologias
3. `planejamento/PLANEJAMENTO-COMPLETO-AGENTE-SDR.md` ← Planejamento

### Troubleshooting de deploy
1. `deploy/DEPLOY-EASYPANEL.md` ← Troubleshooting completo
2. `deploy/CONFIGURAR-VARIAVEIS-EASYPANEL.md` ← Problemas com variáveis
3. `deploy/CHECKLIST-DEPLOY.md` ← Validação passo a passo

---

## 📊 Mapa de Navegação

```
DOCS/
├── README.md (você está aqui)
│
├── deploy/                          ← 🚀 Deploy e Configuração
│   ├── QUICKSTART-EASYPANEL.md      ← ⚡ Comece aqui!
│   ├── DEPLOY-EASYPANEL.md          ← 📖 Guia completo
│   ├── MEU-DEPLOY.md                ← 🎯 Seu projeto
│   ├── RESUMO-DEPLOY.md             ← 📋 Resumo
│   ├── CHECKLIST-DEPLOY.md          ← ✅ Validação
│   └── CONFIGURAR-VARIAVEIS-EASYPANEL.md
│
├── credenciais/                     ← 🔑 Credenciais e Tokens
│   ├── COMO-GERAR-TOKENS.md         ← 🔐 Gerar tokens
│   ├── DIFERENCA-IDS-WHATSAPP.md    ← 🆔 IDs WhatsApp
│   └── ONDE-ENCONTRAR-APP-SECRET.md ← 🔍 App Secret
│
├── planejamento/                    ← 📐 Arquitetura
│   ├── PLANEJAMENTO-COMPLETO-AGENTE-SDR.md
│   ├── ESTRUTURA-DO-AGENTE-SDR-WPP.md
│   └── DOCUMENTACAO-COMPLETA-TECNOLOGIAS-2025.md
│
└── legacy/                          ← 🗄️ Arquivos antigos
    └── Agentes em JSON do N8N/
```

---

## 🔍 Busca Rápida

### Por Palavra-Chave

**Deploy:**
- `deploy/QUICKSTART-EASYPANEL.md`
- `deploy/DEPLOY-EASYPANEL.md`

**Credenciais:**
- `/CREDENCIAIS-NECESSARIAS.md` (raiz)
- `credenciais/COMO-GERAR-TOKENS.md`

**WhatsApp:**
- `credenciais/DIFERENCA-IDS-WHATSAPP.md`
- `credenciais/ONDE-ENCONTRAR-APP-SECRET.md`

**Variáveis de Ambiente:**
- `deploy/CONFIGURAR-VARIAVEIS-EASYPANEL.md`

**Troubleshooting:**
- `deploy/DEPLOY-EASYPANEL.md` (seção completa)
- `deploy/CHECKLIST-DEPLOY.md`

**Arquitetura:**
- `planejamento/ESTRUTURA-DO-AGENTE-SDR-WPP.md`

---

## ✨ Dicas

💡 **Novo no projeto?** Comece por `deploy/QUICKSTART-EASYPANEL.md`

🔧 **Problemas no deploy?** Veja `deploy/DEPLOY-EASYPANEL.md`

🔑 **Faltam credenciais?** Consulte `/CREDENCIAIS-NECESSARIAS.md`

📖 **Quer entender como funciona?** Leia `planejamento/ESTRUTURA-DO-AGENTE-SDR-WPP.md`

---

**Última atualização:** Janeiro 2025
**Versão:** 1.0.0

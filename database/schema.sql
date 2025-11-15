-- ============================================================================
-- SCHEMA.SQL - AGENTE SDR WHATSAPP
-- ============================================================================
-- Schemas SQL para Supabase (PostgreSQL + pgvector)
--
-- Tabelas:
-- 1. leads_wpp - Gerenciamento de leads
-- 2. knowledge - Base de conhecimento (RAG híbrido)
-- 3. reunioes - Eventos do Google Calendar
--
-- Autor: Claude Code
-- Versão: 1.0
-- Data: Janeiro 2025
-- ============================================================================

-- Ativar extensão pgvector (para embeddings)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABELA: leads_wpp
-- ============================================================================
-- Gerencia leads que interagem via WhatsApp

CREATE TABLE IF NOT EXISTS leads_wpp (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),

    -- Controle de interações
    ultima_interacao_lead TIMESTAMPTZ,
    ultima_interacao_agente TIMESTAMPTZ,
    agendar_conversa TIMESTAMPTZ,  -- Follow-up personalizado

    -- Sistema de follow-up
    fup_enviado INTEGER DEFAULT 0,  -- Contador de follow-ups
    fup_ultima_data TIMESTAMPTZ,
    fup_proximo_horario TIMESTAMPTZ,

    -- Tags e status
    tags TEXT[] DEFAULT ARRAY['IA'],  -- IA, BREAK, reuniao_*, nao_interessado, etc
    status VARCHAR(50) DEFAULT 'ativo',  -- ativo, inativo, convertido

    -- Metadados
    origem VARCHAR(100) DEFAULT 'whatsapp',
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_leads_telefone ON leads_wpp(telefone);
CREATE INDEX idx_leads_tags ON leads_wpp USING GIN(tags);
CREATE INDEX idx_leads_fup_proximo ON leads_wpp(fup_proximo_horario)
    WHERE fup_proximo_horario IS NOT NULL;
CREATE INDEX idx_leads_status ON leads_wpp(status);

-- Trigger para atualizar atualizado_em
CREATE OR REPLACE FUNCTION update_atualizado_em()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_leads_timestamp
BEFORE UPDATE ON leads_wpp
FOR EACH ROW
EXECUTE FUNCTION update_atualizado_em();


-- ============================================================================
-- TABELA: knowledge
-- ============================================================================
-- Base de conhecimento com RAG híbrido (semântico + BM25)

CREATE TABLE IF NOT EXISTS knowledge (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Conteúdo
    assunto VARCHAR(255) NOT NULL,
    conteudo TEXT NOT NULL,

    -- Q&A
    perguntas TEXT[],
    respostas TEXT[],

    -- RAG: Embedding para busca semântica
    embedding vector(1536),  -- OpenAI text-embedding-3-small

    -- Metadados
    tags TEXT[],
    categoria VARCHAR(100),
    prioridade INTEGER DEFAULT 1,  -- 1-10 (quanto maior, mais importante)
    ativo BOOLEAN DEFAULT TRUE,

    -- Controle
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para similaridade semântica (ivfflat)
CREATE INDEX idx_knowledge_embedding ON knowledge
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Índice full-text search para BM25 (busca por palavras-chave)
CREATE INDEX idx_knowledge_conteudo_fts ON knowledge
USING gin(to_tsvector('portuguese', conteudo));

-- Índices adicionais
CREATE INDEX idx_knowledge_tags ON knowledge USING GIN(tags);
CREATE INDEX idx_knowledge_categoria ON knowledge(categoria);
CREATE INDEX idx_knowledge_ativo ON knowledge(ativo) WHERE ativo = TRUE;

-- Trigger para atualizar atualizado_em
CREATE TRIGGER trigger_update_knowledge_timestamp
BEFORE UPDATE ON knowledge
FOR EACH ROW
EXECUTE FUNCTION update_atualizado_em();


-- ============================================================================
-- FUNÇÃO: hybrid_search
-- ============================================================================
-- Busca híbrida: 60% semântica + 40% BM25

CREATE OR REPLACE FUNCTION hybrid_search(
    query_embedding vector(1536),
    query_text TEXT,
    match_count INT DEFAULT 5,
    semantic_weight FLOAT DEFAULT 0.6
)
RETURNS TABLE (
    id UUID,
    assunto VARCHAR,
    conteudo TEXT,
    similarity_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    WITH semantic_search AS (
        SELECT
            k.id,
            k.assunto,
            k.conteudo,
            1 - (k.embedding <=> query_embedding) as score
        FROM knowledge k
        WHERE k.ativo = TRUE
        ORDER BY k.embedding <=> query_embedding
        LIMIT match_count * 2
    ),
    keyword_search AS (
        SELECT
            k.id,
            k.assunto,
            k.conteudo,
            ts_rank(
                to_tsvector('portuguese', k.conteudo),
                plainto_tsquery('portuguese', query_text)
            ) as score
        FROM knowledge k
        WHERE
            k.ativo = TRUE
            AND to_tsvector('portuguese', k.conteudo) @@
                plainto_tsquery('portuguese', query_text)
        ORDER BY score DESC
        LIMIT match_count * 2
    )
    SELECT
        COALESCE(s.id, k.id) as id,
        COALESCE(s.assunto, k.assunto) as assunto,
        COALESCE(s.conteudo, k.conteudo) as conteudo,
        (
            COALESCE(s.score, 0) * semantic_weight +
            COALESCE(k.score, 0) * (1 - semantic_weight)
        ) as similarity_score
    FROM semantic_search s
    FULL OUTER JOIN keyword_search k ON s.id = k.id
    ORDER BY similarity_score DESC
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- TABELA: reunioes
-- ============================================================================
-- Gerencia reuniões agendadas no Google Calendar

CREATE TABLE IF NOT EXISTS reunioes (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads_wpp(id) ON DELETE CASCADE,

    -- Integração Google Calendar
    google_event_id VARCHAR(255) UNIQUE,

    -- Dados da reunião
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,

    -- Horários
    data_inicio TIMESTAMPTZ NOT NULL,
    data_fim TIMESTAMPTZ NOT NULL,

    -- Participantes (JSONB para flexibilidade)
    participantes JSONB,  -- [{"email": "...", "nome": "...", "confirmado": true}]

    -- Status
    status VARCHAR(50) DEFAULT 'agendada',  -- agendada, confirmada, cancelada, concluida

    -- Lembretes
    lembrete_24h_enviado BOOLEAN DEFAULT FALSE,
    lembrete_2h_enviado BOOLEAN DEFAULT FALSE,

    -- Controle
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_reunioes_lead ON reunioes(lead_id);
CREATE INDEX idx_reunioes_google_id ON reunioes(google_event_id);
CREATE INDEX idx_reunioes_data_inicio ON reunioes(data_inicio);
CREATE INDEX idx_reunioes_status ON reunioes(status);

-- Índice para buscar reuniões próximas (lembretes)
CREATE INDEX idx_reunioes_proximas ON reunioes(data_inicio, status)
WHERE status = 'agendada';

-- Trigger para atualizar atualizado_em
CREATE TRIGGER trigger_update_reunioes_timestamp
BEFORE UPDATE ON reunioes
FOR EACH ROW
EXECUTE FUNCTION update_atualizado_em();


-- ============================================================================
-- POLÍTICAS RLS (Row Level Security)
-- ============================================================================
-- Habilitar RLS para segurança

-- Leads
ALTER TABLE leads_wpp ENABLE ROW LEVEL SECURITY;

-- Permitir leitura autenticada
CREATE POLICY "Permitir leitura autenticada de leads"
ON leads_wpp FOR SELECT
TO authenticated
USING (true);

-- Permitir inserção autenticada
CREATE POLICY "Permitir inserção autenticada de leads"
ON leads_wpp FOR INSERT
TO authenticated
WITH CHECK (true);

-- Permitir atualização autenticada
CREATE POLICY "Permitir atualização autenticada de leads"
ON leads_wpp FOR UPDATE
TO authenticated
USING (true);


-- Knowledge
ALTER TABLE knowledge ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir leitura autenticada de knowledge"
ON knowledge FOR SELECT
TO authenticated
USING (ativo = TRUE);


-- Reuniões
ALTER TABLE reunioes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir leitura autenticada de reuniões"
ON reunioes FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Permitir inserção autenticada de reuniões"
ON reunioes FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Permitir atualização autenticada de reuniões"
ON reunioes FOR UPDATE
TO authenticated
USING (true);


-- ============================================================================
-- DADOS DE EXEMPLO (opcional, comentado)
-- ============================================================================

-- Exemplo de conhecimento
/*
INSERT INTO knowledge (assunto, conteudo, embedding, tags, categoria)
VALUES (
    'Sobre a Vertical Partners',
    'A Vertical Partners é uma empresa especializada em soluções de IA para negócios...',
    -- embedding seria gerado via código
    NULL,
    ARRAY['empresa', 'institucional'],
    'institucional'
);
*/

-- Exemplo de lead
/*
INSERT INTO leads_wpp (nome, telefone, email, tags)
VALUES (
    'João Silva',
    '5511999999999',
    'joao@email.com',
    ARRAY['IA', 'alta_intencao']
);
*/

-- ============================================================================
-- FIM DO SCHEMA
-- ============================================================================

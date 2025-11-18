"""
CORE/MEMORY.PY
==============
Sistema de memória, buffer e RAG híbrido:
- RedisMemoryManager: Histórico conversacional no Redis
- MessageBuffer: Agrupamento de mensagens (30s)
- HybridRetriever: RAG 60% semântico + 40% BM25
- KnowledgeManager: Gerenciamento da base de conhecimento
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

import redis.asyncio as redis
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from loguru import logger

from core.integrations import SupabaseClient


# ==============================================================================
# REDIS MEMORY MANAGER
# ==============================================================================

@dataclass
class Message:
    """Estrutura de uma mensagem."""
    role: str  # "human" ou "ai"
    content: str
    timestamp: str
    metadata: Dict = None


class RedisMemoryManager:
    """
    Gerencia memória conversacional com Redis.

    Features:
    - Histórico persistente (168h = 7 dias)
    - Limite de 100 mensagens por conversa
    - Sumarização automática quando necessário
    - Contexto deslizante para o agente
    """

    def __init__(self, redis_client: redis.Redis):
        """
        Inicializa manager de memória.

        Args:
            redis_client: Cliente Redis assíncrono
        """
        self.redis = redis_client
        self.max_messages = 100
        self.ttl_hours = 168  # 7 dias

    async def add_message(
        self,
        phone: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        Adiciona mensagem ao histórico.

        Args:
            phone: Número de telefone (chave única)
            role: "human" ou "ai"
            content: Conteúdo da mensagem
            metadata: Metadados opcionais (tipo, message_id, etc)
        """
        key = f"chat_history:{phone}"

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        # Adicionar à lista (início)
        await self.redis.lpush(key, json.dumps(message))

        # Limitar tamanho
        await self.redis.ltrim(key, 0, self.max_messages - 1)

        # Definir TTL
        await self.redis.expire(key, self.ttl_hours * 3600)

        logger.debug(f"Mensagem adicionada ao histórico de {phone}")

    async def get_history(
        self,
        phone: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Recupera histórico de conversação.

        Args:
            phone: Número de telefone
            limit: Quantidade máxima de mensagens (None = todas)

        Returns:
            Lista de mensagens (mais recentes primeiro)
        """
        key = f"chat_history:{phone}"
        limit = limit or self.max_messages

        messages_raw = await self.redis.lrange(key, 0, limit - 1)

        messages = [
            Message(**json.loads(msg))
            for msg in messages_raw
        ]

        return messages

    async def get_history_formatted(
        self,
        phone: str,
        limit: Optional[int] = None,
        reverse: bool = True
    ) -> List[Dict]:
        """
        Retorna histórico formatado para LangChain.

        Args:
            phone: Número de telefone
            limit: Limite de mensagens
            reverse: Se True, retorna em ordem cronológica

        Returns:
            Lista de dicts {"role": "human"/"ai", "content": "..."}
        """
        messages = await self.get_history(phone, limit)

        formatted = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        if reverse:
            formatted = list(reversed(formatted))

        return formatted

    async def clear_history(self, phone: str) -> bool:
        """
        Limpa completamente o histórico de conversação.

        Args:
            phone: Número de telefone

        Returns:
            True se limpou com sucesso
        """
        key = f"chat_history:{phone}"

        # Deletar chave do Redis
        deleted = await self.redis.delete(key)

        if deleted:
            logger.info(f"✅ Histórico limpo para {phone}")
            return True
        else:
            logger.warning(f"⚠️ Nenhum histórico encontrado para {phone}")
            return False

    async def get_conversation_summary(self, phone: str) -> str:
        """
        Gera resumo da conversa (útil para contextos longos).

        Args:
            phone: Número de telefone

        Returns:
            Resumo textual da conversa
        """
        messages = await self.get_history(phone, limit=20)

        if not messages:
            return "Nenhuma conversa anterior."

        # Formatar para resumo simples
        summary_parts = []
        for msg in reversed(messages):
            role_label = "Lead" if msg.role == "human" else "Agente"
            summary_parts.append(f"{role_label}: {msg.content[:100]}")

        return "\n".join(summary_parts[-10:])  # Últimas 10 mensagens


# ==============================================================================
# MESSAGE BUFFER
# ==============================================================================

class MessageBuffer:
    """
    Agrupa mensagens enviadas rapidamente pelo lead.

    Aguarda 30 segundos desde a última mensagem antes de processar.
    Evita múltiplas respostas fragmentadas quando lead envia várias mensagens.
    """

    def __init__(self, redis_client: redis.Redis, process_callback):
        """
        Inicializa buffer de mensagens.

        Args:
            redis_client: Cliente Redis
            process_callback: Função async para processar buffer
                              callback(phone, combined_content, messages)
        """
        self.redis = redis_client
        self.process_callback = process_callback
        self.window_seconds = 30
        self.tasks: Dict[str, asyncio.Task] = {}

    async def add_message(self, phone: str, message: Dict):
        """
        Adiciona mensagem ao buffer.

        Se já existe timer rodando, cancela e reinicia.

        Args:
            phone: Número de telefone
            message: Dict com dados da mensagem
                     {message_id, content, timestamp, media_url?, media_type?}
        """
        # Cancelar timer existente
        if phone in self.tasks:
            self.tasks[phone].cancel()

        # Adicionar mensagem ao buffer Redis
        key = f"buffer:{phone}"
        await self.redis.lpush(key, json.dumps(message))
        await self.redis.expire(key, 60)  # TTL 60s

        # Criar novo timer
        self.tasks[phone] = asyncio.create_task(
            self._process_after_delay(phone)
        )

        logger.debug(f"Mensagem adicionada ao buffer de {phone}")

    async def _process_after_delay(self, phone: str):
        """
        Aguarda 30s sem novas mensagens e processa buffer.

        Args:
            phone: Número de telefone
        """
        try:
            # Aguardar janela de tempo
            await asyncio.sleep(self.window_seconds)

            # Recuperar todas as mensagens do buffer
            key = f"buffer:{phone}"
            messages_raw = await self.redis.lrange(key, 0, -1)

            if not messages_raw:
                return

            # Limpar buffer
            await self.redis.delete(key)

            # Parse mensagens
            messages = [json.loads(msg) for msg in reversed(messages_raw)]

            # Combinar conteúdo
            combined_content = self._combine_messages(messages)

            logger.info(f"Processando buffer de {phone}: {len(messages)} mensagens")

            # Processar com callback
            await self.process_callback(phone, combined_content, messages)

        except asyncio.CancelledError:
            # Timer cancelado, nova mensagem chegou
            logger.debug(f"Buffer de {phone} cancelado (nova mensagem)")
        except Exception as e:
            logger.error(f"Erro ao processar buffer de {phone}: {e}")
        finally:
            # Remover task
            if phone in self.tasks:
                del self.tasks[phone]

    def _combine_messages(self, messages: List[Dict]) -> str:
        """
        Combina múltiplas mensagens em uma única entrada.

        Args:
            messages: Lista de mensagens do buffer

        Returns:
            Conteúdo combinado
        """
        text_parts = []
        media_items = []

        for msg in messages:
            # Textos
            if msg.get('content'):
                text_parts.append(msg['content'])

            # Mídias
            if msg.get('media_url'):
                media_items.append({
                    'url': msg['media_url'],
                    'type': msg['media_type']
                })

        # Combinar textos
        combined = "\n".join(text_parts)

        # Adicionar referências de mídia
        if media_items:
            media_desc = "\n".join([
                f"[{item['type'].upper()}]: {item['url']}"
                for item in media_items
            ])
            combined += f"\n\nMídias anexadas:\n{media_desc}"

        return combined


# ==============================================================================
# SESSION STATE MANAGER
# ==============================================================================

class SessionStateManager:
    """
    Gerencia estado da sessão no Redis.

    Armazena contexto temporário da conversa:
    - Intenção identificada
    - Dados temporários
    - Tool em execução
    - Aguardando confirmação
    """

    def __init__(self, redis_client: redis.Redis):
        """Inicializa manager de sessão."""
        self.redis = redis_client
        self.ttl_hours = 24

    async def set_state(self, phone: str, state_data: Dict):
        """
        Define estado da sessão.

        Args:
            phone: Número de telefone
            state_data: Dados do estado
        """
        key = f"session:{phone}"

        # Salvar cada campo como hash
        for field, value in state_data.items():
            await self.redis.hset(key, field, json.dumps(value))

        # TTL 24h
        await self.redis.expire(key, self.ttl_hours * 3600)

    async def get_state(self, phone: str) -> Dict:
        """
        Recupera estado da sessão.

        Args:
            phone: Número de telefone

        Returns:
            Dict com estado ou {} se não existe
        """
        key = f"session:{phone}"
        state_raw = await self.redis.hgetall(key)

        if not state_raw:
            return {}

        # Parse JSON de cada campo
        state = {
            field.decode(): json.loads(value.decode())
            for field, value in state_raw.items()
        }

        return state

    async def update_state(self, phone: str, updates: Dict):
        """
        Atualiza campos específicos do estado.

        Args:
            phone: Número de telefone
            updates: Campos a atualizar
        """
        current_state = await self.get_state(phone)
        current_state.update(updates)
        await self.set_state(phone, current_state)

    async def clear_state(self, phone: str):
        """Limpa estado da sessão."""
        key = f"session:{phone}"
        await self.redis.delete(key)


# ==============================================================================
# HYBRID RETRIEVER (RAG)
# ==============================================================================

class HybridRetriever:
    """
    RAG Híbrido: 60% Busca Semântica + 40% BM25.

    Combina similaridade vetorial (embeddings) com busca por palavras-chave
    para melhor precisão na recuperação de conhecimento.
    """

    def __init__(
        self,
        supabase_client: SupabaseClient,
        embeddings: OpenAIEmbeddings
    ):
        """
        Inicializa retriever híbrido.

        Args:
            supabase_client: Cliente Supabase
            embeddings: OpenAI embeddings
        """
        self.supabase = supabase_client
        self.embeddings = embeddings

    async def retrieve(
        self,
        query: str,
        k: int = 5,
        semantic_weight: float = 0.6
    ) -> List[Document]:
        """
        Busca híbrida com pesos ajustados.

        Args:
            query: Pergunta do usuário
            k: Quantidade de documentos a retornar
            semantic_weight: Peso da busca semântica (default: 0.6 = 60%)

        Returns:
            Lista de documentos relevantes (LangChain Document)
        """
        # 1. Gerar embedding da query
        query_embedding = await self.embeddings.aembed_query(query)

        # 2. Executar busca híbrida no Supabase
        results = await self.supabase.hybrid_search(
            query_embedding=query_embedding,
            query_text=query,
            match_count=k,
            semantic_weight=semantic_weight
        )

        # 3. Converter para Documents do LangChain
        documents = [
            Document(
                page_content=r['conteudo'],
                metadata={
                    'id': r['id'],
                    'assunto': r['assunto'],
                    'score': r['similarity_score'],
                    'source': 'knowledge_base'
                }
            )
            for r in results
        ]

        logger.info(f"RAG híbrido: {len(documents)} documentos recuperados")
        return documents

    async def retrieve_formatted(
        self,
        query: str,
        k: int = 5
    ) -> str:
        """
        Busca e retorna contexto formatado.

        Args:
            query: Pergunta
            k: Quantidade de docs

        Returns:
            String formatada para inserir no prompt
        """
        documents = await self.retrieve(query, k)

        if not documents:
            return "Nenhum conhecimento relevante encontrado."

        # Formatar contexto
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(
                f"[Documento {i}]\n"
                f"Assunto: {doc.metadata['assunto']}\n"
                f"Conteúdo: {doc.page_content}\n"
                f"Relevância: {doc.metadata['score']:.2f}\n"
            )

        return "\n".join(context_parts)


# ==============================================================================
# KNOWLEDGE MANAGER
# ==============================================================================

class KnowledgeManager:
    """
    Gerencia base de conhecimento no Supabase.

    Funcionalidades:
    - Adicionar conhecimento com embeddings
    - Importação em massa
    - Atualização de embeddings
    - Busca e recuperação
    """

    def __init__(
        self,
        supabase_client: SupabaseClient,
        embeddings: OpenAIEmbeddings
    ):
        """
        Inicializa knowledge manager.

        Args:
            supabase_client: Cliente Supabase
            embeddings: OpenAI embeddings
        """
        self.supabase = supabase_client
        self.embeddings = embeddings

    async def add_knowledge(
        self,
        assunto: str,
        conteudo: str,
        perguntas: Optional[List[str]] = None,
        respostas: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        categoria: Optional[str] = None
    ) -> str:
        """
        Adiciona novo conhecimento com embedding.

        Args:
            assunto: Título/assunto do conhecimento
            conteudo: Conteúdo detalhado
            perguntas: Lista de perguntas relacionadas
            respostas: Lista de respostas
            tags: Tags para categorização
            categoria: Categoria principal

        Returns:
            ID do conhecimento criado
        """
        # Gerar embedding do conteúdo
        embedding = await self.embeddings.aembed_query(conteudo)

        # Inserir no Supabase
        result = await self.supabase.add_knowledge(
            assunto=assunto,
            conteudo=conteudo,
            embedding=embedding,
            perguntas=perguntas,
            respostas=respostas,
            tags=tags,
            categoria=categoria
        )

        logger.info(f"Conhecimento '{assunto}' adicionado à base")
        return result['id']

    async def bulk_import_from_json(self, file_path: str):
        """
        Importa conhecimento em massa de arquivo JSON.

        Formato esperado:
        [
            {
                "assunto": "...",
                "conteudo": "...",
                "perguntas": ["...", "..."],
                "respostas": ["...", "..."],
                "tags": ["...", "..."],
                "categoria": "..."
            },
            ...
        ]

        Args:
            file_path: Caminho do arquivo JSON
        """
        import json
        from pathlib import Path

        data = json.loads(Path(file_path).read_text())

        logger.info(f"Importando {len(data)} conhecimentos...")

        for item in data:
            try:
                await self.add_knowledge(**item)
            except Exception as e:
                logger.error(f"Erro ao importar {item.get('assunto')}: {e}")

        logger.info("Importação concluída")

    async def update_embeddings_batch(self, batch_size: int = 10):
        """
        Atualiza embeddings de toda a base de conhecimento.

        Útil quando mudar o modelo de embeddings.

        Args:
            batch_size: Quantidade de documentos por lote
        """
        # TODO: Implementar lógica de atualização em lote
        # 1. Buscar todos os conhecimentos
        # 2. Gerar novos embeddings
        # 3. Atualizar no Supabase
        logger.warning("update_embeddings_batch não implementado")


# ==============================================================================
# CONVERSATION SUMMARIZER
# ==============================================================================

class ConversationSummarizer:
    """
    Sumariza conversas longas para economizar tokens.

    Quando histórico > 1000 tokens, cria resumo automático.
    """

    def __init__(self, llm):
        """
        Inicializa sumarizador.

        Args:
            llm: Modelo LLM para sumarização
        """
        self.llm = llm

    async def summarize_if_needed(
        self,
        messages: List[Message],
        max_tokens: int = 1000
    ) -> Optional[str]:
        """
        Sumariza conversa se necessário.

        Args:
            messages: Lista de mensagens
            max_tokens: Limite de tokens

        Returns:
            Resumo da conversa ou None se não necessário
        """
        # Estimar tokens (aproximação simples: 1 token ≈ 4 caracteres)
        total_chars = sum(len(msg.content) for msg in messages)
        estimated_tokens = total_chars // 4

        if estimated_tokens < max_tokens:
            return None

        # Criar resumo
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in messages
        ])

        summary_prompt = f"""
        Resuma a conversa abaixo de forma concisa, mantendo:
        - Principais tópicos discutidos
        - Informações importantes sobre o lead
        - Intenções identificadas
        - Próximos passos acordados

        Conversa:
        {conversation_text}

        Resumo:
        """

        summary = await self.llm.apredict(summary_prompt)

        logger.info("Conversa sumarizada para economizar tokens")
        return summary


# ==============================================================================
# EXPORTAÇÕES
# ==============================================================================

__all__ = [
    'RedisMemoryManager',
    'MessageBuffer',
    'SessionStateManager',
    'HybridRetriever',
    'KnowledgeManager',
    'ConversationSummarizer',
    'Message'
]

"""
CORE/AGENT.PY
=============
Agente SDR principal com tools customizadas.

Componentes:
- AgenteSDR: Orquestrador principal
- Tools: WhatsApp, Google Calendar, Supabase, Knowledge, Media Analysis
- MessageFormatter: Fragmentação humanizada de mensagens
"""

import asyncio
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool, StructuredTool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field
from loguru import logger

from core.integrations import (
    WhatsAppClient,
    GoogleCalendarClient,
    SupabaseClient,
    ElevenLabsClient
)
from core.memory import (
    RedisMemoryManager,
    HybridRetriever,
    SessionStateManager
)


# ==============================================================================
# MESSAGE FORMATTER
# ==============================================================================

class MessageFormatter:
    """
    Formata e fragmenta mensagens para envio humanizado.

    Fragmentação: 20-30 palavras por mensagem.
    """

    @staticmethod
    def fragmentar_mensagem(texto: str, max_palavras: int = 30) -> List[str]:
        """
        Fragmenta texto em mensagens de 20-30 palavras.

        Args:
            texto: Texto completo
            max_palavras: Máximo de palavras por fragmento

        Returns:
            Lista de fragmentos
        """
        # Dividir por pontuação forte primeiro
        sentencas = re.split(r'([.!?\n]+)', texto)

        fragmentos = []
        fragmento_atual = ""

        for i in range(0, len(sentencas), 2):
            sentenca = sentencas[i]
            pontuacao = sentencas[i+1] if i+1 < len(sentencas) else ""

            palavras_sentenca = len(sentenca.split())
            palavras_atual = len(fragmento_atual.split())

            # Se adicionar ultrapassaria limite, salvar fragmento
            if palavras_atual + palavras_sentenca > max_palavras and fragmento_atual:
                fragmentos.append(fragmento_atual.strip())
                fragmento_atual = sentenca + pontuacao
            else:
                fragmento_atual += sentenca + pontuacao

        # Adicionar último fragmento
        if fragmento_atual.strip():
            fragmentos.append(fragmento_atual.strip())

        return fragmentos

    @staticmethod
    async def enviar_fragmentado(
        whatsapp_client: WhatsAppClient,
        telefone: str,
        texto: str,
        delay_min: float = 1.0,
        delay_max: float = 5.0
    ):
        """
        Envia mensagem fragmentada com delay natural.

        Args:
            whatsapp_client: Cliente WhatsApp
            telefone: Número do destinatário
            texto: Texto completo
            delay_min: Delay mínimo entre mensagens (segundos)
            delay_max: Delay máximo entre mensagens (segundos)
        """
        import random

        fragmentos = MessageFormatter.fragmentar_mensagem(texto)

        for i, fragmento in enumerate(fragmentos):
            if i > 0:
                # Delay natural entre mensagens
                await asyncio.sleep(random.uniform(delay_min, delay_max))

            await whatsapp_client.send_text(telefone, fragmento)

        logger.info(f"Mensagem fragmentada enviada: {len(fragmentos)} partes")


# ==============================================================================
# TOOLS SCHEMAS (Pydantic)
# ==============================================================================

class EnviarMensagemInput(BaseModel):
    telefone: str = Field(description="Número de telefone do destinatário (ex: 5511999999999)")
    texto: str = Field(description="Texto da mensagem a enviar")


class EnviarAudioInput(BaseModel):
    telefone: str = Field(description="Número de telefone do destinatário")
    texto_para_falar: str = Field(description="Texto que será convertido em áudio")


class ConsultaHorariosInput(BaseModel):
    data_inicio: str = Field(description="Data de início no formato ISO (YYYY-MM-DD)")
    data_fim: str = Field(description="Data de fim no formato ISO (YYYY-MM-DD)")
    duracao_minutos: int = Field(default=60, description="Duração da reunião em minutos")


class AgendaReuniaoInput(BaseModel):
    titulo: str = Field(description="Título da reunião")
    data_hora_inicio: str = Field(description="Data/hora início (ISO: YYYY-MM-DDTHH:MM:SS)")
    participantes: List[str] = Field(description="Lista de emails dos participantes")
    descricao: Optional[str] = Field(default=None, description="Descrição da reunião")


class CancelaReuniaoInput(BaseModel):
    evento_id: str = Field(description="ID do evento no Google Calendar")


class ReagendaReuniaoInput(BaseModel):
    evento_id: str = Field(description="ID do evento")
    nova_data_hora_inicio: str = Field(description="Nova data/hora (ISO)")
    nova_data_hora_fim: str = Field(description="Nova data/hora fim (ISO)")


class AtualizaTagInput(BaseModel):
    telefone: str = Field(description="Número de telefone do lead")
    tag: str = Field(description="Tag a adicionar (ex: 'reuniao_agendada', 'nao_interessado')")


class BuscarConhecimentoInput(BaseModel):
    pergunta: str = Field(description="Pergunta ou tópico para buscar na base de conhecimento")


class AnalisarImagemInput(BaseModel):
    url_imagem: str = Field(description="URL da imagem para analisar")


class TranscreverAudioInput(BaseModel):
    url_audio: str = Field(description="URL do áudio para transcrever")


# ==============================================================================
# AGENTE SDR
# ==============================================================================

class AgenteSDR:
    """
    Agente SDR principal com todas as ferramentas.

    Integra:
    - LangChain Agent Executor
    - 15+ Tools customizadas
    - Memória conversacional Redis
    - RAG híbrido
    - Formatação humanizada
    """

    def __init__(
        self,
        whatsapp_client: WhatsAppClient,
        google_calendar_client: GoogleCalendarClient,
        supabase_client: SupabaseClient,
        elevenlabs_client: ElevenLabsClient,
        redis_memory: RedisMemoryManager,
        hybrid_retriever: HybridRetriever,
        session_state: SessionStateManager,
        openai_api_key: str,
        prompt_path: str = "config/prompt.md"
    ):
        """Inicializa agente SDR."""
        self.whatsapp = whatsapp_client
        self.google_calendar = google_calendar_client
        self.supabase = supabase_client
        self.elevenlabs = elevenlabs_client
        self.memory = redis_memory
        self.retriever = hybrid_retriever
        self.session_state = session_state

        # LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=openai_api_key
        )

        # Carregar prompt
        self.prompt_principal = Path(prompt_path).read_text()

        # Criar tools
        self.tools = self._create_tools()

        # Criar agente
        self.agent = self._create_agent()

        logger.info("Agente SDR inicializado com sucesso")

    def _create_tools(self) -> List[BaseTool]:
        """Cria todas as tools do agente."""

        tools = [
            # === WHATSAPP TOOLS ===
            StructuredTool.from_function(
                func=self._tool_enviar_mensagem,
                name="enviar_mensagem",
                description="Envia mensagem de texto fragmentada para o lead via WhatsApp",
                args_schema=EnviarMensagemInput
            ),

            StructuredTool.from_function(
                func=self._tool_enviar_audio,
                name="enviar_audio",
                description="Converte texto em áudio via ElevenLabs e envia para o lead",
                args_schema=EnviarAudioInput
            ),

            # === GOOGLE CALENDAR TOOLS ===
            StructuredTool.from_function(
                func=self._tool_consulta_horarios,
                name="consulta_horarios",
                description="Busca horários disponíveis no Google Calendar",
                args_schema=ConsultaHorariosInput
            ),

            StructuredTool.from_function(
                func=self._tool_agenda_reuniao,
                name="agenda_reuniao",
                description="Agenda nova reunião no Google Calendar com Google Meet",
                args_schema=AgendaReuniaoInput
            ),

            StructuredTool.from_function(
                func=self._tool_cancela_reuniao,
                name="cancela_reuniao",
                description="Cancela reunião existente no Google Calendar",
                args_schema=CancelaReuniaoInput
            ),

            StructuredTool.from_function(
                func=self._tool_reagenda_reuniao,
                name="reagenda_reuniao",
                description="Reagenda reunião para nova data/hora",
                args_schema=ReagendaReuniaoInput
            ),

            # === SUPABASE TOOLS ===
            StructuredTool.from_function(
                func=self._tool_atualizar_tag,
                name="atualizar_tag",
                description="Adiciona tag ao lead (ex: 'reuniao_agendada', 'nao_interessado')",
                args_schema=AtualizaTagInput
            ),

            # === KNOWLEDGE BASE TOOL ===
            StructuredTool.from_function(
                func=self._tool_buscar_conhecimento,
                name="buscar_conhecimento",
                description="Busca informações relevantes na base de conhecimento via RAG híbrido",
                args_schema=BuscarConhecimentoInput
            ),

            # === MEDIA ANALYSIS TOOLS ===
            StructuredTool.from_function(
                func=self._tool_analisar_imagem,
                name="analisar_imagem",
                description="Analisa imagem enviada pelo lead usando visão computacional",
                args_schema=AnalisarImagemInput
            ),

            StructuredTool.from_function(
                func=self._tool_transcrever_audio,
                name="transcrever_audio",
                description="Transcreve áudio enviado pelo lead para texto",
                args_schema=TranscreverAudioInput
            ),
        ]

        return tools

    # === IMPLEMENTAÇÃO DAS TOOLS ===

    async def _tool_enviar_mensagem(self, telefone: str, texto: str) -> str:
        """Tool: Enviar mensagem fragmentada."""
        try:
            await MessageFormatter.enviar_fragmentado(
                self.whatsapp,
                telefone,
                texto
            )

            # Salvar na memória
            await self.memory.add_message(telefone, "ai", texto)

            return f"Mensagem enviada com sucesso para {telefone}"
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return f"Erro ao enviar mensagem: {str(e)}"

    async def _tool_enviar_audio(self, telefone: str, texto_para_falar: str) -> str:
        """Tool: Enviar áudio via ElevenLabs."""
        try:
            # Gerar áudio
            audio_bytes = await self.elevenlabs.text_to_speech(texto_para_falar)

            # Upload no Supabase Storage
            audio_path = f"audios/{telefone}/{datetime.now().timestamp()}.mp3"
            audio_url = await self.supabase.upload_file(
                bucket="midias",
                file_path=audio_path,
                file_data=audio_bytes,
                content_type="audio/mpeg"
            )

            # Enviar via WhatsApp
            await self.whatsapp.send_audio(telefone, audio_url)

            # Salvar na memória
            await self.memory.add_message(
                telefone,
                "ai",
                f"[ÁUDIO]: {texto_para_falar}",
                metadata={"type": "audio", "url": audio_url}
            )

            return f"Áudio enviado com sucesso para {telefone}"
        except Exception as e:
            logger.error(f"Erro ao enviar áudio: {e}")
            return f"Erro ao enviar áudio: {str(e)}"

    async def _tool_consulta_horarios(
        self,
        data_inicio: str,
        data_fim: str,
        duracao_minutos: int = 60
    ) -> str:
        """Tool: Consultar horários disponíveis."""
        try:
            inicio = datetime.fromisoformat(data_inicio)
            fim = datetime.fromisoformat(data_fim)

            slots = await self.google_calendar.listar_horarios_disponiveis(
                inicio,
                fim,
                duracao_minutos
            )

            if not slots:
                return "Nenhum horário disponível neste período."

            # Formatar resposta
            horarios_formatados = []
            for i, slot in enumerate(slots[:5], 1):  # Máximo 5 opções
                dia = slot['inicio'].strftime("%d/%m/%Y")
                hora = slot['inicio'].strftime("%H:%M")
                horarios_formatados.append(f"{i}. {dia} às {hora}")

            return "Horários disponíveis:\n" + "\n".join(horarios_formatados)
        except Exception as e:
            logger.error(f"Erro ao consultar horários: {e}")
            return f"Erro ao consultar horários: {str(e)}"

    async def _tool_agenda_reuniao(
        self,
        titulo: str,
        data_hora_inicio: str,
        participantes: List[str],
        descricao: Optional[str] = None
    ) -> str:
        """Tool: Agendar reunião."""
        try:
            inicio = datetime.fromisoformat(data_hora_inicio)
            fim = inicio + timedelta(minutes=60)  # 1 hora de duração padrão

            # Criar evento no Google Calendar
            evento = await self.google_calendar.agendar_reuniao(
                titulo=titulo,
                data_inicio=inicio,
                data_fim=fim,
                participantes=participantes,
                descricao=descricao
            )

            # Salvar no Supabase
            lead_telefone = await self._get_telefone_from_context()
            lead = await self.supabase.get_lead(lead_telefone)

            reuniao_data = {
                "lead_id": lead['id'],
                "google_event_id": evento['id'],
                "titulo": titulo,
                "descricao": descricao,
                "data_inicio": inicio.isoformat(),
                "data_fim": fim.isoformat(),
                "participantes": participantes,
                "status": "agendada"
            }

            await self.supabase.create_reuniao(reuniao_data)

            # Adicionar tag
            await self.supabase.add_tag(lead_telefone, "reuniao_agendada")

            # Link do Meet
            meet_link = evento.get('hangoutLink', 'N/A')

            return f"Reunião agendada com sucesso!\nData: {inicio.strftime('%d/%m/%Y %H:%M')}\nLink do Meet: {meet_link}"
        except Exception as e:
            logger.error(f"Erro ao agendar reunião: {e}")
            return f"Erro ao agendar reunião: {str(e)}"

    async def _tool_cancela_reuniao(self, evento_id: str) -> str:
        """Tool: Cancelar reunião."""
        try:
            success = await self.google_calendar.cancelar_reuniao(evento_id)

            if success:
                # Atualizar Supabase
                reuniao = await self.supabase.get_reuniao_by_google_id(evento_id)
                if reuniao:
                    await self.supabase.update_reuniao(
                        reuniao['id'],
                        {"status": "cancelada"}
                    )

                # Atualizar tag do lead
                lead_telefone = await self._get_telefone_from_context()
                await self.supabase.remove_tag(lead_telefone, "reuniao_agendada")
                await self.supabase.add_tag(lead_telefone, "reuniao_cancelada")

                return "Reunião cancelada com sucesso."
            else:
                return "Não foi possível cancelar a reunião."
        except Exception as e:
            logger.error(f"Erro ao cancelar reunião: {e}")
            return f"Erro ao cancelar reunião: {str(e)}"

    async def _tool_reagenda_reuniao(
        self,
        evento_id: str,
        nova_data_hora_inicio: str,
        nova_data_hora_fim: str
    ) -> str:
        """Tool: Reagendar reunião."""
        try:
            inicio = datetime.fromisoformat(nova_data_hora_inicio)
            fim = datetime.fromisoformat(nova_data_hora_fim)

            evento = await self.google_calendar.reagendar_reuniao(
                evento_id,
                inicio,
                fim
            )

            # Atualizar Supabase
            reuniao = await self.supabase.get_reuniao_by_google_id(evento_id)
            if reuniao:
                await self.supabase.update_reuniao(
                    reuniao['id'],
                    {
                        "data_inicio": inicio.isoformat(),
                        "data_fim": fim.isoformat(),
                        "status": "agendada"
                    }
                )

            # Atualizar tag
            lead_telefone = await self._get_telefone_from_context()
            await self.supabase.remove_tag(lead_telefone, "reuniao_cancelada")
            await self.supabase.add_tag(lead_telefone, "reuniao_reagendada")

            return f"Reunião reagendada para {inicio.strftime('%d/%m/%Y %H:%M')}"
        except Exception as e:
            logger.error(f"Erro ao reagendar reunião: {e}")
            return f"Erro ao reagendar reunião: {str(e)}"

    async def _tool_atualizar_tag(self, telefone: str, tag: str) -> str:
        """Tool: Atualizar tag do lead."""
        try:
            await self.supabase.add_tag(telefone, tag)
            return f"Tag '{tag}' adicionada ao lead {telefone}"
        except Exception as e:
            logger.error(f"Erro ao atualizar tag: {e}")
            return f"Erro ao atualizar tag: {str(e)}"

    async def _tool_buscar_conhecimento(self, pergunta: str) -> str:
        """Tool: Buscar na base de conhecimento."""
        try:
            contexto = await self.retriever.retrieve_formatted(pergunta, k=3)
            return f"Conhecimento relevante encontrado:\n\n{contexto}"
        except Exception as e:
            logger.error(f"Erro ao buscar conhecimento: {e}")
            return f"Erro ao buscar conhecimento: {str(e)}"

    async def _tool_analisar_imagem(self, url_imagem: str) -> str:
        """Tool: Analisar imagem com GPT-4o-mini."""
        try:
            # Usar GPT-4o-mini com visão
            response = await self.llm.apredict(
                f"Analise esta imagem e descreva o que vê: {url_imagem}"
            )
            return f"Análise da imagem: {response}"
        except Exception as e:
            logger.error(f"Erro ao analisar imagem: {e}")
            return f"Erro ao analisar imagem: {str(e)}"

    async def _tool_transcrever_audio(self, url_audio: str) -> str:
        """Tool: Transcrever áudio com Whisper."""
        try:
            # Baixar áudio
            audio_bytes = await self.whatsapp.download_media(url_audio)

            # Transcrever com OpenAI Whisper
            from openai import AsyncOpenAI
            client = AsyncOpenAI()

            # Salvar temporariamente
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_bytes)
                temp_path = f.name

            # Transcrever
            with open(temp_path, "rb") as audio_file:
                transcription = await client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio_file,
                    language="pt"
                )

            # Limpar arquivo temp
            Path(temp_path).unlink()

            return f"Transcrição do áudio: {transcription.text}"
        except Exception as e:
            logger.error(f"Erro ao transcrever áudio: {e}")
            return f"Erro ao transcrever áudio: {str(e)}"

    # === MÉTODOS AUXILIARES ===

    async def _get_telefone_from_context(self) -> str:
        """Obtém telefone do contexto atual."""
        # TODO: Implementar lógica para obter telefone do contexto
        # Por enquanto, retornar placeholder
        return "placeholder_telefone"

    def _create_agent(self) -> AgentExecutor:
        """Cria agent executor com prompt e tools."""

        # Template do prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.prompt_principal),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Criar agente
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt_template
        )

        # Executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10
        )

        return agent_executor

    async def process_message(
        self,
        phone: str,
        message: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Processa mensagem do lead.

        Args:
            phone: Telefone do lead
            message: Mensagem recebida
            metadata: Metadados (mídia, etc)

        Returns:
            Resposta do agente
        """
        try:
            # Salvar mensagem na memória
            await self.memory.add_message(phone, "human", message, metadata)

            # Recuperar histórico
            chat_history = await self.memory.get_history_formatted(phone, limit=20)

            # Executar agente
            result = await self.agent.ainvoke({
                "input": message,
                "chat_history": chat_history
            })

            response = result["output"]

            logger.info(f"Agente processou mensagem de {phone}")
            return response

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem."


# ==============================================================================
# EXPORTAÇÕES
# ==============================================================================

__all__ = [
    'AgenteSDR',
    'MessageFormatter'
]

"""
CORE/FOLLOWUP.PY
================
Sistema de follow-up automatizado.

Timeline:
- FUP 1: 30 minutos após última mensagem
- FUP 2: 4 horas após FUP 1
- FUP 3: 12 horas após FUP 2
- FUP 4: 24 horas após FUP 3

Horário: 07h-21h
Janela: 72 horas totais

Autor: Claude Code
Versão: 1.0
Data: Janeiro 2025
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
from loguru import logger

from core.integrations import WhatsAppClient, SupabaseClient
from core.memory import RedisMemoryManager


class FollowUpManager:
    """
    Gerencia sistema de follow-up automatizado.

    Características:
    - Timeline progressivo: 30min → 4h → 12h → 24h
    - Análise de desinteresse antes de enviar
    - Horário comercial (7h-21h)
    - Janela de 72h
    """

    # Timeline de follow-ups (em minutos)
    TIMELINE = {
        1: 30,      # 30 minutos
        2: 240,     # 4 horas
        3: 720,     # 12 horas
        4: 1440,    # 24 horas
    }

    HORARIO_INICIO = 7   # 7h
    HORARIO_FIM = 21     # 21h

    def __init__(
        self,
        whatsapp_client: WhatsAppClient,
        supabase_client: SupabaseClient,
        memory: RedisMemoryManager,
        llm,
        prompt_followup_path: str = "config/prompt-followup.md"
    ):
        """Inicializa follow-up manager."""
        self.whatsapp = whatsapp_client
        self.supabase = supabase_client
        self.memory = memory
        self.llm = llm

        # Carregar prompt de follow-up
        self.prompt_followup = Path(prompt_followup_path).read_text()

    async def verificar_e_enviar_followups(self):
        """
        Verifica todos os leads e envia follow-ups necessários.

        Chamado periodicamente (ex: a cada 5 minutos).
        """
        agora = datetime.utcnow()

        # Buscar leads elegíveis para follow-up
        leads = await self._buscar_leads_elegiveis(agora)

        logger.info(f"Follow-up: {len(leads)} leads elegíveis")

        for lead in leads:
            try:
                await self._processar_followup_lead(lead, agora)
            except Exception as e:
                logger.error(f"Erro ao processar follow-up de {lead['telefone']}: {e}")

    async def _buscar_leads_elegiveis(self, agora: datetime) -> List[Dict]:
        """
        Busca leads elegíveis para follow-up.

        Critérios:
        - fup_proximo_horario <= agora
        - tags não contém BREAK, nao_interessado, atendimento_humano, reuniao_agendada
        - fup_enviado < 4
        """
        # Query no Supabase
        result = self.supabase.client.table('leads_wpp')\
            .select('*')\
            .lte('fup_proximo_horario', agora.isoformat())\
            .lt('fup_enviado', 4)\
            .execute()

        leads = result.data

        # Filtrar por tags
        leads_elegiveis = []
        for lead in leads:
            tags = lead.get('tags', [])

            # Tags que bloqueiam follow-up
            tags_bloqueio = {'BREAK', 'nao_interessado', 'atendimento_humano', 'reuniao_agendada'}

            if not any(tag in tags_bloqueio for tag in tags):
                leads_elegiveis.append(lead)

        return leads_elegiveis

    async def _processar_followup_lead(self, lead: Dict, agora: datetime):
        """
        Processa follow-up de um lead.

        1. Verifica horário comercial
        2. Analisa histórico (desinteresse)
        3. Gera mensagem
        4. Envia
        5. Atualiza lead
        """
        telefone = lead['telefone']
        fup_numero = lead['fup_enviado'] + 1

        # 1. Verificar horário comercial
        if not self._is_horario_comercial(agora):
            logger.info(f"Fora do horário comercial para {telefone}")
            # Reagendar para próximo horário comercial
            proximo_horario = self._proximo_horario_comercial(agora)
            await self.supabase.update_lead(telefone, {
                'fup_proximo_horario': proximo_horario.isoformat()
            })
            return

        # 2. Analisar histórico (detectar desinteresse)
        desinteresse = await self._analisar_desinteresse(telefone)

        if desinteresse:
            logger.info(f"Desinteresse detectado para {telefone}, adicionando tag BREAK")
            await self.supabase.add_tag(telefone, 'BREAK')
            return

        # 3. Gerar mensagem de follow-up
        mensagem = await self._gerar_mensagem_followup(telefone, fup_numero)

        # 4. Enviar mensagem
        await self._enviar_followup(telefone, mensagem)

        # 5. Atualizar lead
        await self._atualizar_lead_pos_followup(telefone, fup_numero, agora)

        logger.info(f"Follow-up {fup_numero} enviado para {telefone}")

    def _is_horario_comercial(self, dt: datetime) -> bool:
        """Verifica se está em horário comercial (7h-21h)."""
        hora = dt.hour
        return self.HORARIO_INICIO <= hora < self.HORARIO_FIM

    def _proximo_horario_comercial(self, dt: datetime) -> datetime:
        """Calcula próximo horário comercial."""
        if dt.hour < self.HORARIO_INICIO:
            # Hoje às 7h
            return dt.replace(hour=self.HORARIO_INICIO, minute=0, second=0)
        elif dt.hour >= self.HORARIO_FIM:
            # Amanhã às 7h
            amanha = dt + timedelta(days=1)
            return amanha.replace(hour=self.HORARIO_INICIO, minute=0, second=0)
        else:
            # Já está em horário comercial
            return dt

    async def _analisar_desinteresse(self, telefone: str) -> bool:
        """
        Analisa histórico de conversa para detectar desinteresse.

        Usa LLM para identificar sinais de desinteresse.

        Returns:
            True se detectar desinteresse, False caso contrário
        """
        # Buscar histórico
        historico = await self.memory.get_history_formatted(telefone, limit=20)

        if len(historico) < 2:
            return False  # Pouco histórico, não dá para analisar

        # Formatar histórico
        historico_texto = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in historico
        ])

        # Prompt de análise
        prompt_analise = f"""
        Analise o histórico de conversa abaixo e identifique se o lead demonstra DESINTERESSE.

        Sinais de desinteresse:
        - Respostas muito curtas e secas
        - Ignorou perguntas diretas
        - Deu desculpas vagas
        - Disse explicitamente que não tem interesse
        - Padrão de engajamento decrescente

        Histórico:
        {historico_texto}

        Responda APENAS "SIM" se detectar desinteresse claro, ou "NÃO" caso contrário.
        """

        resposta = await self.llm.apredict(prompt_analise)
        desinteresse = "SIM" in resposta.upper()

        return desinteresse

    async def _gerar_mensagem_followup(self, telefone: str, fup_numero: int) -> str:
        """
        Gera mensagem de follow-up contextualizada.

        Usa o prompt de follow-up e histórico da conversa.
        """
        # Buscar histórico
        historico = await self.memory.get_history_formatted(telefone, limit=10)

        # Formatar histórico
        historico_texto = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in historico
        ])

        # Prompt de geração
        prompt = f"""
        {self.prompt_followup}

        ---

        CONTEXTO:
        - Este é o follow-up número {fup_numero}
        - Histórico recente da conversa:

        {historico_texto}

        ---

        Gere uma mensagem de follow-up adequada para o estágio {fup_numero}.
        Seja contextual, agregue valor e siga as orientações do prompt de follow-up.

        IMPORTANTE: Fragmente a mensagem em partes de 20-30 palavras.
        Separe cada fragmento com "|||".

        Mensagem:
        """

        mensagem_completa = await self.llm.apredict(prompt)

        return mensagem_completa

    async def _enviar_followup(self, telefone: str, mensagem: str):
        """
        Envia mensagem de follow-up fragmentada.
        """
        # Fragmentar por |||
        fragmentos = [f.strip() for f in mensagem.split("|||") if f.strip()]

        for i, fragmento in enumerate(fragmentos):
            if i > 0:
                await asyncio.sleep(2)  # Delay entre fragmentos

            await self.whatsapp.send_text(telefone, fragmento)

        # Salvar na memória
        await self.memory.add_message(
            telefone,
            "ai",
            mensagem,
            metadata={"type": "followup"}
        )

    async def _atualizar_lead_pos_followup(
        self,
        telefone: str,
        fup_numero: int,
        agora: datetime
    ):
        """
        Atualiza lead após envio de follow-up.

        - Incrementa fup_enviado
        - Atualiza fup_ultima_data
        - Calcula e define fup_proximo_horario (se aplicável)
        - Atualiza ultima_interacao_agente
        """
        # Calcular próximo follow-up
        if fup_numero < 4:
            proximo_fup_minutos = self.TIMELINE.get(fup_numero + 1)
            if proximo_fup_minutos:
                proximo_horario = agora + timedelta(minutes=proximo_fup_minutos)

                # Ajustar para horário comercial
                if not self._is_horario_comercial(proximo_horario):
                    proximo_horario = self._proximo_horario_comercial(proximo_horario)
            else:
                proximo_horario = None
        else:
            # Último follow-up, não agendar próximo
            proximo_horario = None

        # Atualizar no Supabase
        updates = {
            'fup_enviado': fup_numero,
            'fup_ultima_data': agora.isoformat(),
            'ultima_interacao_agente': agora.isoformat()
        }

        if proximo_horario:
            updates['fup_proximo_horario'] = proximo_horario.isoformat()
        else:
            # Se foi o último follow-up, adicionar tag BREAK
            await self.supabase.add_tag(telefone, 'BREAK')

        await self.supabase.update_lead(telefone, updates)

    async def agendar_primeiro_followup(self, telefone: str):
        """
        Agenda primeiro follow-up após interação inicial.

        Chamado quando agente envia primeira resposta ao lead.
        """
        agora = datetime.utcnow()
        primeiro_fup = agora + timedelta(minutes=self.TIMELINE[1])  # 30min

        # Ajustar para horário comercial
        if not self._is_horario_comercial(primeiro_fup):
            primeiro_fup = self._proximo_horario_comercial(primeiro_fup)

        # Atualizar lead
        await self.supabase.update_lead(telefone, {
            'fup_proximo_horario': primeiro_fup.isoformat(),
            'fup_enviado': 0
        })

        logger.info(f"Primeiro follow-up agendado para {telefone}: {primeiro_fup}")


# ==============================================================================
# SCHEDULER DE FOLLOW-UPS
# ==============================================================================

class FollowUpScheduler:
    """
    Agenda execução periódica do sistema de follow-up.

    Usa APScheduler para executar a cada 5 minutos.
    """

    def __init__(self, followup_manager: FollowUpManager):
        """Inicializa scheduler."""
        self.followup_manager = followup_manager
        self.scheduler = None

    def start(self):
        """Inicia scheduler."""
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        self.scheduler = AsyncIOScheduler()

        # Executar a cada 5 minutos
        self.scheduler.add_job(
            self.followup_manager.verificar_e_enviar_followups,
            'interval',
            minutes=5,
            id='followup_job'
        )

        self.scheduler.start()
        logger.info("Follow-up scheduler iniciado (executa a cada 5 minutos)")

    def stop(self):
        """Para scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Follow-up scheduler parado")


__all__ = ['FollowUpManager', 'FollowUpScheduler']

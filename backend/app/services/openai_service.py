"""
Serviço para integração com OpenAI ChatGPT.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from openai import AsyncOpenAI, OpenAIError

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Serviço para interagir com ChatGPT para análises financeiras.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ):
        """
        Inicializa o serviço OpenAI.

        Args:
            api_key: Chave da API OpenAI
            model: Modelo a usar (gpt-3.5-turbo ou gpt-4)
            max_tokens: Máximo de tokens por resposta
            temperature: Temperatura para geração (0-1)
        """
        if not api_key:
            raise ValueError("OPENAI_API_KEY não configurada")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def _call_chatgpt(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None
    ) -> str:
        """
        Chama a API do ChatGPT.

        Args:
            system_prompt: Instruções do sistema
            user_message: Mensagem do usuário
            temperature: Override de temperatura (opcional)

        Returns:
            Resposta do modelo

        Raises:
            OpenAIError: Se houver erro na API
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=temperature or self.temperature
            )

            return response.choices[0].message.content.strip()

        except OpenAIError as e:
            logger.error(f"Erro ao chamar OpenAI API: {e}")
            raise

    async def analyze_spending(
        self,
        summary: Dict,
        timeframe: str = "last_month"
    ) -> str:
        """
        Analisa gastos do usuário e sugere melhorias.

        Args:
            summary: Resumo financeiro com totais, categorias, etc
            timeframe: Período analisado

        Returns:
            Análise detalhada com sugestões

        Example:
            summary = {
                "total_income": 5000.00,
                "total_expense": 4200.00,
                "balance": 800.00,
                "top_categories": [
                    {"name": "Alimentação", "total": 1200.00},
                    {"name": "Transporte", "total": 800.00}
                ]
            }
        """
        system_prompt = """Você é um consultor financeiro experiente.
Analise os dados financeiros fornecidos e forneça:
1. Resumo da situação financeira
2. Identificação de padrões de gastos
3. Sugestões práticas de economia
4. Alertas sobre gastos excessivos

Seja objetivo, empático e focado em ações práticas."""

        user_message = f"""Analise minha situação financeira do período: {timeframe}

Resumo:
- Receitas: R$ {summary.get('total_income', 0):.2f}
- Despesas: R$ {summary.get('total_expense', 0):.2f}
- Saldo: R$ {summary.get('balance', 0):.2f}

Principais categorias de gastos:
"""
        for cat in summary.get('top_categories', [])[:5]:
            user_message += f"\n- {cat['name']}: R$ {cat['total']:.2f}"

        return await self._call_chatgpt(system_prompt, user_message)

    async def chat_with_context(
        self,
        message: str,
        financial_data: Dict
    ) -> str:
        """
        Chat interativo com contexto financeiro do usuário.

        Args:
            message: Pergunta/mensagem do usuário
            financial_data: Dados financeiros para contexto

        Returns:
            Resposta contextualizada

        Example:
            financial_data = {
                "current_balance": 1500.00,
                "monthly_income": 5000.00,
                "monthly_expense": 3500.00,
                "categories": {...}
            }
        """
        system_prompt = """Você é um assistente financeiro pessoal inteligente.
Use os dados financeiros do usuário para fornecer respostas personalizadas.
Seja claro, prático e mantenha um tom profissional mas amigável.
Se não tiver informação suficiente, pergunte ao usuário."""

        context_str = f"""
Contexto financeiro do usuário:
- Saldo atual: R$ {financial_data.get('current_balance', 0):.2f}
- Receita mensal média: R$ {financial_data.get('monthly_income', 0):.2f}
- Despesa mensal média: R$ {financial_data.get('monthly_expense', 0):.2f}
"""

        user_message = f"{context_str}\n\nPergunta: {message}"

        return await self._call_chatgpt(system_prompt, user_message)

    async def generate_insights(
        self,
        categories: List[Dict],
        transactions: List[Dict]
    ) -> str:
        """
        Gera insights sobre padrões de categorização.

        Args:
            categories: Lista de categorias com estatísticas
            transactions: Amostra de transações recentes

        Returns:
            Insights sobre padrões de gastos

        Example:
            categories = [
                {"name": "Alimentação", "count": 45, "total": 1200.00},
                {"name": "Transporte", "count": 20, "total": 800.00}
            ]
        """
        system_prompt = """Você é um analista financeiro especializado em padrões de consumo.
Analise as categorias e transações para identificar:
1. Padrões interessantes de gastos
2. Categorias que merecem atenção
3. Oportunidades de otimização
4. Tendências ao longo do tempo"""

        categories_str = "Categorias:\n"
        for cat in categories[:10]:
            categories_str += f"- {cat['name']}: {cat['count']} transações, R$ {cat['total']:.2f}\n"

        transactions_str = "\nTransações recentes:\n"
        for tx in transactions[:10]:
            transactions_str += f"- {tx['date']}: {tx['description']} - R$ {tx['amount']:.2f} ({tx.get('category', 'Sem categoria')})\n"

        user_message = categories_str + transactions_str

        return await self._call_chatgpt(system_prompt, user_message)

    async def create_projections(
        self,
        goals: Dict,
        current_state: Dict
    ) -> str:
        """
        Cria projeções financeiras e plano para atingir metas.

        Args:
            goals: Metas financeiras do usuário
            current_state: Estado financeiro atual

        Returns:
            Projeções e plano de ação

        Example:
            goals = {
                "savings_target": 10000.00,
                "target_date": "2024-12-31",
                "purpose": "Emergência"
            }
            current_state = {
                "current_savings": 2000.00,
                "monthly_income": 5000.00,
                "monthly_expense": 3500.00
            }
        """
        system_prompt = """Você é um planejador financeiro certificado.
Analise as metas e situação atual do usuário para criar:
1. Projeção realista de atingimento das metas
2. Plano de ação mensal detalhado
3. Ajustes necessários nos gastos
4. Marcos intermediários para acompanhamento

Seja realista e considere imprevistos."""

        user_message = f"""
Meta financeira:
- Objetivo: Poupar R$ {goals.get('savings_target', 0):.2f}
- Prazo: {goals.get('target_date', 'Não definido')}
- Propósito: {goals.get('purpose', 'Não especificado')}

Situação atual:
- Poupança atual: R$ {current_state.get('current_savings', 0):.2f}
- Receita mensal: R$ {current_state.get('monthly_income', 0):.2f}
- Despesa mensal: R$ {current_state.get('monthly_expense', 0):.2f}
- Capacidade de poupança mensal: R$ {current_state.get('monthly_income', 0) - current_state.get('monthly_expense', 0):.2f}

Crie um plano realista para atingir essa meta.
"""

        return await self._call_chatgpt(system_prompt, user_message, temperature=0.5)

    async def health_check(self) -> bool:
        """
        Verifica se a API está funcionando.

        Returns:
            True se API está acessível
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except OpenAIError as e:
            logger.error(f"Health check falhou: {e}")
            return False

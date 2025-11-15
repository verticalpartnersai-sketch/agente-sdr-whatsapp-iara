#!/usr/bin/env python3
"""
Gerador de Tokens e Senhas
===========================

Gera tokens seguros para configuração do Agente SDR WhatsApp.

Uso:
    python gerar_tokens.py

Autor: Claude Code
Data: Janeiro 2025
"""

import secrets
import string


def gerar_token(length=32):
    """Gera token alfanumérico aleatório."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def gerar_senha(length=24):
    """Gera senha forte com caracteres especiais."""
    alphabet = string.ascii_letters + string.digits + '!@#$%&*-_=+'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def main():
    """Gera todos os tokens necessários."""
    print("=" * 70)
    print("🔐 GERADOR DE TOKENS - AGENTE SDR WHATSAPP")
    print("=" * 70)
    print()

    print("📋 Tokens Gerados:")
    print("-" * 70)
    print()

    # WhatsApp Webhook Verify Token
    webhook_token = gerar_token(32)
    print("# WhatsApp Webhook Verify Token (você cria este)")
    print(f"WHATSAPP_WEBHOOK_VERIFY_TOKEN={webhook_token}")
    print()

    # Redis Password
    redis_password = gerar_senha(24)
    print("# Redis Password (senha forte)")
    print(f"REDIS_PASSWORD={redis_password}")
    print()

    # RabbitMQ Password
    rabbitmq_password = gerar_senha(24)
    print("# RabbitMQ Password (senha forte)")
    print(f"RABBITMQ_PASSWORD={rabbitmq_password}")
    print()

    print("-" * 70)
    print()
    print("⚠️  IMPORTANTE:")
    print("   1. COPIE e SALVE estes tokens com segurança")
    print("   2. Adicione no Easypanel (Environment Variables)")
    print("   3. Use o MESMO WHATSAPP_WEBHOOK_VERIFY_TOKEN no Meta Developers")
    print("   4. NUNCA compartilhe estes tokens publicamente")
    print()
    print("✅ Tokens prontos para uso!")
    print("=" * 70)


if __name__ == "__main__":
    main()

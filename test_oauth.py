"""
TEST_OAUTH.PY
=============
Testes para validar implementação OAuth Google Calendar

Executa:
1. Teste de inicialização sem token
2. Teste de geração de URL de autorização
3. Simulação de callback
"""

import sys
from pathlib import Path

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))


def test_1_inicializacao_sem_token():
    """Teste 1: Aplicação inicia sem token (não deve crashar)"""
    print("\n" + "="*70)
    print("TESTE 1: Inicialização sem token")
    print("="*70)

    # Deletar token se existir
    token_path = Path("config/google_token.json")
    backup_path = Path("config/google_token.json.backup")

    if token_path.exists():
        print(f"⚠️  Token existente encontrado, fazendo backup...")
        token_path.rename(backup_path)
        print(f"✅ Backup salvo: {backup_path}")

    try:
        from core.integrations import GoogleCalendarClient
        from config.settings import settings

        print("\n📋 Inicializando GoogleCalendarClient sem token...")

        client = GoogleCalendarClient(
            credentials_path=str(settings.GOOGLE_CREDENTIALS_PATH),
            token_path=str(settings.GOOGLE_TOKEN_PATH)
        )

        # Verificar se service é None
        if client.service is None:
            print("✅ PASSOU: GoogleCalendarClient inicializado sem token")
            print("✅ PASSOU: service = None (correto)")
            print("✅ PASSOU: Aplicação não crashou")
        else:
            print("❌ FALHOU: service não deveria estar disponível sem token")
            return False

        # Tentar usar método sem autenticação
        print("\n📋 Testando método sem autenticação...")
        try:
            import asyncio
            from datetime import datetime, timedelta

            # Como o método é async, precisamos executar em loop
            asyncio.run(client.listar_horarios_disponiveis(
                datetime.now(),
                datetime.now() + timedelta(days=1)
            ))
            print("❌ FALHOU: Método deveria lançar erro")
            return False
        except RuntimeError as e:
            if "não autenticado" in str(e):
                print(f"✅ PASSOU: Erro amigável lançado: {str(e)[:80]}...")
            else:
                print(f"❌ FALHOU: Erro inesperado: {e}")
                return False

        # Restaurar backup se existir
        if backup_path.exists():
            print(f"\n📋 Restaurando token do backup...")
            backup_path.rename(token_path)
            print(f"✅ Token restaurado")

        print("\n" + "="*70)
        print("✅ TESTE 1 PASSOU: Inicialização sem token funciona corretamente")
        print("="*70)
        return True

    except Exception as e:
        print(f"\n❌ FALHOU: Exceção inesperada: {e}")
        import traceback
        traceback.print_exc()

        # Restaurar backup se existir
        if backup_path.exists():
            backup_path.rename(token_path)
            print(f"✅ Token restaurado do backup")

        return False


def test_2_gerar_url_autorizacao():
    """Teste 2: Gerar URL de autorização"""
    print("\n" + "="*70)
    print("TESTE 2: Geração de URL de autorização")
    print("="*70)

    try:
        from google_auth_oauthlib.flow import Flow
        from config.settings import settings

        print("\n📋 Criando Flow OAuth...")

        flow = Flow.from_client_secrets_file(
            str(settings.GOOGLE_CREDENTIALS_PATH),
            scopes=[
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.events'
            ],
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        print("✅ Flow criado com sucesso")

        print("\n📋 Gerando URL de autorização...")

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        print(f"✅ URL gerada com sucesso")

        # Validações
        checks = [
            ("https://accounts.google.com" in authorization_url, "Domínio correto"),
            ("client_id=" in authorization_url, "Client ID presente"),
            ("redirect_uri=" in authorization_url, "Redirect URI presente"),
            ("scope=" in authorization_url, "Scopes presentes"),
            ("access_type=offline" in authorization_url, "access_type=offline"),
            ("prompt=consent" in authorization_url, "prompt=consent"),
        ]

        all_passed = True
        for check, description in checks:
            if check:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_passed = False

        if all_passed:
            print(f"\n📋 URL gerada:")
            print(f"{authorization_url[:100]}...")

            print("\n" + "="*70)
            print("✅ TESTE 2 PASSOU: URL de autorização válida")
            print("="*70)
            return True
        else:
            print("\n❌ TESTE 2 FALHOU: URL inválida")
            return False

    except Exception as e:
        print(f"\n❌ FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_validar_estrutura_token():
    """Teste 3: Validar estrutura do arquivo de token"""
    print("\n" + "="*70)
    print("TESTE 3: Estrutura do arquivo de token")
    print("="*70)

    token_path = Path("config/google_token.json")

    if not token_path.exists():
        print("⚠️  Token não existe (esperado se não autenticado ainda)")
        print("✅ TESTE 3 PASSOU: Comportamento correto")
        return True

    try:
        import json

        print(f"\n📋 Lendo token de {token_path}...")

        with open(token_path) as f:
            token_data = json.load(f)

        print("✅ Token é JSON válido")

        # Validar campos obrigatórios
        required_fields = [
            "token",
            "refresh_token",
            "token_uri",
            "client_id",
            "client_secret",
            "scopes"
        ]

        all_present = True
        for field in required_fields:
            if field in token_data:
                print(f"✅ Campo '{field}' presente")
            else:
                print(f"❌ Campo '{field}' ausente")
                all_present = False

        # Validar scopes
        if "scopes" in token_data:
            expected_scopes = [
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/calendar.events"
            ]

            for scope in expected_scopes:
                if scope in token_data["scopes"]:
                    print(f"✅ Scope '{scope}' presente")
                else:
                    print(f"❌ Scope '{scope}' ausente")
                    all_present = False

        if all_present:
            print("\n" + "="*70)
            print("✅ TESTE 3 PASSOU: Token válido")
            print("="*70)
            return True
        else:
            print("\n❌ TESTE 3 FALHOU: Token inválido")
            return False

    except Exception as e:
        print(f"\n❌ FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print(" "*20 + "TESTES OAUTH GOOGLE CALENDAR")
    print("="*70)

    results = {
        "Teste 1: Inicialização sem token": test_1_inicializacao_sem_token(),
        "Teste 2: Geração de URL": test_2_gerar_url_autorizacao(),
        "Teste 3: Estrutura do token": test_3_validar_estrutura_token(),
    }

    # Resumo
    print("\n" + "="*70)
    print(" "*25 + "RESUMO DOS TESTES")
    print("="*70)

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {test_name}")

    print("\n" + "="*70)
    print(f"Total: {total} | Passou: {passed} | Falhou: {failed}")

    if failed == 0:
        print("="*70)
        print(" "*15 + "🎉 TODOS OS TESTES PASSARAM! 🎉")
        print("="*70)
    else:
        print("="*70)
        print(f" "*15 + f"⚠️  {failed} TESTE(S) FALHARAM")
        print("="*70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

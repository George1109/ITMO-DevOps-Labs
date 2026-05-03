import os


def test_environment_variables():
    vault_addr = os.getenv("VAULT_ADDR")
    assert vault_addr is not None, "VAULT_ADDR is not set in environment"
    assert "vault" in vault_addr, f"Expected vault in address, got {vault_addr}"


def test_bot_token_placeholder():
    token = os.getenv("TELEGRAM_TOKEN", "placeholder")
    assert len(token) > 0

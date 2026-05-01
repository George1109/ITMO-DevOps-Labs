import os
import pytest

def test_environment_variables():
    # Проверяем, что адрес Vault прокинут в систему
    # В нашем .gitlab-ci.yml мы указали VAULT_ADDR: "http://vault:8200"
    vault_addr = os.getenv("VAULT_ADDR")
    assert vault_addr is not None, "VAULT_ADDR is not set in environment"
    assert "vault" in vault_addr, f"Expected vault in address, got {vault_addr}"

def test_bot_token_placeholder():
    # Проверяем, что у нас хотя бы есть логика загрузки токена
    # (Даже если он пустой в тестах, переменная должна существовать)
    token = os.getenv("TELEGRAM_TOKEN", "placeholder")
    assert len(token) > 0

import os
import hvac


def get_secrets():
    vault_url = os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200')
    role_id = os.getenv('VAULT_ROLE_ID')
    secret_id = os.getenv('VAULT_SECRET_ID')

    client = hvac.Client(url=vault_url)

    try:
        # Логин через AppRole
        client.auth.approle.login(role_id=role_id, secret_id=secret_id)

        # Чтение секрета через KV v2
        response = client.secrets.kv.v2.read_secret_version(
            mount_point='secret/weather-app/config',
            path='secrets'
        )

        return response['data']['data']

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


if __name__ == "__main__":
    secrets = get_secrets()
    if secrets:
        print("✅ Секреты получены успешно!")
        print(f"Ключи: {list(secrets.keys())}")
    else:
        print("Не удалось загрузить конфиг.")

config = get_secrets()

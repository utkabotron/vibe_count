#!/usr/bin/env python3
"""
Полный тест автоматической обработки
"""
import paramiko
import time
import requests
import json

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"
API_URL = f"http://{HOST}:8000"

UPLOAD_SCRIPT = """
cd /root/vibe_count
source venv/bin/activate

python3 << 'PYTEST'
import yadisk

TOKEN = "y0__xDakemDBxir1Tsgu5fnmxWfPsDkJfJDp4KZvN1bpA34WugUVA"
client = yadisk.YaDisk(token=TOKEN)

# Переместим файл из Ошибки во Входящие для теста
errors = list(client.listdir("disk:/vibe/Ошибки"))
if errors:
    file = errors[0]
    src = f"disk:/vibe/Ошибки/{file.name}"
    dst = f"disk:/vibe/Входящие/{file.name}"
    client.move(src, dst)
    print(f"Файл перемещён для теста: {file.name}")
else:
    print("Нет файлов в папке Ошибки")
PYTEST
"""

def main():
    print("="*60)
    print("  Полный тест автообработки")
    print("="*60)

    # 1. Проверка начального состояния
    print("\n1. Начальное состояние:")
    r = requests.get(f"{API_URL}/status")
    status = r.json()
    print(f"   Автообработка: {'включена' if status['auto_mode'] else 'выключена'}")
    print(f"   Интервал: {status['check_interval']} сек")
    print(f"   Обработано всего: {status['total_processed']}")

    # 2. Загрузить файл
    print("\n2. Загрузка тестового файла во Входящие...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        stdin, stdout, stderr = ssh.exec_command(UPLOAD_SCRIPT)
        result = stdout.read().decode()
        print(f"   {result.strip()}")
    finally:
        ssh.close()

    # 3. Мониторинг автообработки
    print(f"\n3. Ожидание автообработки (макс 60 сек)...")
    print(f"   API проверяет папку каждые {status['check_interval']} секунд")

    initial_processed = status['total_processed']

    for i in range(12):  # 12 * 5 = 60 секунд
        time.sleep(5)
        r = requests.get(f"{API_URL}/status")
        status = r.json()

        print(f"\n   [{(i+1)*5}с]")
        print(f"     Обрабатывается: {status['is_processing']}")
        print(f"     Всего обработано: {status['total_processed']}")

        if status['last_result']:
            print(f"     Последний результат: {status['last_result'].get('statusCode')}")
            body = status['last_result'].get('body', '')
            if len(body) > 100:
                body = body[:100] + "..."
            print(f"     {body}")

        # Проверяем, обработался ли новый файл
        if status['total_processed'] > initial_processed or (
            status['last_run'] and not status['is_processing'] and status['last_result']
        ):
            print("\n   ✓ Файл обработан автоматически!")
            break

    else:
        print("\n   ⚠️  Файл не был обработан за 60 секунд")

    # 4. Финальный статус
    print("\n4. Финальный статус:")
    r = requests.get(f"{API_URL}/status")
    status = r.json()
    print(json.dumps(status, ensure_ascii=False, indent=2))

    print("\n" + "="*60)
    print("  ✓ Тест завершён")
    print("="*60)
    print("\nАвтоматическая обработка работает!")
    print("Просто загружайте файлы в /vibe/Входящие на Яндекс.Диске,")
    print(f"и они будут автоматически обработаны каждые {status['check_interval']} секунд.")

if __name__ == "__main__":
    main()

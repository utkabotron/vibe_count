#!/usr/bin/env python3
"""
Тест исправленной валидации
"""
import paramiko
import time
import requests
import json

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"
API_URL = f"http://{HOST}:8000"

MOVE_FILE_SCRIPT = """
cd /root/vibe_count
source venv/bin/activate

python3 << 'PYTEST'
import yadisk

TOKEN = "y0__xDakemDBxir1Tsgu5fnmxWfPsDkJfJDp4KZvN1bpA34WugUVA"
client = yadisk.YaDisk(token=TOKEN)

# Переместим файл из Ошибки во Входящие
errors = list(client.listdir("disk:/vibe/Ошибки"))
if errors:
    file = errors[0]
    src = f"disk:/vibe/Ошибки/{file.name}"
    dst = f"disk:/vibe/Входящие/{file.name}"
    client.move(src, dst)
    print(f"Файл перемещён: {file.name}")
else:
    print("Нет файлов в Ошибках")
PYTEST
"""

CHECK_FOLDERS_SCRIPT = """
cd /root/vibe_count
source venv/bin/activate

python3 << 'PYTEST'
import yadisk

TOKEN = "y0__xDakemDBxir1Tsgu5fnmxWfPsDkJfJDp4KZvN1bpA34WugUVA"
client = yadisk.YaDisk(token=TOKEN)

print("\\nСтруктура папок:")

folders = ["disk:/vibe/Входящие", "disk:/vibe/Архив", "disk:/vibe/Ошибки"]
for folder in folders:
    items = list(client.listdir(folder))
    name = folder.split('/')[-1]
    print(f"  {name}: {len(items)} файлов")
    if items and len(items) <= 3:
        for item in items[:3]:
            print(f"    - {item.name[:50]}...")

# Проверка архива по датам
if client.exists("disk:/vibe/Архив"):
    years = list(client.listdir("disk:/vibe/Архив"))
    if years:
        print(f"\\n  Архив по годам:")
        for year in years:
            months = list(client.listdir(f"disk:/vibe/Архив/{year.name}"))
            for month in months:
                files = list(client.listdir(f"disk:/vibe/Архив/{year.name}/{month.name}"))
                print(f"    {year.name}/{month.name}: {len(files)} файлов")
PYTEST
"""

def main():
    print("="*60)
    print("  Тест исправленной валидации")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 1. Переместить файл из Ошибки
        print("\n1. Перемещение файла из Ошибки во Входящие...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        stdin, stdout, stderr = ssh.exec_command(MOVE_FILE_SCRIPT)
        result = stdout.read().decode()
        print(f"   {result.strip()}")

        # 2. Ждём автообработки
        print("\n2. Ожидание автообработки (40 сек)...")
        time.sleep(40)

        # 3. Проверка статуса
        print("\n3. Статус обработки:")
        r = requests.get(f"{API_URL}/status")
        status = r.json()
        print(f"   Обработано всего: {status['total_processed']}")
        if status['last_result']:
            print(f"   Последний результат:")
            print(f"     Код: {status['last_result'].get('statusCode')}")
            print(f"     Сообщение: {status['last_result'].get('body', '')[:150]}")

        # 4. Проверка структуры папок
        print("\n4. Проверка структуры папок:")
        stdin, stdout, stderr = ssh.exec_command(CHECK_FOLDERS_SCRIPT)
        result = stdout.read().decode()
        print(result)

        # 5. Проверка логов
        print("\n5. Последние логи:")
        stdin, stdout, stderr = ssh.exec_command("tail -30 /root/vibe_count/logs/api-error.log | grep -E 'обработан|перемещ|архив|предупреждени' | tail -10")
        logs = stdout.read().decode()
        if logs:
            print(logs)
        else:
            print("   (нет релевантных логов)")

        print("\n" + "="*60)
        print("  Тест завершён")
        print("="*60)

    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

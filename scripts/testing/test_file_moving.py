#!/usr/bin/env python3
"""
Тест перемещения файлов на Яндекс.Диске
"""
import paramiko
import time

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

TEST_SCRIPT = """
cd /root/vibe_count
source venv/bin/activate

python3 << 'PYTEST'
import yadisk
import sys

TOKEN = "y0__xDakemDBxir1Tsgu5fnmxWfPsDkJfJDp4KZvN1bpA34WugUVA"
client = yadisk.YaDisk(token=TOKEN)

print("="*60)
print("  Проверка структуры папок на Яндекс.Диске")
print("="*60)

# Проверим структуру папок
folders = [
    "disk:/vibe/Входящие",
    "disk:/vibe/Архив",
    "disk:/vibe/Ошибки"
]

print("\\nСтруктура папок:")
for folder in folders:
    if client.exists(folder):
        try:
            items = list(client.listdir(folder))
            print(f"  ✓ {folder}: {len(items)} файлов")
            if items and len(items) <= 5:
                for item in items[:5]:
                    print(f"    - {item.name}")
        except Exception as e:
            print(f"  ⚠️  {folder}: ошибка чтения - {e}")
    else:
        print(f"  ❌ {folder}: не существует")

# Проверим подпапки в Архиве
print("\\nПодпапки в Архиве:")
try:
    if client.exists("disk:/vibe/Архив"):
        years = list(client.listdir("disk:/vibe/Архив"))
        if years:
            for year in years:
                print(f"  {year.name}:")
                months = list(client.listdir(f"disk:/vibe/Архив/{year.name}"))
                for month in months:
                    files = list(client.listdir(f"disk:/vibe/Архив/{year.name}/{month.name}"))
                    print(f"    {month.name}: {len(files)} файлов")
        else:
            print("  (пусто)")
except Exception as e:
    print(f"  Ошибка: {e}")

print("\\n" + "="*60)
PYTEST
"""

def main():
    print("="*60)
    print("  Тест перемещения файлов")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # 1. Проверка структуры папок ДО обработки
        print("1. Проверка структуры папок:")
        stdin, stdout, stderr = ssh.exec_command(TEST_SCRIPT)
        output = stdout.read().decode()
        print(output)

        # 2. Запуск обработки через API
        print("\n2. Запуск обработки через API...")
        stdin, stdout, stderr = ssh.exec_command(
            "curl -X POST http://localhost:8000/process 2>/dev/null"
        )
        result = stdout.read().decode()
        print(f"   Ответ API: {result}")

        # 3. Ждём завершения обработки
        print("\n3. Ожидание завершения обработки (15 сек)...")
        time.sleep(15)

        # 4. Проверка статуса
        print("\n4. Проверка статуса обработки:")
        stdin, stdout, stderr = ssh.exec_command(
            "curl -s http://localhost:8000/status"
        )
        status = stdout.read().decode()
        print(f"   {status}")

        # 5. Проверка структуры папок ПОСЛЕ обработки
        print("\n5. Проверка структуры папок после обработки:")
        stdin, stdout, stderr = ssh.exec_command(TEST_SCRIPT)
        output = stdout.read().decode()
        print(output)

        # 6. Проверка логов
        print("\n6. Последние логи обработки:")
        stdin, stdout, stderr = ssh.exec_command(
            "tail -20 /root/vibe_count/logs/api-error.log | grep -A 5 'перемещ\\|move\\|архив\\|ошибк'"
        )
        logs = stdout.read().decode()
        if logs:
            print(logs)
        else:
            print("   (нет релевантных логов)")

        print("\n" + "="*60)
        print("  Тест завершён")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

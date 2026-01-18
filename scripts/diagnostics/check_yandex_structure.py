#!/usr/bin/env python3
"""
Check Yandex Disk folder structure
"""
import paramiko

# Server credentials
HOST = "188.225.46.190"
USERNAME = "root"
PASSWORD = "b7AAm^YH*@gUjp"

SCRIPT = """
import yadisk

YANDEX_OAUTH_TOKEN = "y0__xDakemDBxir1Tsgu5fnmxWfPsDkJfJDp4KZvN1bpA34WugUVA"
client = yadisk.YaDisk(token=YANDEX_OAUTH_TOKEN)

print("Структура /vibe:")
try:
    files = list(client.listdir("/vibe"))
    for item in files:
        file_type = "DIR" if item.type == "dir" else "FILE"
        print(f"  [{file_type}] {item.name}")
except Exception as e:
    print(f"Ошибка: {e}")

print("\\nПроверка подпапок:")
for folder in ["Входящие", "Обработанные", "Ошибки"]:
    path = f"/vibe/{folder}"
    try:
        if client.exists(path):
            print(f"  ✓ {path}")
        else:
            print(f"  ✗ {path} - не найдена")
    except Exception as e:
        print(f"  ✗ {path} - ошибка: {e}")
"""

def main():
    print("="*60)
    print("  Проверка структуры Яндекс.Диска")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        command = f"""cd /root/vibe_count && source venv/bin/activate && python3 -c '{SCRIPT}'"""
        stdin, stdout, stderr = ssh.exec_command(command)

        output = stdout.read().decode()
        errors = stderr.read().decode()

        if output:
            print(output)

        if errors and "Error" not in output:
            print("\nОшибки:")
            print(errors)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

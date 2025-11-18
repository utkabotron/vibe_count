#!/usr/bin/env python3
"""
Setup Yandex Disk folders remotely on VPS
"""
import paramiko

# Server credentials
HOST = "188.225.46.190"
USERNAME = "root"
PASSWORD = "b7AAm^YH*@gUjp"

# Python script to create folders
SCRIPT = """
import yadisk
import os

YANDEX_OAUTH_TOKEN = "y0__xDakemDBxir1Tsgu5fnmxWfPsDkJfJDp4KZvN1bpA34WugUVA"

client = yadisk.YaDisk(token=YANDEX_OAUTH_TOKEN)

print("Проверка токена...")
if not client.check_token():
    print("ОШИБКА: Токен невалидный!")
    exit(1)

print("✓ Токен валидный")

# Get disk info
disk_info = client.get_disk_info()
total_space = disk_info.total_space / (1024**3)
used_space = disk_info.used_space / (1024**3)
print(f"Диск: {used_space:.2f}/{total_space:.2f} GB")

# Create folders
folders = ["/Входящие", "/Обработанные", "/Ошибки"]

for folder in folders:
    try:
        if client.exists(folder):
            print(f"{folder} - существует ✓")
        else:
            client.mkdir(folder)
            print(f"{folder} - создана ✓")
    except Exception as e:
        print(f"{folder} - ошибка: {e}")

print("Готово!")
"""

def main():
    print("="*60)
    print("  Создание папок на Яндекс.Диске (удаленно)")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # Run script on server
        command = f"""cd /root/vibe_count && source venv/bin/activate && python3 -c '{SCRIPT}'"""

        stdin, stdout, stderr = ssh.exec_command(command)

        # Read output
        output = stdout.read().decode()
        errors = stderr.read().decode()

        if output:
            print(output)

        if errors:
            print("\nОшибки:")
            print(errors)

        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            print("\n" + "="*60)
            print("  ✓ ПАПКИ СОЗДАНЫ!")
            print("="*60)
        else:
            print(f"\n❌ Ошибка выполнения (код: {exit_status})")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

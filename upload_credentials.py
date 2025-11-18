#!/usr/bin/env python3
"""
Upload credentials to Timeweb VPS
"""
import paramiko
import os
from pathlib import Path

# Server credentials
HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"
REMOTE_DIR = "/root/vibe_count"

def upload_file(sftp, local_path, remote_path, description=""):
    """Upload file to server"""
    if description:
        print(f"  Загрузка {description}...", end=" ")

    try:
        sftp.put(str(local_path), remote_path)
        print("✓")
        return True
    except Exception as e:
        print(f"✗ ({e})")
        return False

def main():
    print("="*60)
    print("  Загрузка credentials на сервер")
    print("="*60)

    # Check local files exist
    env_file = Path(".env")
    creds_file = Path("vibecount-credentials-gsheets.json")

    if not env_file.exists():
        print(f"\n❌ Файл .env не найден!")
        print("Создайте .env файл с API ключами")
        return

    if not creds_file.exists():
        print(f"\n❌ Файл vibecount-credentials-gsheets.json не найден!")
        print("Скопируйте файл credentials из Keys/")
        return

    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # Open SFTP session
        sftp = ssh.open_sftp()

        # Upload files
        success = True
        success &= upload_file(sftp, env_file, f"{REMOTE_DIR}/.env", ".env")
        success &= upload_file(sftp, creds_file, f"{REMOTE_DIR}/vibecount-credentials-gsheets.json", "Google credentials")

        # Set permissions
        print("\n  Установка прав доступа...", end=" ")
        stdin, stdout, stderr = ssh.exec_command(f"chmod 600 {REMOTE_DIR}/.env {REMOTE_DIR}/vibecount-credentials-gsheets.json")
        stdout.channel.recv_exit_status()
        print("✓")

        if success:
            print("\n" + "="*60)
            print("  ✓ CREDENTIALS ЗАГРУЖЕНЫ!")
            print("="*60)
            print("\nПоследний шаг - настройка cron:")
            print("  1. Подключитесь к серверу: ssh root@188.225.46.190")
            print("  2. Выполните: crontab -e")
            print("  3. Добавьте строку:")
            print("     */10 * * * * /root/vibe_count/run.sh")
            print("  4. Сохраните (Ctrl+O, Enter, Ctrl+X)")
            print("\nДля тестирования:")
            print("  cd /root/vibe_count && ./run.sh")

        sftp.close()

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

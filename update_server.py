#!/usr/bin/env python3
"""
Update code on server
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Обновление кода на сервере")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # Install poppler-utils for pdf2image
        print("1. Установка poppler-utils для PDF обработки...")
        stdin, stdout, stderr = ssh.exec_command("DEBIAN_FRONTEND=noninteractive apt install -y poppler-utils")
        stdout.channel.recv_exit_status()
        print("   ✓ poppler-utils установлен")

        # Pull latest code
        print("\n2. Обновление кода из GitHub...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/vibe_count && git pull")
        output = stdout.read().decode()
        print(f"   {output.strip()}")

        print("\n" + "="*60)
        print("  ✓ КОД ОБНОВЛЕН!")
        print("="*60)
        print("\nТеперь можно протестировать обработку PDF")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

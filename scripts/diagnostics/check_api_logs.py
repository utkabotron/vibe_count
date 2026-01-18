#!/usr/bin/env python3
"""
Check API logs on server
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Проверка логов API")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)

        # Check error logs
        print("\n1. Логи ошибок (последние 50 строк):")
        stdin, stdout, stderr = ssh.exec_command("tail -50 /root/vibe_count/logs/api-error.log")
        output = stdout.read().decode()
        if output:
            print(output)
        else:
            print("   (пусто)")

        # Check output logs
        print("\n2. Логи вывода (последние 50 строк):")
        stdin, stdout, stderr = ssh.exec_command("tail -50 /root/vibe_count/logs/api.log")
        output = stdout.read().decode()
        if output:
            print(output)
        else:
            print("   (пусто)")

        # Check service status
        print("\n3. Статус сервиса:")
        stdin, stdout, stderr = ssh.exec_command("systemctl status vibe-count-api --no-pager")
        output = stdout.read().decode()
        print(output)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

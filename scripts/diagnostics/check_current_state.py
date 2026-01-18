#!/usr/bin/env python3
"""
Check current processing state
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)

        # Check API status
        print("="*60)
        print("СТАТУС API")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/status", timeout=15)
        output = stdout.read().decode()
        print(output)

        # Check latest error logs (last 15 lines)
        print("\n" + "="*60)
        print("ПОСЛЕДНИЕ ЛОГИ ОШИБОК (15 строк)")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command("tail -15 /root/vibe_count/logs/api-error.log", timeout=15)
        output = stdout.read().decode()
        print(output)

        # Check service status
        print("\n" + "="*60)
        print("СТАТУС SYSTEMD СЕРВИСА")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command("systemctl status vibe-count-api --no-pager | head -20", timeout=15)
        output = stdout.read().decode()
        print(output)

        # List files in Incoming folder
        print("\n" + "="*60)
        print("ФАЙЛЫ ВО ВХОДЯЩИХ")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command(
            "curl -s 'https://cloud-api.yandex.net/v1/disk/resources?path=disk:/vibe/Входящие' -H 'Authorization: OAuth y0_AgAAAAB4yvn3AAzVpgAAAAEbGzouAADgaKgLvhXVxEMWPzYd86q2Wr4lfw' | python3 -c \"import sys, json; data = json.load(sys.stdin); items = data.get('_embedded', {}).get('items', []); print(f'Всего файлов: {len(items)}'); [print(f'  - {item['name']}') for item in items[:5]]\"",
            timeout=30
        )
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            print(output)
        if error:
            print("ОШИБКА:", error)

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

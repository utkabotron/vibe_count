#!/usr/bin/env python3
"""
Check logs for duplicate processing
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

        # Check logs for the processed file
        print("="*60)
        print("ЛОГИ ОБРАБОТКИ ПОСЛЕДНЕГО ФАЙЛА")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command(
            "grep -A 10 '999 72 73 Норебо_3500' /root/vibe_count/logs/api-error.log | tail -50",
            timeout=15
        )
        output = stdout.read().decode()
        print(output)

        # Check how many times the file was processed
        print("\n" + "="*60)
        print("СКОЛЬКО РАЗ ФАЙЛ ОБРАБАТЫВАЛСЯ")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command(
            "grep 'Обработка файла: 999 72 73 Норебо_3500' /root/vibe_count/logs/api-error.log | wc -l",
            timeout=15
        )
        count = stdout.read().decode().strip()
        print(f"Количество обработок: {count}")

        # Check for "Данные записаны в Google Sheets"
        print("\n" + "="*60)
        print("СКОЛЬКО РАЗ ЗАПИСЫВАЛОСЬ В SHEETS")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command(
            "grep 'Данные записаны в Google Sheets' /root/vibe_count/logs/api-error.log | tail -5",
            timeout=15
        )
        output = stdout.read().decode()
        print(output)

        # Check systemd unit file for workers
        print("\n" + "="*60)
        print("КОЛИЧЕСТВО ВОРКЕРОВ В SYSTEMD")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command(
            "grep 'ExecStart' /etc/systemd/system/vibe-count-api.service",
            timeout=15
        )
        output = stdout.read().decode()
        print(output)

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

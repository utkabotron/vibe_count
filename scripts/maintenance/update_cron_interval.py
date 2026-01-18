#!/usr/bin/env python3
"""
Update cron interval to 5 minutes
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Обновление интервала cron на 5 минут")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # Remove old cron
        print("1. Удаление старого cron...")
        stdin, stdout, stderr = ssh.exec_command("crontab -r 2>/dev/null || true")
        stdout.channel.recv_exit_status()
        print("   ✓ Старый cron удален")

        # Add new cron with 5 minute interval
        print("\n2. Добавление нового cron (каждые 5 минут)...")
        new_cron = "*/5 * * * * /root/vibe_count/run.sh"
        stdin, stdout, stderr = ssh.exec_command(f"echo '{new_cron}' | crontab -")
        stdout.channel.recv_exit_status()
        print("   ✓ Cron обновлен")

        # Verify
        print("\n3. Проверка:")
        stdin, stdout, stderr = ssh.exec_command("crontab -l")
        result = stdout.read().decode()
        print(f"   {result.strip()}")

        print("\n" + "="*60)
        print("  ✓ CRON ОБНОВЛЕН!")
        print("="*60)
        print("\nСистема теперь запускается каждые 5 минут")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

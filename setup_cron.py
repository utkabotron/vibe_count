#!/usr/bin/env python3
"""
Setup cron job on Timeweb VPS
"""
import paramiko
import sys

# Server credentials
HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Настройка cron на сервере")
    print("="*60)

    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # Check current crontab
        print("Проверка текущего crontab...")
        stdin, stdout, stderr = ssh.exec_command("crontab -l 2>/dev/null || echo 'No crontab'")
        current_cron = stdout.read().decode().strip()
        print(f"Текущий crontab:\n{current_cron}\n")

        # Add cron job if not exists
        cron_line = "*/10 * * * * /root/vibe_count/run.sh"

        if cron_line in current_cron:
            print("✓ Cron задача уже настроена!")
        else:
            print("Добавление cron задачи...")

            # Add new cron job
            if current_cron == "No crontab":
                new_cron = cron_line
            else:
                new_cron = current_cron + "\n" + cron_line

            # Write new crontab
            stdin, stdout, stderr = ssh.exec_command(f"echo '{new_cron}' | crontab -")
            stdout.channel.recv_exit_status()

            print("✓ Cron задача добавлена!")

        # Verify
        print("\nПроверка установки:")
        stdin, stdout, stderr = ssh.exec_command("crontab -l")
        final_cron = stdout.read().decode()
        print(final_cron)

        print("\n" + "="*60)
        print("  ✓ CRON НАСТРОЕН!")
        print("="*60)
        print("\nСистема будет запускаться каждые 10 минут")
        print("\nПроверка логов:")
        print("  ssh root@188.225.46.190 'tail -f /root/vibe_count/logs/cron.log'")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

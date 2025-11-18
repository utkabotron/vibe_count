#!/usr/bin/env python3
"""
Check current logs
"""
import paramiko
import time

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)

        print("Ожидание 5 секунд для завершения обработки...")
        time.sleep(5)

        print("\n" + "="*60)
        print("  Полный лог")
        print("="*60 + "\n")

        stdin, stdout, stderr = ssh.exec_command("cat /root/vibe_count/logs/cron.log")
        log = stdout.read().decode()

        print(log)

        print("\n" + "="*60)
        print("  Анализ")
        print("="*60 + "\n")

        if "Нет файлов для обработки" in log:
            print("✓ Система работает! Папка /vibe/Входящие пуста")
            print("\nЗагрузите тестовый счет для обработки")
        elif "успешно обработан" in log or "обработан успешно" in log:
            print("✅ Файл обработан успешно!")
        elif "ERROR" in log:
            print("⚠️  Обнаружена ошибка:")
            # Find last error
            lines = log.split('\n')
            for line in lines:
                if "ERROR" in line:
                    print(f"   {line}")
        else:
            print("Система работает, проверьте лог выше")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

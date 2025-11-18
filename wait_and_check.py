#!/usr/bin/env python3
"""
Wait and check full processing
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

        print("Ожидание 30 секунд для полной обработки через OpenAI...")
        time.sleep(30)

        print("\n" + "="*60)
        print("  Полный лог обработки")
        print("="*60 + "\n")

        stdin, stdout, stderr = ssh.exec_command("cat /root/vibe_count/logs/cron.log")
        log = stdout.read().decode()

        print(log)

        print("\n" + "="*60)
        print("  Результат")
        print("="*60 + "\n")

        if "успешно обработан" in log or "Данные записаны" in log:
            print("✅ ФАЙЛ УСПЕШНО ОБРАБОТАН!")
            print("\nПроверьте Google Sheets:")
            print("https://docs.google.com/spreadsheets/d/1YrGvOG3jTjD-4bD5aqkKlUy_Ami0X_I4qzqtPQAOQHo/edit")
        elif "ERROR" in log:
            print("⚠️  Ошибка при обработке")
            lines = log.split('\n')
            for line in lines:
                if "ERROR" in line:
                    print(f"  {line}")
        else:
            print("Обработка возможно все еще идет...")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

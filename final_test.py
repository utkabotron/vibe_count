#!/usr/bin/env python3
"""
Final test of the deployment
"""
import paramiko
import time

# Server credentials
HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Финальный тест системы")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # Clear old logs
        print("Очистка старых логов...")
        stdin, stdout, stderr = ssh.exec_command("rm -f /root/vibe_count/logs/cron.log")
        stdout.channel.recv_exit_status()

        # Run test
        print("\n" + "="*60)
        print("  Тестовый запуск")
        print("="*60)
        print("\nЗапуск обработчика...\n")

        stdin, stdout, stderr = ssh.exec_command("cd /root/vibe_count && ./run.sh")

        # Wait for execution
        time.sleep(3)

        # Check log
        print("\n" + "="*60)
        print("  Результат")
        print("="*60 + "\n")

        stdin, stdout, stderr = ssh.exec_command("cat /root/vibe_count/logs/cron.log")
        log = stdout.read().decode()

        if log:
            print(log)
        else:
            print("(лог пуст)")

        # Analyze result
        print("\n" + "="*60)
        print("  Анализ")
        print("="*60)

        if "ERROR" in log:
            print("\n⚠️  Обнаружены ошибки в логе")
            if "Resource not found" in log or "PathNotFoundError" in log:
                print("   Проблема: Папки на Яндекс.Диске не найдены")
            elif "Forbidden" in log:
                print("   Проблема: Недостаточно прав доступа к Яндекс.Диску")
            else:
                print("   Проверьте лог выше для деталей")
        elif "Нет файлов для обработки" in log or "No files to process" in log:
            print("\n✓ Система работает корректно!")
            print("   В папке /vibe/Входящие пока нет файлов для обработки")
            print("\n   Следующие шаги:")
            print("   1. Загрузите тестовый счет в /vibe/Входящие")
            print("   2. Подождите до 10 минут (cron запускается каждые 10 минут)")
            print("   3. Проверьте Google Sheets")
        elif "успешно обработан" in log or "successfully processed" in log:
            print("\n✅ ОТЛИЧНО! Файл обработан успешно!")
            print("   Проверьте Google Sheets для просмотра результатов")
        else:
            print("\n   Система запущена, но результат неопределенный")
            print("   Проверьте лог выше")

        print("\n" + "="*60)
        print("  Информация")
        print("="*60)
        print("\nCron задача: */10 * * * * /root/vibe_count/run.sh")
        print("Google Sheets: https://docs.google.com/spreadsheets/d/1YrGvOG3jTjD-4bD5aqkKlUy_Ami0X_I4qzqtPQAOQHo/edit")
        print("Яндекс.Диск: https://disk.yandex.com/client/disk/vibe")
        print("\nМониторинг логов:")
        print("  ssh root@188.225.46.190 'tail -f /root/vibe_count/logs/cron.log'")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

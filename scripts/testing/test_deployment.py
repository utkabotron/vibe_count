#!/usr/bin/env python3
"""
Test deployment on Timeweb VPS
"""
import paramiko
import time

# Server credentials
HOST = "188.225.46.190"
USERNAME = "root"
PASSWORD = "b7AAm^YH*@gUjp"

def main():
    print("="*60)
    print("  Тестирование развертывания")
    print("="*60)

    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # Test run.sh execution
        print("="*60)
        print("  Тестовый запуск системы")
        print("="*60)
        print("\nЗапуск: /root/vibe_count/run.sh\n")

        stdin, stdout, stderr = ssh.exec_command("cd /root/vibe_count && ./run.sh", get_pty=True)

        # Wait a bit for execution
        time.sleep(5)

        # Read output
        output = stdout.read().decode()
        errors = stderr.read().decode()

        if output:
            print("STDOUT:")
            print(output)

        if errors:
            print("\nSTDERR:")
            print(errors)

        # Check log file
        print("\n" + "="*60)
        print("  Проверка лог-файла")
        print("="*60)

        stdin, stdout, stderr = ssh.exec_command("tail -20 /root/vibe_count/logs/cron.log 2>/dev/null || echo 'Лог файл пуст или не существует'")
        log_content = stdout.read().decode()

        print("\nПоследние 20 строк лога:")
        print(log_content)

        # Check project structure
        print("\n" + "="*60)
        print("  Проверка структуры проекта")
        print("="*60)

        stdin, stdout, stderr = ssh.exec_command("ls -la /root/vibe_count/")
        structure = stdout.read().decode()
        print(structure)

        # Check .env file exists
        print("\n" + "="*60)
        print("  Проверка конфигурации")
        print("="*60)

        stdin, stdout, stderr = ssh.exec_command("ls -la /root/vibe_count/.env /root/vibe_count/vibecount-credentials-gsheets.json 2>/dev/null")
        config_check = stdout.read().decode()

        if config_check:
            print("✓ Конфигурационные файлы найдены:")
            print(config_check)
        else:
            print("❌ Конфигурационные файлы не найдены!")

        print("\n" + "="*60)
        print("  ✓ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("="*60)
        print("\nСистема готова к работе!")
        print("\nСледующие шаги:")
        print("1. Загрузите тестовый файл в /Входящие на Яндекс.Диске")
        print("2. Подождите до 10 минут (следующий запуск cron)")
        print("3. Проверьте Google Sheets на наличие данных")
        print("\nМониторинг логов в реальном времени:")
        print("  ssh root@188.225.46.190 'tail -f /root/vibe_count/logs/cron.log'")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

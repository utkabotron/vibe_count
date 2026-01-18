#!/usr/bin/env python3
"""
Диагностика состояния сервера
"""
import paramiko
import sys

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def run_command(ssh, command, label):
    """Выполнить команду и вывести результат"""
    print(f"\n{label}")
    print("-" * 60)
    try:
        stdin, stdout, stderr = ssh.exec_command(command, timeout=10)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        exit_status = stdout.channel.recv_exit_status()

        if output:
            print(output)
        if error and exit_status != 0:
            print(f"ERROR: {error}")

        return exit_status == 0
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def diagnose_server():
    """Провести диагностику сервера"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("="*60)
        print("  ДИАГНОСТИКА СЕРВЕРА 72.56.70.180")
        print("="*60)

        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=10)
        print("✓ SSH подключение установлено")

        # Проверка базовых параметров
        run_command(ssh, "uname -a", "1. Система:")
        run_command(ssh, "python3 --version", "2. Python:")
        run_command(ssh, "df -h /", "3. Место на диске:")

        # Проверка установки проекта
        vibe_exists = run_command(ssh, "ls -la /root/vibe_count", "4. Директория проекта:")

        if vibe_exists:
            print("\n✓ Проект установлен")

            # Проверка виртуального окружения
            run_command(ssh, "ls -la /root/vibe_count/venv/bin/python3", "5. Виртуальное окружение:")

            # Проверка файлов конфигурации
            run_command(ssh, "test -f /root/vibe_count/.env && echo 'EXISTS' || echo 'NOT FOUND'", "6. Файл .env:")
            run_command(ssh, "test -f /root/vibe_count/vibecount-credentials-gsheets.json && echo 'EXISTS' || echo 'NOT FOUND'", "7. Google credentials:")

            # Проверка systemd сервиса
            run_command(ssh, "systemctl status vibe-count-api", "8. Статус API сервиса:")

            # Проверка poppler-utils
            run_command(ssh, "which pdfinfo", "9. poppler-utils (pdfinfo):")

            # Проверка логов
            run_command(ssh, "tail -5 /root/vibe_count/logs/api.log 2>/dev/null || echo 'Log file not found'", "10. Последние строки лога:")

        else:
            print("\n⚠ Проект НЕ установлен")
            print("   → Требуется полная установка (deploy_to_server.py)")

        # Проверка доступности API
        print("\n" + "="*60)
        print("  ПРОВЕРКА API")
        print("="*60)

        api_check = run_command(ssh, "curl -s http://localhost:8000/health", "11. Health endpoint:")

        if api_check:
            print("\n✓ API доступен")
        else:
            print("\n⚠ API не отвечает")

        print("\n" + "="*60)
        print("  ДИАГНОСТИКА ЗАВЕРШЕНА")
        print("="*60)

        return True

    except paramiko.SSHException as e:
        print(f"\n❌ SSH ошибка: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    success = diagnose_server()
    sys.exit(0 if success else 1)

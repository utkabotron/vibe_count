#!/usr/bin/env python3
"""
Диагностика проблем с REST API
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def run_command(ssh, cmd, description):
    """Выполнить команду и вывести результат"""
    print(f"\n{description}")
    print(f"  $ {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode()
    error = stderr.read().decode()

    if output:
        print(f"  {output}")
    if error:
        print(f"  ERROR: {error}")

    return output, error

def main():
    print("="*60)
    print("  Диагностика REST API")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # 1. Статус сервиса
        run_command(ssh, "systemctl status vibe-count-api --no-pager", "1. Статус сервиса:")

        # 2. Логи ошибок
        run_command(ssh, "tail -30 /root/vibe_count/logs/api-error.log", "2. Последние логи ошибок:")

        # 3. Логи вывода
        run_command(ssh, "tail -30 /root/vibe_count/logs/api.log", "3. Последние логи вывода:")

        # 4. Проверка порта
        run_command(ssh, "netstat -tlnp | grep 8000", "4. Проверка порта 8000:")

        # 5. Firewall
        run_command(ssh, "ufw status", "5. Статус firewall:")

        # 6. Альтернативная проверка порта
        run_command(ssh, "ss -tlnp | grep 8000", "6. Проверка порта (ss):")

        # 7. Процессы uvicorn
        run_command(ssh, "ps aux | grep uvicorn", "7. Процессы uvicorn:")

        # 8. Тест curl изнутри сервера
        output, error = run_command(ssh, "curl -s http://localhost:8000/health", "8. Тест curl изнутри сервера:")

        if not output or "healthy" not in output:
            print("\n❌ API не отвечает даже изнутри сервера!")
            print("\nПопытка перезапуска сервиса...")
            run_command(ssh, "systemctl restart vibe-count-api", "Перезапуск сервиса:")
            run_command(ssh, "sleep 3", "Ожидание...")
            run_command(ssh, "curl -s http://localhost:8000/health", "Повторный тест:")

        print("\n" + "="*60)
        print("  Диагностика завершена")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

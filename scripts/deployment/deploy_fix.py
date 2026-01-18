#!/usr/bin/env python3
"""
Деплой исправлений на сервер
"""
import paramiko
import time

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Деплой исправлений")
    print("="*60)

    for attempt in range(3):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            print(f"\nПопытка {attempt + 1}/3...")
            print("Подключение к серверу...")
            ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
            print("✓ Подключено")

            # 1. Pull latest code
            print("\n1. Обновление кода...")
            stdin, stdout, stderr = ssh.exec_command("cd /root/vibe_count && git pull")
            output = stdout.read().decode()
            print(f"   {output.strip()}")

            # 2. Restart API
            print("\n2. Перезапуск API...")
            stdin, stdout, stderr = ssh.exec_command("systemctl restart vibe-count-api")
            stdout.channel.recv_exit_status()
            print("   ✓ Перезапущен")

            # 3. Wait and check
            print("\n3. Ожидание запуска (5 сек)...")
            time.sleep(5)

            stdin, stdout, stderr = ssh.exec_command("systemctl is-active vibe-count-api")
            status = stdout.read().decode().strip()
            print(f"   Статус: {status}")

            # 4. Test API
            print("\n4. Проверка API...")
            stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/health")
            result = stdout.read().decode()

            if result and "healthy" in result:
                print(f"   ✓ API работает: {result}")

                print("\n" + "="*60)
                print("  ✓ Деплой успешен!")
                print("="*60)
                return True
            else:
                print("   ⚠️  API не отвечает")
                # Проверка логов
                stdin, stdout, stderr = ssh.exec_command("tail -20 /root/vibe_count/logs/api-error.log")
                logs = stdout.read().decode()
                if logs:
                    print("\nПоследние логи:")
                    print(logs)

        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            if attempt < 2:
                print(f"   Повтор через 10 сек...")
                time.sleep(10)
        finally:
            ssh.close()

    print("\n" + "="*60)
    print("  ❌ Не удалось подключиться к серверу")
    print("="*60)
    return False

if __name__ == "__main__":
    main()

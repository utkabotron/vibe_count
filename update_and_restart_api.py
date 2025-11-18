#!/usr/bin/env python3
"""
Update code and restart API service
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Обновление и перезапуск API")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # 1. Pull latest code
        print("1. Обновление кода...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/vibe_count && git pull")
        output = stdout.read().decode()
        print(f"   {output.strip()}")

        # 2. Restart service
        print("\n2. Перезапуск сервиса...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart vibe-count-api")
        stdout.channel.recv_exit_status()
        print("   ✓ Сервис перезапущен")

        # 3. Wait and check status
        print("\n3. Ожидание запуска (3 сек)...")
        stdin, stdout, stderr = ssh.exec_command("sleep 3 && systemctl is-active vibe-count-api")
        status = stdout.read().decode().strip()
        print(f"   Статус: {status}")

        # 4. Test API
        print("\n4. Тестирование API...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/health")
        result = stdout.read().decode()

        if result and "healthy" in result:
            print(f"   ✓ API работает: {result}")

            # Test other endpoints
            print("\n5. Тестирование других эндпоинтов...")

            stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/")
            result = stdout.read().decode()
            print(f"   Root: {result[:100]}...")

            stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/status")
            result = stdout.read().decode()
            print(f"   Status: {result}")

            print("\n" + "="*60)
            print("  ✓ API УСПЕШНО ЗАПУЩЕН!")
            print("="*60)
            print(f"\nAPI доступен: http://{HOST}:8000")
            print("Документация: http://{HOST}:8000/docs")
            print("\nПопробуйте:")
            print(f"  curl http://{HOST}:8000/health")
            print(f"  curl -X POST http://{HOST}:8000/process")

        else:
            print("   ❌ API не отвечает!")
            print("\nПроверка логов ошибок:")
            stdin, stdout, stderr = ssh.exec_command("tail -20 /root/vibe_count/logs/api-error.log")
            logs = stdout.read().decode()
            print(logs)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

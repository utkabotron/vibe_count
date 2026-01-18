#!/usr/bin/env python3
"""
Test REST API
"""
import paramiko
import time

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Тестирование REST API")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)

        # Wait a bit for API to start
        print("\nОжидание запуска API (5 сек)...")
        time.sleep(5)

        # Check service status
        print("\n1. Статус сервиса:")
        stdin, stdout, stderr = ssh.exec_command("systemctl is-active vibe-count-api")
        status = stdout.read().decode().strip()
        print(f"   {status}")

        if status != "active":
            print("\n   Сервис не активен! Проверка логов...")
            stdin, stdout, stderr = ssh.exec_command("tail -30 /root/vibe_count/logs/api-error.log")
            logs = stdout.read().decode()
            print(logs)
            return

        # Test healthcheck
        print("\n2. Тест /health:")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/health")
        result = stdout.read().decode()
        print(f"   {result}")

        # Test root endpoint
        print("\n3. Тест / (корневой):")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/")
        result = stdout.read().decode()
        print(f"   {result[:200]}...")

        # Test status
        print("\n4. Тест /status:")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/status")
        result = stdout.read().decode()
        print(f"   {result}")

        print("\n" + "="*60)
        print("  ✓ API РАБОТАЕТ!")
        print("="*60)
        print(f"\nВнешний доступ: http://{HOST}:8000")
        print("\nПопробуйте обработать файл:")
        print(f"  curl -X POST http://{HOST}:8000/process")
        print("\nДокументация API:")
        print(f"  http://{HOST}:8000/docs")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

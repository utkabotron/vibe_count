#!/usr/bin/env python3
"""
Setup REST API on server
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Настройка REST API")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # 1. Stop and remove cron
        print("1. Остановка cron...")
        stdin, stdout, stderr = ssh.exec_command("crontab -r 2>/dev/null || true")
        stdout.channel.recv_exit_status()
        print("   ✓ Cron удален")

        # 2. Pull latest code
        print("\n2. Обновление кода...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/vibe_count && git pull")
        output = stdout.read().decode()
        print(f"   {output.strip()}")

        # 3. Install FastAPI dependencies
        print("\n3. Установка зависимостей API...")
        stdin, stdout, stderr = ssh.exec_command(
            "cd /root/vibe_count && source venv/bin/activate && pip install fastapi 'uvicorn[standard]'"
        )
        stdout.channel.recv_exit_status()
        print("   ✓ FastAPI и uvicorn установлены")

        # 4. Create systemd service file
        print("\n4. Создание systemd сервиса...")

        service_content = """[Unit]
Description=Vibe Count Invoice Processing API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/vibe_count
Environment="PATH=/root/vibe_count/venv/bin"
ExecStart=/root/vibe_count/venv/bin/uvicorn src.api:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

StandardOutput=append:/root/vibe_count/logs/api.log
StandardError=append:/root/vibe_count/logs/api-error.log

[Install]
WantedBy=multi-user.target
"""

        stdin, stdout, stderr = ssh.exec_command(f"cat > /etc/systemd/system/vibe-count-api.service << 'EOF'\n{service_content}\nEOF")
        stdout.channel.recv_exit_status()
        print("   ✓ Сервис создан")

        # 5. Reload systemd and enable service
        print("\n5. Активация сервиса...")
        stdin, stdout, stderr = ssh.exec_command("systemctl daemon-reload")
        stdout.channel.recv_exit_status()

        stdin, stdout, stderr = ssh.exec_command("systemctl enable vibe-count-api")
        stdout.channel.recv_exit_status()

        stdin, stdout, stderr = ssh.exec_command("systemctl start vibe-count-api")
        stdout.channel.recv_exit_status()
        print("   ✓ Сервис запущен")

        # 6. Check status
        print("\n6. Проверка статуса...")
        stdin, stdout, stderr = ssh.exec_command("systemctl status vibe-count-api --no-pager")
        output = stdout.read().decode()

        if "active (running)" in output:
            print("   ✓ API успешно запущен!")
        else:
            print("   ⚠️  Проблема с запуском, проверьте логи")
            print(output)

        # 7. Test API
        print("\n7. Тестирование API...")
        stdin, stdout, stderr = ssh.exec_command("sleep 2 && curl -s http://localhost:8000/health")
        result = stdout.read().decode()
        if result:
            print(f"   ✓ API отвечает: {result}")
        else:
            print("   ⚠️  API не отвечает")

        print("\n" + "="*60)
        print("  ✓ REST API НАСТРОЕН!")
        print("="*60)
        print(f"\nAPI доступен по адресу: http://{HOST}:8000")
        print("\nДоступные эндпоинты:")
        print("  GET  /              - Информация об API")
        print("  GET  /health        - Healthcheck")
        print("  GET  /status        - Статус обработки")
        print("  POST /process       - Запустить обработку (async)")
        print("  POST /process-sync  - Запустить обработку (sync)")
        print("\nУправление сервисом:")
        print("  systemctl status vibe-count-api")
        print("  systemctl restart vibe-count-api")
        print("  systemctl stop vibe-count-api")
        print("\nЛоги:")
        print("  tail -f /root/vibe_count/logs/api.log")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

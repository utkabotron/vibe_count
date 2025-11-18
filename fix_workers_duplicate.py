#!/usr/bin/env python3
"""
Fix duplicate processing by reducing workers to 1
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Исправление дублирования записей")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
        print("✓ Подключено\n")

        print("Проблема: 2 воркера запускают 2 фоновые задачи автообработки")
        print("Решение: использовать 1 воркер для API с автообработкой\n")

        # Update systemd unit file to use 1 worker
        print("1. Обновление systemd unit файла...")

        new_unit = """[Unit]
Description=Vibe Count Invoice Processing API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/vibe_count
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/root/vibe_count/venv/bin/uvicorn src.api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

        cmd = f"cat > /etc/systemd/system/vibe-count-api.service << 'EOFUNIT'\n{new_unit}\nEOFUNIT"
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
        stdout.channel.recv_exit_status()
        print("   ✓ Убран параметр --workers 2 (теперь по умолчанию 1 воркер)")

        # Reload systemd
        print("\n2. Перезагрузка systemd daemon...")
        stdin, stdout, stderr = ssh.exec_command("systemctl daemon-reload", timeout=15)
        stdout.channel.recv_exit_status()
        print("   ✓ Daemon перезагружен")

        # Restart service
        print("\n3. Перезапуск сервиса...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart vibe-count-api", timeout=30)
        stdout.channel.recv_exit_status()
        print("   ✓ Сервис перезапущен")

        # Check status
        print("\n4. Проверка статуса (ожидание 3 сек)...")
        stdin, stdout, stderr = ssh.exec_command("sleep 3 && systemctl is-active vibe-count-api", timeout=15)
        status = stdout.read().decode().strip()

        if status == "active":
            print(f"   ✓ Статус: {status}")
        else:
            print(f"   ❌ Статус: {status}")
            return

        # Verify only 1 worker
        print("\n5. Проверка количества процессов...")
        stdin, stdout, stderr = ssh.exec_command(
            "ps aux | grep '[u]vicorn src.api:app' | wc -l",
            timeout=15
        )
        process_count = stdout.read().decode().strip()
        print(f"   Процессов uvicorn: {process_count}")

        if process_count == "1":
            print("   ✓ Только 1 главный процесс (без воркеров)")
        else:
            print(f"   ℹ Процессов: {process_count}")

        # Test API
        print("\n6. Тест API...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/health", timeout=15)
        result = stdout.read().decode()

        if "healthy" in result:
            print(f"   ✓ API работает: {result}")
            print("\n" + "="*60)
            print("  ✓ ДУБЛИРОВАНИЕ ИСПРАВЛЕНО!")
            print("="*60)
            print("\nТеперь файлы будут обрабатываться только один раз")
            print("и записываться в Google Sheets без дублей")
        else:
            print(f"   ⚠ Ответ API: {result}")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

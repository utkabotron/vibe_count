#!/usr/bin/env python3
"""
Fix systemd service PATH for poppler
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Исправление PATH в systemd сервисе")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
        print("✓ Подключено\n")

        # Check current unit file
        print("1. Проверка текущего unit файла...")
        stdin, stdout, stderr = ssh.exec_command("cat /etc/systemd/system/vibe-count-api.service", timeout=10)
        unit_content = stdout.read().decode()
        print(unit_content)

        # Check if Environment PATH is already set
        if "Environment=" in unit_content and "/usr/bin" in unit_content:
            print("\n   ✓ PATH уже настроен")
        else:
            print("\n2. Добавление Environment PATH...")

            # Create new unit file with PATH
            new_unit = """[Unit]
Description=Vibe Count Invoice Processing API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/vibe_count
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/root/vibe_count/venv/bin/uvicorn src.api:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

            # Write new unit file
            cmd = f"cat > /etc/systemd/system/vibe-count-api.service << 'EOFUNIT'\n{new_unit}\nEOFUNIT"
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
            stdout.channel.recv_exit_status()
            print("   ✓ Unit файл обновлен")

            # Reload systemd
            print("\n3. Перезагрузка systemd daemon...")
            stdin, stdout, stderr = ssh.exec_command("systemctl daemon-reload", timeout=15)
            stdout.channel.recv_exit_status()
            print("   ✓ Daemon перезагружен")

        # Restart service
        print("\n4. Перезапуск сервиса...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart vibe-count-api", timeout=30)
        stdout.channel.recv_exit_status()
        print("   ✓ Сервис перезапущен")

        # Check status
        print("\n5. Проверка статуса (ожидание 3 сек)...")
        stdin, stdout, stderr = ssh.exec_command("sleep 3 && systemctl is-active vibe-count-api", timeout=15)
        status = stdout.read().decode().strip()

        if status == "active":
            print(f"   ✓ Статус: {status}")
        else:
            print(f"   ❌ Статус: {status}")
            return

        # Test API
        print("\n6. Тест API...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/health", timeout=15)
        result = stdout.read().decode()

        if "healthy" in result:
            print(f"   ✓ API работает: {result}")
            print("\n" + "="*60)
            print("  ✓ SYSTEMD СЕРВИС НАСТРОЕН!")
            print("="*60)
            print("\nTеперь API имеет доступ к /usr/bin/pdfinfo")
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

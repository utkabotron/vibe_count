#!/usr/bin/env python3
"""
Script to deploy vibe_count to Timeweb VPS
"""
import paramiko
import time
import sys

# Server credentials
HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def run_command(ssh, command, description=""):
    """Execute command on remote server"""
    if description:
        print(f"\n{'='*60}")
        print(f"  {description}")
        print('='*60)

    stdin, stdout, stderr = ssh.exec_command(command)

    # Print output in real-time
    for line in stdout:
        print(line.strip())

    # Check for errors
    err = stderr.read().decode()
    if err:
        print(f"STDERR: {err}")

    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print(f"Warning: Command exited with status {exit_status}")

    time.sleep(1)
    return exit_status

def main():
    print("Подключение к серверу Timeweb VPS...")

    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to server
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print(f"✓ Подключено к {HOST}\n")

        # 1. Update system
        run_command(ssh, "apt update", "Обновление списка пакетов")

        # 2. Install required packages
        run_command(ssh,
            "DEBIAN_FRONTEND=noninteractive apt install -y python3 python3-pip python3-venv git",
            "Установка Python, Git и зависимостей")

        # 3. Clone or update repository
        print("\n" + "="*60)
        print("  Клонирование репозитория")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command("ls /root/vibe_count 2>/dev/null")
        if stdout.channel.recv_exit_status() == 0:
            print("Репозиторий существует, обновляем...")
            run_command(ssh, "cd /root/vibe_count && git pull")
        else:
            print("Клонируем репозиторий...")
            run_command(ssh, "cd /root && git clone https://github.com/utkabotron/vibe_count.git")

        # 4. Create virtual environment
        run_command(ssh, "cd /root/vibe_count && python3 -m venv venv",
            "Создание виртуального окружения")

        # 5. Install dependencies
        run_command(ssh,
            "cd /root/vibe_count && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt",
            "Установка Python зависимостей")

        # 6. Create directories
        run_command(ssh, "cd /root/vibe_count && mkdir -p logs temp",
            "Создание директорий")

        # 7. Create run.sh script
        run_command(ssh, """cat > /root/vibe_count/run.sh << 'EOF'
#!/bin/bash
cd /root/vibe_count
source venv/bin/activate
python src/main.py >> logs/cron.log 2>&1
EOF""", "Создание скрипта запуска run.sh")

        run_command(ssh, "chmod +x /root/vibe_count/run.sh")

        print("\n" + "="*60)
        print("  ✓ DEPLOYMENT УСПЕШНО ЗАВЕРШЕН!")
        print("="*60)
        print("\nСледующие шаги:")
        print("1. Загрузить .env файл на сервер")
        print("2. Загрузить vibecount-credentials-gsheets.json")
        print("3. Настроить cron задачу")
        print("\nИспользуйте следующий скрипт для завершения настройки:")
        print("  python upload_credentials.py")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

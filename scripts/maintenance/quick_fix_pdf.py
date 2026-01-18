#!/usr/bin/env python3
"""
Quick fix - install pdf2image only
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Быстрая установка pdf2image")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=10)
        print("✓ Подключено\n")

        # Install pdf2image
        print("1. Установка pdf2image в venv...")
        command = "cd /root/vibe_count && source venv/bin/activate && pip install pdf2image"
        stdin, stdout, stderr = ssh.exec_command(command, timeout=60)

        # Read output
        output = stdout.read().decode()
        error = stderr.read().decode()

        print(output)
        if error:
            print("STDERR:", error)

        # Restart API
        print("\n2. Перезапуск API...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart vibe-count-api", timeout=30)
        stdout.channel.recv_exit_status()
        print("   ✓ API перезапущен")

        # Check status
        print("\n3. Проверка статуса...")
        stdin, stdout, stderr = ssh.exec_command("sleep 2 && curl -s http://localhost:8000/health", timeout=30)
        result = stdout.read().decode()

        if "healthy" in result:
            print(f"   ✓ API работает: {result}")
            print("\n" + "="*60)
            print("  ✓ ГОТОВО!")
            print("="*60)
        else:
            print(f"   ⚠ Ответ: {result}")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

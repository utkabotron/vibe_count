#!/usr/bin/env python3
"""
Install poppler-utils system package
"""
import paramiko
import time

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Установка poppler-utils")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
        print("✓ Подключено\n")

        # Install poppler-utils
        print("1. Установка poppler-utils...")
        print("   (это может занять 1-2 минуты)")

        command = "apt-get install -y poppler-utils"
        stdin, stdout, stderr = ssh.exec_command(command, timeout=180)

        # Wait for completion
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        error = stderr.read().decode()

        if exit_status == 0:
            print("   ✓ poppler-utils установлен")
        else:
            print(f"   ⚠ Код выхода: {exit_status}")
            if error:
                print(f"   Ошибка: {error[:500]}")

        # Verify installation
        print("\n2. Проверка установки...")
        stdin, stdout, stderr = ssh.exec_command("which pdfinfo", timeout=10)
        path = stdout.read().decode().strip()

        if path:
            print(f"   ✓ pdfinfo найден: {path}")
        else:
            print("   ❌ pdfinfo не найден в PATH")
            return

        # Restart API
        print("\n3. Перезапуск API...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart vibe-count-api", timeout=30)
        stdout.channel.recv_exit_status()
        print("   ✓ API перезапущен")

        # Wait and check
        print("\n4. Ожидание запуска (3 сек)...")
        time.sleep(3)

        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/health", timeout=15)
        result = stdout.read().decode()

        if "healthy" in result:
            print(f"   ✓ API работает: {result}")
            print("\n" + "="*60)
            print("  ✓ ВСЁ ГОТОВО!")
            print("="*60)
            print("\nТеперь PDF файлы будут обрабатываться корректно")
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

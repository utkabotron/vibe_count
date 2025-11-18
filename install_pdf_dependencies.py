#!/usr/bin/env python3
"""
Install PDF processing dependencies on server
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Установка зависимостей для обработки PDF")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # 1. Install poppler-utils (system package)
        print("1. Установка poppler-utils (системный пакет)...")
        stdin, stdout, stderr = ssh.exec_command(
            "DEBIAN_FRONTEND=noninteractive apt-get update && "
            "DEBIAN_FRONTEND=noninteractive apt-get install -y poppler-utils"
        )
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("   ✓ poppler-utils установлен")
        else:
            print(f"   ⚠ Код выхода: {exit_status}")
            error = stderr.read().decode()
            if error:
                print(f"   Ошибка: {error}")

        # 2. Install pdf2image (Python package)
        print("\n2. Установка pdf2image (Python пакет)...")
        stdin, stdout, stderr = ssh.exec_command(
            "cd /root/vibe_count && source venv/bin/activate && pip install pdf2image"
        )
        output = stdout.read().decode()
        print(f"   {output.strip()}")

        # 3. Verify pdfplumber is installed
        print("\n3. Проверка pdfplumber...")
        stdin, stdout, stderr = ssh.exec_command(
            "cd /root/vibe_count && source venv/bin/activate && pip show pdfplumber"
        )
        output = stdout.read().decode()
        if "Name: pdfplumber" in output:
            print("   ✓ pdfplumber уже установлен")
        else:
            print("   Установка pdfplumber...")
            stdin, stdout, stderr = ssh.exec_command(
                "cd /root/vibe_count && source venv/bin/activate && pip install pdfplumber"
            )
            output = stdout.read().decode()
            print(f"   {output.strip()}")

        # 4. Restart API service
        print("\n4. Перезапуск API сервиса...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart vibe-count-api")
        stdout.channel.recv_exit_status()
        print("   ✓ Сервис перезапущен")

        # 5. Check status
        print("\n5. Проверка статуса (ожидание 3 сек)...")
        stdin, stdout, stderr = ssh.exec_command("sleep 3 && systemctl is-active vibe-count-api")
        status = stdout.read().decode().strip()

        if status == "active":
            print(f"   ✓ Статус: {status}")

            # Test API
            print("\n6. Тест API...")
            stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/health")
            result = stdout.read().decode()

            if result and "healthy" in result:
                print(f"   ✓ API работает: {result}")
            else:
                print(f"   ⚠ Ответ API: {result}")
        else:
            print(f"   ❌ Статус: {status}")

        print("\n" + "="*60)
        print("  ✓ ЗАВИСИМОСТИ УСТАНОВЛЕНЫ!")
        print("="*60)
        print("\nТеперь PDF файлы будут обрабатываться корректно")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

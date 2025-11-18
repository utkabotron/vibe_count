#!/usr/bin/env python3
"""
Deploy update to server with new dependencies
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    print("="*60)
    print("  Обновление на сервере (pdfplumber)")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        # Pull latest code
        print("1. Обновление кода из GitHub...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/vibe_count && git pull")
        output = stdout.read().decode()
        print(f"   {output.strip()}")

        # Update dependencies
        print("\n2. Обновление зависимостей...")
        stdin, stdout, stderr = ssh.exec_command(
            "cd /root/vibe_count && source venv/bin/activate && pip install pdfplumber && pip uninstall -y PyPDF2 pdf2image"
        )
        stdout.channel.recv_exit_status()
        print("   ✓ pdfplumber установлен, PyPDF2 и pdf2image удалены")

        # Remove poppler-utils (no longer needed)
        print("\n3. Очистка ненужных пакетов...")
        stdin, stdout, stderr = ssh.exec_command("apt remove -y poppler-utils")
        stdout.channel.recv_exit_status()
        print("   ✓ poppler-utils удален")

        print("\n" + "="*60)
        print("  ✓ ОБНОВЛЕНИЕ ЗАВЕРШЕНО!")
        print("="*60)
        print("\nТеперь PDF обрабатываются через pdfplumber")
        print("Быстрее и дешевле!")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

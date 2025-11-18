#!/usr/bin/env python3
"""
Check latest processing logs
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)

        # Check latest error logs
        print("="*60)
        print("ПОСЛЕДНИЕ ЛОГИ (последние 30 строк)")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command("tail -30 /root/vibe_count/logs/api-error.log", timeout=15)
        output = stdout.read().decode()
        print(output)

        # Check if file is still in Incoming folder
        print("\n" + "="*60)
        print("ПРОВЕРКА ФАЙЛОВ ВО ВХОДЯЩИХ")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command(
            "cd /root/vibe_count && source venv/bin/activate && python -c \"from src.file_processor import FileProcessor; fp = FileProcessor(); files = fp.list_incoming_files(); print(f'Файлов во Входящих: {len(files)}'); [print(f'  - {f}') for f in files[:5]]\"",
            timeout=30
        )
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(output)
        if error:
            print("STDERR:", error)

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

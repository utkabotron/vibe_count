#!/usr/bin/env python3
"""
Проверка проблемы с перемещением файлов
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("Подключение к серверу...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✓ Подключено\n")

        # Проверка логов ошибок
        print("Последние ошибки из логов:")
        stdin, stdout, stderr = ssh.exec_command("tail -50 /root/vibe_count/logs/api-error.log | grep -E 'ERROR|Ошибка|перемещ' | tail -20")
        output = stdout.read().decode()
        if output:
            print(output)
        else:
            print("(нет ошибок)")

        # Проверка статуса API
        print("\nСтатус API:")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/status")
        result = stdout.read().decode()
        print(result)

        # Проверка какие файлы сейчас во Входящих
        print("\n\nФайлы во Входящих:")
        stdin, stdout, stderr = ssh.exec_command("""
cd /root/vibe_count && source venv/bin/activate && python3 << 'EOF'
import yadisk
client = yadisk.YaDisk(token="y0__xDakemDBxir1Tsgu5fnmxWfPsDkJfJDp4KZvN1bpA34WugUVA")
files = list(client.listdir("disk:/vibe/Входящие"))
print(f"Всего файлов: {len(files)}")
for f in files[:5]:
    print(f"  - {f.name}")
EOF
""")
        result = stdout.read().decode()
        print(result)

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

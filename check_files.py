#!/usr/bin/env python3
"""
Check files on Yandex Disk
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

SCRIPT = """
import yadisk

YANDEX_OAUTH_TOKEN = "y0__xDakemDBxir1Tsgu5fnmxWfPsDkJfJDp4KZvN1bpA34WugUVA"
client = yadisk.YaDisk(token=YANDEX_OAUTH_TOKEN)

print("Файлы в /vibe/Входящие:")
try:
    files = list(client.listdir("/vibe/Входящие"))
    if files:
        for f in files:
            print(f"  - {f.name} ({f.type})")
    else:
        print("  (пусто)")
except Exception as e:
    print(f"Ошибка: {e}")
"""

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)

        command = f"""cd /root/vibe_count && source venv/bin/activate && python3 -c '{SCRIPT}'"""
        stdin, stdout, stderr = ssh.exec_command(command)

        output = stdout.read().decode()
        print(output)

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Проверка .env на сервере
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)

        print("Содержимое .env файла:")
        stdin, stdout, stderr = ssh.exec_command("cat /root/vibe_count/.env")
        output = stdout.read().decode()
        print(output)

    finally:
        ssh.close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Проверка папок на Яндекс.Диске
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

TEST_SCRIPT = """
cd /root/vibe_count
source venv/bin/activate

python3 << 'PYTEST'
import yadisk

TOKEN = "y0__xDakemDBxir1Tsgu5fnmxWfPsDkJfJDp4KZvN1bpA34WugUVA"
client = yadisk.YaDisk(token=TOKEN)

print("="*60)
print("  Структура папок на Яндекс.Диске")
print("="*60)

# Проверка папок
folders = {
    "Входящие": "disk:/vibe/Входящие",
    "Архив": "disk:/vibe/Архив",
    "Ошибки": "disk:/vibe/Ошибки"
}

for name, path in folders.items():
    print(f"\\n{name} ({path}):")
    if client.exists(path):
        try:
            items = list(client.listdir(path))
            print(f"  Файлов: {len(items)}")
            if items:
                for item in items[:10]:
                    size_kb = item.size / 1024 if hasattr(item, 'size') and item.size else 0
                    print(f"    - {item.name} ({size_kb:.1f} KB)")
        except Exception as e:
            print(f"  Ошибка: {e}")
    else:
        print(f"  ❌ Папка не существует")

print("\\n" + "="*60)
PYTEST
"""

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        stdin, stdout, stderr = ssh.exec_command(TEST_SCRIPT)
        output = stdout.read().decode()
        print(output)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

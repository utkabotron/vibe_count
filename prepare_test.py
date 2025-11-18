#!/usr/bin/env python3
"""
Подготовка к тесту перемещения файлов
"""
import paramiko

HOST = "72.56.70.180"
USERNAME = "root"
PASSWORD = "rS,f+8w4-Zi1M+"

PREP_SCRIPT = """
cd /root/vibe_count
source venv/bin/activate

python3 << 'PYTEST'
import yadisk

TOKEN = "y0__xDakemDBxir1Tsgu5fnmxWfPsDkJfJDp4KZvN1bpA34WugUVA"
client = yadisk.YaDisk(token=TOKEN)

print("="*60)
print("  Подготовка к тесту")
print("="*60)

# 1. Создать папку Архив если её нет
print("\\n1. Создание папки Архив...")
if not client.exists("disk:/vibe/Архив"):
    client.mkdir("disk:/vibe/Архив")
    print("   ✓ Папка Архив создана")
else:
    print("   - Папка Архив уже существует")

# 2. Переместить файл из Ошибки во Входящие
print("\\n2. Перемещение файла из Ошибки во Входящие...")
errors_files = list(client.listdir("disk:/vibe/Ошибки"))
if errors_files:
    file = errors_files[0]
    src = f"disk:/vibe/Ошибки/{file.name}"
    dst = f"disk:/vibe/Входящие/{file.name}"

    print(f"   Файл: {file.name}")
    client.move(src, dst)
    print(f"   ✓ Перемещён: Ошибки -> Входящие")
else:
    print("   - Нет файлов в папке Ошибки")

# 3. Проверка результата
print("\\n3. Проверка результата:")
incoming = list(client.listdir("disk:/vibe/Входящие"))
print(f"   Входящие: {len(incoming)} файлов")
if incoming:
    for f in incoming:
        print(f"     - {f.name}")

print("\\n" + "="*60)
print("  Готово к тесту!")
print("="*60)
PYTEST
"""

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        stdin, stdout, stderr = ssh.exec_command(PREP_SCRIPT)
        output = stdout.read().decode()
        print(output)
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

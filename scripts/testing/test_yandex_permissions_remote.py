#!/usr/bin/env python3
"""
Тест прав доступа к Яндекс.Диску через SSH на сервере
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
import sys

TOKEN = "y0__xDakemDBxir1Tsgu5fnmxWfPsDkJfJDp4KZvN1bpA34WugUVA"

print("="*60)
print("  Проверка прав доступа к Яндекс.Диску")
print("="*60)

client = yadisk.YaDisk(token=TOKEN)

try:
    # 1. Проверка подключения
    print("\\n1. Проверка подключения...")
    if client.check_token():
        print("   ✓ Токен валиден")
    else:
        print("   ❌ Токен невалиден")
        sys.exit(1)

    # 2. Проверка чтения
    print("\\n2. Проверка чтения (список файлов в /vibe/Входящие):")
    try:
        files = list(client.listdir("disk:/vibe/Входящие"))
        print(f"   ✓ Чтение работает: найдено {len(files)} файлов")
    except Exception as e:
        print(f"   ❌ Ошибка чтения: {e}")

    # 3. Проверка записи - создание тестовой папки
    print("\\n3. Проверка записи (создание папки /vibe/test_permissions):")
    try:
        test_path = "disk:/vibe/test_permissions"

        # Удалим если существует
        if client.exists(test_path):
            client.remove(test_path, permanently=True)
            print("   - Удалена старая тестовая папка")

        client.mkdir(test_path)
        print("   ✓ Запись работает: папка создана")

        # Удалим тестовую папку
        client.remove(test_path, permanently=True)
        print("   - Тестовая папка удалена")

    except yadisk.exceptions.ForbiddenError as e:
        print(f"   ❌ Нет прав на запись (403 Forbidden)")
        print(f"   Токен имеет только права на чтение!")
    except Exception as e:
        print(f"   ❌ Ошибка записи: {type(e).__name__}: {e}")

    # 4. Проверка перемещения
    print("\\n4. Проверка перемещения файлов:")
    try:
        files = list(client.listdir("disk:/vibe/Входящие"))
        if files:
            test_file = files[0]
            print(f"   Тестовый файл: {test_file.name}")

            # Создадим временную папку
            temp_path = "disk:/vibe/test_move_temp"
            if not client.exists(temp_path):
                client.mkdir(temp_path)

            src = f"disk:/vibe/Входящие/{test_file.name}"
            dst = f"{temp_path}/{test_file.name}"

            print(f"   Попытка: {src} -> {dst}")
            client.move(src, dst)
            print("   ✓ Перемещение работает!")

            # Вернём обратно
            client.move(dst, src)
            print("   - Файл возвращён обратно")

            # Удалим папку
            client.remove(temp_path, permanently=True)
        else:
            print("   ⚠️  Нет файлов для теста")

    except yadisk.exceptions.ForbiddenError as e:
        print(f"   ❌ Нет прав на перемещение (403 Forbidden)")
    except Exception as e:
        print(f"   ❌ Ошибка перемещения: {type(e).__name__}: {e}")

    print("\\n" + "="*60)
    print("  Проверка завершена")
    print("="*60)

except Exception as e:
    print(f"\\n❌ Общая ошибка: {e}")
    import traceback
    traceback.print_exc()
PYTEST
"""

def main():
    print("="*60)
    print("  Тест прав доступа на сервере")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nПодключение к {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("✓ Подключено\n")

        stdin, stdout, stderr = ssh.exec_command(TEST_SCRIPT)

        # Читаем вывод
        output = stdout.read().decode()
        error = stderr.read().decode()

        print(output)
        if error:
            print("\nОшибки:")
            print(error)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

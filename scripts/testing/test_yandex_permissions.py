#!/usr/bin/env python3
"""
Тест прав доступа к Яндекс.Диску
"""
import yadisk

TOKEN = "y0__xDakemDBxir1Tsgu5fnmxWfPsDkJfJDp4KZvN1bpA34WugUVA"

def main():
    print("="*60)
    print("  Проверка прав доступа к Яндекс.Диску")
    print("="*60)

    client = yadisk.YaDisk(token=TOKEN)

    try:
        # 1. Проверка подключения
        print("\n1. Проверка подключения...")
        if client.check_token():
            print("   ✓ Токен валиден")
        else:
            print("   ❌ Токен невалиден")
            return

        # 2. Получение информации о диске
        print("\n2. Информация о диске:")
        disk_info = client.get_disk_info()
        print(f"   Всего места: {disk_info.total_space / 1024**3:.2f} GB")
        print(f"   Использовано: {disk_info.used_space / 1024**3:.2f} GB")

        # 3. Проверка чтения - список файлов
        print("\n3. Проверка чтения (список файлов в /vibe/Входящие):")
        try:
            files = list(client.listdir("disk:/vibe/Входящие"))
            print(f"   ✓ Чтение работает: найдено {len(files)} файлов")
        except Exception as e:
            print(f"   ❌ Ошибка чтения: {e}")

        # 4. Проверка записи - создание тестовой папки
        print("\n4. Проверка записи (создание папки /vibe/test):")
        try:
            # Удалим если существует
            if client.exists("disk:/vibe/test"):
                client.remove("disk:/vibe/test")
                print("   - Удалена старая тестовая папка")

            client.mkdir("disk:/vibe/test")
            print("   ✓ Запись работает: папка создана")

            # Удалим тестовую папку
            client.remove("disk:/vibe/test")
            print("   - Тестовая папка удалена")
        except yadisk.exceptions.ForbiddenError as e:
            print(f"   ❌ Нет прав на запись: {e}")
        except Exception as e:
            print(f"   ❌ Ошибка записи: {e}")

        # 5. Проверка перемещения
        print("\n5. Проверка перемещения файлов:")
        try:
            # Попробуем переместить первый файл из Входящие во временную папку
            files = list(client.listdir("disk:/vibe/Входящие"))
            if files:
                test_file = files[0]
                print(f"   Тестовый файл: {test_file.name}")

                # Создадим временную папку если её нет
                if not client.exists("disk:/vibe/test_move"):
                    client.mkdir("disk:/vibe/test_move")

                # Попробуем переместить (на самом деле скопируем и удалим)
                src = f"disk:/vibe/Входящие/{test_file.name}"
                dst = f"disk:/vibe/test_move/{test_file.name}"

                print(f"   Попытка: {src} -> {dst}")
                client.move(src, dst)
                print("   ✓ Перемещение работает!")

                # Вернём обратно
                client.move(dst, src)
                print("   - Файл возвращён обратно")

                # Удалим тестовую папку
                client.remove("disk:/vibe/test_move")
            else:
                print("   ⚠️  Нет файлов для теста перемещения")
        except yadisk.exceptions.ForbiddenError as e:
            print(f"   ❌ Нет прав на перемещение: {e}")
        except Exception as e:
            print(f"   ❌ Ошибка перемещения: {e}")

        print("\n" + "="*60)
        print("  Проверка завершена")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

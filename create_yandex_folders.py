#!/usr/bin/env python3
"""
Create necessary folders on Yandex Disk
"""
import yadisk
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

YANDEX_OAUTH_TOKEN = os.getenv('YANDEX_OAUTH_TOKEN')

def main():
    print("="*60)
    print("  Создание папок на Яндекс.Диске")
    print("="*60)

    # Create Yandex Disk client
    client = yadisk.YaDisk(token=YANDEX_OAUTH_TOKEN)

    # Verify token
    print("\nПроверка токена...")
    try:
        if client.check_token():
            print("✓ Токен валидный")
        else:
            print("❌ Токен невалидный!")
            return
    except Exception as e:
        print(f"❌ Ошибка проверки токена: {e}")
        return

    # Get disk info
    try:
        disk_info = client.get_disk_info()
        total_space = disk_info.total_space / (1024**3)  # GB
        used_space = disk_info.used_space / (1024**3)  # GB
        print(f"\nИнформация о диске:")
        print(f"  Всего: {total_space:.2f} GB")
        print(f"  Использовано: {used_space:.2f} GB")
    except Exception as e:
        print(f"Ошибка получения информации о диске: {e}")

    # Folders to create
    folders = [
        '/Входящие',
        '/Обработанные',
        '/Ошибки'
    ]

    print("\n" + "="*60)
    print("  Создание папок")
    print("="*60 + "\n")

    for folder in folders:
        try:
            # Check if folder exists
            if client.exists(folder):
                print(f"  {folder} - уже существует ✓")
            else:
                # Create folder
                client.mkdir(folder)
                print(f"  {folder} - создана ✓")
        except Exception as e:
            print(f"  {folder} - ошибка: {e} ❌")

    print("\n" + "="*60)
    print("  ✓ ГОТОВО!")
    print("="*60)
    print("\nТеперь можете загрузить тестовый файл в /Входящие")
    print("Система автоматически обработает его в течение 10 минут")

if __name__ == "__main__":
    main()

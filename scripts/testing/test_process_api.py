#!/usr/bin/env python3
"""
Test file processing via API
"""
import requests
import time

HOST = "72.56.70.180"
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}"

def main():
    print("="*60)
    print(f"  Тестирование обработки файла через API")
    print("="*60)

    # 1. Check current status
    print("\n1. Проверка начального статуса...")
    response = requests.get(f"{BASE_URL}/status", timeout=10)
    print(f"   Статус: {response.json()}")

    # 2. Start processing
    print("\n2. Запуск обработки...")
    response = requests.post(f"{BASE_URL}/process", timeout=10)

    if response.status_code == 202:
        print(f"   ✓ Обработка запущена: {response.json()}")

        # 3. Poll status
        print("\n3. Ожидание завершения обработки...")
        max_attempts = 60  # 60 seconds max
        for i in range(max_attempts):
            time.sleep(1)
            response = requests.get(f"{BASE_URL}/status", timeout=10)
            status = response.json()

            if status["is_processing"]:
                print(f"   [{i+1}s] Обработка... (последний запуск: {status['last_run']})")
            else:
                print(f"\n   ✓ Обработка завершена!")
                print(f"\n   Результат:")
                if status["last_result"]:
                    result = status["last_result"]
                    print(f"     Статус код: {result.get('statusCode')}")
                    print(f"     Сообщение: {result.get('body')}")
                    print(f"     Всего обработано: {status['total_processed']}")
                break
        else:
            print(f"\n   ⚠️  Превышено время ожидания ({max_attempts} сек)")

    elif response.status_code == 409:
        print(f"   ⚠️  Обработка уже выполняется: {response.json()}")
    else:
        print(f"   ❌ Ошибка: {response.status_code}")
        print(f"   {response.text}")

    print("\n" + "="*60)
    print("  Тестирование завершено")
    print("="*60)

if __name__ == "__main__":
    main()

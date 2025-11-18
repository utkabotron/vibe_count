#!/usr/bin/env python3
"""
Тест автоматической обработки файлов
"""
import requests
import time
import json

HOST = "72.56.70.180"
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}"

def main():
    print("="*60)
    print("  Тест автоматической обработки")
    print("="*60)

    # Ждём запуска API
    print("\n1. Ожидание запуска API (10 сек)...")
    time.sleep(10)

    # Проверяем healthcheck
    print("\n2. Проверка healthcheck...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   ✓ API доступен: {r.json()}")
    except Exception as e:
        print(f"   ❌ API недоступен: {e}")
        return

    # Проверяем корневой эндпоинт
    print("\n3. Информация об API:")
    r = requests.get(f"{BASE_URL}/", timeout=5)
    info = r.json()
    print(f"   Версия: {info.get('version')}")
    print(f"   Автообработка: {'включена' if info.get('auto_mode') else 'выключена'}")
    print(f"   Интервал проверки: {info.get('check_interval')}")

    # Проверяем статус
    print("\n4. Текущий статус:")
    r = requests.get(f"{BASE_URL}/status", timeout=5)
    status = r.json()
    print(json.dumps(status, ensure_ascii=False, indent=2))

    # Мониторим обработку
    print("\n5. Мониторинг автообработки (60 сек)...")
    for i in range(12):  # 12 проверок по 5 секунд = 60 сек
        time.sleep(5)
        r = requests.get(f"{BASE_URL}/status", timeout=5)
        status = r.json()

        print(f"\n   [{i*5+5}с] Статус:")
        print(f"     Обрабатывается: {status['is_processing']}")
        print(f"     Всего обработано: {status['total_processed']}")
        if status['last_result']:
            print(f"     Последний результат: {status['last_result'].get('body', 'N/A')}")

        if status['total_processed'] > 0 and not status['is_processing']:
            print("\n   ✓ Файл обработан автоматически!")
            break

    print("\n" + "="*60)
    print("  Тест завершён")
    print("="*60)

if __name__ == "__main__":
    main()

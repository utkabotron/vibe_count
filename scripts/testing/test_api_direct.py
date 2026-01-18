#!/usr/bin/env python3
"""
Test API directly via HTTP requests
"""
import requests
import json

HOST = "72.56.70.180"
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}"

def test_endpoint(method, path, description):
    """Test an API endpoint"""
    url = f"{BASE_URL}{path}"
    print(f"\n{description}")
    print(f"  {method} {url}")

    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, timeout=30)

        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return response
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Не удается подключиться к API")
        return None
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return None

def main():
    print("="*60)
    print(f"  Тестирование API: {BASE_URL}")
    print("="*60)

    # Test health
    test_endpoint("GET", "/health", "1. Healthcheck")

    # Test root
    test_endpoint("GET", "/", "2. Корневой эндпоинт")

    # Test status
    test_endpoint("GET", "/status", "3. Статус системы")

    # Test process (optional)
    print("\n4. Запуск обработки файла?")
    print("   (Пропускаем для теста)")

    print("\n" + "="*60)
    print("  Тестирование завершено")
    print("="*60)
    print(f"\nAPI Документация: {BASE_URL}/docs")
    print(f"Запуск обработки: curl -X POST {BASE_URL}/process")

if __name__ == "__main__":
    main()

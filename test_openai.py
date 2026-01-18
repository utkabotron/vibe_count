#!/usr/bin/env python3
"""
Тест валидности OpenAI API ключа
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def test_openai_api():
    """Проверить валидность OpenAI API ключа"""
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("❌ OPENAI_API_KEY не найден в .env")
        return False

    try:
        client = OpenAI(api_key=api_key)

        # Минимальный тестовый запрос
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )

        print("✓ OpenAI API ключ валиден")
        print(f"  Model: {response.model}")
        print(f"  Response: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"❌ Ошибка OpenAI API: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_api()
    exit(0 if success else 1)

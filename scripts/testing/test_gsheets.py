#!/usr/bin/env python3
"""
Тест доступа к Google Sheets
"""
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def test_google_sheets():
    """Проверить доступ к Google Sheets"""
    creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'vibecount-credentials-gsheets.json')
    sheets_id = os.getenv('GOOGLE_SHEETS_ID')

    if not os.path.exists(creds_path):
        print(f"❌ Credentials файл не найден: {creds_path}")
        return False

    if not sheets_id:
        print("❌ GOOGLE_SHEETS_ID не найден в .env")
        return False

    try:
        creds = Credentials.from_service_account_file(
            creds_path,
            scopes=SCOPES
        )
        client = gspread.authorize(creds)

        # Попытка открыть таблицу
        sheet = client.open_by_key(sheets_id)

        print(f"✓ Доступ к Google Sheets успешен")
        print(f"  Таблица: {sheet.title}")
        print(f"  URL: https://docs.google.com/spreadsheets/d/{sheets_id}")

        # Попробовать получить первый worksheet
        try:
            worksheet = sheet.get_worksheet(0)
            print(f"  Worksheet: {worksheet.title}")
        except Exception as e:
            print(f"  ⚠ Не удалось получить worksheet: {e}")

        return True

    except Exception as e:
        print(f"❌ Ошибка Google Sheets: {e}")
        return False

if __name__ == "__main__":
    success = test_google_sheets()
    exit(0 if success else 1)

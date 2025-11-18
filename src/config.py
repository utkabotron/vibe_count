"""
Конфигурация приложения
Загружает переменные окружения из .env файла
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


class Config:
    """Класс конфигурации приложения"""

    # Yandex Disk
    YANDEX_CLIENT_ID = os.getenv('YANDEX_CLIENT_ID')
    YANDEX_CLIENT_SECRET = os.getenv('YANDEX_CLIENT_SECRET')
    YANDEX_OAUTH_TOKEN = os.getenv('YANDEX_OAUTH_TOKEN')

    # Yandex Disk папки
    YANDEX_INCOMING_FOLDER = os.getenv('YANDEX_INCOMING_FOLDER', '/Входящие')
    YANDEX_PROCESSED_FOLDER = os.getenv('YANDEX_PROCESSED_FOLDER', '/Обработанные')
    YANDEX_ERROR_FOLDER = os.getenv('YANDEX_ERROR_FOLDER', '/Ошибки')

    # OpenAI API
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL_VISION = 'gpt-4o'  # Модель для изображений
    OPENAI_MODEL_TEXT = 'gpt-4-turbo'  # Модель для текста

    # Google Sheets
    GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')
    GOOGLE_CREDENTIALS_PATH = BASE_DIR / os.getenv('GOOGLE_CREDENTIALS_PATH', 'vibecount-credentials-gsheets.json')

    # Настройки обработки
    MAX_RETRIES = 3  # Максимальное количество попыток при ошибках API
    TIMEOUT = 120  # Таймаут для API запросов (секунды)

    # Валидация
    VALIDATION_TOLERANCE = 0.01  # Допустимая погрешность для математических проверок
    VALID_VAT_RATES = [0, 10, 20]  # Допустимые ставки НДС

    @classmethod
    def validate(cls):
        """Проверка наличия обязательных переменных окружения"""
        required_vars = [
            'YANDEX_OAUTH_TOKEN',
            'OPENAI_API_KEY',
            'GOOGLE_SHEETS_ID',
        ]

        missing = []
        for var in required_vars:
            if not getattr(cls, var):
                missing.append(var)

        if missing:
            raise ValueError(
                f"Отсутствуют обязательные переменные окружения: {', '.join(missing)}\n"
                f"Проверьте файл .env"
            )

        # Проверка наличия файла с credentials
        if not cls.GOOGLE_CREDENTIALS_PATH.exists():
            raise FileNotFoundError(
                f"Файл с Google credentials не найден: {cls.GOOGLE_CREDENTIALS_PATH}"
            )

        return True


# Валидация конфигурации при импорте
if __name__ != '__main__':
    try:
        Config.validate()
    except (ValueError, FileNotFoundError) as e:
        print(f"ПРЕДУПРЕЖДЕНИЕ: {e}")

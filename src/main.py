"""
Главный модуль обработчика документов
Точка входа для Yandex Cloud Function
"""
import logging
from .config import Config
from .file_processor import FileProcessor
from .llm_handler import LLMHandler
from .sheets_writer import SheetsWriter
from .validator import Validator

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def handler(event=None, context=None):
    """
    Обработчик документов (для Yandex Cloud Function и REST API)

    Args:
        event: Событие триггера (опционально)
        context: Контекст выполнения (опционально)

    Returns:
        dict: Статус выполнения
    """
    logger.info("Запуск обработчика документов")

    try:
        # Инициализация компонентов
        file_processor = FileProcessor()
        llm_handler = LLMHandler()
        sheets_writer = SheetsWriter()
        validator = Validator()

        # Шаг 1: Сканирование папки Входящие
        logger.info("Сканирование папки /Входящие")
        file_info = file_processor.get_next_file()

        if not file_info:
            logger.info("Нет файлов для обработки")
            return {
                'statusCode': 200,
                'body': 'Нет файлов для обработки'
            }

        logger.info(f"Обработка файла: {file_info['name']}")

        # Шаг 2: Скачивание файла
        local_path = file_processor.download_file(file_info)

        # Шаг 3: Определение типа и обработка через LLM
        file_type = file_processor.detect_file_type(file_info['name'])
        logger.info(f"Тип файла: {file_type}")

        extracted_data = llm_handler.process_file(local_path, file_type)
        logger.info("Данные извлечены из документа")

        # Шаг 4: Валидация данных
        validation_result = validator.validate(extracted_data)

        if validation_result['errors']:
            logger.error(f"Ошибки валидации: {validation_result['errors']}")
            # Перемещаем файл в папку Ошибки
            file_processor.move_to_error(file_info, validation_result['errors'])
            return {
                'statusCode': 400,
                'body': f"Файл {file_info['name']} перемещен в /Ошибки из-за ошибок валидации"
            }

        if validation_result['warnings']:
            logger.warning(f"Предупреждения: {validation_result['warnings']}")

        # Шаг 5: Получение ссылки на файл
        file_link = file_processor.get_public_link(file_info)

        # Шаг 6: Запись в Google Sheets
        sheets_writer.write_data(extracted_data, file_link)
        logger.info("Данные записаны в Google Sheets")

        # Шаг 7: Архивация файла
        document_date = extracted_data['document_info']['invoice_date']
        file_processor.move_to_archive(file_info, document_date)
        logger.info(f"Файл успешно обработан и перемещен в архив")

        return {
            'statusCode': 200,
            'body': f"Успешно обработан файл: {file_info['name']}"
        }

    except Exception as e:
        logger.exception(f"Ошибка при обработке: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Ошибка: {str(e)}"
        }


if __name__ == '__main__':
    # Для локального тестирования
    result = handler(None, None)
    print(result)

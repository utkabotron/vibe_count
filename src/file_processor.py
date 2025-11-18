"""
Модуль работы с файлами на Яндекс.Диске
"""
import logging
import os
from datetime import datetime
from pathlib import Path
import yadisk

from config import Config

logger = logging.getLogger(__name__)


class FileProcessor:
    """Класс для работы с файлами на Яндекс.Диске"""

    def __init__(self):
        """Инициализация клиента Яндекс.Диска"""
        self.client = yadisk.YaDisk(token=Config.YANDEX_OAUTH_TOKEN)

        # Проверка подключения
        if not self.client.check_token():
            raise ValueError("Неверный токен Яндекс.Диска")

        logger.info("Подключение к Яндекс.Диску установлено")

    def get_next_file(self):
        """
        Получить первый файл из папки Входящие для обработки

        Returns:
            dict или None: Информация о файле или None если файлов нет
        """
        try:
            files = list(self.client.listdir(Config.YANDEX_INCOMING_FOLDER))

            # Фильтрация: пропускаем файлы начинающиеся с 000_
            valid_files = [
                f for f in files
                if f.type == 'file' and not f.name.startswith('000_')
            ]

            if not valid_files:
                return None

            # Возвращаем первый файл
            return {
                'name': valid_files[0].name,
                'path': valid_files[0].path,
                'size': valid_files[0].size
            }

        except Exception as e:
            logger.error(f"Ошибка при сканировании папки: {e}")
            raise

    def download_file(self, file_info):
        """
        Скачать файл во временную директорию

        Args:
            file_info (dict): Информация о файле

        Returns:
            Path: Путь к скачанному файлу
        """
        # TODO: Реализовать скачивание файла
        pass

    def detect_file_type(self, filename):
        """
        Определить тип файла по расширению

        Args:
            filename (str): Имя файла

        Returns:
            str: Тип файла ('image', 'pdf', 'docx', 'xlsx')
        """
        ext = Path(filename).suffix.lower()

        if ext in ['.jpg', '.jpeg', '.png']:
            return 'image'
        elif ext == '.pdf':
            return 'pdf'
        elif ext in ['.doc', '.docx']:
            return 'docx'
        elif ext in ['.xls', '.xlsx']:
            return 'xlsx'
        else:
            raise ValueError(f"Неподдерживаемый тип файла: {ext}")

    def get_public_link(self, file_info):
        """
        Получить публичную ссылку на файл

        Args:
            file_info (dict): Информация о файле

        Returns:
            str: Публичная ссылка
        """
        # TODO: Реализовать получение публичной ссылки
        pass

    def move_to_archive(self, file_info, document_date):
        """
        Переместить файл в архив с созданием структуры папок

        Args:
            file_info (dict): Информация о файле
            document_date (str): Дата документа в формате DD.MM.YYYY
        """
        # TODO: Реализовать перемещение в архив
        pass

    def move_to_error(self, file_info, errors):
        """
        Переместить файл в папку Ошибки

        Args:
            file_info (dict): Информация о файле
            errors (list): Список ошибок
        """
        # TODO: Реализовать перемещение в папку ошибок
        pass

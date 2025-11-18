"""
Модуль работы с файлами на Яндекс.Диске
"""
import logging
import os
from datetime import datetime
from pathlib import Path
import yadisk

from .config import Config

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
        try:
            # Создаем временную директорию если её нет
            temp_dir = Path('temp')
            temp_dir.mkdir(exist_ok=True)

            # Локальный путь для сохранения
            local_path = temp_dir / file_info['name']

            # Скачиваем файл
            self.client.download(file_info['path'], str(local_path))

            logger.info(f"Файл скачан: {file_info['name']} ({file_info['size']} байт)")
            return local_path

        except Exception as e:
            logger.error(f"Ошибка при скачивании файла: {e}")
            raise

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
        try:
            file_path = file_info['path']

            # Проверяем, есть ли уже публичная ссылка
            try:
                meta = self.client.get_meta(file_path)
                if hasattr(meta, 'public_url') and meta.public_url:
                    logger.info(f"Использована существующая публичная ссылка")
                    return meta.public_url
            except:
                pass

            # Публикуем файл и получаем ссылку
            self.client.publish(file_path)
            meta = self.client.get_meta(file_path)
            public_url = meta.public_url

            logger.info(f"Создана публичная ссылка для файла: {file_info['name']}")
            return public_url

        except Exception as e:
            logger.error(f"Ошибка при получении публичной ссылки: {e}")
            # Возвращаем альтернативную ссылку (прямой доступ через API)
            return f"https://disk.yandex.ru/client/disk{file_info['path']}"

    def move_to_archive(self, file_info, document_date):
        """
        Переместить файл в архив с созданием структуры папок

        Args:
            file_info (dict): Информация о файле
            document_date (str): Дата документа в формате DD.MM.YYYY
        """
        try:
            # Парсим дату документа
            date_obj = datetime.strptime(document_date, '%d.%m.%Y')
            year = date_obj.strftime('%Y')
            month = date_obj.strftime('%m')

            # Формируем путь к архивной папке
            archive_folder = f"{Config.YANDEX_PROCESSED_FOLDER}/{year}/{month}"

            # Создаем структуру папок если её нет
            self._ensure_folder_exists(archive_folder)

            # Целевой путь для файла
            destination = f"{archive_folder}/{file_info['name']}"

            # Перемещаем файл
            self.client.move(file_info['path'], destination, overwrite=True)

            logger.info(f"Файл перемещен в архив: {destination}")

        except Exception as e:
            logger.error(f"Ошибка при перемещении файла в архив: {e}")
            raise

    def _ensure_folder_exists(self, folder_path):
        """
        Убедиться что папка существует, создать если нет

        Args:
            folder_path (str): Путь к папке
        """
        try:
            if not self.client.exists(folder_path):
                # Создаем папки по частям (для надежности)
                parts = folder_path.split('/')
                current_path = ""

                for part in parts:
                    if not part or part == "disk:":
                        if part == "disk:":
                            current_path = "disk:"
                        continue

                    current_path = f"{current_path}/{part}" if current_path else part

                    if not self.client.exists(current_path):
                        self.client.mkdir(current_path)
                        logger.info(f"Создана папка: {current_path}")
        except Exception as e:
            logger.error(f"Ошибка при создании папки {folder_path}: {e}")
            raise

    def move_to_error(self, file_info, errors):
        """
        Переместить файл в папку Ошибки

        Args:
            file_info (dict): Информация о файле
            errors (list): Список ошибок
        """
        try:
            # Убеждаемся что папка Ошибки существует
            self._ensure_folder_exists(Config.YANDEX_ERROR_FOLDER)

            # Целевой путь для файла
            destination = f"{Config.YANDEX_ERROR_FOLDER}/{file_info['name']}"

            # Перемещаем файл
            self.client.move(file_info['path'], destination, overwrite=True)

            # Логируем ошибки
            error_msg = '; '.join(errors) if isinstance(errors, list) else str(errors)
            logger.error(
                f"Файл перемещен в папку ошибок: {destination}\n"
                f"Причина: {error_msg}"
            )

        except Exception as e:
            logger.error(f"Ошибка при перемещении файла в папку ошибок: {e}")
            raise

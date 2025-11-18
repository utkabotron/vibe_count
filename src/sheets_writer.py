"""
Модуль записи данных в Google Sheets
"""
import logging
import gspread
from google.oauth2.service_account import Credentials

from .config import Config

logger = logging.getLogger(__name__)


class SheetsWriter:
    """Класс для записи данных в Google Sheets"""

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    def __init__(self):
        """Инициализация клиента Google Sheets"""
        credentials = Credentials.from_service_account_file(
            Config.GOOGLE_CREDENTIALS_PATH,
            scopes=self.SCOPES
        )

        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open_by_key(Config.GOOGLE_SHEETS_ID).sheet1

        logger.info("Подключение к Google Sheets установлено")

    def write_data(self, data, file_link):
        """
        Записать данные в Google Sheets

        Args:
            data (dict): Извлеченные и валидированные данные
            file_link (str): Ссылка на оригинальный файл
        """
        # Уплощаем данные: каждый товар = отдельная строка
        rows = self._flatten_data(data, file_link)

        # Записываем строки в таблицу
        self.sheet.append_rows(rows, value_input_option='USER_ENTERED')

        logger.info(f"Записано {len(rows)} строк в Google Sheets")

    def _flatten_data(self, data, file_link):
        """
        Преобразовать JSON в плоские строки для таблицы

        Args:
            data (dict): Извлеченные данные
            file_link (str): Ссылка на файл

        Returns:
            list: Список строк для записи
        """
        rows = []

        # Извлекаем общие данные
        doc = data.get('document_info', {})
        recipient = data.get('recipient_details', {})
        buyer = data.get('buyer_details', {})
        logistics = data.get('logistics', {})
        totals = data.get('totals', {})

        # Для каждого товара создаем отдельную строку
        for item in data.get('items', []):
            row = [
                # Информация о документе
                doc.get('invoice_number'),
                doc.get('invoice_date'),

                # Реквизиты получателя
                recipient.get('bank_name'),
                recipient.get('inn'),
                recipient.get('kpp'),
                recipient.get('payee_name'),
                recipient.get('bic'),
                recipient.get('corr_account'),
                recipient.get('current_account'),

                # Реквизиты покупателя
                buyer.get('name'),
                buyer.get('inn'),
                buyer.get('kpp'),

                # Логистика
                logistics.get('consignee'),
                logistics.get('consignor'),

                # Товар
                item.get('name'),
                item.get('unit'),
                item.get('quantity'),
                item.get('price_unit'),
                item.get('total_sum'),
                item.get('vat_rate'),
                item.get('vat_amount'),

                # Итоги документа (дублируются для каждой строки товара)
                totals.get('total_without_vat'),
                totals.get('total_vat'),
                totals.get('total_amount'),

                # Служебные поля
                'На проверку',  # Статус
                file_link  # Ссылка на файл
            ]

            rows.append(row)

        return rows

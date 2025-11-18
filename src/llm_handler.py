"""
Модуль интеграции с OpenAI API
"""
import logging
import json
from pathlib import Path
from openai import OpenAI

from config import Config

logger = logging.getLogger(__name__)


class LLMHandler:
    """Класс для работы с OpenAI API"""

    SYSTEM_PROMPT = """Ты — эксперт по извлечению структурированных данных из бухгалтерских документов (счета на оплату, накладные, УПД). Твоя задача — проанализировать предоставленный файл и извлечь данные в строгом формате JSON.

ПРАВИЛА ИЗВЛЕЧЕНИЯ:
1. Если поле отсутствует в документе, установи значение null.
2. Даты приведи к формату "DD.MM.YYYY".
3. Числовые значения очисти от пробелов и символов валют (например, "10 000,00" -> 10000.00).
4. Для табличной части товаров/услуг найди начало таблицы и извлеки все строки.

СТРУКТУРА JSON:
{
  "document_info": {
    "invoice_number": "Номер счета",
    "invoice_date": "Дата выставления (DD.MM.YYYY)"
  },
  "recipient_details": {
    "bank_name": "Банк получателя",
    "inn": "ИНН получателя",
    "kpp": "КПП получателя",
    "payee_name": "Получатель платежа",
    "bic": "БИК",
    "corr_account": "Корреспондентский счет",
    "current_account": "Расчетный счет"
  },
  "buyer_details": {
    "name": "Покупатель",
    "inn": "ИНН покупателя",
    "kpp": "КПП покупателя"
  },
  "logistics": {
    "consignee": "Грузополучатель",
    "consignor": "Грузоотправитель"
  },
  "items": [
    {
      "name": "Наименование",
      "unit": "Ед. изм.",
      "quantity": число,
      "price_unit": число,
      "total_sum": число,
      "vat_rate": число (например, 20 для 20%),
      "vat_amount": число
    }
  ],
  "totals": {
    "total_without_vat": число,
    "total_vat": число,
    "total_amount": число
  }
}

Верни только валидный JSON без markdown-разметки."""

    def __init__(self):
        """Инициализация клиента OpenAI"""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info("OpenAI клиент инициализирован")

    def process_file(self, file_path, file_type):
        """
        Обработать файл через OpenAI API

        Args:
            file_path (Path): Путь к файлу
            file_type (str): Тип файла

        Returns:
            dict: Извлеченные данные в формате JSON
        """
        if file_type in ['image', 'pdf']:
            return self._process_image(file_path)
        elif file_type in ['docx', 'xlsx']:
            return self._process_text(file_path)
        else:
            raise ValueError(f"Неподдерживаемый тип файла: {file_type}")

    def _process_image(self, file_path):
        """
        Обработать изображение или PDF через GPT-4 Vision

        Args:
            file_path (Path): Путь к файлу

        Returns:
            dict: Извлеченные данные
        """
        # TODO: Реализовать обработку изображений
        pass

    def _process_text(self, file_path):
        """
        Обработать текстовый документ через GPT-4 Turbo

        Args:
            file_path (Path): Путь к файлу

        Returns:
            dict: Извлеченные данные
        """
        # TODO: Реализовать обработку текстовых файлов
        pass

    def _extract_text_from_docx(self, file_path):
        """Извлечь текст из DOCX файла"""
        # TODO: Реализовать извлечение текста из DOCX
        pass

    def _extract_text_from_xlsx(self, file_path):
        """Извлечь текст из XLSX файла"""
        # TODO: Реализовать извлечение текста из XLSX
        pass

"""
Модуль валидации извлеченных данных
"""
import logging
import re
from datetime import datetime
from .config import Config

logger = logging.getLogger(__name__)


class Validator:
    """Класс для валидации извлеченных данных"""

    def __init__(self):
        """Инициализация валидатора"""
        self.tolerance = Config.VALIDATION_TOLERANCE
        self.valid_vat_rates = Config.VALID_VAT_RATES

    def validate(self, data):
        """
        Валидация извлеченных данных

        Args:
            data (dict): Извлеченные данные

        Returns:
            dict: Результат валидации с ошибками и предупреждениями
        """
        errors = []
        warnings = []

        # Проверка обязательных полей
        errors.extend(self._validate_required_fields(data))

        # Проверка формата даты
        date_error = self._validate_date(data.get('document_info', {}).get('invoice_date'))
        if date_error:
            errors.append(date_error)

        # Проверка ИНН
        inn_errors = self._validate_inn(data)
        errors.extend(inn_errors)

        # Проверка товаров
        items = data.get('items', [])
        if not items:
            errors.append("Отсутствуют товары в документе")
        else:
            for i, item in enumerate(items, 1):
                item_errors, item_warnings = self._validate_item(item, i)
                errors.extend(item_errors)
                warnings.extend(item_warnings)

        # Проверка итоговых сумм
        totals_errors, totals_warnings = self._validate_totals(data)
        errors.extend(totals_errors)
        warnings.extend(totals_warnings)

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _validate_required_fields(self, data):
        """Проверка обязательных полей"""
        errors = []

        # Проверка document_info
        if not data.get('document_info', {}).get('invoice_number'):
            errors.append("Отсутствует номер счета")
        if not data.get('document_info', {}).get('invoice_date'):
            errors.append("Отсутствует дата счета")

        # Проверка recipient_details
        if not data.get('recipient_details', {}).get('inn'):
            errors.append("Отсутствует ИНН получателя")
        if not data.get('recipient_details', {}).get('payee_name'):
            errors.append("Отсутствует название получателя")

        return errors

    def _validate_date(self, date_str):
        """Проверка формата даты DD.MM.YYYY"""
        if not date_str:
            return None

        try:
            datetime.strptime(date_str, '%d.%m.%Y')
            return None
        except ValueError:
            return f"Неверный формат даты: {date_str}. Ожидается DD.MM.YYYY"

    def _validate_inn(self, data):
        """Проверка ИНН (10 или 12 цифр)"""
        errors = []

        recipient_inn = data.get('recipient_details', {}).get('inn')
        if recipient_inn and not re.match(r'^\d{10}$|^\d{12}$', str(recipient_inn)):
            errors.append(f"Неверный формат ИНН получателя: {recipient_inn}")

        buyer_inn = data.get('buyer_details', {}).get('inn')
        if buyer_inn and not re.match(r'^\d{10}$|^\d{12}$', str(buyer_inn)):
            errors.append(f"Неверный формат ИНН покупателя: {buyer_inn}")

        return errors

    def _validate_item(self, item, index):
        """Валидация товарной позиции"""
        errors = []
        warnings = []

        # Проверка обязательных полей
        if not item.get('name'):
            errors.append(f"Товар {index}: отсутствует наименование")

        quantity = item.get('quantity')
        price_unit = item.get('price_unit')
        total_sum = item.get('total_sum')

        # Проверка диапазонов
        if quantity is not None and quantity <= 0:
            errors.append(f"Товар {index}: количество должно быть > 0")
        if price_unit is not None and price_unit <= 0:
            errors.append(f"Товар {index}: цена должна быть > 0")

        # Проверка математики: цена × количество = сумма
        if all(x is not None for x in [quantity, price_unit, total_sum]):
            expected_sum = quantity * price_unit
            if abs(expected_sum - total_sum) > self.tolerance:
                errors.append(
                    f"Товар {index}: ошибка расчета. "
                    f"{quantity} × {price_unit} = {expected_sum}, "
                    f"но указано {total_sum}"
                )

        # Проверка НДС
        vat_rate = item.get('vat_rate')
        vat_amount = item.get('vat_amount')

        if vat_rate is not None and vat_rate not in self.valid_vat_rates:
            warnings.append(f"Товар {index}: нестандартная ставка НДС {vat_rate}%")

        # Проверка расчета НДС
        if all(x is not None for x in [total_sum, vat_rate, vat_amount]):
            expected_vat = total_sum * (vat_rate / 100)
            if abs(expected_vat - vat_amount) > self.tolerance:
                errors.append(
                    f"Товар {index}: ошибка расчета НДС. "
                    f"{total_sum} × {vat_rate}% = {expected_vat}, "
                    f"но указано {vat_amount}"
                )

        return errors, warnings

    def _validate_totals(self, data):
        """Проверка итоговых сумм документа"""
        errors = []
        warnings = []

        items = data.get('items', [])
        totals = data.get('totals', {})

        if not totals:
            warnings.append("Отсутствуют итоговые суммы документа")
            return errors, warnings

        # Расчет сумм из товаров
        calc_total_sum = sum(item.get('total_sum', 0) for item in items)
        calc_total_vat = sum(item.get('vat_amount', 0) for item in items)

        total_without_vat = totals.get('total_without_vat')
        total_vat = totals.get('total_vat')
        total_amount = totals.get('total_amount')

        # Проверка: сумма товаров = сумма без НДС
        if total_without_vat is not None:
            if abs(calc_total_sum - total_without_vat) > self.tolerance:
                errors.append(
                    f"Несоответствие суммы без НДС: "
                    f"сумма товаров = {calc_total_sum}, "
                    f"указано = {total_without_vat}"
                )

        # Проверка: сумма НДС товаров = общий НДС
        if total_vat is not None:
            if abs(calc_total_vat - total_vat) > self.tolerance:
                errors.append(
                    f"Несоответствие суммы НДС: "
                    f"сумма НДС товаров = {calc_total_vat}, "
                    f"указано = {total_vat}"
                )

        # Проверка: сумма без НДС + НДС = итого
        if all(x is not None for x in [total_without_vat, total_vat, total_amount]):
            expected_total = total_without_vat + total_vat
            if abs(expected_total - total_amount) > self.tolerance:
                errors.append(
                    f"Ошибка расчета итоговой суммы: "
                    f"{total_without_vat} + {total_vat} = {expected_total}, "
                    f"но указано {total_amount}"
                )

        return errors, warnings

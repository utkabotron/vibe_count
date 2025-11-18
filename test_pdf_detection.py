#!/usr/bin/env python3
"""
Тест автоматического определения типа PDF (скан vs текстовый документ)
"""
import logging
from pathlib import Path
from src.llm_handler import LLMHandler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_pdf_detection(pdf_path: str):
    """
    Тест определения типа PDF файла

    Args:
        pdf_path: Путь к PDF файлу для тестирования
    """
    path = Path(pdf_path)

    if not path.exists():
        print(f"❌ Файл не найден: {pdf_path}")
        return

    if path.suffix.lower() != '.pdf':
        print(f"❌ Это не PDF файл: {pdf_path}")
        return

    print(f"\n{'='*60}")
    print(f"Тестируем файл: {path.name}")
    print(f"{'='*60}\n")

    # Создаем экземпляр LLMHandler
    handler = LLMHandler()

    # Тестируем метод определения типа PDF
    is_scanned = handler._is_scanned_pdf(path)

    print(f"\n{'='*60}")
    if is_scanned:
        print(f"✅ Результат: СКАН")
        print(f"   Будет использован: GPT-4o Vision API")
    else:
        print(f"✅ Результат: ТЕКСТОВЫЙ ДОКУМЕНТ")
        print(f"   Будет использован: GPT-4 Turbo API")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Использование: python test_pdf_detection.py <путь_к_pdf_файлу>")
        print("\nПример:")
        print("  python test_pdf_detection.py '/path/to/document.pdf'")
        sys.exit(1)

    pdf_path = sys.argv[1]
    test_pdf_detection(pdf_path)

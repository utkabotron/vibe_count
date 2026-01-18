# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Обзор проекта

Vibe Counting - это система автоматической обработки бухгалтерских документов (счета, накладные, УПД) с использованием OpenAI API. Система сканирует папку на Яндекс.Диске, извлекает структурированные данные из документов с помощью GPT-4 Vision, валидирует их и записывает в Google Sheets для проверки оператором (Human-in-the-Loop).

## Архитектура

### Основной поток обработки (main.py)

1. `FileProcessor` сканирует папку `/vibe/Входящие` на Яндекс.Диске
2. Берет первый файл (игнорирует файлы с префиксом `000_`)
3. `LLMHandler` обрабатывает документ через OpenAI API:
   - Изображения (JPG, PNG) и PDF → GPT-4o Vision
   - Текстовые файлы (DOCX, XLSX) → GPT-4 Turbo (после текстового извлечения)
4. `Validator` проверяет данные:
   - Математические проверки (цена × количество = сумма, расчеты НДС)
   - Итоговые суммы документа
   - Обязательные поля
5. `SheetsWriter` записывает данные в Google Sheets со статусом "На проверку"
6. `FileProcessor` архивирует файл в `/vibe/Архив/ГОД/МЕСЯЦ` или перемещает в `/vibe/Ошибки`

### REST API (api.py)

FastAPI-приложение с автоматической фоновой обработкой:
- **Автообработка**: Фоновая задача периодически проверяет папку `/vibe/Входящие` (по умолчанию каждые 30 секунд)
- **Эндпоинты управления**:
  - `POST /process` - обработать файл вручную (асинхронно)
  - `POST /process-sync` - обработать файл синхронно
  - `GET /status` - получить статус обработки
  - `POST /auto/enable|disable` - управление автоматической обработкой
  - `POST /auto/interval/{seconds}` - изменить интервал проверки

### Модули

- `config.py` - Конфигурация из .env, валидация переменных окружения
- `file_processor.py` - Работа с Яндекс.Диском (скачивание, архивация, получение публичных ссылок)
- `llm_handler.py` - Интеграция с OpenAI API, извлечение текста из PDF/DOCX/XLSX
- `sheets_writer.py` - Запись данных в Google Sheets (уплощение JSON, маппинг на колонки)
- `validator.py` - Валидация данных (soft validation - расчетные ошибки = warnings, а не errors)

## Структура проекта

```
/
├── src/                        # Основной код приложения
├── scripts/                    # Вспомогательные скрипты (см. scripts/README.md)
│   ├── deployment/            # Деплой и настройка (deploy_simple.sh и др.)
│   ├── testing/               # Тесты компонентов
│   ├── diagnostics/           # Диагностика системы
│   ├── maintenance/           # Обслуживание и обновления
│   └── utilities/             # Вспомогательные утилиты
├── docs/                       # Документация
│   ├── reports/               # Отчеты о развертывании
│   └── old/                   # Архивные планы разработки
├── logs/                       # Логи приложения
├── temp/                       # Временные файлы
├── requirements.txt            # Python зависимости
├── .env                        # Переменные окружения (не в git)
└── vibecount-credentials-gsheets.json  # Google Sheets credentials (не в git)
```

## Команды разработки

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск обработчика однократно (обрабатывает один файл)
python src/main.py

# Запуск REST API с автообработкой (локально на порту 8000)
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000

# Или через модуль
python src/api.py
```

### Работа с сервером (72.56.70.180)

**Сервер:** 72.56.70.180
**API порт:** 8001 (production)
**API URL:** http://72.56.70.180:8001

```bash
# Деплой на сервер (автоматический)
./scripts/deployment/deploy_simple.sh

# Обновление кода на сервере
python scripts/maintenance/update_server.py

# Проверка логов API на сервере
python scripts/diagnostics/check_api_logs.py

# Диагностика сервера
python scripts/diagnostics/diagnose_server.py

# Перезапуск API на сервере
python scripts/maintenance/update_and_restart_api.py

# Проверка статуса API
curl http://72.56.70.180:8001/health
curl http://72.56.70.180:8001/status
```

### Тестирование

```bash
# Тест API
python scripts/testing/test_api.py

# Тест OpenAI API ключа
python scripts/testing/test_openai.py

# Тест Google Sheets доступа
python scripts/testing/test_gsheets.py

# Тест автоматической обработки
python scripts/testing/test_auto_processing.py

# Тест полного цикла
python scripts/testing/test_full_auto.py

# Тест валидации
python scripts/testing/test_validation_fix.py

# Тест перемещения файлов
python scripts/testing/test_file_moving.py

# Тест определения типа PDF (скан vs текстовый документ)
python scripts/testing/test_pdf_detection.py "/path/to/file.pdf"
```

### Работа с Яндекс.Диском

```bash
# Создание структуры папок локально
python scripts/utilities/create_yandex_folders.py

# Создание структуры папок на удаленном сервере
python scripts/deployment/setup_yandex_folders_remote.py

# Проверка структуры Яндекс.Диска
python scripts/diagnostics/check_yandex_structure.py

# Проверка прав доступа к Яндекс.Диску
python scripts/testing/test_yandex_permissions.py
```

## Конфигурация

### Переменные окружения (.env)

Обязательные:
- `YANDEX_OAUTH_TOKEN` - OAuth токен для Яндекс.Диска
- `OPENAI_API_KEY` - API ключ OpenAI
- `GOOGLE_SHEETS_ID` - ID таблицы Google Sheets
- `GOOGLE_CREDENTIALS_PATH` - Путь к JSON-файлу с credentials Service Account

Опциональные (с дефолтными значениями):
- `YANDEX_INCOMING_FOLDER=disk:/vibe/Входящие` - папка для новых документов
- `YANDEX_PROCESSED_FOLDER=disk:/vibe/Архив` - папка для обработанных
- `YANDEX_ERROR_FOLDER=disk:/vibe/Ошибки` - папка для файлов с ошибками

### Структура данных

Система извлекает документы в JSON формат:
```json
{
  "document_info": {"invoice_number": "...", "invoice_date": "DD.MM.YYYY"},
  "recipient_details": {"bank_name": "...", "inn": "...", "kpp": "...", ...},
  "buyer_details": {"name": "...", "inn": "...", "kpp": "..."},
  "logistics": {"consignee": "...", "consignor": "..."},
  "items": [{"name": "...", "quantity": 1.0, "price_unit": 100.0, "total_sum": 100.0, "vat_rate": 20, "vat_amount": 20.0, ...}],
  "totals": {"total_without_vat": 100.0, "total_vat": 20.0, "total_amount": 120.0}
}
```

## Важные особенности

### Валидация (validator.py)

- **Soft validation**: Математические ошибки (расчеты цен, НДС, итогов) теперь генерируют **warnings**, а не errors
- Errors только для критичных проблем (отсутствие обязательных полей, некорректные форматы дат)
- Допуск на округление: `VALIDATION_TOLERANCE = 0.01`
- Файлы с warnings все равно попадают в Google Sheets для проверки оператором

### Архивация файлов

При успешной обработке файлы перемещаются в структуру:
```
/vibe/Архив/
  └── YYYY/         # Год из даты документа
      └── MM/       # Месяц из даты документа
          └── filename.pdf
```

Функция `_ensure_folder_exists()` создает вложенные папки автоматически.

### PDF обработка

PDF файлы обрабатываются с **автоматическим определением типа документа**:

1. **Метод `_is_scanned_pdf()`** анализирует первую страницу PDF:
   - Извлекает текст через `pdfplumber`
   - Если текста меньше 100 символов → определяется как **скан**
   - Если текста достаточно → определяется как **текстовый PDF**

2. **В зависимости от типа выбирается API**:
   - **Скан** → **GPT-4o Vision**: Конвертация первой страницы в PNG через `pdf2image`, отправка как изображение
   - **Текстовый документ** → **GPT-4 Turbo**: Извлечение текста и таблиц через `pdfplumber`, отправка как текст

3. **Преимущества**:
   - Экономия токенов: текстовые PDF дешевле в обработке (~90% случаев)
   - Точность: сканы обрабатываются Vision API для лучшего распознавания
   - Автоматическая обработка: без ручной настройки

**Тестирование типа PDF**: `python test_pdf_detection.py <путь_к_файлу.pdf>`

### OpenAI API

- Используется `response_format={"type": "json_object"}` для структурированного вывода
- `temperature=0` для детерминированности
- `max_tokens=4096` для больших документов
- Модели: `gpt-4o` (vision), `gpt-4-turbo` (text)

### Автоматическая обработка (api.py)

- Фоновая задача `auto_process_loop()` запускается при старте API через `lifespan`
- Проверяет папку каждые `check_interval` секунд (по умолчанию 30)
- Использует `asyncio.to_thread()` для вызова синхронного `handler()` без блокировки
- Состояние обработки отслеживается в глобальной переменной `processing_status`

### Логирование

- Основные логи: `logs/api.log` (для REST API)
- Cron логи: `logs/cron.log` (для запусков по расписанию)
- Формат: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Развертывание

### Локальная разработка
1. Создать `.env` из `.env.example`
2. Установить зависимости: `pip install -r requirements.txt`
3. Положить `vibecount-credentials-gsheets.json` в корень проекта
4. Запустить: `python src/api.py` или `python src/main.py`

### Production (сервер 72.56.70.180)

**Автоматический деплой:**
```bash
./scripts/deployment/deploy_simple.sh
```

**Конфигурация:**
- **Порт:** 8001 (избегает конфликта с nano-banana-api на порту 8000)
- **Systemd сервис:** `/etc/systemd/system/vibe-count-api.service`
- **Рабочая директория:** `/root/vibe_count`
- **Пользователь:** root
- **Автозапуск:** Включен (через systemd)

**Systemd сервис:**
```ini
[Unit]
Description=Vibe Count API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/vibe_count
Environment="PATH=/root/vibe_count/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/root/vibe_count/venv/bin/uvicorn src.api:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10
StandardOutput=append:/root/vibe_count/logs/api-output.log
StandardError=append:/root/vibe_count/logs/api-error.log

[Install]
WantedBy=multi-user.target
```

**ВАЖНО:** PATH должен включать `/usr/bin` для доступа к `pdfinfo` (poppler-utils)

**Управление сервисом:**
```bash
# Проверить статус
ssh root@72.56.70.180 "systemctl status vibe-count-api"

# Перезапустить
ssh root@72.56.70.180 "systemctl restart vibe-count-api"

# Просмотр логов
ssh root@72.56.70.180 "journalctl -u vibe-count-api -f"
ssh root@72.56.70.180 "tail -f /root/vibe_count/logs/api-output.log"
```

**Мониторинг:**
- API health: http://72.56.70.180:8001/health
- Статус автообработки: http://72.56.70.180:8001/status
- Логи: `/root/vibe_count/logs/`

**Документация деплоя:**
- `docs/reports/DEPLOYMENT_SUCCESS.md` - успешное развертывание
- `docs/reports/PORT_CHANGE_SUMMARY.md` - изменение портов
- `docs/reports/SERVER_CLEANUP_REPORT.md` - очистка сервера

## Типичные задачи

### Добавление нового поля в извлечение данных
1. Обновить `SYSTEM_PROMPT` в `llm_handler.py` с новой структурой JSON
2. Обновить валидацию в `validator.py` если нужна проверка
3. Добавить маппинг в `sheets_writer.py` для записи в новую колонку Google Sheets

### Изменение логики валидации
- Редактировать `validator.py`
- Помнить о soft validation: расчетные ошибки → warnings, критичные → errors

### Изменение интервала автообработки
```bash
curl -X POST http://72.56.70.180:8001/auto/interval/60
```

### Отключение автообработки
```bash
curl -X POST http://72.56.70.180:8001/auto/disable
```

## Troubleshooting

### "Нет файлов для обработки"
- Проверить папку `/vibe/Входящие` на Яндекс.Диске
- Убедиться что файлы не начинаются с `000_` (они игнорируются)

### Ошибки OpenAI API
- Проверить `OPENAI_API_KEY` в `.env`
- Проверить баланс на платформе OpenAI
- Логи содержат детали ошибок API

### Файлы попадают в `/vibe/Ошибки`
- Проверить `logs/api.log` для деталей валидации
- Проверить структуру документа (может не соответствовать ожидаемому формату)
- Проверить что все обязательные поля присутствуют

### Google Sheets ошибки
- Проверить что Service Account email добавлен в доступ к таблице
- Проверить `GOOGLE_SHEETS_ID` в `.env`
- Проверить путь к `vibecount-credentials-gsheets.json`

### PDF не обрабатывается с ошибкой "Unable to get page count"

**Проблема:** Ошибка `Unable to get page count. Is poppler installed and in PATH?`

**Причина:** `pdfinfo` (из пакета poppler-utils) не доступен в PATH для Python процесса

**Решение:**

1. **Проверить установку poppler-utils:**
   ```bash
   ssh root@72.56.70.180 "which pdfinfo"
   # Должно вернуть: /usr/bin/pdfinfo
   ```

2. **Убедиться что PATH в systemd сервисе включает /usr/bin:**
   ```bash
   ssh root@72.56.70.180 "cat /etc/systemd/system/vibe-count-api.service | grep Environment"
   # Должно быть: Environment="PATH=/root/vibe_count/venv/bin:/usr/local/bin:/usr/bin:/bin"
   ```

3. **Если PATH неправильный, исправить:**
   ```bash
   python scripts/maintenance/fix_systemd_path.py
   ```

4. **Установка poppler-utils (если отсутствует):**
   - macOS: `brew install poppler`
   - Ubuntu/Debian: `apt-get install -y poppler-utils`
   - Сервер: `python scripts/maintenance/install_poppler.py`

### Ошибка "FileNotFoundError: [Errno 2] No such file or directory: 'pdfinfo'"

Это значит что systemd сервис не имеет доступа к `/usr/bin` в PATH. См. решение выше.

# Отчет о развертывании Vibe Counting API

**Дата:** 2026-01-18
**Сервер:** 72.56.70.180
**Статус:** ✅ УСПЕШНО РАЗВЕРНУТО

---

## Выполненные задачи

### 1. Локальная подготовка

- ✅ Созданы директории `logs/` и `temp/`
- ✅ Добавлен `pdf2image>=1.16.0` в requirements.txt
- ✅ Исправлены пути в .env:
  - `YANDEX_INCOMING_FOLDER=disk:/vibe/Входящие`
  - `YANDEX_PROCESSED_FOLDER=disk:/vibe/Архив` (было `/vibe/Обработанные`)
  - `YANDEX_ERROR_FOLDER=disk:/vibe/Ошибки`

### 2. Создание вспомогательных скриптов

- ✅ `deploy_simple.sh` - автоматическое развертывание через SSH
- ✅ `DEPLOY_MANUAL.md` - пошаговая инструкция для ручного развертывания
- ✅ `diagnose_server.py` - скрипт диагностики сервера
- ✅ `test_openai.py` - тест валидности OpenAI API ключа
- ✅ `test_gsheets.py` - тест доступа к Google Sheets

### 3. Развертывание на сервере

- ✅ Настроены SSH ключи для беспарольного доступа
- ✅ Установлены системные зависимости (Python, poppler-utils)
- ✅ Создано виртуальное окружение Python
- ✅ Установлены Python зависимости из requirements.txt
- ✅ Скопированы credentials (.env, vibecount-credentials-gsheets.json)
- ✅ Настроен systemd сервис `vibe-count-api.service`

### 4. Решенные проблемы

**Проблема:** На порту 8000 работал старый проект `nano-banana-v2`
**Решение:** Vibe Count API переведен на порт 8001, nano-banana продолжает работать на порту 8000

**Проблема:** Отсутствие pip/venv в локальном WSL окружении
**Решение:** Создан bash-скрипт для развертывания без Python зависимостей

---

## Текущее состояние системы

### Сервисы на сервере

На сервере работают **два независимых API**:

1. **Vibe Count API** (новый) - Порт **8001**
   - Invoice AI Pipeline для автоматической обработки бухгалтерских документов
   - URL: http://72.56.70.180:8001

2. **Nano Banana API** (существующий) - Порт **8000**
   - Сохранен на оригинальном порту без изменений
   - URL: http://72.56.70.180:8000

Оба сервиса работают одновременно без конфликтов.

### Vibe Count API Информация

```json
{
  "message": "Invoice AI Pipeline API",
  "version": "2.0.0",
  "description": "Автоматическая обработка файлов из /vibe/Входящие",
  "auto_mode": true,
  "check_interval": "30 секунд"
}
```

### Статус автообработки

```json
{
  "is_processing": false,
  "last_run": "2026-01-18T12:57:55",
  "last_result": {
    "statusCode": 200,
    "body": "Нет файлов для обработки"
  },
  "total_processed": 2,
  "auto_mode": true,
  "check_interval": 30
}
```

**Автообработка:** ✅ Включена
**Интервал проверки:** 30 секунд
**Обработано документов:** 2

### Systemd Сервис

```
Status: active (running)
PID: 1955639
Memory: 59.0M
CPU: 1.313s
Uptime: ~1 минута
```

### Доступные эндпоинты

- `GET /` - Информация об API
- `GET /health` - Healthcheck ✅ Работает
- `GET /status` - Статус автообработки ✅ Работает
- `POST /process` - Обработать файл вручную (асинхронно)
- `POST /process-sync` - Обработать файл синхронно
- `POST /auto/enable` - Включить автообработку
- `POST /auto/disable` - Выключить автообработку
- `POST /auto/interval/{seconds}` - Установить интервал проверки

---

## Проверка работы

### Базовые тесты

```bash
# Health check
curl http://72.56.70.180:8001/health
# Ответ: {"status":"healthy","timestamp":"2026-01-18T12:58:01.952512"}

# Статус автообработки
curl http://72.56.70.180:8001/status
# Показывает: auto_mode: true, check_interval: 30

# API информация
curl http://72.56.70.180:8001/
# Показывает: "Invoice AI Pipeline API" v2.0.0
```

### Логи

```bash
# Логи API
ssh root@72.56.70.180 "tail -f /root/vibe_count/logs/api-output.log"

# Systemd логи
ssh root@72.56.70.180 "journalctl -u vibe-count-api -f"
```

---

## Управление сервисом

### Перезапуск

```bash
ssh root@72.56.70.180 "systemctl restart vibe-count-api"
```

### Остановка

```bash
ssh root@72.56.70.180 "systemctl stop vibe-count-api"
```

### Просмотр статуса

```bash
ssh root@72.56.70.180 "systemctl status vibe-count-api"
```

### Управление автообработкой

```bash
# Отключить
curl -X POST http://72.56.70.180:8001/auto/disable

# Включить
curl -X POST http://72.56.70.180:8001/auto/enable

# Изменить интервал (например, на 60 секунд)
curl -X POST http://72.56.70.180:8001/auto/interval/60
```

---

## Дальнейшие шаги

### 1. Создание папок на Yandex.Disk

Выполните на сервере:

```bash
ssh root@72.56.70.180
cd /root/vibe_count
source venv/bin/activate
python3 -c "
from yadisk import YaDisk
import os
from dotenv import load_dotenv

load_dotenv()
disk = YaDisk(token=os.getenv('YANDEX_OAUTH_TOKEN'))

for folder in ['/vibe', '/vibe/Входящие', '/vibe/Архив', '/vibe/Ошибки']:
    try:
        disk.mkdir(folder)
        print(f'✓ Создана папка: {folder}')
    except:
        print(f'ℹ Папка уже существует: {folder}')
"
```

### 2. Тестирование обработки файла

1. Загрузите тестовый документ (PDF/JPG счет или накладную) в Yandex.Disk `/vibe/Входящие`
2. Подождите 30 секунд (интервал автопроверки)
3. Проверьте логи:
   ```bash
   ssh root@72.56.70.180 "tail -f /root/vibe_count/logs/api-output.log"
   ```
4. Проверьте Google Sheets (ID: 1YrGvOG3jTjD-4bD5aqkKlUy_Ami0X_I4qzqtPQAOQHo)
5. Проверьте архивацию в `/vibe/Архив/YYYY/MM/`

### 3. Мониторинг

Рекомендуется отслеживать:
- Логи API: `/root/vibe_count/logs/api-output.log`
- Статус сервиса: `systemctl status vibe-count-api`
- Состояние автообработки: `GET /status`

---

## Структура проекта на сервере

```
/root/vibe_count/
├── src/                    # Исходный код
├── venv/                   # Виртуальное окружение Python
├── logs/                   # Логи приложения
│   ├── api.log            # Старые логи
│   ├── api-output.log     # Stdout systemd
│   └── api-error.log      # Stderr systemd
├── temp/                   # Временные файлы
├── .env                    # Переменные окружения (credentials)
├── vibecount-credentials-gsheets.json  # Google Sheets credentials
├── requirements.txt        # Python зависимости
├── CLAUDE.md              # Документация для Claude
└── README.md              # Общая документация
```

---

## Критические файлы

### На сервере

- `/etc/systemd/system/vibe-count-api.service` - Конфигурация systemd сервиса
- `/root/vibe_count/.env` - Переменные окружения (токены, ключи)
- `/root/vibe_count/vibecount-credentials-gsheets.json` - Google Service Account credentials

### Локально

- `deploy_simple.sh` - Скрипт автоматического развертывания
- `DEPLOY_MANUAL.md` - Инструкция для ручного развертывания
- `.env` - Локальная копия переменных окружения

---

## Troubleshooting

### API не отвечает

```bash
# Проверить статус сервиса
ssh root@72.56.70.180 "systemctl status vibe-count-api"

# Проверить логи ошибок
ssh root@72.56.70.180 "cat /root/vibe_count/logs/api-error.log"

# Проверить systemd логи
ssh root@72.56.70.180 "journalctl -u vibe-count-api -n 100"
```

### Автообработка не работает

```bash
# Проверить статус
curl http://72.56.70.180:8001/status

# Включить, если выключена
curl -X POST http://72.56.70.180:8001/auto/enable

# Проверить логи
ssh root@72.56.70.180 "tail -f /root/vibe_count/logs/api-output.log"
```

### Обновление кода

```bash
cd "/mnt/c/PK/Projects/Vibe Counting"
./deploy_simple.sh
```

---

## Конфигурация

### Переменные окружения (.env)

```env
YANDEX_OAUTH_TOKEN=your_yandex_oauth_token_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_SHEETS_ID=your_google_sheets_id_here
GOOGLE_CREDENTIALS_PATH=vibecount-credentials-gsheets.json
YANDEX_INCOMING_FOLDER=disk:/vibe/Входящие
YANDEX_PROCESSED_FOLDER=disk:/vibe/Архив
YANDEX_ERROR_FOLDER=disk:/vibe/Ошибки
```

---

## Заключение

✅ **Vibe Counting API успешно развернут и работает**

- API доступен по адресу: http://72.56.70.180:8001
- Автообработка включена (проверка каждые 30 секунд)
- Systemd сервис настроен на автозапуск при перезагрузке сервера
- Все критичные проблемы из плана решены

**Следующий шаг:** Протестируйте обработку реального документа, загрузив файл в `/vibe/Входящие` на Yandex.Disk.

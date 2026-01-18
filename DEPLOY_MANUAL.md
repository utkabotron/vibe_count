# Ручное развертывание Vibe Counting

## Шаг 1: Настройка SSH ключа (беспарольный доступ)

Откройте WSL терминал и выполните:

```bash
cd "/mnt/c/PK/Projects/Vibe Counting"

# Создать SSH ключ (нажимайте Enter на всех вопросах)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Скопировать ключ на сервер (введите пароль: rS,f+8w4-Zi1M+)
ssh-copy-id root@72.56.70.180

# Проверить подключение без пароля
ssh root@72.56.70.180 "echo 'SSH ключ работает!'"
```

## Шаг 2: Запустить автоматический деплой

После настройки SSH ключа:

```bash
# Сделать скрипт исполняемым
chmod +x deploy_simple.sh

# Запустить развертывание
./deploy_simple.sh
```

## Альтернатива: Пошаговое ручное развертывание

Если автоматический скрипт не работает, выполните вручную:

### 1. Подключиться к серверу

```bash
ssh root@72.56.70.180
```

Пароль: `rS,f+8w4-Zi1M+`

### 2. На сервере: Установить системные зависимости

```bash
apt-get update
apt-get install -y python3 python3-venv python3-pip git poppler-utils curl
```

### 3. На сервере: Создать/обновить проект

```bash
# Создать директорию
mkdir -p /root/vibe_count
cd /root/vibe_count

# Создать виртуальное окружение
python3 -m venv venv

# Создать директории
mkdir -p logs temp src
```

### 4. На локальной машине: Скопировать файлы

Откройте **новый терминал WSL** (не закрывая SSH сессию):

```bash
cd "/mnt/c/PK/Projects/Vibe Counting"

# Скопировать исходный код
scp -r src/ root@72.56.70.180:/root/vibe_count/

# Скопировать зависимости
scp requirements.txt root@72.56.70.180:/root/vibe_count/

# Скопировать credentials
scp .env root@72.56.70.180:/root/vibe_count/
scp vibecount-credentials-gsheets.json root@72.56.70.180:/root/vibe_count/
```

### 5. На сервере: Установить Python зависимости

Вернитесь в SSH терминал:

```bash
cd /root/vibe_count
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. На сервере: Настроить systemd сервис

```bash
cat > /etc/systemd/system/vibe-count-api.service <<'EOF'
[Unit]
Description=Vibe Count API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/vibe_count
Environment="PATH=/root/vibe_count/venv/bin"
ExecStart=/root/vibe_count/venv/bin/uvicorn src.api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### 7. На сервере: Запустить сервис

```bash
systemctl daemon-reload
systemctl enable vibe-count-api
systemctl start vibe-count-api

# Проверить статус
systemctl status vibe-count-api

# Проверить логи
journalctl -u vibe-count-api -n 50 --no-pager

# Проверить API
sleep 3
curl http://localhost:8000/health
```

### 8. На сервере: Создать папки на Yandex.Disk

```bash
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

## Проверка работы

### На локальной машине

```bash
# Health check
curl http://72.56.70.180:8000/health

# Статус автообработки
curl http://72.56.70.180:8000/status

# Просмотр логов
ssh root@72.56.70.180 "tail -f /root/vibe_count/logs/api.log"
```

## Управление сервисом

```bash
# Перезапуск
ssh root@72.56.70.180 "systemctl restart vibe-count-api"

# Остановка
ssh root@72.56.70.180 "systemctl stop vibe-count-api"

# Просмотр статуса
ssh root@72.56.70.180 "systemctl status vibe-count-api"

# Просмотр логов в реальном времени
ssh root@72.56.70.180 "journalctl -u vibe-count-api -f"
```

## Troubleshooting

### API не запускается

```bash
ssh root@72.56.70.180 "journalctl -u vibe-count-api -n 100 --no-pager"
```

### Проверить зависимости

```bash
ssh root@72.56.70.180 "cd /root/vibe_count && venv/bin/pip list"
```

### Проверить переменные окружения

```bash
ssh root@72.56.70.180 "cat /root/vibe_count/.env"
```

### Ручной запуск для тестирования

```bash
ssh root@72.56.70.180
cd /root/vibe_count
source venv/bin/activate
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

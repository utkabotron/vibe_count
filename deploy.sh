#!/bin/bash
# Скрипт развертывания Vibe Counting на сервер без Python зависимостей
# Использует только SSH и базовые утилиты

set -e  # Остановка при ошибке

HOST="72.56.70.180"
USER="root"
PASS="rS,f+8w4-Zi1M+"
PROJECT_DIR="/root/vibe_count"

echo "=========================================="
echo "  РАЗВЕРТЫВАНИЕ VIBE COUNTING"
echo "=========================================="

# Функция для выполнения SSH команд
ssh_exec() {
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$USER@$HOST" "$1"
}

# Функция для копирования файлов
scp_file() {
    sshpass -p "$PASS" scp -o StrictHostKeyChecking=no "$1" "$USER@$HOST:$2"
}

echo -e "\n1. Проверка доступности сервера..."
if ping -c 1 -W 2 "$HOST" > /dev/null 2>&1; then
    echo "   ✓ Сервер доступен"
else
    echo "   ❌ Сервер недоступен"
    exit 1
fi

echo -e "\n2. Проверка SSH подключения..."
if ssh_exec "echo 'connected'" > /dev/null 2>&1; then
    echo "   ✓ SSH подключение работает"
else
    echo "   ❌ Не удалось подключиться по SSH"
    exit 1
fi

echo -e "\n3. Проверка существующей установки..."
if ssh_exec "test -d $PROJECT_DIR && echo 'exists'" | grep -q "exists"; then
    echo "   ✓ Проект уже установлен - выполняется обновление"
    UPDATE_MODE=true
else
    echo "   ℹ Проект не найден - выполняется полная установка"
    UPDATE_MODE=false
fi

if [ "$UPDATE_MODE" = false ]; then
    echo -e "\n4. Установка системных зависимостей..."
    ssh_exec "apt-get update && apt-get install -y python3 python3-venv python3-pip git poppler-utils"
    echo "   ✓ Зависимости установлены"

    echo -e "\n5. Клонирование репозитория..."
    # Здесь нужно будет использовать git или создать директорию вручную
    ssh_exec "mkdir -p $PROJECT_DIR"
    echo "   ✓ Директория создана"
else
    echo -e "\n4. Обновление кода..."
    ssh_exec "cd $PROJECT_DIR && git pull || echo 'Git pull не удался - используем ручное обновление'"
fi

echo -e "\n6. Копирование файлов проекта..."
# Создаем tar архив локально и отправляем на сервер
tar czf /tmp/vibe_count.tar.gz -C "$(pwd)" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='temp/*' \
    --exclude='logs/*' \
    src/ requirements.txt CLAUDE.md README.md 2>/dev/null || true

scp_file "/tmp/vibe_count.tar.gz" "/tmp/"
ssh_exec "cd $PROJECT_DIR && tar xzf /tmp/vibe_count.tar.gz && rm /tmp/vibe_count.tar.gz"
rm /tmp/vibe_count.tar.gz
echo "   ✓ Файлы скопированы"

echo -e "\n7. Создание виртуального окружения..."
ssh_exec "cd $PROJECT_DIR && python3 -m venv venv"
echo "   ✓ Виртуальное окружение создано"

echo -e "\n8. Установка Python зависимостей..."
ssh_exec "cd $PROJECT_DIR && venv/bin/pip install --upgrade pip && venv/bin/pip install -r requirements.txt"
echo "   ✓ Зависимости установлены"

echo -e "\n9. Создание директорий..."
ssh_exec "cd $PROJECT_DIR && mkdir -p logs temp"
echo "   ✓ Директории созданы"

echo -e "\n10. Копирование credentials..."
if [ -f ".env" ]; then
    scp_file ".env" "$PROJECT_DIR/"
    echo "   ✓ .env скопирован"
else
    echo "   ⚠ .env не найден локально"
fi

if [ -f "vibecount-credentials-gsheets.json" ]; then
    scp_file "vibecount-credentials-gsheets.json" "$PROJECT_DIR/"
    echo "   ✓ Google credentials скопированы"
else
    echo "   ⚠ vibecount-credentials-gsheets.json не найден"
fi

echo -e "\n11. Настройка systemd сервиса..."
cat > /tmp/vibe-count-api.service <<'EOF'
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

scp_file "/tmp/vibe-count-api.service" "/etc/systemd/system/"
rm /tmp/vibe-count-api.service
echo "   ✓ Systemd сервис настроен"

echo -e "\n12. Запуск API сервиса..."
ssh_exec "systemctl daemon-reload && systemctl enable vibe-count-api && systemctl restart vibe-count-api"
echo "   ✓ Сервис запущен"

echo -e "\n13. Ожидание запуска API (5 сек)..."
sleep 5

echo -e "\n14. Проверка работы API..."
API_STATUS=$(ssh_exec "curl -s http://localhost:8000/health" || echo "failed")
if echo "$API_STATUS" | grep -q "healthy"; then
    echo "   ✓ API работает корректно"
    echo "   Response: $API_STATUS"
else
    echo "   ⚠ API не отвечает или ответ некорректен"
    echo "   Response: $API_STATUS"
    echo -e "\n   Проверьте логи:"
    echo "   ssh root@$HOST 'journalctl -u vibe-count-api -n 50'"
fi

echo -e "\n=========================================="
echo "  РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО"
echo "=========================================="
echo ""
echo "API доступен по адресу: http://$HOST:8000"
echo "Health check: http://$HOST:8000/health"
echo "Status: http://$HOST:8000/status"
echo ""
echo "Для просмотра логов:"
echo "  ssh root@$HOST 'tail -f /root/vibe_count/logs/api.log'"

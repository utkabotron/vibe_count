#!/bin/bash
# Упрощенный скрипт развертывания (требует настроенный SSH ключ)
# Сначала выполните: ssh-copy-id root@72.56.70.180

set -e

HOST="72.56.70.180"
USER="root"
PROJECT_DIR="/root/vibe_count"

echo "=========================================="
echo "  РАЗВЕРТЫВАНИЕ VIBE COUNTING"
echo "=========================================="

# Проверка SSH подключения
echo -e "\n1. Проверка SSH подключения..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes "$USER@$HOST" "echo 'connected'" > /dev/null 2>&1; then
    echo "   ✓ SSH ключ настроен"
else
    echo "   ❌ SSH ключ не настроен. Выполните:"
    echo "      ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N \"\""
    echo "      ssh-copy-id root@72.56.70.180"
    exit 1
fi

# Проверка существующей установки
echo -e "\n2. Проверка существующей установки..."
if ssh "$USER@$HOST" "test -d $PROJECT_DIR && echo 'exists'" | grep -q "exists"; then
    echo "   ✓ Проект установлен - обновление"
    MODE="update"
else
    echo "   ℹ Новая установка"
    MODE="install"
fi

if [ "$MODE" = "install" ]; then
    echo -e "\n3. Установка системных зависимостей..."
    ssh "$USER@$HOST" "apt-get update > /dev/null 2>&1 && apt-get install -y python3 python3-venv python3-pip git poppler-utils curl > /dev/null 2>&1"
    echo "   ✓ Зависимости установлены"

    echo -e "\n4. Создание директории проекта..."
    ssh "$USER@$HOST" "mkdir -p $PROJECT_DIR/src $PROJECT_DIR/logs $PROJECT_DIR/temp"
    echo "   ✓ Директории созданы"
fi

echo -e "\n5. Копирование файлов..."
rsync -az --delete \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='temp/*' \
    --exclude='logs/*' \
    --exclude='*.sh' \
    --exclude='*.md' \
    src/ "$USER@$HOST:$PROJECT_DIR/src/"

scp requirements.txt "$USER@$HOST:$PROJECT_DIR/"
scp .env "$USER@$HOST:$PROJECT_DIR/" 2>/dev/null || echo "   ⚠ .env не найден"
scp vibecount-credentials-gsheets.json "$USER@$HOST:$PROJECT_DIR/" 2>/dev/null || echo "   ⚠ credentials не найдены"
echo "   ✓ Файлы скопированы"

if [ "$MODE" = "install" ]; then
    echo -e "\n6. Создание виртуального окружения..."
    ssh "$USER@$HOST" "cd $PROJECT_DIR && python3 -m venv venv"
    echo "   ✓ Venv создан"
fi

echo -e "\n7. Установка Python зависимостей..."
ssh "$USER@$HOST" "cd $PROJECT_DIR && venv/bin/pip install --quiet --upgrade pip && venv/bin/pip install --quiet -r requirements.txt"
echo "   ✓ Зависимости установлены"

echo -e "\n8. Настройка systemd сервиса..."
ssh "$USER@$HOST" "cat > /etc/systemd/system/vibe-count-api.service" <<'EOF'
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
StandardOutput=append:/root/vibe_count/logs/api-output.log
StandardError=append:/root/vibe_count/logs/api-error.log

[Install]
WantedBy=multi-user.target
EOF
echo "   ✓ Сервис настроен"

echo -e "\n9. Запуск/перезапуск API..."
ssh "$USER@$HOST" "systemctl daemon-reload && systemctl enable vibe-count-api && systemctl restart vibe-count-api"
echo "   ✓ Сервис перезапущен"

echo -e "\n10. Ожидание запуска (5 сек)..."
sleep 5

echo -e "\n11. Проверка работы API..."
API_RESPONSE=$(ssh "$USER@$HOST" "curl -s http://localhost:8000/health" || echo "failed")

if echo "$API_RESPONSE" | grep -q "healthy"; then
    echo "   ✓ API работает!"
    echo "   Response: $API_RESPONSE"
else
    echo "   ⚠ API не отвечает"
    echo "   Проверьте логи: ssh $USER@$HOST 'journalctl -u vibe-count-api -n 50'"
    exit 1
fi

echo -e "\n12. Проверка статуса автообработки..."
STATUS=$(ssh "$USER@$HOST" "curl -s http://localhost:8000/status")
echo "$STATUS" | head -20

echo -e "\n=========================================="
echo "  ✓ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО"
echo "=========================================="
echo ""
echo "API: http://$HOST:8000"
echo "Health: http://$HOST:8000/health"
echo "Status: http://$HOST:8000/status"
echo ""
echo "Команды управления:"
echo "  Логи API: ssh $USER@$HOST 'tail -f $PROJECT_DIR/logs/api.log'"
echo "  Systemd логи: ssh $USER@$HOST 'journalctl -u vibe-count-api -f'"
echo "  Перезапуск: ssh $USER@$HOST 'systemctl restart vibe-count-api'"
echo "  Статус: ssh $USER@$HOST 'systemctl status vibe-count-api'"

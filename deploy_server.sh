#!/bin/bash
# Deployment script for Timeweb VPS
set -e

echo "=== Обновление системы ==="
apt update && apt upgrade -y

echo "=== Установка необходимых пакетов ==="
apt install -y python3 python3-pip python3-venv git

echo "=== Клонирование репозитория ==="
cd /root
if [ -d "vibe_count" ]; then
    echo "Репозиторий уже существует, обновляем..."
    cd vibe_count
    git pull
else
    git clone https://github.com/utkabotron/vibe_count.git
    cd vibe_count
fi

echo "=== Создание виртуального окружения ==="
python3 -m venv venv

echo "=== Активация окружения и установка зависимостей ==="
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Создание директорий ==="
mkdir -p logs temp

echo "=== Создание скрипта запуска ==="
cat > run.sh << 'RUNEOF'
#!/bin/bash
cd /root/vibe_count
source venv/bin/activate
python src/main.py >> logs/cron.log 2>&1
RUNEOF

chmod +x run.sh

echo "=== Deployment завершен! ==="
echo ""
echo "Следующие шаги:"
echo "1. Загрузите .env файл с API ключами"
echo "2. Загрузите vibecount-credentials-gsheets.json в директорию проекта"
echo "3. Настройте cron: crontab -e"
echo "   Добавьте: */10 * * * * /root/vibe_count/run.sh"

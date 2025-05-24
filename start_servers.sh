#!/bin/bash

# Скрипт для запуска серверов для тестирования производительности

echo "🚀 Запуск серверов для тестирования производительности..."

# Активируем виртуальное окружение
source venv/bin/activate

# Функция для остановки всех процессов при завершении
cleanup() {
    echo "🛑 Остановка всех серверов..."
    pkill -f "gunicorn"
    pkill -f "nginx"
    exit 0
}

# Настраиваем обработку сигналов
trap cleanup SIGINT SIGTERM

# Создаем директорию для кэша nginx
sudo mkdir -p /tmp/nginx_cache
sudo chmod 777 /tmp/nginx_cache

# 1. Запуск Django приложения через gunicorn на порту 8000
echo "📦 Запуск Django приложения через gunicorn (порт 8000)..."
gunicorn -c gunicorn.conf.py askme_gusev.wsgi &
DJANGO_PID=$!

# 2. Запуск простого WSGI приложения через gunicorn на порту 8081  
echo "📦 Запуск простого WSGI приложения через gunicorn (порт 8081)..."
gunicorn -c gunicorn_simple.conf.py simple_wsgi:application &
SIMPLE_PID=$!

# 3. Запуск nginx с нашей конфигурацией
echo "🌐 Запуск nginx..."
# Проверяем конфигурацию
sudo nginx -t -c $(pwd)/askme_gusev.nginx.conf

if [ $? -eq 0 ]; then
    sudo nginx -c $(pwd)/askme_gusev.nginx.conf
else
    echo "❌ Ошибка в конфигурации nginx"
    kill $DJANGO_PID $SIMPLE_PID
    exit 1
fi

echo "✅ Все серверы запущены!"
echo "📊 Django app: http://localhost:8000"
echo "📊 Simple WSGI: http://localhost:8081" 
echo "📊 Nginx proxy: http://localhost"
echo ""
echo "Нажмите Ctrl+C для остановки всех серверов"

# Ждем сигнала завершения
wait 
#!/bin/bash

echo "🚀 Запуск серверов для тестирования производительности..."

source venv/bin/activate

echo "🛑 Остановка старых процессов..."

sudo fuser -k 80/tcp 2>/dev/null || true
sudo fuser -k 8000/tcp 2>/dev/null || true  
sudo fuser -k 8081/tcp 2>/dev/null || true

sudo pkill -9 -f nginx 2>/dev/null || true

sudo pkill -9 -f "gunicorn.*askme_gusev" 2>/dev/null || true
sudo pkill -9 -f "gunicorn.*simple_wsgi" 2>/dev/null || true
sudo pkill -9 -f "gunicorn" 2>/dev/null || true

sudo rm -f /tmp/gunicorn.pid /tmp/gunicorn_simple.pid 2>/dev/null || true

sleep 3

echo "✅ Старые процессы остановлены"

cleanup() {
    echo "🛑 Остановка всех серверов..."
    pkill -f "gunicorn"
    pkill -f "nginx"
    exit 0
}

trap cleanup SIGINT SIGTERM

sudo mkdir -p /tmp/nginx_cache
sudo chmod 777 /tmp/nginx_cache

echo "📦 Запуск Django приложения через gunicorn (порт 8000)..."
gunicorn -c gunicorn.conf.py askme_gusev.wsgi &
DJANGO_PID=$!

echo "📦 Запуск простого WSGI приложения через gunicorn (порт 8081)..."
gunicorn -c gunicorn_simple.conf.py simple_wsgi:application &
SIMPLE_PID=$!

echo "🌐 Запуск nginx..."
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

wait 
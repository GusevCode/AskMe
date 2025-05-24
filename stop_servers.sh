#!/bin/bash

echo "🛑 Остановка всех серверов..."

echo "🔌 Освобождение портов..."
sudo fuser -k 80/tcp 2>/dev/null || true
sudo fuser -k 8000/tcp 2>/dev/null || true  
sudo fuser -k 8081/tcp 2>/dev/null || true

echo "🌐 Остановка nginx..."
sudo pkill -9 -f nginx 2>/dev/null || true

echo "🐍 Остановка gunicorn..."
sudo pkill -9 -f "gunicorn.*askme_gusev" 2>/dev/null || true
sudo pkill -9 -f "gunicorn.*simple_wsgi" 2>/dev/null || true
sudo pkill -9 -f "gunicorn" 2>/dev/null || true

echo "🗑️ Очистка PID файлов..."
sudo rm -f /tmp/gunicorn.pid /tmp/gunicorn_simple.pid 2>/dev/null || true

echo "🧹 Очистка кэша..."
sudo rm -rf /tmp/nginx_cache/* 2>/dev/null || true

echo "✅ Все серверы остановлены и кэш очищен!"

echo "🔍 Проверка портов..."
if netstat -tlnp 2>/dev/null | grep -E ':(80|8000|8081) ' > /dev/null; then
    echo "⚠️ Некоторые порты все еще заняты:"
    netstat -tlnp 2>/dev/null | grep -E ':(80|8000|8081) '
else
    echo "✅ Все порты свободны"
fi 
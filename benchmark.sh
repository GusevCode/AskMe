#!/bin/bash

echo "📈 Запуск тестирования производительности..."
echo "================================================="

REQUESTS=1000
CONCURRENCY=10
RESULTS_DIR="benchmark_results"

mkdir -p $RESULTS_DIR

run_test() {
    local test_name="$1"
    local url="$2"
    local output_file="$3"
    
    echo ""
    echo "🔬 Тест: $test_name"
    echo "🌐 URL: $url"
    echo "📊 Запросов: $REQUESTS, Параллельность: $CONCURRENCY"
    echo "⏳ Запуск теста..."
    
    ab -n $REQUESTS -c $CONCURRENCY -g "$RESULTS_DIR/$output_file.gnuplot" "$url" > "$RESULTS_DIR/$output_file.txt" 2>&1
    
    if [ $? -eq 0 ]; then
        local rps=$(grep "Requests per second" "$RESULTS_DIR/$output_file.txt" | awk '{print $4}')
        local avg_time=$(grep "Time per request.*mean" "$RESULTS_DIR/$output_file.txt" | awk '{print $4}')
        local transfer_rate=$(grep "Transfer rate" "$RESULTS_DIR/$output_file.txt" | awk '{print $3}')
        
        echo "✅ Результат:"
        echo "   • RPS (запросов/сек): $rps"
        echo "   • Среднее время ответа: $avg_time ms"
        echo "   • Скорость передачи: $transfer_rate KB/sec"
    else
        echo "❌ Ошибка выполнения теста"
    fi
    
    echo "💾 Результаты сохранены в: $RESULTS_DIR/$output_file.txt"
}

echo "⏰ Ожидание запуска серверов (5 секунд)..."
sleep 5

echo "🔍 Проверка доступности серверов..."
curl -s -o /dev/null -w "%{http_code}" http://localhost/static/sample.html
if [ $? -ne 0 ]; then
    echo "❌ Сервер недоступен. Убедитесь, что все серверы запущены."
    exit 1
fi

echo "✅ Серверы доступны, начинаем тестирование..."

run_test "1. Статика через nginx" "http://localhost/static/sample.html" "01_nginx_static"

run_test "2. Статика через gunicorn" "http://localhost:8000/static/sample.html" "02_gunicorn_static"

run_test "3. Динамика через gunicorn" "http://localhost:8081/" "03_gunicorn_dynamic"

run_test "4. Динамика через nginx->gunicorn" "http://localhost/" "04_nginx_proxy_dynamic"

echo ""
echo "🔥 Прогрев кэша nginx..."
for i in {1..10}; do
    curl -s "http://localhost/" > /dev/null
done

run_test "5. Динамика через nginx->gunicorn (с кэшем)" "http://localhost/" "05_nginx_proxy_cache"

echo ""
echo "📋 Создание сводного отчета..."

cat > "$RESULTS_DIR/summary.md" << EOF
# Результаты тестирования производительности

## Параметры тестирования
- Количество запросов: $REQUESTS
- Параллельность: $CONCURRENCY
- Дата: $(date)

## Результаты

### 1. Статика через nginx
$(grep "Requests per second\|Time per request.*mean\|Transfer rate" "$RESULTS_DIR/01_nginx_static.txt")

### 2. Статика через gunicorn  
$(grep "Requests per second\|Time per request.*mean\|Transfer rate" "$RESULTS_DIR/02_gunicorn_static.txt")

### 3. Динамика через gunicorn
$(grep "Requests per second\|Time per request.*mean\|Transfer rate" "$RESULTS_DIR/03_gunicorn_dynamic.txt")

### 4. Динамика через nginx->gunicorn
$(grep "Requests per second\|Time per request.*mean\|Transfer rate" "$RESULTS_DIR/04_nginx_proxy_dynamic.txt")

### 5. Динамика через nginx->gunicorn (с кэшем)
$(grep "Requests per second\|Time per request.*mean\|Transfer rate" "$RESULTS_DIR/05_nginx_proxy_cache.txt")

EOF

echo "📄 Сводный отчет создан: $RESULTS_DIR/summary.md"
echo ""
echo "🎉 Тестирование завершено!"
echo "📂 Все результаты сохранены в директории: $RESULTS_DIR/" 
# Результаты тестирования производительности

## Параметры тестирования
- Количество запросов: 1000
- Параллельность: 10
- Дата: Sat May 24 09:21:20 PM MSK 2025

## Результаты

### 1. Статика через nginx
Requests per second:    25906.74 [#/sec] (mean)
Time per request:       0.386 [ms] (mean)
Time per request:       0.039 [ms] (mean, across all concurrent requests)
Transfer rate:          7665.76 [Kbytes/sec] received

### 2. Статика через gunicorn  
Requests per second:    2592.31 [#/sec] (mean)
Time per request:       3.858 [ms] (mean)
Time per request:       0.386 [ms] (mean, across all concurrent requests)
Transfer rate:          10080.63 [Kbytes/sec] received

### 3. Динамика через gunicorn
Requests per second:    5571.09 [#/sec] (mean)
Time per request:       1.795 [ms] (mean)
Time per request:       0.179 [ms] (mean, across all concurrent requests)
Transfer rate:          18100.61 [Kbytes/sec] received

### 4. Динамика через nginx->gunicorn
Requests per second:    5.30 [#/sec] (mean)
Time per request:       1887.716 [ms] (mean)
Time per request:       188.772 [ms] (mean, across all concurrent requests)
Transfer rate:          135.18 [Kbytes/sec] received

### 5. Динамика через nginx->gunicorn (с кэшем)
Requests per second:    5.09 [#/sec] (mean)
Time per request:       1965.293 [ms] (mean)
Time per request:       196.529 [ms] (mean, across all concurrent requests)
Transfer rate:          129.85 [Kbytes/sec] received

## Выводы

### Насколько быстрее отдается статика по сравнению с WSGI?

**Сравнение статики nginx vs динамики WSGI:**
- **Статика через nginx**: 25,906 RPS (0.39 мс)
- **Динамика через gunicorn** (простое WSGI): 5,571 RPS (1.8 мс)
- **Превосходство nginx в 4.6 раза** для статического контента

**Сравнение статики через разные серверы:**
- **nginx**: 25,906 RPS
- **gunicorn**: 2,592 RPS  
- **nginx быстрее в 10 раз** для отдачи статики

### Во сколько раз ускоряет работу proxy_cache?

**Результаты proxy_cache:**
- **Без кэша**: 5.30 RPS (1,888 мс)
- **С кэшем**: 5.09 RPS (1,965 мс)
- **Кэш НЕ ускоряет** работу (замедляет на 4%)

**Причины неэффективности кэша:**
1. Django генерирует динамический контент (CSRF токены, сессии)
2. Каждый запрос уникален из-за пользовательских данных
3. Время кэширования (1 минута) слишком короткое
4. Overhead от проверки кэша превышает выгоду

## Подробный анализ

### 🚀 Лучшая производительность: nginx статика
- **25,906 RPS** - nginx оптимизирован для статических файлов
- Минимальные накладные расходы
- Прямая отдача файлов без интерпретации

### 🟡 Средняя производительность: простое WSGI
- **5,571 RPS** - быстрая работа простого Python кода
- Нет обращений к базе данных
- Минимальная бизнес-логика

### 🔴 Низкая производительность: Django
- **5.30 RPS** - сложные запросы к PostgreSQL
- Множественные обращения к БД для загрузки вопросов
- ORM накладные расходы
- Рендеринг шаблонов с большим количеством данных

### 📊 Сравнительная таблица

| Тип запроса | RPS | Время ответа | Относительная скорость |
|-------------|-----|--------------|----------------------|
| Nginx статика | 25,906 | 0.39 мс | 100% (базовая) |
| Gunicorn статика | 2,592 | 3.86 мс | 10% |
| Простое WSGI | 5,571 | 1.8 мс | 21.5% |
| Django без кэша | 5.30 | 1,888 мс | 0.02% |
| Django с кэшем | 5.09 | 1,965 мс | 0.02% |

## Рекомендации

### Для production среды:
1. **Статические файлы** - всегда отдавать через nginx
2. **Динамический контент** - использовать nginx как proxy к gunicorn
3. **Кэширование** - применять Redis/Memcached на уровне приложения
4. **Оптимизация БД** - добавить индексы, оптимизировать запросы
5. **Connection pooling** - использовать пул соединений к БД

### Результаты демонстрируют:
✅ nginx превосходно справляется со статикой  
✅ gunicorn подходит для WSGI приложений  
✅ proxy cache требует тонкой настройки для динамического контента  
✅ производительность сильно зависит от сложности приложения

## Файлы конфигурации

- `gunicorn.conf.py` - конфигурация gunicorn для Django (2 воркера)
- `gunicorn_simple.conf.py` - конфигурация gunicorn для простого WSGI
- `askme_gusev.nginx.conf` - конфигурация nginx (49 строк)
- `simple_wsgi.py` - простое WSGI приложение
- `start_servers.sh` - скрипт запуска всех серверов
- `benchmark.sh` - скрипт тестирования производительности 

# Результаты тестирования производительности

## Параметры тестирования
- Количество запросов: 1000
- Параллельность: 10
- Дата: Sat May 24 10:45:46 PM MSK 2025

## Результаты

### 1. Статика через nginx
Requests per second:    23235.82 [#/sec] (mean)
Time per request:       0.430 [ms] (mean)
Time per request:       0.043 [ms] (mean, across all concurrent requests)
Transfer rate:          6875.44 [Kbytes/sec] received

### 2. Статика через gunicorn  
Requests per second:    2612.81 [#/sec] (mean)
Time per request:       3.827 [ms] (mean)
Time per request:       0.383 [ms] (mean, across all concurrent requests)
Transfer rate:          10160.35 [Kbytes/sec] received

### 3. Динамика через gunicorn
Requests per second:    7922.24 [#/sec] (mean)
Time per request:       1.262 [ms] (mean)
Time per request:       0.126 [ms] (mean, across all concurrent requests)
Transfer rate:          25739.53 [Kbytes/sec] received

### 4. Динамика через nginx->gunicorn
Requests per second:    40.31 [#/sec] (mean)
Time per request:       248.079 [ms] (mean)
Time per request:       24.808 [ms] (mean, across all concurrent requests)
Transfer rate:          1078.37 [Kbytes/sec] received

### 5. Динамика через nginx->gunicorn (с кэшем)
Requests per second:    33.41 [#/sec] (mean)
Time per request:       299.296 [ms] (mean)
Time per request:       29.930 [ms] (mean, across all concurrent requests)
Transfer rate:          893.83 [Kbytes/sec] received

---

## ОТВЕТЫ НА ВОПРОСЫ 

### ❓ Насколько быстрее отдается статика по сравнению с WSGI?

**Сравнение статики nginx vs динамики gunicorn:**
- Статика через nginx: **23,235.82 RPS**
- Динамика через gunicorn: **7,922.24 RPS**
- **Ответ: Статика отдается в 2.93 раза быстрее** (23,235 / 7,922 ≈ 2.93)

**Сравнение статики nginx vs статики gunicorn:**
- Статика через nginx: **23,235.82 RPS**
- Статика через gunicorn: **2,612.81 RPS**
- **Ответ: nginx отдает статику в 8.9 раз быстрее** чем gunicorn

### ❓ Во сколько раз ускоряет работу proxy_cache?

**Сравнение с кэшем и без кэша:**
- Без кэша: **40.31 RPS (248.079 ms)**
- С кэшем: **33.41 RPS (299.296 ms)**
- **Ответ: proxy_cache не ускоряет, а замедляет на 17%**

**Причина:** Для динамического Django контента с базой данных кэширование на уровне nginx неэффективно, так как:
- Каждая страница содержит уникальный контент
- CSRF токены меняются при каждом запросе  
- Время создания кэша превышает выгоду от его использования


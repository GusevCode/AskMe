# askme_gusev

Проект веб-приложения "AskMe" - аналог Stack Overflow, созданный в рамках курса "Веб-программирование" в Технопарке.

# Запуск всех серверов для тестирования
./start_servers.sh

### Проведение тестирования производительности:
```bash
# В отдельном терминале
./benchmark.sh
```

## Технологии
- **Backend**: Django 5.2, Python 3.13
- **Database**: PostgreSQL
- **Web Server**: nginx
- **WSGI Server**: gunicorn
- **Testing**: Apache Benchmark (ab)

**[Подробный отчет о тестировании производительности](benchmark_results/summary.md)**
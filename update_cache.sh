#!/bin/bash
# Скрипт для обновления кэша через cron

cd /home/Alexey/Projects/technopark/Web/askme_gusev
source venv/bin/activate
python manage.py update_cache >> /var/log/askme_cache_update.log 2>&1 
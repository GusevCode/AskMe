# Gunicorn configuration file

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Увеличиваем timeout до 2 минут
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "debug"
accesslog = "-"
errorlog = "-"
capture_output = True

# Process naming
proc_name = "askme_gusev"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Memory optimizations
preload_app = True
max_worker_lifetime = 60 * 30  # 30 minutes
graceful_timeout = 60

# SSL (если потребуется в будущем)
# keyfile = None
# certfile = None 
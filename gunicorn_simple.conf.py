# Gunicorn configuration file for simple WSGI app

# Server socket
bind = "127.0.0.1:8081"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "simple_wsgi"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn_simple.pid" 
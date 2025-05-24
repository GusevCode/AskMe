bind = "127.0.0.1:8081"
backlog = 2048

workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

max_requests = 1000
max_requests_jitter = 50

loglevel = "info"
accesslog = "-"
errorlog = "-"

proc_name = "simple_wsgi"

daemon = False
pidfile = "/tmp/gunicorn_simple.pid" 
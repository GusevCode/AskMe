bind = "127.0.0.1:8000"
backlog = 2048

workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

max_requests = 1000
max_requests_jitter = 50

loglevel = "debug"
accesslog = "-"
errorlog = "-"
capture_output = True

proc_name = "askme_gusev"

daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

preload_app = True
max_worker_lifetime = 60 * 30
graceful_timeout = 60
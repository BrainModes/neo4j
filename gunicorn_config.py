from config import get_settings

_settings = get_settings()

workers = _settings.WORKERS
threads = _settings.THREADS
bind = f'{_settings.HOST}:{_settings.PORT}'
daemon = 'false'
worker_connections = _settings.WORKER_CONNECTIONS
accesslog = 'access.log'
errorlog = 'error.log'
loglevel = _settings.LOGLEVEL

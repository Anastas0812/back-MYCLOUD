from .settings_local import *

DEBUG = False

ALLOWED_HOSTS = [
    'домен.ru',
    'www.твой_домен.ru',
    'IP_адрес_сервера',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

SECURE_BROWSER_XSS_FILTER = True
CSRF_TRUSTED_ORIGINS = [
    'https://твой_домен.ru',
]

import os
from .settings_local import *

DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '168.222.142.98',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SECURE_BROWSER_XSS_FILTER = True
CSRF_TRUSTED_ORIGINS = [
    'http://168.222.142.98'
]

CORS_ALLOWED_ORIGINS = [
    'http://168.222.142.98',
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'content-type',
    'x-csrftoken',
]
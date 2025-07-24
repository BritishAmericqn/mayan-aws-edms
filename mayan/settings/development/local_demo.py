"""
Local demo settings for quick research platform demonstration.
Minimal setup to showcase research app without full Mayan complexity.
"""

from mayan.settings.base import *

# Use SQLite for quick demo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'demo.db',
    }
}

# Minimal apps for demo
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # DRF for API demo
    'rest_framework',
    
    # Core Mayan apps needed for research
    'mayan.apps.common',
    'mayan.apps.events',
    'mayan.apps.permissions',
    'mayan.apps.acls',
    'mayan.apps.navigation',
    'mayan.apps.appearance',
    'mayan.apps.documents',
    
    # Our research app
    'mayan.apps.research',
]

# Disable complex middleware for demo
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Demo-friendly settings
DEBUG = True
SECRET_KEY = 'demo-key-not-for-production'
ALLOWED_HOSTS = ['*']

# DRF settings for API demo
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = []

# Disable complex storage for demo
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = BASE_DIR / 'demo_media'
MEDIA_URL = '/media/'

# Disable celery for demo
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True 
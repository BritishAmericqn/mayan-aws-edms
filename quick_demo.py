#!/usr/bin/env python
"""
Standalone research platform demo script.
Shows the research models and admin interface without full Mayan complexity.
"""

import os
import sys
import django
from django.conf import settings

# Minimal Django configuration for demo
DEMO_SETTINGS = {
    'DEBUG': True,
    'SECRET_KEY': 'demo-key-only',
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    'INSTALLED_APPS': [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
    ],
    'MIDDLEWARE': [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ],
    'ROOT_URLCONF': 'quick_demo_urls',
    'STATIC_URL': '/static/',
    'USE_TZ': True,
    'REST_FRAMEWORK': {
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ],
    },
    'TEMPLATES': [{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }],
}

if __name__ == '__main__':
    if not settings.configured:
        settings.configure(**DEMO_SETTINGS)
        django.setup()
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv) 
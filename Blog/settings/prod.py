from . base import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Use sentry for production error handling
sentry_sdk.init(
    dsn=os.environ['sentrydsn'],
    integrations=[DjangoIntegration()],
    send_default_pii=True,  # Associate users with errors
    traces_sample_rate=1.0,
)

DEBUG = False
SECURE_SSL_REDIRECT = True # Redirect all non-HTTPS requests to HTTPS

ALLOWED_HOSTS = ['www.walnutmind.org', 'walnutmind.org']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DBName'],
        'HOST': os.environ['DBHost'],
        'PORT': 5432,
        'USER': os.environ['DBUser'],
        'PASSWORD': os.environ['DBPass'],
    }
}

AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
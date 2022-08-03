import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

# Use sentry for production error handling
sentry_sdk.init(
    dsn=os.environ['sentrydsn'], integrations=[DjangoIntegration()], send_default_pii=True,
    # Associate users with errors
    traces_sample_rate=1.0,

)

ALLOWED_HOSTS = ['www.walnutmind.org', 'walnutmind.org']

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql', 'NAME': os.environ['DBName'],
        'HOST':     os.environ['DBHost'], 'PORT': 5432, 'USER': os.environ['DBUser'],
        'PASSWORD': os.environ['DBPass'],
    }
}

AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']

DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {
    "location": "archives/",
}

DBBACKUP_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DBBACKUP_STORAGE_OPTIONS = {
    'access_key': os.environ['AWS_ACCESS_KEY_ID'],
    'secret_key': os.environ['AWS_SECRET_ACCESS_KEY'],
    'bucket_name': os.environ['AWS_STORAGE_BUCKET_NAME'],
    'default_acl': 'private',
    'location': 'archives/',
}

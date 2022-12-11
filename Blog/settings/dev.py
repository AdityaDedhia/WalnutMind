# Use admin mails instead of sentry for staging error handling.
import sys

from .base import *

ADMINS = [('Aditya Dedhia', 'aditya23dedhia@gmail.com'), ]

ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1', 'www.halflife-edu-dev.herokuapp.com',
                 'halflife-edu-dev.herokuapp.com']

APPEND_SLASH = False
PREPEND_WWW = False
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
DEBUG = True
SECURE_SSL_REDIRECT = False
CORS_REPLACE_HTTPS_REFERER = False
HOST_SCHEME = "http://"
SECURE_HSTS_SECONDS = None
SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': os.environ['DEVDBNAME'],
		'HOST': os.environ['DEVDBHOST'],
		'PORT': 5432,
		'USER': os.environ['DEVDBUSER'],
		'PASSWORD': os.environ['DEVDBPASS'],
		'TEST': {
			'NAME': os.environ['DEVDBNAME'],
		}
	}
}
BROKER_URL = os.environ['CLOUDAMQP_URL']

MIDDLEWARE = MIDDLEWARE + [
	'debug_toolbar.middleware.DebugToolbarMiddleware',  # DEBUG TOOLBAR
]

INSTALLED_APPS = INSTALLED_APPS + [
	'debug_toolbar',
]

AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_TEST_BUCKET_NAME']

INTERNAL_IPS = [  # Debugging IPs
	'127.0.0.1', '146.0.191.120',
]

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_CALLER_ID = os.environ.get('TWILIO_CALLER_ID')

REALEMAIL_API_KEY = os.environ.get('REALEMAIL_API_KEY')
IPINVESTIGATOR_API_KEY = os.environ.get('IPINVESTIGATOR_API_KEY')

# Use admin mails instead of sentry for staging error handling.
import sys

from .base import *

ADMINS = [('Aditya Dedhia', 'aditya23dedhia@gmail.com'), ]

ALLOWED_HOSTS = ['www.halflife-edu-dev.herokuapp.com',
                 'halflife-edu-dev.herokuapp.com']

APPEND_SLASH = True
PREPEND_WWW = True

if 'test' in sys.argv:
	DATABASES = {
		'default': {
			'ENGINE':   'django.db.backends.postgresql', 'NAME': os.environ['TESTDBName'],
			'HOST':     os.environ['TESTDBHost'], 'PORT': 5432, 'USER': os.environ['TESTDBUser'],
			'PASSWORD': os.environ['TESTDBPass'], 'TEST': {
				'NAME': os.environ['TESTDBName']
			}
		}
	}
else:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql',
			'NAME': os.environ['DEVDBName'],
			'HOST': os.environ['DEVDBHost'],
			'PORT': 5432,
			'USER': os.environ['DEVDBUser'],
			'PASSWORD': os.environ['DEVDBPass'],
			'TEST': {
				'NAME': os.environ['TESTDBName']
			}
		}
	}

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

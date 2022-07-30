from .base import *

# Use admin mails instead of sentry for staging error handling.
import sys

ADMINS = [
	('Aditya Dedhia', 'aditya23dedhia@gmail.com'),
]

ALLOWED_HOSTS = ['127.0.0.1', 'www.halflife-edu-dev.herokuapp.com',
                 'halflife-edu-dev.herokuapp.com']

if 'test' in sys.argv:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql',
			'NAME': os.environ['TESTDBName'],
			'HOST': os.environ['TESTDBHost'],
			'PORT': 5432,
			'USER': os.environ['TESTDBUser'],
			'PASSWORD': os.environ['TESTDBPass'],
			'TEST': {
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

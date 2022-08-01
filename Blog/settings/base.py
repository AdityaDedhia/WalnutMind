import os
import dotenv
from pathlib import Path
from django_archive import archivers

BASE_DIR = Path(__file__).resolve().parent.parent.parent

dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
	dotenv.load_dotenv(dotenv_file)
SECRET_KEY = os.environ['SECRET_KEY']
SITE_ID = 1
WSGI_APPLICATION = 'Blog.wsgi.application'
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

HOSTCOUNTRY_CODE = "LU"
DEBUG = False
SECURE_SSL_REDIRECT = True

# ARCHIVE SETTINGS -----------------------------------------------------------manage.py archive
ARCHIVE_DIRECTORY = 'archives/'
ARCHIVE_FILENAME = '%Y-%m-%d--%H-%M'
ARCHIVE_FORMAT = archivers.ZIP

# USER SETTINGS (MODIFIABLE)

PUBS_ACCESS = 2  # ANONYMOUS ACCESS LIMIT BEFORE SIGNIN
BASIC_STORAGE = 104857600 * 2  # MAXIMUM BASIC STORAGE (in bytes)
STANDARD_STORAGE = 104857600 * 50  # MAXIMUM STANDARD STORAGE (in bytes)
PREMIUM_STORAGE = 104857600 * 500  # MAXIMUM PREMIUM STORAGE (in bytes)

PUBS_WIDTH = 1200
PUBS_HEIGHT = 900

HITCOUNT_KEEP_HIT_ACTIVE = {'days': 1}  # HIT COUNT LASTS 1 DAY
HITCOUNT_HITS_PER_IP_LIMIT = 20  # ACTIVE HIT COUNT LIMIT PER IP (ANY 1 DAY)
HITCOUNT_KEEP_HIT_IN_DATABASE = {
	'days': 365}  # if hitcount_cleanup is run, only delete hits older than 1 year.

# DO NOT CHANGE THIS -----------------------------------------------------
CSRF_COOKIE_SECURE = True  # Prevent CSRF cookie from being sent over HTTP
SESSION_COOKIE_SECURE = True  # Prevent session cookie from being sent over HTTP
SECURE_HSTS_SECONDS = 31536000  # Sending of HSTS header 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Sending of HSTS header
SECURE_HSTS_PRELOAD = True  # Sending of HSTS header
SECURE_BROWSER_XSS_FILTER = True  # Prevent cross-site scripting attacks in browsers

SERVER_EMAIL = 'support@walnutmind.org'

# CONFIG SETTINGS ---------------------------------------------------
RESOURCES_LIFESPAN = 60 * 30  # 30 Minute cache

# MFA SETTINGS ---------------------------------------------------
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 172800  # 2 days before login session expires
TWO_FACTOR_REMEMBER_COOKIE_AGE = 172800  # 2 day session window until redo MFA
LOGIN_URL = 'two_factor:login'
LOGIN_REDIRECT_URL = '/'

OTP_EMAIL_SUBJECT = 'Your Walnut Mind MFA Token'
OTP_EMAIL_TOKEN_VALIDITY = 120  # 2 minutes until token expires
OTP_EMAIL_THROTTLE_FACTOR = 10  # 10,20,40,80,160..seconds between emails
OTP_ADMIN_HIDE_SENSITIVE_DATA = True  # Hide sensitive data from staff
TWO_FACTOR_CALL_GATEWAY = 'two_factor.gateways.twilio.gateway.Twilio'
TWO_FACTOR_SMS_GATEWAY = 'two_factor.gateways.twilio.gateway.Twilio'
TWO_FACTOR_PHONE_THROTTLE_FACTOR = 50  # 50,100,200,400,800..seconds between texts/calls

AXES_LOCK_OUT_AT_FAILURE = False
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_COOLOFF_TIME = 120  # 2 minutes
AXES_RESET_ON_SUCCESS = True
AXES_ENABLE_ACCESS_FAILURE_LOG = True

INSTALLED_APPS = [
	'dal',  # BEFORE django.contrib.admin
	'dal_select2',  # BEFORE django.contrib.admin
	'django.contrib.admin',
	'django.contrib.auth',
	'axes',  # AFTER django.contrib.admin
	'django_otp',  # 2FA
	'django_otp.plugins.otp_static',  # 2FA
	'django_otp.plugins.otp_totp',  # 2FA
	'django_otp.plugins.otp_email',  # 2FA
	'two_factor.plugins.email',  # 2FA
	'two_factor.plugins.phonenumber',  # 2FA
	'two_factor',  # 2FA

	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'whitenoise.runserver_nostatic',
	'django.contrib.staticfiles',
	'django_cleanup.apps.CleanupConfig',
	'django.contrib.postgres',
	'django.contrib.sites',
	'django.contrib.sitemaps',
	'django_countries',
	'ckeditor',
	'ckeditor_uploader',
	'django.contrib.humanize',
	'storages',
	'taggit',
	'rest_framework',
	'embed_video',
	'widget_tweaks',
	'hitcount',
	'dbbackup',  # automated S3 db archive
	'django_archive',  # manual archives using: manage.py archive
	'Users',
	'Articles',
	'Commentaries',
	'Diaries',
	'Wiki',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'whitenoise.middleware.WhiteNoiseMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django_otp.middleware.OTPMiddleware',  # AFTER AUTHMIDDLEWARE
	'two_factor.middleware.threadlocals.ThreadLocals',  # AFTER AUTHMIDDLEWARE
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django.middleware.common.BrokenLinkEmailsMiddleware',
	'Blog.middleware.BlacklistBlockMiddleware',
	'axes.middleware.AxesMiddleware',  # AFTER AUTHMIDDLEWARE
]

ROOT_URLCONF = 'Blog.urls'

ADMIN_URL = '&mfHQp04wVAYsorpv9clIsPv0CDq4vEsfB&pdJd^h38T27^A0dsC1UH!54gx8h3dQ7U6p$3QgTyhp8' \
           '!YrS7o9OFsIfl*eZ4dNxqGI$kq/'

#  ANALYTICS
RAYGUN_RUM_APIKEY = 'FCe3U689WU8Bb6WQEQsBlQ'
G_TAG = 'G-4XQDC6FX9D'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, 'templates')],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.template.context_processors.media',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
				'django_settings_export.settings_export',
			],
		},
	},
]

SETTINGS_EXPORT = [
	'ADMIN_URL',
	'RAYGUN_RUM_APIKEY',
	'G_TAG',
]

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]
AUTHENTICATION_BACKENDS = [
	'axes.backends.AxesBackend',
	'django.contrib.auth.backends.ModelBackend',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

TAGGIT_CASE_INSENSITIVE = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# RICH TEXT EDITOR-------------
CKEDITOR_CONFIGS = {
	'default': {
		'skin': 'kama',
		'height': 400,
		'width': 400,
		'toolbarCanCollapse': True,
		'toolbarStartupExpanded': False,
		'tabSpaces': 4,
		'toolbar': 'custom',
		'toolbar_custom': [
			{'name': 'document', 'items': ['Maximize', 'Source', '-', 'Templates']},
			{'name': 'clipboard', 'items': ['Undo', 'Redo']},
			{'name': 'editing', 'items': ['Find', 'Replace']},

			{'name': 'links',
			 'items': ['Link', 'Unlink', 'Anchor']},
			{'name': 'insert',
			 'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'SpecialChar', 'Iframe']},

			{'name': 'paragraph',
			 'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-',
			           'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},

			{'name': 'styles',
			 'items': ['Bold', 'Italic', 'Underline', 'Strike', 'TextColor', 'BGColor',
			           'Subscript', 'Superscript', 'Format', 'Font', 'FontSize', '-',
			           'RemoveFormat']},

		],
		'extraPlugins': ','.join([
			'uploadimage',  # the upload image feature
			# your extra plugins here
			'div',
			'autolink',
			'autoembed',
			'embedsemantic',
			'find',
			'notification',
		]),
		'removePlugins': 'exportpdf',

	},

}

# FILES------------------------------------------------------------

GEOIP_PATH = os.path.join(BASE_DIR, 'geoIP')

STATIC_HOST = os.environ.get('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/static/'

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
	BASE_DIR / "static",
]

MEDIA_URL = '/user_content/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'user_content')

CKEDITOR_UPLOAD_PATH = "uploads/ckeditor/"

AWS_S3_FILE_OVERWRITE = False  # rename files uploaded with same name
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_REGION_NAME = 'us-east-2'
AWS_S3_ADDRESSING_STYLE = 'virtual'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

# SETTINGS NOT WORKING IN PRODUCTION
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
# django_heroku.settings(locals())

# EMAIL FOR USER MANAGEMENT
EMAIL_FROM_USER = 'support@walnutmind.org'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'support@walnutmind.org'
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
DEFAULT_FROM_EMAIL = 'support@walnutmind.org'


def get_cache():
	import os
	try:
		servers = os.environ['MEMCACHIER_SERVERS']
		username = os.environ['MEMCACHIER_USERNAME']
		password = os.environ['MEMCACHIER_PASSWORD']
		return {
			'default': {
				'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
				# TIMEOUT is not the connection timeout! It's the default expiration
				# timeout that should be applied to keys! Setting it to `None`
				# disables expiration.
				'TIMEOUT': None,
				'LOCATION': servers,
				'OPTIONS': {
					'binary': True,
					'username': username,
					'password': password,
					'behaviors': {
						# Enable faster IO
						'no_block': True,
						'tcp_nodelay': True,
						# Keep connection alive
						'tcp_keepalive': True,
						# Timeout settings
						'connect_timeout': 2000,  # ms
						'send_timeout': 750 * 1000,  # us
						'receive_timeout': 750 * 1000,  # us
						'_poll_timeout': 2000,  # ms
						# Better failover
						'ketama': True,
						'remove_failed': 1,
						'retry_timeout': 2,
						'dead_timeout': 30,
					}
				}
			}
		}
	except:
		return {
			'default': {
				'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
			}
		}


CACHES = get_cache()

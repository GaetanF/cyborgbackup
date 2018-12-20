"""
Django settings for cyborgbackup project.

Generated by 'django-admin startproject' using Django 1.11.15.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import urllib.parse
from datetime import timedelta
from celery.schedules import crontab
from kombu import Queue, Exchange
from kombu.common import Broadcast

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JOBOUTPUT_ROOT = os.path.join(BASE_DIR, 'job_output')

SCRIPTS_DIR = os.path.join(BASE_DIR, 'cyborgbackup', 'scripts')
PROVIDER_DIR = os.path.join(BASE_DIR, 'cyborgbackup', 'provider')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
try:
    SECRET_KEY
except NameError:
    SECRET_FILE = os.path.join(BASE_DIR, 'secret.txt')
    try:
        SECRET_KEY = open(SECRET_FILE).read().strip()
    except IOError:
        try:
            import random
            choices = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            SECRET_KEY = ''.join([random.SystemRandom().choice(choices) for i in range(50)])
            secret = open(SECRET_FILE, 'w')
            secret.write(SECRET_KEY)
            secret.close()
        except IOError:
            Exception('Please create a %s file with random characters \
            to generate your secret key!' % SECRET_FILE)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
SQL_DEBUG = False

ALLOWED_HOSTS = ['web', 'localhost', '127.0.0.1', '::1', '*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'rest_framework',
    'rest_framework.authtoken',
    'channels',
    'cyborgbackup.ui',
    'cyborgbackup.api',
    'cyborgbackup.main'
]

BROKER_URL = "amqp://{}:{}@{}/{}".format(os.environ.get("RABBITMQ_DEFAULT_USER", "cyborgbackup"),
                                         os.environ.get("RABBITMQ_DEFAULT_PASS", "cyborgbackup"),
                                         os.environ.get("RABBITMQ_HOST", "rabbitmq"),
                                         urllib.parse.quote(
                                             os.environ.get(
                                                 "RABBITMQ_DEFAULT_VHOST",
                                                 "cyborgbackup"),
                                             safe=''
                                         ))

CHANNEL_LAYERS = {
    'default': {'BACKEND': 'asgi_amqp.AMQPChannelLayer',
                'ROUTING': 'cyborgbackup.main.routing.channel_routing',
                'CONFIG': {'url': BROKER_URL}}
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
]

ROOT_URLCONF = 'cyborgbackup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'cyborgbackup/templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cyborgbackup.wsgi.application'

ASGI_APPLICATION = 'cyborgbackup.routing.application'

ASGI_AMQP = {
    'INIT_FUNC': 'cyborgbackup.prepare_env',
    'MODEL': 'cyborgbackup.main.models.channels.ChannelGroup',
}


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_NAME', 'cyborgbackup'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', 5432),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'cyborgbackup.api.pagination.Pagination',
    'PAGE_SIZE': 25,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'cyborgbackup.api.authentication.SessionAuthentication',
        'cyborgbackup.api.authentication.LoggedBasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'cyborgbackup.api.permissions.ModelAccessPermission',
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'cyborgbackup.api.filters.TypeFilterBackend',
        'cyborgbackup.api.filters.FieldLookupBackend',
        'rest_framework.filters.SearchFilter',
        'cyborgbackup.api.filters.OrderByBackend',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'cyborgbackup.api.parsers.JSONParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'cyborgbackup.api.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_METADATA_CLASS': 'cyborgbackup.api.metadata.Metadata',
    'EXCEPTION_HANDLER': 'cyborgbackup.api.views.api_exception_handler',
    'VIEW_NAME_FUNCTION': 'cyborgbackup.api.generics.get_view_name',
    'VIEW_DESCRIPTION_FUNCTION': 'cyborgbackup.api.generics.get_view_description',
    'NON_FIELD_ERRORS_KEY': '__all__',
    'DEFAULT_VERSION': 'v1',
    # 'URL_FORMAT_OVERRIDE': None,
}

# Absolute filesystem path to the directory to store logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)-8s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            '()': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'rest_framework.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'cyborgbackup': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
# LOGGING['handlers']['console']['()'] = 'cyborgbackup.main.utils.handlers.ColorHandler'
LOGGING['handlers']['console'] = {
    '()': 'logging.StreamHandler',
    'level': 'DEBUG',
    'formatter': 'simple',
}


AUTH_USER_MODEL = 'main.User'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'cyborgbackup', 'static'),
    os.path.join(BASE_DIR, 'cyborgbackup', 'ui', 'static'),
)

STATIC_URL = '/static/'

NAMED_URL_GRAPH = {}

PERSISTENT_CALLBACK_MESSAGES = True
USE_CALLBACK_QUEUE = True
CALLBACK_QUEUE = "callback_tasks"

IGNORE_CELERY_INSPECTOR = True
CELERY_RDBSIG = 1
CELERY_ALWAYS_EAGER = True
CELERY_BROKER_URL = BROKER_URL
CELERY_BROKER_POOL_LIMIT = None
CELERY_EVENT_QUEUE_TTL = 5
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TRACK_STARTED = True
CELERYD_TASK_TIME_LIMIT = None
CELERYD_TASK_SOFT_TIME_LIMIT = None
CELERYD_POOL_RESTARTS = True
CELERY_RESULT_BACKEND = 'django-db'
CELERY_IMPORTS = ('cyborgbackup.main.utils.tasks', 'cyborgbackup.main.tasks')
CELERY_QUEUES = (
    Queue('cyborgbackup', Exchange('cyborgbackup'), routing_key='cyborgbackup'),
    Broadcast('cyborgbackup_broadcast_all')
)
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_ROUTES = {}
CELERY_BEAT_SCHEDULER = 'celery.beat.PersistentScheduler'
CELERY_BEAT_SCHEDULE_FILENAME = os.path.join(
    BASE_DIR,
    '..',
    '..',
    'var',
    'run',
    'celerybeat-schedule')
CELERY_BEAT_MAX_LOOP_INTERVAL = 60
CELERY_BEAT_SCHEDULE = {
    'cyborgbackup_notify_daily': {
        'task': 'cyborgbackup.main.tasks.cyborgbackup_notifier',
        'schedule': crontab(minute='0', hour='*'),
        'args': ('daily',)
    },
    'cyborgbackup_notify_weekly': {
        'task': 'cyborgbackup.main.tasks.cyborgbackup_notifier',
        'schedule': crontab(hour=0, minute=0, day_of_week=6),
        'args': ('weekly',)
    },
    'cyborgbackup_notify_monthly': {
        'task': 'cyborgbackup.main.tasks.cyborgbackup_notifier',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),
        'args': ('monthly',)
    },
    'cyborgbackup_scheduler': {
        'task': 'cyborgbackup.main.tasks.cyborgbackup_periodic_scheduler',
        'schedule': timedelta(seconds=30),
        'options': {'expires': 20}
    },
    'cyborgbackup_compute_Size': {
        'task': 'cyborgbackup.main.tasks.compute_borg_size',
        'schedule': timedelta(seconds=10),
        'options': {'expires': 20}
    },
    'cyborgbackup_prune_catalog': {
        'task': 'cyborgbackup.main.tasks.prune_catalog',
        'schedule': timedelta(seconds=30),
        'options': {'expires': 20}
    },
    'task_manager': {
        'task': 'cyborgbackup.main.utils.tasks.run_task_manager',
        'schedule': timedelta(seconds=20),
        'options': {'expires': 20}
    },
}

ACTIVITY_STREAM_ENABLED = False

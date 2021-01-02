import psycopg2.extensions

APP_MOUNTDIR = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'NAME': 'ats',
        'USER': 'webapp',
        'PASSWORD': 'password'
    },
    'serial': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'NAME': 'ats',
        'USER': 'webapp',
        'PASSWORD': 'password',
        'OPTIONS': {
            'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE
        }
    }
}

LOGIN_REDIRECT_URL = "%s/ats/top/" % APP_MOUNTDIR
LOGIN_URL = "%s/ats/login/" % APP_MOUNTDIR
LOGOUT_URL = "%s/ats/logout/" % APP_MOUNTDIR

MY_LOG_LEVEL = 'DEBUG'
MY_LOG_PATH = '%s/%s/ats.log' % (os.getenv('HOME'), 'log')

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
        'verbose': {
            'format': '%(asctime)s,%(levelname)-8s,%(module)s,L%(lineno)s,%(message)s',
        },
        'simple': {
            'format': '%(asctime)s,%(levelname)-8s,%(message)s',
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': MY_LOG_PATH,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'ats': {
            'handlers': ['file'],
            'level': MY_LOG_LEVEL,
            'propagate': False,
        },
    },
}

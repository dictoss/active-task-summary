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

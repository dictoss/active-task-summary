APP_MOUNTDIR = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'NAME': 'ats',
        'USER': 'webapp',
        'PASSWORD': 'password'
    }
}

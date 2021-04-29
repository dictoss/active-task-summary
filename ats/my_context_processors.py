from django.apps import apps


ats_settings = apps.get_app_config('ats')


def app_info(request):

    return {'app_info': {
        'name': ats_settings.name,
        'longname': ats_settings.verbose_name,
        'auther': ats_settings.APP_AUTHER,
        'version': ats_settings.APP_VERSION,
        }
    }


def is_lastname_front(request):
    return {'is_lastname_front': ats_settings.ATS_IS_LASTNAME_FRONT}

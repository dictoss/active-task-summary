
from ats import ats_settings


def app_info(request):
    return {'app_info': {
        'name': ats_settings.APP_NAME,
        'longname': ats_settings.APP_LONGNAME,
        'auther': ats_settings.APP_AUTHER,
        'version': ats_settings.APP_VERSION,
        }
    }


def is_lastname_front(request):
    return {'is_lastname_front': ats_settings.ATS_IS_LASTNAME_FRONT}

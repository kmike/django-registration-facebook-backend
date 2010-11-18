from django.conf import settings

FACEBOOK_APP_ID = settings.FACEBOOK_APP_ID
FACEBOOK_API_KEY = settings.FACEBOOK_API_KEY
FACEBOOK_SECRET_KEY = settings.FACEBOOK_SECRET_KEY
FACEBOOK_REQUIRED_FIELDS = getattr(settings, 'FACEBOOK_REQUIRED_FIELDS', [])
REGISTRATION_OPEN = getattr(settings, 'REGISTRATION_OPEN', True)
FACEBOOK_POST_REGISTRATION_REDIRECT = getattr(
    settings, 'FACEBOOK_POST_REGISTRATION_REDIRECT',
    getattr(settings, 'LOGIN_REDIRECT_URL', '/')
)

FACEBOOK_AUTH_BACKEND = getattr(settings, 'FACEBOOK_AUTH_BACKEND',
                                'facebook_connect.FacebookConnectBackend')

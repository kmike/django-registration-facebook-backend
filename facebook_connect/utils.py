import facebook
from facebook_connect.settings import FACEBOOK_APP_ID, FACEBOOK_SECRET_KEY

def get_facebook_user(request):
    return facebook.get_user_from_cookie(
        request.COOKIES,
        FACEBOOK_APP_ID,
        FACEBOOK_SECRET_KEY
    )

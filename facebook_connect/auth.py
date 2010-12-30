from django.contrib.auth.models import User
from facebook_connect.models import FacebookProfile

class FacebookBackend(object):

    supports_object_permissions = False
    supports_inactive_user = False
    supports_anonymous_user = False

    def authenticate(self, facebook_uid=None):
        try:
            return FacebookProfile.objects.get(uid=facebook_uid).user
        except:
            return None

    def get_user(self, user_id=None):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None

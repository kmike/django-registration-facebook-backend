from django.forms import Form
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import AnonymousUser, User
from django.db.models import Q

from registration import signals
import facebook

from facebook_connect.models import FacebookProfile
import facebook_connect.settings

class FacebookConnectBackend(object):

    def register(self, request, **kwargs):
        params = facebook.get_user_from_cookie(
            request.COOKIES,
            facebook_connect.settings.FACEBOOK_APP_ID,
            facebook_connect.settings.FACEBOOK_SECRET_KEY
        )
        if params:
            uid = params['uid']
            try:
                profile = FacebookProfile.objects.get(uid=uid)
            except FacebookProfile.DoesNotExist:
                profile = self.create_facebook_profile(uid, params)
                # Should we redirect here, or return False and
                # redirect in post_registration_redirect?
                if not profile:
                    return False

            user_obj = profile.user

            signals.user_registered.send(
                sender=self.__class__,
                user=user_obj,
                request=request
            )

            user = authenticate(uid=uid)
            login(request, user)
        elif request.user.is_authenticated():
            user_obj = request.user
        else:
            # Perhaps we should handle this differently?
            user_obj = AnonymousUser()
        return user_obj

    def create_facebook_profile(self, uid, params):
        # Check that the username is unique, and if so, create a user and profile
        try:
            existing_user = User.objects.get(username=uid)
            return False
        except User.DoesNotExist:
            user_obj = User.objects.create_user(
                username=uid,
                email='',
                password=User.objects.make_random_password(16)
            )
            return FacebookProfile.objects.create(user=user_obj, uid=uid)

    def registration_allowed(self, request):
        return facebook_connect.settings.REGISTRATION_OPEN

    def get_form_class(self, request):
        # Pass back an empty instance of the form class, because we are not using a registration form.
        return Form

    def post_registration_redirect(self, request, user):
        if user is False:
            redirect_url = '/'
        else:
            redirect_url = facebook_connect.settings.FACEBOOK_POST_REGISTRATION_REDIRECT
        return (redirect_url, (), {})

    def activate(self, request):
        return NotImplementedError

    def post_activation_redirect(self, request, user):
        return NotImplementedError


class FacebookConnectEmailBackend(FacebookConnectBackend):

    def get_user_data(self, params):
        # retrieve additional user info via facebook graph api
        api = facebook.GraphAPI(params['access_token'])
        try:
            data = api.get_object('me')
            # prevent fake email accounts creation
            if len(data.get('email', '')) > 75:
                data['email'] = None
            return data
        except facebook.GraphAPIError:
            return {'email': None}


    def create_facebook_profile(self, uid, params):
        # Check that the username and email is unique,
        # and if so, create a user and profile
        assert 'email' in facebook_connect.settings.FACEBOOK_REQUIRED_FIELDS
        user_data = self.get_user_data(params)
        email = user_data['email']
        try:
            existing_user = User.objects.get(Q(username=uid) or Q(email=email))
            return False
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=uid,
                email=email,
                password=User.objects.make_random_password(16)
            )
            user.first_name = user_data.get('first_name', '')
            user.last_name = user_data.get('last_name', '')
            user.save()
            return FacebookProfile.objects.create(user=user, uid=uid)

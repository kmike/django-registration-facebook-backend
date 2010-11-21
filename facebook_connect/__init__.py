from django.forms import Form
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import AnonymousUser, User
from django.db.models import Q

import facebook
from registration import signals

from facebook_connect.models import FacebookProfile
from facebook_connect.utils import get_facebook_user
import facebook_connect.settings

class FacebookConnectBackend(object):
    _existing_user = None
    def register(self, request, **kwargs):
        params = get_facebook_user(request)
        if params:
            uid = params['uid']
            try:
                profile = FacebookProfile.objects.get(uid=uid)
            except FacebookProfile.DoesNotExist:
                if request.user.is_authenticated():
                    # just create a profile
                    profile = FacebookProfile.objects.create(user=request.user, uid=uid)
                else:
                    # perform additional checks and optionally create django user
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

            user = authenticate(facebook_uid=uid)
            login(request, user)
        elif request.user.is_authenticated():
            user_obj = request.user
        else:
            # Perhaps we should handle this differently?
            user_obj = AnonymousUser()
        return user_obj

    def create_facebook_profile(self, uid, params):
        # Check that the username is unique, and if so, create a user
        # and profile. Should set _existing_user attribute if there is an
        # existing user.
        try:
            self._existing_user = User.objects.get(username=uid)
            return False
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=uid,
                email='',
                password=User.objects.make_random_password(16)
            )
            return FacebookProfile.objects.create(user=user, uid=uid)

    def registration_allowed(self, request):
        return facebook_connect.settings.REGISTRATION_OPEN

    def get_form_class(self, request):
        # Pass back an empty instance of the form class, because we are not using a registration form.
        return Form

    def post_registration_redirect(self, request, user):
        if user is False:
            if self._existing_user is not None:
                return self.associate_redirect(request)
            redirect_url = '/'
        else:
            redirect_url = facebook_connect.settings.FACEBOOK_POST_REGISTRATION_REDIRECT
        return (redirect_url, (), {})

    def associate_redirect(self, request):
        return ('facebook_associate', [self._existing_user.username], {})

    def activate(self, request):
        return NotImplementedError

    def post_activation_redirect(self, request, user):
        return NotImplementedError


class FacebookConnectEmailBackend(FacebookConnectBackend):
    """ Facebook backend that should be used together with
    some email authentication backend. Email is considered required
    and unique.
    """

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

        # If there is no facebook email available then user must login first
        if not email:
            self._existing_user = AnonymousUser()
            return False

        try:
            self._existing_user = User.objects.get(Q(username=uid) | Q(email=email))
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

    def associate_redirect(self, request):
        if self._existing_user.is_anonymous():
            return ('facebook_email_associate', [], {})
        return super(FacebookConnectEmailBackend, self).associate_redirect(request)


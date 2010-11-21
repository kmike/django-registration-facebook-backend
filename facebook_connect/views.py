import hashlib
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.simple import direct_to_template
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect

from registration.backends import get_backend

import facebook_connect.settings
from facebook_connect.forms import LoginForm, EmailAuthenticationForm

def _associate(request):
    backend = get_backend(facebook_connect.settings.FACEBOOK_AUTH_BACKEND)
#    import ipdb; ipdb.set_trace()
    new_user = backend.register(request)
    to, args, kwargs = backend.post_registration_redirect(request, new_user)
    return redirect(to, *args, **kwargs)

@csrf_protect
def facebook_associate(request, username,
                       template_name='facebook_connect/associate.html'):
    """ Login user and then try to associate facebook account again """

    form = LoginForm(request, request.POST or None,
                     initial={'username': username })
    if form.is_valid():
        login(request, form.get_user())
        return _associate(request)
    return direct_to_template(request, template_name, {'form': form})

@csrf_protect
def facebook_email_associate(request, template_name='facebook_connect/email_associate.html'):
    """ Login user via email and then try to associate facebook account """

    form = EmailAuthenticationForm(request, request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return _associate(request)
    return direct_to_template(request, template_name, {'form': form})


def facebook_login(request):
    params = _verify_signature(request.COOKIES)
    if params:
        user = authenticate(facebook_uid=params['user'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(settings.LOGIN_REDIRECT_URL, {}, ())
            else:
                # Disabled account, redirect and notify?
                return redirect('/', {}, ())
        else:
            # Invalid user, redirect and notify?
            return redirect('/', {}, ())
    elif request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL, {}, ())
    else:
        return redirect('/', {}, ())


def _verify_signature(cookies):
    api_key = facebook_connect.settings.FACEBOOK_API_KEY
    key_prefix = api_key + '_'
    params = dict()
    signature = ''

    for key in sorted(cookies):
        if key.startswith(key_prefix):
            k = key.replace(key_prefix, '')
            v = cookies[key]
            params[k] = v
            signature += '%s=%s' % (k, v)

    hashed = hashlib.md5(signature)
    hashed.update(facebook_connect.settings.FACEBOOK_SECRET_KEY)

    if hashed.hexdigest() == cookies.get(api_key, ''):
        return params
    else:
        return False

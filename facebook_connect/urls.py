from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from registration.views import register
from facebook_connect.settings import FACEBOOK_AUTH_BACKEND

urlpatterns = patterns('',
    url(r'^register/$',
        register,
        { 'backend': FACEBOOK_AUTH_BACKEND },
        name='facebook_register'),
    url(r'^facebook/xd_receiver.html$',
        'django.views.generic.simple.direct_to_template',
        { 'template':'facebook_connect/xd_receiver.html' },
        name='facebook_xd_receiver'),
    url(r'^login/$',
        'facebook_connect.views.facebook_login',
        name='facebook_login'),
)

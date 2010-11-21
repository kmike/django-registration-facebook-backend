from django.conf.urls.defaults import *
from registration.views import register, activate
from facebook_connect.settings import FACEBOOK_AUTH_BACKEND
from facebook_connect.views import facebook_associate, facebook_email_associate

urlpatterns = patterns('',
    url(r'^register/$',
        register,
        { 'backend': FACEBOOK_AUTH_BACKEND },
        name='facebook_register'),
    url(r'^associate/$',
        facebook_email_associate,
        name='facebook_email_associate'),
    url(r'^associate/(?P<username>[\w.@+-]+)/$',
        facebook_associate,
        name='facebook_associate'),
    url(r'^facebook/xd_receiver.html$',
        'django.views.generic.simple.direct_to_template',
        { 'template':'facebook_connect/xd_receiver.html' },
        name='facebook_xd_receiver'),
    url(r'^login/$',
        'facebook_connect.views.facebook_login',
        name='facebook_login'),
)

from django import template
from facebook_connect import settings

register = template.Library()

@register.inclusion_tag('facebook_connect/facebook_javascript.html')
def facebook_javascript():
    return {
        'facebook_api_key': settings.FACEBOOK_API_KEY,
        'facebook_app_id': settings.FACEBOOK_APP_ID,
        'facebook_required_fields': settings.FACEBOOK_REQUIRED_FIELDS
    }

@register.inclusion_tag('facebook_connect/facebook_register.html')
def facebook_register():
    return {}

@register.inclusion_tag('facebook_connect/facebook_login.html')
def facebook_login():
    return {}

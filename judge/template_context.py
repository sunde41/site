from functools import partial

from django.conf import settings
from django.contrib.auth.context_processors import PermWrapper
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.utils.functional import SimpleLazyObject, new_method_proxy

from judge.utils.caniuse import CanIUse, SUPPORT
from .models import Profile


class FixedSimpleLazyObject(SimpleLazyObject):
    if not hasattr(SimpleLazyObject, '__iter__'):
        __iter__ = new_method_proxy(iter)


def get_resource(request):
    use_https = getattr(settings, 'DMOJ_SSL', 0)
    if use_https == 1:
        scheme = 'https' if request.is_secure() else 'http'
    elif use_https > 1:
        scheme = 'https'
    else:
        scheme = 'http'
    return {
        'PYGMENT_THEME': getattr(settings, 'PYGMENT_THEME', None),
        'INLINE_JQUERY': getattr(settings, 'INLINE_JQUERY', True),
        'INLINE_FONTAWESOME': getattr(settings, 'INLINE_FONTAWESOME', True),
        'JQUERY_JS': getattr(settings, 'JQUERY_JS', '//ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'),
        'SCHEME': scheme,
        'CANONICAL': getattr(settings, 'CANONICAL', ''),
    }


def get_profile(request):
    if request.user.is_authenticated:
        return Profile.objects.get_or_create(user=request.user)[0]
    return None


def comet_location(request):
    if request.is_secure():
        websocket = getattr(settings, 'EVENT_DAEMON_GET_SSL', settings.EVENT_DAEMON_GET)
        poll = getattr(settings, 'EVENT_DAEMON_POLL_SSL', settings.EVENT_DAEMON_POLL)
    else:
        websocket = settings.EVENT_DAEMON_GET
        poll = settings.EVENT_DAEMON_POLL
    return {'EVENT_DAEMON_LOCATION': websocket,
            'EVENT_DAEMON_POLL_LOCATION': poll}



def general_info(request):
    path = request.get_full_path()
    return {
        'LOGIN_RETURN_PATH': '' if path.startswith('/accounts/') else path,
        'perms': PermWrapper(request.user),
    }


def site(request):
    return {'site': get_current_site(request)}


def site_name(request):
    return {'SITE_NAME': getattr(settings, 'SITE_NAME', 'DMOJ'),
            'SITE_LONG_NAME': getattr(settings, 'SITE_LONG_NAME', getattr(settings, 'SITE_NAME', 'DMOJ')),
            'SITE_ADMIN_EMAIL': getattr(settings, 'SITE_ADMIN_EMAIL', False)}


def math_setting(request):
    caniuse = CanIUse(request.META.get('HTTP_USER_AGENT', ''))
    engine = 'mml' if bool(getattr(settings, 'MATHOID_URL', False)) and caniuse.mathml == SUPPORT else 'jax'
    return {'MATH_ENGINE': engine, 'REQUIRE_JAX': engine == 'jax', 'caniuse': caniuse}

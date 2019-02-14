from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django_social_share.templatetags.social_share import post_to_gplus_url, post_to_twitter_url, post_to_facebook_url

from . import registry


def make_func(name, template, url_func):
    def func(request, *args):
        link_text = args[-1]
        context = {'request': request, 'link_text': mark_safe(link_text)}
        context = url_func(context, *args[:-1])
        return mark_safe(get_template(template).render(context))

    func.__name__ = name
    registry.function(name, func)


for name, template, url_func in SHARES:
    make_func(name, template, url_func)


@registry.function
def recaptcha_init(language=None):
    return get_template('snowpenguin/recaptcha/recaptcha_init.html').render({'explicit': False, 'language': language})

# -*- coding: utf-8 -*-

import itertools
import json

from django.utils.http import urlquote
from jinja2.ext import Extension
from statici18n.templatetags.statici18n import inlinei18n

from judge.highlight_code import highlight_code
from judge.user_translations import ugettext
from . import (datetime, filesize, language, markdown, rating, reference, render,
               spaceless, submission, timedelta)
from . import registry

registry.function('str', unicode)
registry.filter('str', unicode)
registry.filter('json', json.dumps)
registry.filter('highlight', highlight_code)
registry.filter('urlquote', urlquote)
registry.filter('roundfloat', round)
registry.function('inlinei18n', inlinei18n)
registry.function('user_trans', ugettext)


@registry.function
def counter(start=1):
    return itertools.count(start).next


class DMOJExtension(Extension):
    def __init__(self, env):
        super(DMOJExtension, self).__init__(env)
        env.globals.update(registry.globals)
        env.filters.update(registry.filters)
        env.tests.update(registry.tests)

# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.db import DatabaseError
from django.utils.translation import ugettext_lazy


class JudgeAppConfig(AppConfig):
    name = 'judge'
    verbose_name = ugettext_lazy('Online Judge')

    def ready(self):
        # WARNING: AS THIS IS NOT A FUNCTIONAL PROGRAMMING LANGUAGE,
        #          OPERATIONS MAY HAVE SIDE EFFECTS.
        #          DO NOT REMOVE THINKING THE IMPORT IS UNUSED.
        # noinspection PyUnresolvedReferences
        from . import signals, jinja2

        from judge.models import Language, Profile
        from django.contrib.auth.models import User

        try:
            lang = Language.get_python2()
            for user in User.objects.filter(profile=None):
                # These poor profileless users
                profile = Profile(user=user, language=lang)
                profile.save()
        except DatabaseError:
            pass

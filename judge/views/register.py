# -*- coding: utf-8 -*-

import re

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import get_default_password_validators
from django.forms import CharField, ChoiceField, ModelChoiceField
from django.shortcuts import render
from django.utils.translation import ugettext, ugettext_lazy as _
from registration.backends.default.views import (RegistrationView as OldRegistrationView,
                                                 ActivationView as OldActivationView)
from registration.forms import RegistrationForm
from sortedm2m.forms import SortedMultipleChoiceField

from judge.models import Profile, Language, TIMEZONE
from judge.widgets import Select2Widget, Select2MultipleWidget

valid_id = re.compile(r'^\w+$')
bad_mail_regex = map(re.compile, getattr(settings, 'BAD_MAIL_PROVIDER_REGEX', ()))


class CustomRegistrationForm(RegistrationForm):
    username = forms.RegexField(regex=r'^\w+$', max_length=30, label=_('Username'),
                                error_messages={'invalid': _('A username must contain letters, '
                                                             'numbers, or underscores')})
    display_name = CharField(max_length=50, required=False, label=_('Real name (optional)'))
    language = ModelChoiceField(queryset=Language.objects.all(), label=_('Preferred language'), empty_label=None,
                                widget=Select2Widget(attrs={'style': 'width:100%'}))

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError(ugettext(u'The email address "%s" is already taken. Only one registration '
                                                 u'is allowed per address.') % self.cleaned_data['email'])
        if '@' in self.cleaned_data['email']:
            domain = self.cleaned_data['email'].split('@')[-1].lower()
            if (domain in getattr(settings, 'BAD_MAIL_PROVIDERS', ())
                    or any(regex.match(domain) for regex in bad_mail_regex)):
                raise forms.ValidationError(ugettext(u'Your email provider is not allowed due to history of abuse. '
                                                     u'Please use a reputable email provider.'))
        return self.cleaned_data['email']


class RegistrationView(OldRegistrationView):
    title = _('Registration')
    form_class = CustomRegistrationForm
    template_name = 'registration/registration_form.html'

    def get_context_data(self, **kwargs):
        if 'title' not in kwargs:
            kwargs['title'] = self.title
        kwargs['password_validators'] = get_default_password_validators()
        kwargs['tos_url'] = getattr(settings, 'TERMS_OF_SERVICE_URL', None)
        return super(RegistrationView, self).get_context_data(**kwargs)

    def register(self, form):
        user = super(RegistrationView, self).register(form)
        profile, _ = Profile.objects.get_or_create(user=user, defaults={
            'language': Language.get_python2()
        })

        cleaned_data = form.cleaned_data
        profile.name = cleaned_data['display_name']
        profile.language = cleaned_data['language']
        profile.save()

        return user

    def get_initial(self, *args, **kwargs):
        initial = super(RegistrationView, self).get_initial(*args, **kwargs)
        initial['timezone'] = getattr(settings, 'DEFAULT_USER_TIME_ZONE', 'Asia/Seoul')
        initial['language'] = Language.objects.get(key=getattr(settings, 'DEFAULT_USER_LANGUAGE', 'PY2'))
        return initial


class ActivationView(OldActivationView):
    title = _('Registration')
    template_name = 'registration/activate.html'

    def get_context_data(self, **kwargs):
        if 'title' not in kwargs:
            kwargs['title'] = self.title
        return super(ActivationView, self).get_context_data(**kwargs)
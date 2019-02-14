from operator import attrgetter

import pyotp
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Q
from django.forms import ModelForm, CharField, TextInput, Form
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from django_ace import AceWidget
from judge.models import Profile, Submission, PrivateMessage, Language
from judge.widgets import MathJaxPagedownWidget, HeavyPreviewPageDownWidget, PagedownWidget, \
    Select2Widget, Select2MultipleWidget


def fix_unicode(string, unsafe=tuple(u'\u202a\u202b\u202d\u202e')):
    return string + (sum(k in unsafe for k in string) - string.count(u'\u202c')) * u'\u202c'


class ProfileForm(ModelForm):
    test_site = forms.BooleanField(label=_('Enable experimental features'), initial=False, required=False)

    class Meta:
        model = Profile
        fields = ['name', 'about', 'timezone', 'language', 'ace_theme', 'user_script']
        widgets = {
            'name': TextInput(attrs={'style': 'width:100%;box-sizing:border-box'}),
            'user_script': AceWidget(theme='github'),
            'timezone': Select2Widget(attrs={'style': 'width:200px'}),
            'language': Select2Widget(attrs={'style': 'width:200px'}),
            'ace_theme': Select2Widget(attrs={'style': 'width:200px'}),
        }

        has_math_config = bool(getattr(settings, 'MATHOID_URL', False))
        if has_math_config:
            fields.append('math_engine')
            widgets['math_engine'] = Select2Widget(attrs={'style': 'width:200px'})

        if HeavyPreviewPageDownWidget is not None:
            widgets['about'] = HeavyPreviewPageDownWidget(
                preview=reverse_lazy('profile_preview'),
                attrs={'style': 'max-width:700px;min-width:700px;width:700px'}
            )


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        return fix_unicode(self.cleaned_data['name'] or '')


class ProblemSubmitForm(ModelForm):
    source = CharField(max_length=65536, widget=AceWidget(theme='twilight', no_ace_media=True))

    def __init__(self, *args, **kwargs):
        super(ProblemSubmitForm, self).__init__(*args, **kwargs)
        self.fields['problem'].empty_label = None
        self.fields['problem'].widget = forms.HiddenInput()
        self.fields['language'].empty_label = None
        self.fields['language'].label_from_instance = attrgetter('display_name')
        self.fields['language'].queryset = Language.objects.filter(judges__online=True).distinct()

    class Meta:
        model = Submission
        fields = ['problem', 'source', 'language']


class NewMessageForm(ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ['title', 'content']
        widgets = {}
        if PagedownWidget is not None:
            widgets['content'] = MathJaxPagedownWidget()


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': _('Username')})
        self.fields['password'].widget.attrs.update({'placeholder': _('Password')})


class NoAutoCompleteCharField(forms.CharField):
    def widget_attrs(self, widget):
        attrs = super(NoAutoCompleteCharField, self).widget_attrs(widget)
        attrs['autocomplete'] = 'off'
        return attrs

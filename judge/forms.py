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
from judge.models import Organization, Profile, Submission, PrivateMessage, Language
from judge.utils.subscription import newsletter_id
from judge.widgets import MathJaxPagedownWidget, HeavyPreviewPageDownWidget, PagedownWidget, \
    Select2Widget, Select2MultipleWidget


def fix_unicode(string, unsafe=tuple(u'\u202a\u202b\u202d\u202e')):
    return string + (sum(k in unsafe for k in string) - string.count(u'\u202c')) * u'\u202c'


class ProfileForm(ModelForm):
    if newsletter_id is not None:
        newsletter = forms.BooleanField(label=_('Subscribe to contest updates'), initial=False, required=False)
    test_site = forms.BooleanField(label=_('Enable experimental features'), initial=False, required=False)

    class Meta:
        model = Profile
        fields = ['name', 'about', 'organizations', 'timezone', 'language', 'ace_theme', 'user_script']
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

    def clean(self):
        organizations = self.cleaned_data.get('organizations') or []
        max_orgs = getattr(settings, 'MAX_USER_ORGANIZATION_COUNT', 3)

        if sum(org.is_open for org in organizations) > max_orgs:
            raise ValidationError(_('You may not be part of more than {count} public organizations.').format(count=max_orgs))

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        if not user.has_perm('judge.edit_all_organization'):
            self.fields['organizations'].queryset = Organization.objects.filter(
                Q(is_open=True) | Q(id__in=user.profile.organizations.all())
            )

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


class EditOrganizationForm(ModelForm):
    class Meta:
        model = Organization
        fields = ['about', 'admins']
        widgets = {'admins': Select2MultipleWidget()}
        if HeavyPreviewPageDownWidget is not None:
            widgets['about'] = HeavyPreviewPageDownWidget(preview=reverse_lazy('organization_preview'))


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


class TOTPForm(Form):
    TOLERANCE = getattr(settings, 'DMOJ_TOTP_TOLERANCE_HALF_MINUTES', 1)

    totp_token = NoAutoCompleteCharField(validators=[
        RegexValidator('^[0-9]{6}$', _('Two Factor Authentication tokens must be 6 decimal digits.'))
    ])

    def __init__(self, *args, **kwargs):
        self.totp_key = kwargs.pop('totp_key')
        super(TOTPForm, self).__init__(*args, **kwargs)

    def clean_totp_token(self):
        if not pyotp.TOTP(self.totp_key).verify(self.cleaned_data['totp_token'], valid_window=self.TOLERANCE):
            raise ValidationError(_('Invalid Two Factor Authentication token.'))

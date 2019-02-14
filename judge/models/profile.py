from operator import mul

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Max
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _, pgettext
from fernet_fields import EncryptedCharField
from sortedm2m.fields import SortedManyToManyField

from judge.models.choices import TIMEZONE, ACE_THEMES
from judge.ratings import rating_class

__all__ = ['Profile']


class EncryptedNullCharField(EncryptedCharField):
    def get_prep_value(self, value):
        if not value:
            return None
        return super(EncryptedNullCharField, self).get_prep_value(value)


class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name=_('user associated'))
    name = models.CharField(max_length=50, verbose_name=_('display name'), null=True, blank=True)
    about = models.TextField(verbose_name=_('self-description'), null=True, blank=True)
    language = models.ForeignKey('Language', verbose_name=_('preferred language'))
    timezone = models.CharField(max_length=50, verbose_name=_('location'), choices=TIMEZONE,
                                default=getattr(settings, 'DEFAULT_USER_TIME_ZONE', 'America/Toronto'))
    points = models.FloatField(default=0, db_index=True)
    performance_points = models.FloatField(default=0, db_index=True)
    problem_count = models.IntegerField(default=0, db_index=True)
    ace_theme = models.CharField(max_length=30, choices=ACE_THEMES, default='github')
    last_access = models.DateTimeField(verbose_name=_('last access time'), default=now)
    ip = models.GenericIPAddressField(verbose_name=_('last IP'), blank=True, null=True)
    display_rank = models.CharField(max_length=10, default='user', verbose_name=_('display rank'),
                                    choices=(('user', 'Normal User'), ('setter', 'Problem Setter'), ('admin', 'Admin')))
    rating = models.IntegerField(null=True, default=None)
    current_contest = models.OneToOneField('ContestParticipation', verbose_name=_('current contest'),
                                           null=True, blank=True, related_name='+', on_delete=models.SET_NULL)
    notes = models.TextField(verbose_name=_('internal notes'), help_text=_('Notes for administrators regarding this user.'),
                             null=True, blank=True)


    def calculate_points(self, table=(lambda x: [pow(x, i) for i in xrange(100)])(getattr(settings, 'PP_STEP', 0.95))):
        from judge.models import Problem
        data = (Problem.objects.filter(submission__user=self, submission__points__isnull=False, is_public=True)
                .annotate(max_points=Max('submission__points')).order_by('-max_points')
                .values_list('max_points', flat=True).filter(max_points__gt=0))
        extradata = Problem.objects.filter(submission__user=self, submission__result='AC', is_public=True).values('id').distinct().count()
        bonus_function = getattr(settings, 'PP_BONUS_FUNCTION', lambda n: 300 * (1 - 0.997 ** n))
        points = sum(data)
        problems = len(data)
        entries = min(len(data), len(table))
        pp = sum(map(mul, table[:entries], data[:entries])) + bonus_function(extradata)
        if self.points != points or problems != self.problem_count or self.performance_points != pp:
            self.points = points
            self.problem_count = problems
            self.performance_points = pp
            self.save()
        return points

    calculate_points.alters_data = True

    @cached_property
    def display_name(self):
        if self.name:
            return self.name
        return self.user.username

    @cached_property
    def long_display_name(self):
        if self.name:
            return pgettext('user display name', '%(username)s (%(display)s)') % {
                'username': self.user.username, 'display': self.name
            }
        return self.user.username

    def remove_contest(self):
        self.current_contest = None
        self.save()

    remove_contest.alters_data = True

    def update_contest(self):
        contest = self.current_contest
        if contest is not None and contest.ended:
            self.remove_contest()

    update_contest.alters_data = True

    def get_absolute_url(self):
        return reverse('user_page', args=(self.user.username,))

    def __unicode__(self):
        return self.user.username

    @classmethod
    def get_user_css_class(cls, display_rank, rating, rating_colors=getattr(settings, 'DMOJ_RATING_COLORS', False)):
        if rating_colors:
            return 'rating %s %s' % (rating_class(rating) if rating is not None else 'rate-none', display_rank)
        return display_rank

    @cached_property
    def css_class(self):
        return self.get_user_css_class(self.display_rank, self.rating)

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

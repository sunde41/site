# -*- coding: utf-8 -*-

import re

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from judge.models.profile import Profile

__all__ = ['validate_regex', 'NoticePost']


def validate_regex(regex):
    try:
        re.compile(regex, re.VERBOSE)
    except re.error as e:
        raise ValidationError('Invalid regex: %s' % e.message)


class NoticePost(models.Model):
    title = models.CharField(verbose_name=_('post title'), max_length=100)
    authors = models.ManyToManyField(Profile, verbose_name=_('authors'), blank=True)
    visible = models.BooleanField(verbose_name=_('public visibility'), default=False)
    sticky = models.BooleanField(verbose_name=_('sticky'), default=False)
    publish_on = models.DateTimeField(verbose_name=_('publish after'))
    content = models.TextField(verbose_name=_('post content'))


    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('notice_post', args=(self.id,))

    def can_see(self, user):
        if self.visible and self.publish_on <= timezone.now():
            return True
        if user.has_perm('judge.edit_all_post'):
            return True
        return user.is_authenticated and self.authors.filter(id=user.profile.id).exists()

    class Meta:
        permissions = (
            ('edit_all_post', _('Edit all posts')),
        )
        verbose_name = _('notice post')
        verbose_name_plural = _('notice posts')

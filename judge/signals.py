import errno
import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .caching import finished_submission
from .models import Problem, Contest, Submission, Profile, Language, Judge, \
    ContestSubmission, License


def unlink_if_exists(file):
    try:
        os.unlink(file)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


@receiver(post_save, sender=Problem)
def problem_update(sender, instance, **kwargs):
    if hasattr(instance, '_updating_stats_only'):
        return

    cache.delete_many([
        make_template_fragment_key('submission_problem', (instance.id,)),
        make_template_fragment_key('problem_feed', (instance.id,)),
        'problem_tls:%s' % instance.id, 'problem_mls:%s' % instance.id,
    ])
    cache.delete_many([make_template_fragment_key('problem_authors', (instance.id, lang))
                       for lang, _ in settings.LANGUAGES])
    cache.delete_many(['generated-meta-problem:%s:%d' % (lang, instance.id) for lang, _ in settings.LANGUAGES])


@receiver(post_save, sender=Profile)
def profile_update(sender, instance, **kwargs):
    if hasattr(instance, '_updating_stats_only'):
        return


@receiver(post_save, sender=Contest)
def contest_update(sender, instance, **kwargs):
    if hasattr(instance, '_updating_stats_only'):
        return


@receiver(post_save, sender=License)
def license_update(sender, instance, **kwargs):
    cache.delete(make_template_fragment_key('license_html', (instance.id,)))


@receiver(post_save, sender=Language)
def language_update(sender, instance, **kwargs):
    cache.delete_many([make_template_fragment_key('language_html', (instance.id,)),
                       'lang:cn_map'])


@receiver(post_save, sender=Judge)
def judge_update(sender, instance, **kwargs):
    cache.delete(make_template_fragment_key('judge_html', (instance.id,)))


@receiver(post_delete, sender=Submission)
def submission_delete(sender, instance, **kwargs):
    finished_submission(instance)
    instance.user.calculate_points()


@receiver(post_delete, sender=ContestSubmission)
def contest_submission_delete(sender, instance, **kwargs):
    participation = instance.participation
    participation.recalculate_score()
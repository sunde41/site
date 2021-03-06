# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db.models import Q, Max, Count
from django.http import Http404
from django.utils import timezone
from django.utils.functional import lazy
from django.utils.translation import ugettext as _
from django.views.generic import ListView

from judge.views.detail_view import CommentedDetailView
from judge.models import NoticePost, Problem, Contest, Profile, Submission, Language
from judge.utils.cachedict import CacheDict
from judge.utils.diggpaginator import DiggPaginator
from judge.utils.problems import user_completed_ids
from judge.utils.views import TitleMixin


class PostList(ListView):
    model = NoticePost
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'notice/list.html'
    title = None

    def get_paginator(self, queryset, per_page, orphans=0,
                      allow_empty_first_page=True, **kwargs):
        return DiggPaginator(queryset, per_page, body=6, padding=2,
                             orphans=orphans, allow_empty_first_page=allow_empty_first_page, **kwargs)

    def get_queryset(self):
        return (NoticePost.objects.filter(visible=True, publish_on__lte=timezone.now()).order_by('-sticky', '-publish_on')
                        .prefetch_related('authors__user'))

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['title'] = self.title or _('Page %d of Posts') % context['page_obj'].number
        context['first_page_href'] = reverse('home')
        context['page_prefix'] = reverse('notice_post_list')
        now = timezone.now()

        # Dashboard stuff
        if self.request.user.is_authenticated:
            user = self.request.user.profile
            context['recently_attempted_problems'] = (Submission.objects.filter(user=user)
                                                      .exclude(problem__id__in=user_completed_ids(user))
                                                      .values_list('problem__code', 'problem__name', 'problem__points')
                                                      .annotate(points=Max('points'), latest=Max('date'))
                                                      .order_by('-latest'))[:7]

        visible_contests = Contest.objects.filter(is_public=True).order_by('start_time')
        q = Q(is_private=False)
        visible_contests = visible_contests.filter(q)
        context['current_contests'] = visible_contests.filter(start_time__lte=now, end_time__gt=now)
        context['future_contests'] = visible_contests.filter(start_time__gt=now)

        if self.request.user.is_authenticated:
            profile = self.request.user.profile
        else:
            profile = None

        return context


class PostView(TitleMixin, CommentedDetailView):
    model = NoticePost
    pk_url_kwarg = 'id'
    context_object_name = 'post'
    template_name = 'notice/content.html'

    def get_title(self):
        return self.object.title

    def get_comment_page(self):
        return 'b:%s' % self.object.id

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        return context

    def get_object(self, queryset=None):
        post = super(PostView, self).get_object(queryset)
        if not post.can_see(self.request.user):
            raise Http404()
        return post

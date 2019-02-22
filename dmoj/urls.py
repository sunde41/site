# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect
from django.utils.translation import ugettext_lazy as _

from judge.forms import CustomAuthenticationForm
from judge.views import TitledTemplateView
from judge.views import language, status, problem, register, user, notice, \
    submission, widgets, contests, ranked_submission, stats, preview
from judge.views.problem_data import ProblemDataView, ProblemSubmissionDiff, \
    problem_data_file, problem_init_view
from judge.views.register import RegistrationView, ActivationView
from judge.views.select2 import UserSelect2View, ProblemSelect2View, \
    ContestSelect2View, UserSearchSelect2View, ContestUserSearchSelect2View

########################################################################################################################
admin.autodiscover()
from django.contrib.sites.models import Site
from registration.models import RegistrationProfile
from django.contrib.flatpages.models import FlatPage
admin.site.unregister(Site)
admin.site.unregister(RegistrationProfile)
admin.site.unregister(FlatPage)
########################################################################################################################

register_patterns = [
    url(r'^activate/complete/$',
        TitledTemplateView.as_view(template_name='registration/activation_complete.html',
                                   title='Activation Successful!'),
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
        ActivationView.as_view(title='Activation key invalid'),
        name='registration_activate'),
    url(r'^register/$',
        RegistrationView.as_view(title=_('Register')),
        name='registration_register'),
    url(r'^register/complete/$',
        TitledTemplateView.as_view(template_name='registration/registration_complete.html',
                                   title='Registration Completed'),
        name='registration_complete'),
    url(r'^register/closed/$',
        TitledTemplateView.as_view(template_name='registration/registration_closed.html',
                                   title='Registration not allowed'),
        name='registration_disallowed'),
    url(r'^login/$', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        extra_context={'title': _('Login')},
        authentication_form=CustomAuthenticationForm,
    ), name='auth_login'),
    url(r'^logout/$', user.UserLogoutView.as_view(), name='auth_logout'),
    url(r'^password/change/$', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html'
    ), name='password_change'),
    url(r'^password/change/done/$', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html',
    ), name='password_change_done'),
    url(r'^password/reset/$',auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        html_email_template_name='registration/password_reset_email.html',
        email_template_name='registration/password_reset_email.txt',
    ), name='password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
        ), name='password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),
    url(r'^password/reset/done/$', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),
]


def exception(request):
    raise RuntimeError('@Xyene asked me to cause this')


def paged_list_view(view, name):
    return include([
        url(r'^$', view.as_view(), name=name),
        url(r'^(?P<page>\d+)$', view.as_view(), name=name),
    ])


urlpatterns = [
    url(r'^$', contests.ContestHome.as_view(title=_('Home')), name='home'),
    url(r'^500/$', exception),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^accounts/', include(register_patterns)),
    url(r'^problems/$', problem.ProblemList.as_view(), name='problem_list'),
    url(r'^problem/(?P<problem>[^/]+)', include([
        url(r'^$', problem.ProblemDetail.as_view(), name='problem_detail'),
        url(r'^/editorial$', problem.ProblemSolution.as_view(), name='problem_editorial'),
        url(r'^/clone', problem.clone_problem, name='problem_clone'),
        url(r'^/submit$', problem.problem_submit, name='problem_submit'),
        url(r'^/resubmit/(?P<submission>\d+)$', problem.problem_submit, name='problem_submit'),
        url(r'^/rank/', paged_list_view(ranked_submission.RankedSubmissions, 'ranked_submissions')),
        url(r'^/submissions/', paged_list_view(submission.ProblemSubmissions, 'chronological_submissions')),
        url(r'^/submissions/(?P<user>\w+)/', paged_list_view(submission.UserProblemSubmissions, 'user_submissions')),
        url(r'^/$', lambda _, problem: HttpResponsePermanentRedirect(reverse('problem_detail', args=[problem]))),
        url(r'^/test_data$', ProblemDataView.as_view(), name='problem_data'),
        url(r'^/test_data/init$', problem_init_view, name='problem_data_init'),
        url(r'^/test_data/diff$', ProblemSubmissionDiff.as_view(), name='problem_submission_diff'),
        url(r'^/data/(?P<path>.+)$', problem_data_file, name='problem_data_file'),
    ])),

    url(r'^submissions/', paged_list_view(submission.AllSubmissions, 'all_submissions')),
    url(r'^submissions/user/(?P<user>\w+)/', paged_list_view(submission.AllUserSubmissions, 'all_user_submissions')),
    url(r'^src/(?P<submission>\d+)$', submission.SubmissionSource.as_view(), name='submission_source'),
    url(r'^src/(?P<submission>\d+)/raw$', submission.SubmissionSourceRaw.as_view(), name='submission_source_raw'),
    url(r'^submission/(?P<submission>\d+)', include([
        url(r'^$', submission.SubmissionStatus.as_view(), name='submission_status'),
        url(r'^/abort$', submission.abort_submission, name='submission_abort'),
        url(r'^/html$', submission.single_submission),
    ])),

    url(r'^users/', include([
        url(r'^$', user.users, name='user_list'),
        url(r'^(?P<page>\d+)$', lambda request, page:
        HttpResponsePermanentRedirect('%s?page=%s' % (reverse('user_list'), page))),
        url(r'^find$', user.user_ranking_redirect, name='user_ranking_redirect'),
    ])),

    url(r'^user$', user.UserAboutPage.as_view(), name='user_page'),
    url(r'^edit/profile/$', user.edit_profile, name='user_edit_profile'),
    url(r'^user/(?P<user>\w+)', include([
        url(r'^$', user.UserAboutPage.as_view(), name='user_page'),
        url(r'^/solved', include([
            url(r'^$', user.UserProblemsPage.as_view(), name='user_problems'),
            url(r'/ajax$', user.UserPerformancePointsAjax.as_view(), name='user_pp_ajax'),
        ])),
        url(r'^/submissions/', paged_list_view(submission.AllUserSubmissions, 'all_user_submissions_old')),
        url(r'^/submissions/', lambda _, user: HttpResponsePermanentRedirect(reverse('all_user_submissions', args=[user]))),

        url(r'^/$', lambda _, user: HttpResponsePermanentRedirect(reverse('user_page', args=[user]))),
    ])),

    url(r'^contests/$', contests.ContestList.as_view(), name='contest_list'),
    url(r'^contests/tag/(?P<name>[a-z-]+)', include([
        url(r'^$', contests.ContestTagDetail.as_view(), name='contest_tag'),
        url(r'^/ajax$', contests.ContestTagDetailAjax.as_view(), name='contest_tag_ajax'),
    ])),
    url(r'^contest/(?P<contest>\w+)', include([
        url(r'^$', contests.ContestDetail.as_view(), name='contest_view'),
        url(r'^/ranking/$', contests.contest_ranking, name='contest_ranking'),
        url(r'^/ranking/ajax$', contests.contest_ranking_ajax, name='contest_ranking_ajax'),
        url(r'^/join$', contests.ContestJoin.as_view(), name='contest_join'),
        url(r'^/leave$', contests.ContestLeave.as_view(), name='contest_leave'),
        url(r'^/rank/(?P<problem>\w+)/',
            paged_list_view(ranked_submission.ContestRankedSubmission, 'contest_ranked_submissions')),
        url(r'^/submissions/(?P<user>\w+)/(?P<problem>\w+)/',
            paged_list_view(submission.UserContestSubmissions, 'contest_user_submissions')),
        url(r'^/participations$', contests.own_participation_list, name='contest_participation_own'),
        url(r'^/participations/(?P<user>\w+)$', contests.participation_list, name='contest_participation'),
        url(r'^/$', lambda _, contest: HttpResponsePermanentRedirect(reverse('contest_view', args=[contest]))),
    ])),

    url(r'^runtimes/$', language.LanguageList.as_view(), name='runtime_list'),
    url(r'^runtimes/matrix/$', status.version_matrix, name='version_matrix'),
    url(r'^status/$', status.status_all, name='status_all'),
    url(r'^notice/', paged_list_view(notice.PostList, 'notice_post_list')),
    url(r'^post/(?P<id>\d+)$', notice.PostView.as_view(), name='notice_post'),
    url(r'^widgets/', include([
        url(r'^rejudge$', widgets.rejudge_submission, name='submission_rejudge'),
        url(r'^single_submission$', submission.single_submission_query, name='submission_single_query'),
        url(r'^submission_testcases$', submission.SubmissionTestCaseQuery.as_view(), name='submission_testcases_query'),
        url(r'^detect_timezone$', widgets.DetectTimezone.as_view(), name='detect_timezone'),
        url(r'^status-table$', status.status_table, name='status_table'),
        url(r'^template$', problem.LanguageTemplateAjax.as_view(), name='language_template_ajax'),
        url(r'^select2/', include([
            url(r'^user_search$', UserSearchSelect2View.as_view(), name='user_search_select2_ajax'),
            url(r'^contest_users/(?P<contest>\w+)$', ContestUserSearchSelect2View.as_view(),
                name='contest_user_search_select2_ajax'),
        ])),

        url(r'^preview/', include([
            url(r'^problem$', preview.ProblemMarkdownPreviewView.as_view(), name='problem_preview'),
            url(r'^solution$', preview.SolutionMarkdownPreviewView.as_view(), name='solution_preview'),
        ])),
    ])),

    url(r'^stats/', include([
        url('^language/', include([
            url('^$', stats.language, name='language_stats'),
            url('^data/all/$', stats.language_data, name='language_stats_data_all'),
            url('^data/ac/$', stats.ac_language_data, name='language_stats_data_ac'),
            url('^data/status/$', stats.status_data, name='stats_data_status'),
            url('^data/ac_rate/$', stats.ac_rate, name='language_stats_data_ac_rate'),
        ])),
    ])),

    url(r'^judge-select2/', include([
        url(r'^profile/$', UserSelect2View.as_view(), name='profile_select2'),
        url(r'^problem/$', ProblemSelect2View.as_view(), name='problem_select2'),
        url(r'^contest/$', ContestSelect2View.as_view(), name='contest_select2'),
    ])),
]

favicon_paths = ['apple-touch-icon-180x180.png', 'favicon-32x32.png', 'favicon-16x16.png',]

from django.templatetags.static import static
from django.utils.functional import lazystr
from django.views.generic import RedirectView

for favicon in favicon_paths:
    urlpatterns.append(url(r'^%s$' % favicon, RedirectView.as_view(
        url=lazystr(lambda: static('icons/' + favicon))
    )))

handler404 = 'judge.views.error.error404'
handler403 = 'judge.views.error.error403'
handler500 = 'judge.views.error.error500'

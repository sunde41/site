# -*- coding: utf-8 -*-

from django.contrib import admin

from judge.admin.contest import ContestTagAdmin, ContestAdmin, ContestParticipationAdmin
from judge.admin.interface import NoticePostAdmin
from judge.admin.problem import ProblemAdmin
from judge.admin.profile import ProfileAdmin
from judge.admin.runtime import JudgeAdmin, LanguageAdmin
from judge.admin.submission import SubmissionAdmin
from judge.admin.taxon import ProblemGroupAdmin, ProblemTypeAdmin
from judge.models import NoticePost, Contest, ContestParticipation, \
    ContestTag, Judge, Language,Problem, ProblemGroup, ProblemType, Profile, Submission

admin.site.register(NoticePost, NoticePostAdmin)
admin.site.register(Contest, ContestAdmin)
admin.site.register(ContestParticipation, ContestParticipationAdmin)
admin.site.register(ContestTag, ContestTagAdmin)
admin.site.register(Judge, JudgeAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(ProblemGroup, ProblemGroupAdmin)
admin.site.register(ProblemType, ProblemTypeAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Submission, SubmissionAdmin)
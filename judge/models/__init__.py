from reversion import revisions

from judge.models.choices import TIMEZONE, ACE_THEMES
from judge.models.contest import Contest, ContestTag, ContestParticipation, ContestProblem, ContestSubmission, Rating
from judge.models.interface import validate_regex, NoticePost
from judge.models.problem import ProblemGroup, ProblemType, Problem, ProblemClarification, ProblemTranslation, \
    TranslatedProblemQuerySet, TranslatedProblemForeignKeyQuerySet,LanguageLimit, Solution
from judge.models.problem_data import problem_data_storage, problem_directory_file, ProblemData, ProblemTestCase, \
    CHECKERS
from judge.models.profile import Profile
from judge.models.runtime import Language, RuntimeVersion, Judge
from judge.models.submission import SUBMISSION_RESULT, Submission, SubmissionTestCase

revisions.register(Profile, exclude=['points', 'last_access', 'ip', 'rating'])
revisions.register(Problem, follow=['language_limits'])
revisions.register(LanguageLimit)
revisions.register(Contest, follow=['contest_problems'])
revisions.register(ContestProblem)
revisions.register(NoticePost)
revisions.register(Solution)
revisions.register(Judge, fields=['name', 'created', 'auth_key', 'description'])
revisions.register(Language)
del revisions

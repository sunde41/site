# -*- coding: utf-8 -*-

import os
import re

from django.utils.translation import ugettext_lazy as _
from django_jinja.builtins import DEFAULT_EXTENSIONS
from jinja2 import select_autoescape

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = '5*9f5q57mqmlz2#f$x1h76&jxy#yortjl1v+l*6hd18$d*yx#0'

DEBUG = False
ALLOWED_HOSTS = ['150.95.151.157', 'codingtest.everycoding.net']

SITE_ID = 1
SITE_NAME = 'KCCT'
SITE_LONG_NAME = '고려대학교 코딩 능력 평가 시스템'
SITE_ADMIN_EMAIL = 'sunde41@gmail.com'
SERVER_EMAIL = '고려대학교 코딩 능력 평가 관리자 <sunde41@gmail.com>'
ADMINS = (
    ('고려대학교 코딩 능력 평가 관리자', 'sunde41@gmail.com'),
)

TERMS_OF_SERVICE_URL = 'http://korea.ac.kr/mbshome/mbs/university/subview.do?id=university_090300000000'  # Use a flatpage.

PYGMENT_THEME = 'pygment-github.css'
PROBLEM_DATA_ROOT = '/root/problems'
# Application definition

INSTALLED_APPS = ()

try:
    import wpadmin
except ImportError:
    pass
else:
    del wpadmin
    INSTALLED_APPS += ('wpadmin',)

    WPADMIN = {
        'admin': {
            'title': '고려대학교 코딩 능력 평가 시스템 관리',
            'menu': {
                'top': 'wpadmin.menu.menus.BasicTopMenu',
                'left': 'wpadmin.menu.custom.CustomModelLeftMenuWithDashboard',
            },
            'custom_menu': [
                {
                    'model': 'judge.Problem',
                    'icon': 'fa-question-circle',
                    'children': [
                        'judge.ProblemGroup',
                        'judge.ProblemType',
                    ],
                },
                {
                    'model': 'judge.Submission',
                    'icon': 'fa-check-square-o',
                    'children': [
                        'judge.Language',
                        'judge.Judge',
                    ],
                },
                {
                    'model': 'judge.Contest',
                    'icon': 'fa-bar-chart',
                    'children': [
                        'judge.ContestParticipation',
                        'judge.ContestTag',
                    ],
                },
                {
                    'model': 'auth.User',
                    'icon': 'fa-user',
                    'children': [
                        'auth.Group',
                        'judge.Profile',
                    ],
                },
                ('judge.NoticePost', 'fa-rss-square'),
                ('judge.Solution', 'fa-pencil'),
            ],
            'dashboard': {
                'breadcrumbs': True,
            },
        }
    }

INSTALLED_APPS += (
    'django.contrib.admin',
    'judge',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'registration',
    'reversion',
    'compressor',
    'django_ace',
    'pagedown',
    'sortedm2m',
    'statici18n',
    'django_jinja',
    'ckeditor',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'judge.middleware.DMOJLoginMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'judge.user_log.LogUserAccessMiddleware',
    'judge.timezone.TimezoneMiddleware',
    'judge.middleware.ContestMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ACCOUNT_ACTIVATION_DAYS = 7

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'judge.utils.pwned.PwnedPasswordsValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

SILENCED_SYSTEM_CHECKS = ['urls.W002', 'fields.W342']

ROOT_URLCONF = 'dmoj.urls'
LOGIN_REDIRECT_URL = '/user'
WSGI_APPLICATION = 'dmoj.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': False,
        'OPTIONS': {
            'match_extension': ('.html', '.txt'),
            'match_regex': '^(?!admin/)',
            'context_processors': [
                'django.template.context_processors.media',
                'django.template.context_processors.tz',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'judge.template_context.comet_location',
                'judge.template_context.get_resource',
                'judge.template_context.general_info',
                'judge.template_context.site',
                'judge.template_context.site_name',
                'judge.template_context.math_setting',
            ],
            'autoescape': select_autoescape(['html', 'xml']),
            'trim_blocks': True,
            'lstrip_blocks': True,
            'extensions': DEFAULT_EXTENSIONS + [
                'compressor.contrib.jinja2ext.CompressorExtension',
                'judge.jinja2.DMOJExtension',
                'judge.jinja2.spaceless.SpacelessExtension',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.media',
                'django.template.context_processors.tz',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGES = [
    ('en', _('English')),
    ('ko', _('Korean')),
]

MARKDOWN_ADMIN_EDITABLE_STYLE = {
    'safe_mode': False,
    'texoid': True,
    'math': True,
}

MARKDOWN_DEFAULT_STYLE = {
    'safe_mode': True,
    'nofollow': True,
    'math': True,
}

MARKDOWN_USER_LARGE_STYLE = {
    'safe_mode': True,
    'nofollow': True,
    'math': True,
}

MARKDOWN_STYLES = {
    'comment': MARKDOWN_DEFAULT_STYLE,
    'self-description': MARKDOWN_USER_LARGE_STYLE,
    'problem': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'contest': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'language': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'judge': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'solution': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'contest_tag': MARKDOWN_ADMIN_EDITABLE_STYLE,
}

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Bridged configuration
BRIDGED_JUDGE_ADDRESS = [('localhost', 9999)]
BRIDGED_DJANGO_ADDRESS = [('localhost', 9998)]
BRIDGED_DJANGO_CONNECT = None

# Event Server configuration
EVENT_DAEMON_USE = True
EVENT_DAEMON_POST = 'ws://127.0.0.1:15101/'
EVENT_DAEMON_GET = 'ws://codingtest.everycoding.net/event/'
EVENT_DAEMON_POLL = '/channels/'
EVENT_DAEMON_KEY = None
EVENT_DAEMON_SUBMISSION_KEY = '6Sdmkx^%pk@GsifDfXcwX*Y7LRF%RGT8vmFpSxFBT$fwS7trc8raWfN#CSfQuKApx&$B#Gh2L7p%W!Ww'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'ko-KR'
DEFAULT_USER_TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Cookies
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
# DMOJ_RESOURCES = os.path.join(BASE_DIR, 'resources')
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'resources'),
# ]
STATIC_ROOT = 'static'
STATIC_URL = '/static/'

# Authentication
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

ACE_URL = '//cdnjs.cloudflare.com/ajax/libs/ace/1.2.3/'
JQUERY_JS = '//cdnjs.cloudflare.com/ajax/libs/jquery/2.2.4/jquery.min.js'
SELECT2_JS_URL = '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js'
SELECT2_CSS_URL = '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css'
TIMEZONE_MAP = 'http://naturalearth.springercarto.com/ne3_data/8192/textures/3_no_ice_clouds_8k.jpg'


JUDGE_AMQP_PATH = None
CKEDITOR_BASEPATH = "/static/ckeditor/"
CKEDITOR_CONFIGS = {
    'default': {
        'language' : 'ko',
        'toolbar': [
       { 'name': 'MAX', 'items':['Maximize'] },
       { 'name': 'insert', 'items':['CodeSnippet','addImage','Table','Link','Unlink','Blockquote','HorizontalRule'] },
       { 'name': 'basicstyles', 'items': ['Bold', 'Italic','Underline','Strike', 'TextColor','BGColor', '-', 'RemoveFormat' ] },
       { 'name': 'paragraph', 'items': [ 'NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-','JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock' ] }
        ],
        'height': 300,
        'removeDialogTabs' : 'image:advanced;link:advanced',
        'removeButtons' : 'addFile,Anchor,Image,Subscript,Superscript,Format',
        },
}

COMPRESS_OUTPUT_DIR = 'cache'
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']
COMPRESS_STORAGE = 'compressor.storage.GzipCompressorFileStorage'
STATICFILES_FINDERS += ('compressor.finders.CompressorFinder',)

ENABLE_FTS = False
BAD_MAIL_PROVIDERS = set()

try:
    from local_settings import *
except ImportError:
    pass

# try:
#     with open(os.path.join(os.path.dirname(__file__), 'local_settings.py')) as f:
#         exec f in globals()
# except IOError:
#     pass

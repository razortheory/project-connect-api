import environ

# Build paths inside the project like this: root(...)
env = environ.Env()

root = environ.Path(__file__) - 3
apps_root = root.path('proco')

BASE_DIR = root()

# Project name
# ------------
PROJECT_FULL_NAME = env('PROJECT_FULL_NAME', default='Project Connect')
PROJECT_SHORT_NAME = env('PROJECT_SHORT_NAME', default='Proco')

# Base configurations
# --------------------------------------------------------------------------

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = 'custom_auth.ApplicationUser'


# Application definition
# --------------------------------------------------------------------------

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'drf_secure_token',
    'fcm_django',
]

LOCAL_APPS = [
    'proco.mailing',
    'proco.taskapp',
    'proco.custom_auth',
    'proco.fcm',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# Middleware configurations
# --------------------------------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'drf_secure_token.middleware.UpdateTokenMiddleware',
]


# Rest framework configuration
# http://www.django-rest-framework.org/api-guide/settings/
# --------------------------------------------------------------------------

REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'drf_secure_token.authentication.SecureTokenAuthentication',
    ],
}


# Template configurations
# --------------------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            root('proco', 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'proco.context_processors.google_analytics',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]


# Fixture configurations
# --------------------------------------------------------------------------

FIXTURE_DIRS = [
    root('proco', 'fixtures'),
]


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
# --------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
# --------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
# --------------------------------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = root('static')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

STATICFILES_DIRS = [
    root('proco', 'assets'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = root('media')


CELERY_ENABLED = env.bool('CELERY_ENABLED', default=True)
if CELERY_ENABLED:
    # Celery configuration
    # --------------------------------------------------------------------------

    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_TASK_IGNORE_RESULT = True


# Django mailing configuration
# --------------------------------------------------------------------------

if CELERY_ENABLED:
    TEMPLATED_EMAIL_BACKEND = 'proco.mailing.backends.AsyncTemplateBackend'
    MAILING_USE_CELERY = True

TEMPLATED_EMAIL_TEMPLATE_DIR = 'email'
TEMPLATED_EMAIL_FILE_EXTENSION = 'html'


# FCM Push Notifications configuration
# ------------------------------------

FCM_DJANGO_SETTINGS = {
    'FCM_SERVER_KEY': None,
    # true if you want to have only one active device per registered user at a time
    'ONE_DEVICE_PER_USER': False,
    # devices to which notifications cannot be sent, are deleted upon receiving error response from FCM
    'DELETE_INACTIVE_DEVICES': True,
}

"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from dotenv import dotenv_values
from queue import Queue
from threading import Lock

import dj_database_url

config = dotenv_values(os.path.join("..", ".env"))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config["DEBUG"]

ALLOWED_HOSTS = config["ALLOWED_HOSTS"].split(" ")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_jinja",
    "django_extensions",
    "django_celery_beat",
    "site_settings",
    "products",
    "shops",
    "profiles",
    "catalog",
    "cart",
    "comparison",
    "orders",
    "api_payments",
    "payapp",
    "importdata",
    "discount",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "config.urls"

if DEBUG:
    SHELL_PLUS_PRINT_SQL = True

INTERNAL_IPS = [
    "0.0.0.0",
    "127.0.0.1",
]

ALLOWED_HOSTS += INTERNAL_IPS

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

TEMPLATES = [
    {
        "BACKEND": "django_jinja.jinja2.Jinja2",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "extensions": {
                "jinja2.ext.i18n",
                "django_jinja.builtins.extensions.StaticFilesExtension",
                "django_jinja.builtins.extensions.CsrfExtension",
                "django_jinja.builtins.extensions.CacheExtension",
                "django_jinja.builtins.extensions.DebugExtension",
                "django_jinja.builtins.extensions.UrlsExtension",
            },
            # "policies": {
            #                 "ext.i18n.trimmed": True,
            #             },
            "match_extension": ".jinja2",
            "match_regex": None,
            "app_dirname": "templates",
            "context_processors": [
                "context_processors.settings_context.site_settings",
                "context_processors.menu_context.categories_menu",
                "context_processors.catalog_context.product_placeholders",
                "context_processors.comparison_context.comparison_items",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # "django.template.context_processors.i18n",
            ],
            # "translation_engine": "django.utils.translation",
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {"default": dj_database_url.parse(config["DATABASE_URL"])}

REDIS_URL = config["REDIS_URL"]

CACHE_TTL = 60 * 60 * 24

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": CACHE_TTL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_USER_MODEL = "profiles.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

USE_L10N = True

LOCALE_PATHS = [BASE_DIR / "locale/"]

LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/


STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "media/"
MEDIA_ROOT = "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = reverse_lazy("products:home-page")
LOGIN_URL = reverse_lazy("profiles:login")

COMPARISON_SESSION_ID = "comparison"
COMPARISON_MAX_PRODUCTS = 2

CART_SESSION_KEY = "cart"
CART_SIZE_SESSION_KEY = "cart_size"
CART_PRICE_SESSION_KEY = "cart_price"

PAY_QUEUE = Queue()
PAY_QUEUE_LOCK = Lock()
PAY_URL = reverse_lazy("api_payments:pays")


# Celery configuration

# configure the location of Redis database:
CELERY_BROKER_URL = config["REDIS_URL"]
# configure storing the state and returning values of tasks in Redis
CELERY_RESULT_BACKEND = config["REDIS_URL"]
# CELERYD_LOG_FILE = "/logs/celery.log"
# CELERYD_LOG_LEVEL = "ERROR"
CELERY_CREATE_DIRS = 1
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


# Django Email
# https://docs.djangoproject.com/en/4.2/topics/email/

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config["EMAIL_HOST"]
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_USER_SSL = False
EMAIL_HOST_USER = config["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = config["EMAIL_HOST_PASSWORD"]


# Set the import folder for importadata app
IMPORT_FOLDER = "import_folder"

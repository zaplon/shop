#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Django settings for shop project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf import global_settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

#AUTH_USER_MODEL = amsoil.models.User

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'a9jhke3nvi!9%#e!i^u6)()=b6$n8182u@hmq^iu&xc#nmr3kg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

gettext = lambda s: s
LANGUAGES = (
    ('pl', gettext('Polish')),
    ('en', gettext('English')),
)

# Application definition

INSTALLED_APPS = (
    #'suit',
    'grappelli',
    'django_filters',
    'rest_framework',
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'amsoil',
    'ckeditor',
    'jstemplate',
    'django_inlinecss',
    #'registration',
    'authentication',
    'password_reset',
    'corsheaders',
    'reviews',
    'getpaid',
    'getpaid.backends.transferuj'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'shop.urls'

WSGI_APPLICATION = 'shop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
     'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'shop',
        'USER': 'root',
        'PASSWORD': 'sadyba88',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': { 'init_command':'SET storage_engine=INNODB,character_set_connection=utf8,collation_connection=utf8_polish_ci'},
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'pl'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

MEDIA_ROOT = '/home/jan/PycharmProjects/shop/media/'
MEDIA_URL = '/media/'

STATIC_URL = '/static/'
STATIC_ROOT = '/home/jan/PycharmProjects/shop/static/'
ADMIN_TEMPLATES_ROOT = '/home/jan/PycharmProjects/shop/templates/admin/'
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
)

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
}

JSTEMPLATE_DIRS = [
    os.path.join(BASE_DIR,  'templates'),
    os.path.join(BASE_DIR,  'jstemplates'),
]

FROM_MAIL = 'info@najlepszysyntetyk.pl'

#EMAIL_HOST = 'localhost'
#EMAIL_PORT = 1025

#EMAIL_HOST = 'localhost'
#EMAIL_HOST_USER = 'sklep_info'
#EMAIL_HOST_PASSWORD = "qwer123"
#EMAIL_USE_TLS = True
#EMAIL_USE_SSL = True
#EMAIL_PORT = 25

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'oleje.amsoil@gmail.com'
EMAIL_HOST_PASSWORD = "iskra123"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

LOCALE_PATHS = (
    '/home/jan/PycharmProjects/shop/locale', # replace with correct path here
)

LANGUAGES = (
    ('pl', 'Polski'),
)

CHECKOUT_THANK_YOU = '<h2>Dziękujemy,</h2><p>Twoje zamówienie zostało zarejestrowane w systemie</p>'
CHECKOUT_FAILED ='<h2>Błąd</h2><p>Podczas przetwarzania płatności wystąpił błąd</p>'

AUTH_USER_MODEL = 'authentication.User'

DEBUG = True

CORS_ORIGIN_ALLOW_ALL = True

REVIEWS_SETTINGS = {
    'model':'amsoil.Product'
}


GETPAID_BACKENDS = ('getpaid.backends.transferuj',)

GETPAID_BACKENDS_SETTINGS = {
    'getpaid.backends.transferuj' : {
            'id' : 12132,
            'key' : '781d7a740fbd2b2634b64967dfd887a26a504d14',
            'signing' : True,       # optional
        },
}

SITE_ID=1
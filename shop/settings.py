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

gettext = lambda s: s

class SetRemoteAddrFromForwardedFor(object):
    def process_request(self, request):
        try:
            real_ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            pass
        else:
            # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs.
            # Take just the first one.
            real_ip = real_ip.split(",")[0]
            request.META['REMOTE_ADDR'] = real_ip

LANGUAGES = (
    ('pl', gettext('Polish')),
    ('en', gettext('English')),
)

# Application definition

INSTALLED_APPS = (
    'grappelli',
    'django_filters',
    'rest_framework',
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',	
    'django.contrib.staticfiles',
    'amsoil',
    'ckeditor',
    'jstemplate',
    'django_inlinecss',
    #'registration',
    'authentication',
    'password_reset',
    'corsheaders',
    'getpaid',
    'getpaid.backends.transferuj',
    'reviews',
    'markitup',
)

CORS_URLS_REGEX = r'^/api/.*$'

CORS_ORIGIN_ALLOW_ALL = False

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
    #'SetRemoteAddrFromForwardedFor',
)

ROOT_URLCONF = 'shop.urls'

WSGI_APPLICATION = 'shop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
     'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'shop',
        'USER': 'shop_user',
        'PASSWORD': 'shop_qaz!23',
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

MEDIA_ROOT = '/home/zaplon/webapps/static/media/'
MEDIA_URL = '/static/media/'

STATIC_URL = '/static/'
STATIC_ROOT = '/home/zaplon/webapps/static/'
ADMIN_TEMPLATES_ROOT = '/home/webapps/zaplon/shop/templates/admin/'
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

EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = 'zamowienia'
EMAIL_HOST_PASSWORD = "YUIOP{}|;'"
DEFAULT_FROM_EMAIL = 'zamowienia@zaplon.webfactional.com'
SERVER_EMAIL = 'zamowienia@zaplon.webfactional.com'

LOCALE_PATHS = (
    '/home/zaplon/webapps/shop/locale', # replace with correct path here
)

LANGUAGES = (
    ('pl', 'Polski'),
)

CHECKOUT_THANK_YOU = '<h2>Dziękujemy,</h2><p>Twoje zamówienie zostało zarejestrowane w systemie</p>'
CHECKOUT_FAILED ='<h2>Błąd</h2><p>Podczas przetwarzania płatności wystąpił błąd</p>'

AUTH_USER_MODEL = 'authentication.User'

ALLOWED_HOSTS = [
	'.zaplon.webfactional.com',
	'.najlepszysyntetyk.pl',
	'.secure.transferuj.pl'
]

GETPAID_BACKENDS = ('getpaid.backends.transferuj',)

GETPAID_BACKENDS_SETTINGS = {
    'getpaid.backends.transferuj' : {
            'id' : 12132,
            'key' : '781d7a740fbd2b2634b64967dfd887a26a504d14',
            'signing' : True,       # optional
        },
}

SITE_ID=1

REVIEWS_SETTINGS = {
    'model':'amsoil.Product'
}

MARKITUP_FILTER = ('markdown.markdown', {'safe_mode': False})
#MARKITUP_FILTER = ('django.contrib.markup.templatetags.markup.textile', {})
#MARKITUP_FILTER = ('django_markup.markup.formatter', {'filter_name':'textile', 'safe_mode':False})
MARKITUP_AUTO_PREVIEW = True

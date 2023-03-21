import django
from django.apps import AppConfig


class AppdashConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appDash'
    INSTALLED_APPS = [

        django.contrib.staticfiles
    ]
    STATIC_URL = 'plot/'

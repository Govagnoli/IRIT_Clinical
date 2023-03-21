"""dashboardSAE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import my_view
from .views import test_mongodb
from .views import execute_exe
from .views import recupIvermectin
from .views import import_exec
from .views import requestPNG
from .views import def_param_Genres

urlpatterns = [
    #path('ma-vue/', my_view, name='my_view'),
    #path('executable/', execute_exe, name='executable'),
    path('test-mongodb/', requestPNG, name='test_mongodb'),
    path('def_param_Genres/', def_param_Genres, name='def_param_Genres'),
    #path('test-mongodb-Eliott/', recupIvermectin, name='test-mongodb-Eliott'),
    path('import_exec/', import_exec, name='import_exec'),
]


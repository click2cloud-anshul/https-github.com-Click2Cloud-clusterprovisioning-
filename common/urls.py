from django.conf.urls import include, url
from django.contrib import admin
from common import views

urlpatterns = [
    url(r'^testAPI', views.testAPI),
]

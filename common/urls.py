from django.conf.urls import url

from common import views

urlpatterns = [
    url(r'^health-check$', views.health_check),
]

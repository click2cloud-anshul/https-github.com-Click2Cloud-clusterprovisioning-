from django.conf.urls import url

from common import views

urlpatterns = [
    url(r'^health-check$', views.health_check),
    url(r'^alibaba/clear-instance-list$', views.alibaba_clear_instance_list),
]

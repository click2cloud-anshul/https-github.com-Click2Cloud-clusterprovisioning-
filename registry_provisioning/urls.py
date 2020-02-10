from django.conf.urls import url

from registry_provisioning import views

urlpatterns = [
    url(r'^alibaba/create-namespace$', views.alibaba_create_namespace),
    url(r'^alibaba/delete-namespace$', views.alibaba_delete_namespace),
    url(r'^alibaba/list-namespace$', views.alibaba_list_namespace),
    url(r'^alibaba/update-namespace$', views.alibaba_update_namespace),
]

from django.conf.urls import url

from registry_provisioning import views

urlpatterns = [
    url(r'^alibaba/create-namespace$', views.alibaba_create_namespace),
    url(r'^alibaba/delete-namespace$', views.alibaba_delete_namespace),
    url(r'^alibaba/list-namespace$', views.alibaba_list_namespace),
    url(r'^alibaba/update-namespace$', views.alibaba_update_namespace),
    url(r'^alibaba/create-repository$', views.alibaba_create_repository),
    url(r'^alibaba/list-repository-by-provider$', views.alibaba_list_repository_by_provider),
    url(r'^alibaba/list-repository-by-namespace$', views.alibaba_list_repository_by_namespace),
    url(r'^alibaba/update-repository$', views.alibaba_update_repository),
    url(r'^alibaba/delete-repository$', views.alibaba_delete_repository),
    url(r'^alibaba/list-providers$', views.alibaba_list_providers),
]

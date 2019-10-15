from django.conf.urls import url

from cluster_provisioning import views

urlpatterns = [
    url(r'^alibaba/get-region-list', views.alibaba_region_list),
    # url(r'^get-instance-list', views.alibaba_instance_list),
    url(r'^alibaba/get-ssh-keypair-list', views.alibaba_ssh_key_pair_list),
    url(r'^alibaba/get-network-details', views.alibaba_network_details),
    # url(r'^get-cluster-details', views.cluster_details),
    # url(r'^get-all-clusters-config', views.all_cluster_config),
    # url(r'^get-all-clusters-details', views.all_cluster_details),
    url(r'^alibaba/get-all-clusters-details', views.all_cluster_details),
    url(r'^alibaba/get-all-pod-details', views.all_pod_details),

]

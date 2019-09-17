from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^getRegionList', views.alibaba_region_list),
    url(r'^getKeyPairList', views.alibaba_key_pair_list),
    url(r'^getVPCList', views.get_vpc_list),
    url(r'^getClusterDetails', views.get_cluster_details),
    url(r'^getClusterStatus', views.get_cluster_status),
    url(r'^getClusterConfig', views.get_cluster_config),
    url(r'^getAllClustersDetails', views.get_all_clusters),
    url(r'^createKubernetesCluster', views.create_kubernetes_cluster),
    url(r'^deleteKubernetesCluster', views.delete_kubernetes_cluster),
]

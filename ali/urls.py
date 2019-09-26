from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^getRegionList', views.alibaba_region_list),
    url(r'^getInstanceList', views.alibaba_instance_list),
    url(r'^getKeyPairList', views.alibaba_key_pair_list),
    url(r'^getVPCList', views.get_vpc_list),
    # url(r'^getClusterDetails', views.get_cluster_details),
    url(r'^getAllClusterConfig', views.get_all_cluster_config),
    url(r'^getAllClustersDetails', views.get_all_clusters),
    url(r'^createKubernetesCluster', views.create_kubernetes_cluster),
    url(r'^deleteKubernetesCluster', views.delete_kubernetes_cluster),
    url(r'^getAllPods', views.get_all_pods),
    url(r'^getAllNodes', views.get_all_nodes),
    url(r'^getAllDeployments', views.get_all_deployments),
    url(r'^getAllNamespaces', views.get_all_namespaces),
    url(r'^getAllPersistentVolumeClaims', views.get_all_persistent_volume_claims),
    url(r'^getAllPersistentVolumes', views.get_all_persistent_volumes),
    url(r'^getAllServices', views.get_all_services),
    url(r'^getAllRoles', views.get_all_roles),
    url(r'^getAllStorageClasses', views.get_all_storageclasses),
    url(r'^getAllCronJobs', views.get_all_cronjobs),
    url(r'^getAllJobs', views.get_all_jobs),
    url(r'^getAllSecrets', views.get_all_secrets),
]

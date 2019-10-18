from django.conf.urls import url

from cluster_provisioning import views

urlpatterns = [
    url(r'^alibaba/get-region-list$', views.alibaba_region_list),
    url(r'^alibaba/get-instance-list$', views.alibaba_instance_list),
    url(r'^alibaba/get-ssh-keypair-list$', views.alibaba_ssh_key_pair_list),
    url(r'^alibaba/get-network-details$', views.alibaba_network_details),
    url(r'^alibaba/get-all-clusters-config$', views.all_cluster_config_details),
    url(r'^alibaba/get-all-clusters-details$', views.all_cluster_details),
    url(r'^alibaba/get-all-pod-details$', views.all_pod_details),
    url(r'^alibaba/get-all-namespace-details$', views.all_namespace_details),
    url(r'^alibaba/get-all-role-details$', views.all_role_details),
    url(r'^alibaba/get-all-persistent-volume-details$', views.all_persistent_volume_details),
    url(r'^alibaba/get-all-persistent-volume-claim-details$', views.all_persistent_volume_claim_details),
    url(r'^alibaba/get-all-deployment-details$', views.all_deployment_details),
    url(r'^alibaba/get-all-secret-details$', views.all_secret_details),
    url(r'^alibaba/get-all-node-details$', views.all_node_details),
    url(r'^alibaba/get-all-service-details$', views.all_service_details),
    url(r'^alibaba/get-all-cron-job-details$', views.all_cron_job_details),
    url(r'^alibaba/get-all-job-details$', views.all_job_details),
    url(r'^alibaba/get-all-storage-class-details$', views.all_storage_class_details),
    url(r'^alibaba/get-all-replication-controller-details$', views.all_replication_controller_details),
    url(r'^alibaba/get-all-stateful-set-details$', views.all_stateful_sets_details),
    url(r'^alibaba/get-all-replica-set-details$', views.all_replica_sets_details),
    url(r'^alibaba/get-all-daemon-set-details$', views.all_daemon_set_details),
    url(r'^alibaba/get-all-config-maps-details$', views.all_config_map_details),
    url(r'^alibaba/get-all-ingress-details$', views.all_ingress_details),
    url(r'^alibaba/create-application$', views.create_app),
    url(r'^alibaba/create-kubernetes-cluster$', views.create_kubernetes_cluster),
    url(r'^alibaba/delete-kubernetes-cluster$', views.delete_kubernetes_cluster),
]

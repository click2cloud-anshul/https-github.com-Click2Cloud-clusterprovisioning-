# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your tests here.
from cluster.kuberenetes.operations import Kubernetes_Operations


def all_resources():
    k8s_obj = Kubernetes_Operations(configuration_yaml='<config_file_path>')
    flag, token = k8s_obj.get_token()
    print token
    flag, result = k8s_obj.get_all_resources(cluster_url='<kubernetes_cluster_endpoint>',
                                             token=token)
    print result


def all_pods():
    k8s_obj = Kubernetes_Operations(configuration_yaml='<config_file_path>')
    flag, token = k8s_obj.get_token()
    print token
    flag, result = k8s_obj.get_pods(cluster_url='<kubernetes_cluster_endpoint>',
                                    token=token)
    print result


def all_deployments():
    k8s_obj = Kubernetes_Operations(configuration_yaml='<config_file_path>')
    flag, token = k8s_obj.get_token()
    print token
    flag, result = k8s_obj.get_deployments(cluster_url='<kubernetes_cluster_endpoint>',
                                           token=token)
    print result

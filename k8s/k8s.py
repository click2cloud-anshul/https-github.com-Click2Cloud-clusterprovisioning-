import base64
import json
from os import path

import yaml
import paramiko
from kubernetes import client
from kubernetes.client import Configuration
from kubernetes.config import kube_config
import os


class K8s(object):
    def __init__(self, configuration_yaml):
        self.configuration_yaml = configuration_yaml
        self._configuration_yaml = None

    @property
    def config(self):
        with open(self.configuration_yaml, 'r') as f:
            if self._configuration_yaml is None:
                yaml.warnings({'YAMLLoadWarning': False})
                self._configuration_yaml = yaml.load(f)
        return self._configuration_yaml

    @property
    def clientCoreV1(self):
        k8_loader = kube_config.KubeConfigLoader(self.config)
        call_config = type.__call__(Configuration)
        k8_loader.load_and_set(call_config)
        Configuration.set_default(call_config)
        return client.CoreV1Api()

    def clientAppsV1(self):
        k8_loader = kube_config.KubeConfigLoader(self.config)
        call_config = type.__call__(Configuration)
        k8_loader.load_and_set(call_config)
        Configuration.set_default(call_config)
        return client.AppsV1Api()

    def cluster_role(self, body=None):
        k8_loader = kube_config.KubeConfigLoader(self.config)
        call_config = type.__call__(Configuration)
        k8_loader.load_and_set(call_config)
        Configuration.set_default(call_config)
        return client.apis.RbacAuthorizationV1Api().create_cluster_role_with_http_info(body=body)

    def cluster_role_binding(self, body=None):
        k8_loader = kube_config.KubeConfigLoader(self.config)
        call_config = type.__call__(Configuration)
        k8_loader.load_and_set(call_config)
        Configuration.set_default(call_config)
        return client.apis.RbacAuthorizationV1Api().create_cluster_role_binding_with_http_info(body=body)

    def get_token(self, clusters_folder_directory=None):

        try:
            flag, token = check_for_token(self)
            if flag == 2:
                return True, token
            elif flag == 1:
                return False, ""
            else:
                os.chdir(os.path.join(clusters_folder_directory, 'clusters'))
                with open(path.join(path.dirname(__file__), r"" + os.path.join(clusters_folder_directory,
                                                                               'clusters',
                                                                               "namespace.json"))) as namespace:
                    body = yaml.safe_load(namespace)
                    self.clientCoreV1.create_namespace_with_http_info(body=body)
                    # print (namespace)

                with open(path.join(path.dirname(__file__), r"" + os.path.join(clusters_folder_directory,
                                                                               'clusters', "sa1.json"))) as sa1:
                    body = yaml.safe_load(sa1)
                    namespace = 'click2cloud-ns'
                    self.clientCoreV1.create_namespaced_service_account_with_http_info(body=body,
                                                                                       namespace=namespace)
                    # print (service_account)

                with open(path.join(path.dirname(__file__), r"" + os.path.join(clusters_folder_directory,
                                                                               'clusters', "sa2.json"))) as sa2:
                    body = yaml.safe_load(sa2)
                    namespace = 'click2cloud-ns'
                    self.clientCoreV1.create_namespaced_service_account_with_http_info(body=body,
                                                                                       namespace=namespace)
                    # print (service_account)

                with open(path.join(path.dirname(__file__), r"" + os.path.join(clusters_folder_directory,
                                                                               'clusters',
                                                                               "cluster-role.json"))) as cluster_role:
                    body = yaml.safe_load(cluster_role)
                    self.cluster_role(body=body)
                    # print (cluster_role)
                #
                with open(path.join(path.dirname(__file__), r"" + os.path.join(clusters_folder_directory,
                                                                               'clusters',
                                                                               "cluster-role-binding1.json"))) as cluster_role_binding1:
                    body = yaml.safe_load(cluster_role_binding1)
                    self.cluster_role_binding(body=body)
                    # print (cluster_role_binding)

                with open(path.join(path.dirname(__file__), r"" + os.path.join(clusters_folder_directory,
                                                                               'clusters',
                                                                               "cluster-role-binding2.json"))) as cluster_role_binding2:
                    body = yaml.safe_load(cluster_role_binding2)
                    self.cluster_role_binding(body=body)
                    # print (cluster_role_binding)

                name = 'click2cloud-sa-admin'
                namespace = 'click2cloud-ns'
                service_account = self.clientCoreV1.read_namespaced_service_account(name=name, namespace=namespace)
                # secret = kube_one.clientCoreV1.read_namespaced_secret(name, namespace)
                # service_account_json._secrets
                # service_account_json['']
                secrets_list_for_namespace = service_account._secrets
                for secret in secrets_list_for_namespace:
                    if str(secret._name).__contains__('click2cloud-sa-admin'):
                        secret = self.clientCoreV1.read_namespaced_secret(str(secret._name), namespace)
                        return True, base64.b64decode(secret.data['token'])
        except Exception:
            return False, 'Unable to create token'


def check_for_token(kube_one=None):
    try:
        name = 'click2cloud-sa-admin'
        namespace = 'click2cloud-ns'
        service_account = kube_one.clientCoreV1.read_namespaced_service_account(name=name, namespace=namespace)
        secrets_list_for_namespace = service_account._secrets
        for secret in secrets_list_for_namespace:
            if str(secret._name).__contains__('click2cloud-sa-admin'):
                secret = kube_one.clientCoreV1.read_namespaced_secret(str(secret._name), namespace)
                return 2, base64.b64decode(secret.data['token'])
    except Exception as e:
        try:
            if str(json.loads(e.body)['message']).__contains__('"click2cloud-sa-admin" not found'):
                return 0, None
        except Exception:
            return 1, None

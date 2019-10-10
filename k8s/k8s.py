import base64
import json
from os import path

import requests
import yaml
from kubernetes import client, utils
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

    def create_from_yaml(self, yaml_file=None):
        k8_loader = kube_config.KubeConfigLoader(self.config)
        call_config = type.__call__(Configuration)
        try:
            k8_loader.load_and_set(call_config)
        except Exception as e:
            return 0, e
        Configuration.set_default(call_config)
        k8s_client = client.api_client.ApiClient()
        exception_list = []
        names_list = []
        try:
            if os.stat(path.abspath(yaml_file)).st_size == 0 or not os.path.exists(path.abspath(yaml_file)):
                raise Exception
            with open(path.abspath(yaml_file)) as f:
                yml_document_all = yaml.safe_load_all(f)
                for yml_document in yml_document_all:
                    if "List" in yml_document["kind"]:
                        for yml_object in yml_document["items"]:
                            names_list.append(yml_object['metadata']['name'])
                    else:
                        names_list.append(yml_document['metadata']['name'])
            try:
                utils.create_from_yaml(k8s_client=k8s_client, yaml_file=yaml_file)
                return -1, exception_list, names_list
            except Exception as e:
                try:
                    for api_exceptionse in e.api_exceptions:
                        exception_from_create = json.loads(api_exceptionse.body)
                        string_to_append = ''
                        if 'details' in exception_from_create:
                            if 'group' in exception_from_create['details']:
                                string_to_append = exception_from_create['details']['group']
                            if 'kind' in exception_from_create['details']:
                                if len(string_to_append) > 0:
                                    string_to_append = string_to_append + '.'
                                string_to_append = string_to_append + exception_from_create['details']['kind']
                            if 'name' in exception_from_create['details']:
                                if len(string_to_append) > 0:
                                    string_to_append = string_to_append + '.'
                                string_to_append = string_to_append + exception_from_create['details']['name']
                        exception_list.append(string_to_append + ' ' + exception_from_create['reason'])
                    return 1, exception_list, names_list
                except Exception:
                    return 2, None, None
        except Exception:
            return 0, None, None

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

    def get_pods(self, cluster_url=None, token=None):
        try:
            url = cluster_url + "/api/v1/pods"
            headers = {
                'Authorization': "Bearer " + token,
            }
            response = requests.request("GET", url, headers=headers, verify=False)
            return True, json.loads(response.text)
        except Exception:
            print False, 'Max retries exceeded with url ' + cluster_url

    def get_secrets(self, cluster_url=None, token=None):
        try:
            url = cluster_url + "/api/v1/secrets"
            headers = {
                'Authorization': "Bearer " + token,
            }
            response = requests.request("GET", url, headers=headers, verify=False)
            return True, json.loads(response.text)
        except Exception:
            print False, 'Max retries exceeded with url ' + cluster_url

    def get_nodes(self, cluster_url=None, token=None):
        try:
            url = cluster_url + "/api/v1/nodes"
            headers = {
                'Authorization': "Bearer " + token,
            }
            response = requests.request("GET", url, headers=headers, verify=False)
            return True, json.loads(response.text)
        except Exception:
            print False, 'Max retries exceeded with url ' + cluster_url

    def get_deployments(self, cluster_url=None, token=None):
        try:
            url = cluster_url + "/apis/apps/v1/deployments"
            headers = {
                'Authorization': "Bearer " + token,
            }
            response = requests.request("GET", url, headers=headers, verify=False)
            return True, json.loads(response.text)
        except Exception:
            print False, 'Max retries exceeded with url ' + cluster_url

    def get_namespaces(self, cluster_url=None, token=None):
        try:
            url = cluster_url + "/api/v1/namespaces"
            headers = {
                'Authorization': "Bearer " + token,
            }
            response = requests.request("GET", url, headers=headers, verify=False)
            return True, json.loads(response.text)
        except Exception:
            print False, 'Max retries exceeded with url ' + cluster_url

    def get_persistent_volume_claims(self, cluster_url=None, token=None):
        try:
            url = cluster_url + "/api/v1/persistentvolumeclaims"
            headers = {
                'Authorization': "Bearer " + token,
            }
            response = requests.request("GET", url, headers=headers, verify=False)
            return True, json.loads(response.text)
        except Exception:
            print False, 'Max retries exceeded with url ' + cluster_url

    def get_persistent_volumes(self, cluster_url=None, token=None):
        try:
            url = cluster_url + "/api/v1/persistentvolumes"
            headers = {
                'Authorization': "Bearer " + token,
            }
            response = requests.request("GET", url, headers=headers, verify=False)
            return True, json.loads(response.text)
        except Exception:
            print False, 'Max retries exceeded with url ' + cluster_url

    def get_services(self, cluster_url=None, token=None):
        try:
            url = cluster_url + "/api/v1/services"
            headers = {
                'Authorization': "Bearer " + token,
            }
            response = requests.request("GET", url, headers=headers, verify=False)
            return True, json.loads(response.text)
        except Exception:
            print False, 'Max retries exceeded with url ' + cluster_url

    def get_roles(self, cluster_url=None, token=None):
        try:
            url = cluster_url + "/apis/rbac.authorization.k8s.io/v1/roles"
            headers = {
                'Authorization': "Bearer " + token,
            }
            response = requests.request("GET", url, headers=headers, verify=False)

            url = cluster_url + "/apis/rbac.authorization.k8s.io/v1/clusterroles"
            headers = {
                'Authorization': "Bearer " + token,
            }
            response1 = requests.request("GET", url, headers=headers, verify=False)
            cluster_roles_list = json.loads(response1.text)
            roles_list = json.loads(response.text)
            return True, cluster_roles_list, roles_list
        except Exception:
            print False, 'Max retries exceeded with url ' + cluster_url, ''

    def get_storageclasses(self, cluster_url=None, token=None):
            try:
                url = cluster_url + "/apis/storage.k8s.io/v1/storageclasses"
                headers = {
                    'Authorization': "Bearer " + token,
                }
                response = requests.request("GET", url, headers=headers, verify=False)
                return True, json.loads(response.text)
            except Exception:
                print False, 'Max retries exceeded with url ' + cluster_url

    def get_cronjobs(self, cluster_url=None, token=None):
            try:
                url = cluster_url + "/apis/batch/v1beta1/cronjobs"
                headers = {
                    'Authorization': "Bearer " + token,
                }
                response = requests.request("GET", url, headers=headers, verify=False)
                return True, json.loads(response.text)
            except Exception:
                print False, 'Max retries exceeded with url ' + cluster_url

    def get_jobs(self, cluster_url=None, token=None):
            try:
                url = cluster_url + "/apis/batch/v1/jobs"
                headers = {
                    'Authorization': "Bearer " + token,
                }
                response = requests.request("GET", url, headers=headers, verify=False)
                return True, json.loads(response.text)
            except Exception:
                print False, 'Max retries exceeded with url ' + cluster_url

    def get_daemon_sets(self, cluster_url=None, token=None):
            try:
                url = cluster_url + "/apis/apps/v1/daemonsets"
                headers = {
                    'Authorization': "Bearer " + token,
                }
                response = requests.request("GET", url, headers=headers, verify=False)
                return True, json.loads(response.text)
            except Exception:
                print False, 'Max retries exceeded with url ' + cluster_url

    def get_replica_sets(self, cluster_url=None, token=None):
            try:
                url = cluster_url + "/apis/apps/v1/replicasets"
                headers = {
                    'Authorization': "Bearer " + token,
                }
                response = requests.request("GET", url, headers=headers, verify=False)
                return True, json.loads(response.text)
            except Exception:
                print False, 'Max retries exceeded with url ' + cluster_url

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

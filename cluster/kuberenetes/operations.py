import base64
import json
from os import path

import requests
import yaml
from kubernetes import client, utils
from kubernetes.client import Configuration
from kubernetes.config import kube_config
import os

from clusterProvisioningClient.settings import BASE_DIR


class Kubernetes_Operations(object):
    def __init__(self, configuration_yaml):
        """
        construtor for kubernetes operation class
        :param configuration_yaml:
        """
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

    def get_token(self):
        """
        Generates the token for accessing kubernetes objects
        :return:
        """
        error = False
        response = None
        try:
            flag, token = self.check_for_token()
            if flag == 2:
                # if token for click2cloud-sa-admin is found
                error = False
                response = token

            elif flag == 1:
                # if cluster is unreachable
                raise Exception('Cluster is unreachable')

            else:
                # if service account not found
                path = os.path.join(BASE_DIR, 'cluster', 'dumps')
                if os.path.exists(os.path.join(path, 'namespace.json')):
                    with open(r"" + os.path.join(path, 'namespace.json')) as namespace:
                        body = yaml.safe_load(namespace)
                        self.clientCoreV1.create_namespace_with_http_info(body=body)

                else:
                    raise Exception('Unable to load the file namespace.json')

                if os.path.exists(os.path.join(path, 'service-account.json')):
                    with open(r"" + os.path.join(path, 'service-account.json')) as sa1:
                        body = yaml.safe_load(sa1)
                        namespace = 'click2cloud-ns'
                        self.clientCoreV1.create_namespaced_service_account_with_http_info(body=body,
                                                                                           namespace=namespace)
                else:
                    raise Exception('Unable to load the file service-account.json')

                if os.path.exists(os.path.join(path, 'cluster-role.json')):
                    with open(r"" + os.path.join(path, 'cluster-role.json')) as cluster_role:
                        body = yaml.safe_load(cluster_role)
                        self.cluster_role(body=body)
                else:
                    raise Exception('Unable to load the file cluster-role.json')

                if os.path.exists(os.path.join(path, 'cluster-role-binding1.json')):
                    with open(r"" + os.path.join(path, 'cluster-role-binding1.json')) as cluster_role_binding1:
                        body = yaml.safe_load(cluster_role_binding1)
                        self.cluster_role_binding(body=body)
                else:
                    raise Exception('Unable to load the file cluster-role-binding1.json')

                if os.path.exists(os.path.join(path, 'cluster-role-binding2.json')):
                    with open(r"" + os.path.join(path, 'cluster-role-binding2.json')) as cluster_role_binding2:
                        body = yaml.safe_load(cluster_role_binding2)
                        self.cluster_role_binding(body=body)
                else:
                    raise Exception('Unable to load the file cluster-role-binding2.json')

                flag, token = self.check_for_token()
                if flag == 2:
                    # if token for click2cloud-sa-admin is found
                    error = False
                    response = token

                elif flag == 1:
                    # if cluster is unreachable
                    raise Exception('Cluster is unreachable')

                else:
                    raise Exception('Unable to create token')

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def check_for_token(self):
        """
        checks for the token if it already exists
        :return:
        """
        try:
            name = 'click2cloud-sa-admin'
            namespace = 'click2cloud-ns'
            flag_number = None
            namespace_secrets = self.clientCoreV1.read_namespaced_service_account(name=name, namespace=namespace)
            secrets_list_for_namespace = namespace_secrets._secrets
            for secret in secrets_list_for_namespace:
                if 'click2cloud-sa-admin' in str(secret._name):
                    secret = self.clientCoreV1.read_namespaced_secret(str(secret._name), namespace)
                    # returns 2 if token for click2cloud-sa-admin is found
                    flag_number = 2
                    return flag_number, base64.b64decode(secret.data['token'])
        except Exception as e:
            try:
                if '"click2cloud-sa-admin" not found' in str(json.loads(e.body)['message']):
                    # returns 0 if service account not found
                    flag_number = 0
                    return flag_number, None
            except Exception as e:
                # returns 1 if cluster is unreachable
                flag_number = 1
                return flag_number, e.message

    def get_pods(self, cluster_url=None, token=None):
        """
        it retrives the information for pods
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/api/v1/pods' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            error = False
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

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

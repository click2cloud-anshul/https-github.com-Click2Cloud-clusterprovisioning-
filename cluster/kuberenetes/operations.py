import base64
import json
import uuid
from os import path

import requests
import yaml
from kubernetes import client, utils
from kubernetes.client import Configuration
from kubernetes.config import kube_config
import os

from kubernetes.utils import FailToCreateError
from yaml.scanner import ScannerError

from clusterProvisioningClient.settings import BASE_DIR


def create_file_for_app_deploy(cluster_id, data):
    """
        create the yaml file using data for deploy app on kubernetes cluster with its id as a directory name
        :param cluster_id:
        :param data:
        :return:
        """
    error = False
    response = None
    try:
        file_name = uuid.uuid1().hex
        path = os.path.join(BASE_DIR, 'cluster', 'dumps', cluster_id)
        if not os.path.exists(path):
            os.makedirs(path)
        data = base64.b64decode(data)
        with open(os.path.join(path, file_name), "w+") as outfile:
            outfile.write(data)
        path = os.path.join(BASE_DIR, 'cluster', 'dumps', cluster_id, file_name)
        if os.stat(path).st_size == 0 or not os.path.exists(path):
            raise Exception('Yaml or json file is invalid')
        response = path
    except Exception as e:
        response = e.message
        if isinstance(e, TypeError):
            response = 'Incorrect Padding'
        error = True

    finally:
        return error, response


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
        """
        client core method of kubernetes
        :return:
        """
        k8_loader = kube_config.KubeConfigLoader(self.config)
        call_config = type.__call__(Configuration)
        k8_loader.load_and_set(call_config)
        Configuration.set_default(call_config)
        return client.CoreV1Api()

    def clientAppsV1(self):
        """
        client Apps for kubernetes apps
        :return:
        """
        k8_loader = kube_config.KubeConfigLoader(self.config)
        call_config = type.__call__(Configuration)
        k8_loader.load_and_set(call_config)
        Configuration.set_default(call_config)
        return client.AppsV1Api()

    def cluster_role(self, body=None):
        """
        cluster roles for the kubernetes
        :param body:
        :return:
        """
        k8_loader = kube_config.KubeConfigLoader(self.config)
        call_config = type.__call__(Configuration)
        k8_loader.load_and_set(call_config)
        Configuration.set_default(call_config)
        return client.apis.RbacAuthorizationV1Api().create_cluster_role_with_http_info(body=body)

    def cluster_role_binding(self, body=None):
        """
        cluster role binding of kubernetes
        :param body:
        :return:
        """
        k8_loader = kube_config.KubeConfigLoader(self.config)
        call_config = type.__call__(Configuration)
        k8_loader.load_and_set(call_config)
        Configuration.set_default(call_config)
        return client.apis.RbacAuthorizationV1Api().create_cluster_role_binding_with_http_info(body=body)

    def create_from_yaml(self, cluster_id, data):
        """
        Creates a new app on kubernetes cluster using data
        :param cluster_id: 
        :param data:
        :return: 
        """
        app = {
            'app_name': None,
            'app_kind': None
        }
        response = None
        error = False

        try:
            error, response = create_file_for_app_deploy(cluster_id, data)

            if not error:
                yaml_file_path = response
                kube_loader = kube_config.KubeConfigLoader(self.config)
                call_config = type.__call__(Configuration)
                try:
                    kube_loader.load_and_set(call_config)
                except Exception:
                    # If cluster is unavailable or unreachable.
                    raise Exception('Cluster is unreachable')
                Configuration.set_default(call_config)
                kube_client = client.api_client.ApiClient()
                # kubernetes client object
                exception = None
                flag = False
                try:
                    # App creation on kubernetes cluster
                    utils.create_from_yaml(k8s_client=kube_client, yaml_file=yaml_file_path)
                    flag = True
                except Exception as e:
                    exception = e
                    flag = False
                if flag:
                    # if provided yaml or json is valid
                    with open(path.abspath(yaml_file_path)) as file:
                        yml_document_all = yaml.safe_load_all(file)
                        created_app_list = []
                        for yml_document in yml_document_all:
                            if 'List' in yml_document.get('kind'):
                                for yml_object in yml_document.get('items'):
                                    app.update({
                                        'app_name': yml_object.get('metadata').get('name'),
                                        'app_kind': yml_document.get('kind')
                                    })
                            else:
                                app.update({
                                    'app_name': yml_document.get('metadata').get('name'),
                                    'app_kind': yml_document.get('kind')
                                })
                            created_app_list.append(app)
                            error = False
                            response = created_app_list
                else:
                    # if provided yaml or json is invalid
                    error = True
                    try:

                        if isinstance(exception, KeyError):
                            response = 'Key is missing ' + exception.message
                        elif isinstance(exception, ValueError):
                            response = 'Value is missing ' + exception.message
                        elif isinstance(exception, FailToCreateError):
                            # response_dict.update({'error': e.api_exceptions})
                            api_exception_list = exception.api_exceptions
                            failed_list = []
                            for api_exceptions in api_exception_list:
                                json_error_body = json.loads(api_exceptions.body)
                                if 'message' in json_error_body:
                                    failed_list.append(json_error_body.get('message'))
                            response = failed_list
                        elif isinstance(exception, ScannerError):
                            response = 'Invalid yaml/json'
                        else:
                            response = exception.message
                    except Exception as e:
                        response = e.message
            else:
                # if yaml file is not created.
                raise Exception(response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

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
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_namespaces(self, cluster_url=None, token=None):
        """
            it retrives the information for namespaces
            :param cluster_url:
            :param token:
            :return:
        """
        error = False
        response = None
        try:
            url = '%s/api/v1/namespaces' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_roles(self, cluster_url=None, token=None):
        """
            it retrives the information for roles and cluster roles
            :param cluster_url:
            :param token:
            :return:
        """

        error = False
        response = None
        try:
            url = '%s/apis/rbac.authorization.k8s.io/v1/roles' % cluster_url
            headers = {
                'Authorization': 'Bearer ' + token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            url = '%s/apis/rbac.authorization.k8s.io/v1/clusterroles' % cluster_url
            headers = {
                'Authorization': 'Bearer ' + token,
            }
            response_cluster_roles = requests.request('GET', url, headers=headers, verify=False)
            if response_cluster_roles.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response_cluster_roles.text).get('message')))
            cluster_roles_list = json.loads(response_cluster_roles.text)
            roles_list = json.loads(response.text)
            response = {'cluster_role_list': cluster_roles_list,
                        'role_list': roles_list}
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_persistent_volumes(self, cluster_url=None, token=None):
        """
            it retrives the information for persistent volumes
            :param cluster_url:
            :param token:
            :return:
        """
        error = False
        response = None
        try:
            url = '%s/api/v1/persistentvolumes' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_persistent_volume_claims(self, cluster_url=None, token=None):
        """
        it retrives the information for persistent volumes claims
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/api/v1/persistentvolumeclaims' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_secrets(self, cluster_url=None, token=None):
        """
        it retrives the information for secrets
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/api/v1/secrets' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_nodes(self, cluster_url=None, token=None):
        """
        it retrives the information for nodes
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/api/v1/nodes' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_deployments(self, cluster_url=None, token=None):
        """
        it retrives the information for deployments
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/apis/apps/v1/deployments' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_services(self, cluster_url=None, token=None):
        """
        it retrives the information for services
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/api/v1/services' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_cron_jobs(self, cluster_url=None, token=None):
        """
        it retrives the information for cron jobs
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/apis/batch/v1beta1/cronjobs' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_jobs(self, cluster_url=None, token=None):
        """
        it retrives the information for jobs
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/apis/batch/v1/jobs' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_replication_controllers(self, cluster_url=None, token=None):
        """
        it retrives the information for replication controller
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/api/v1/replicationcontrollers' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_storage_class(self, cluster_url=None, token=None):
        """
        it retrives the information for storage class
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/apis/storage.k8s.io/v1/storageclasses' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_stateful_sets(self, cluster_url=None, token=None):
        """
        it retrives the information for stateful sets
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/apis/apps/v1/statefulsets' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_replica_sets(self, cluster_url=None, token=None):
        """
        it retrives the information for replica_sets
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/apis/apps/v1/replicasets' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_daemon_sets(self, cluster_url=None, token=None):
        """
        it retrives the information for daemon sets
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/apis/apps/v1/daemonsets' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_config_maps(self, cluster_url=None, token=None):
        """
        it retrives the information for config maps
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/api/v1/configmaps' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_ingress_details(self, cluster_url=None, token=None):
        """
        it retrives the information for ingress
        :param cluster_url:
        :param token:
        :return:
        """
        error = False
        response = None
        try:
            url = '%s/apis/networking.k8s.io/v1beta1/ingresses' % cluster_url
            headers = {
                'Authorization': 'Bearer %s' % token,
            }
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code != 200:
                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
            response = json.loads(response.text)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

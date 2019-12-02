import base64
import json
import uuid
from collections import defaultdict
from os import path

import requests
import yaml
from kubernetes import client, utils
from kubernetes.client import Configuration
from kubernetes.config import kube_config
import os

from kubernetes.utils import FailToCreateError
from pint import UnitRegistry
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
        path = os.path.join(BASE_DIR, 'config_dumps', cluster_id)
        data = base64.b64decode(data)
        with open(os.path.join(path, file_name), "w+") as outfile:
            outfile.write(data)
        path = os.path.join(BASE_DIR, 'config_dumps', cluster_id, file_name)
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

    def create_from_yaml(self, cluster_id, data, namespace):
        """
        Creates a new app on kubernetes cluster using data
        :param cluster_id: 
        :param data:
        :param namespace:
        :return: 
        """
        app = {
            'name': None,
            'kind': None
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
                    utils.create_from_yaml(k8s_client=kube_client, yaml_file=yaml_file_path, namespace=namespace)
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
                                        'name': yml_object.get('metadata').get('name'),
                                        'kind': yml_document.get('kind')
                                    })
                            else:
                                app.update({
                                    'name': yml_document.get('metadata').get('name'),
                                    'kind': yml_document.get('kind')
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
                path = os.path.join(BASE_DIR, 'auth_templates')
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

    def delete_object_with_namespace(self, objects, name, namespace, cluster_url, token):
        """
        This method delete the required object from kubernetes cluster
        :param objects:
        :param name:
        :param namespace:
        :param cluster_url
        :param token
        :return:
        """
        error = False
        response = None
        try:
            access_flag_for_delete_action = True
            for object in objects.get('items'):
                if 'metadata' in object and object.get('metadata') is not None:
                    if object.get('metadata').get('name') is not None:
                        if object.get('metadata').get('namespace') is not None:
                            object_name = str(object.get('metadata').get('name'))
                            object_name_namespace = str(object.get('metadata').get('namespace'))
                            if name == object_name and namespace == object_name_namespace:
                                access_flag_for_delete_action = False
                                self_link = object.get('metadata').get('selfLink')
                                url = '%s%s' % (cluster_url, self_link)
                                headers = {
                                    'Authorization': 'Bearer %s' % token,
                                }
                                response = requests.request('DELETE', url, headers=headers, verify=False)
                                if response.status_code != 200:
                                    raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
                                response = json.loads(response.text)
                                break
                        else:
                            # if namespaces is not present
                            raise Exception('Namespace is not present for Object')
                    else:
                        # if name is not present
                        raise Exception('Name is not present for Object')
                else:
                    # metadata is not present
                    raise Exception('Metadata is not present for Object')
            if access_flag_for_delete_action:
                # if object and object's namespace does not matches with requested name and namespaces
                raise Exception(
                    'Object %s is not present for that namespace %s' % (name, namespace))
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_object_without_namespace(self, objects, name, cluster_url, token):
        """
        This method delete the required object from kubernetes cluster
        :param objects:
        :param name:
        :param cluster_url
        :param token
        :return:
        """
        error = False
        response = None
        try:
            access_flag_for_delete_action = True
            for object in objects.get('items'):
                if 'metadata' in object and object.get('metadata') is not None:
                    if object.get('metadata').get('name') is not None:
                        object_name = str(object.get('metadata').get('name'))
                        if name == object_name:
                            access_flag_for_delete_action = False
                            self_link = object.get('metadata').get('selfLink')
                            url = '%s%s' % (cluster_url, self_link)
                            headers = {
                                'Authorization': 'Bearer %s' % token,
                            }
                            response = requests.request('DELETE', url, headers=headers, verify=False)
                            if response.status_code != 200:
                                raise Exception('for url %s : %s' % (url, json.loads(response.text).get('message')))
                            response = json.loads(response.text)
                            break
                    else:
                        # if name is not present
                        raise Exception('Name is not present for object')
                else:
                    # metadata is not present
                    raise Exception('Metadata is not present for object')
            if access_flag_for_delete_action:
                # if object does not matches with requested name
                raise Exception(
                    'Object %s is not present' % name)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def compute_allocated_resources(self):
        """
        Calculate the resouce allocation for the nodes in the given cluster
        e.g. cpu and memory
        :param :
        :return:
        """
        error = False
        response = None
        try:

            ureg = UnitRegistry()
            path = os.path.join(BASE_DIR, 'auth_templates', 'resource-allocated-units')
            ureg.load_definitions(path)
            quantity_obj = ureg.Quantity
            node_list = []
            for node in self.clientCoreV1.list_node().items:
                node_info = {}
                node_name = node.metadata.name
                allocatable = node.status.allocatable
                max_pods = int(int(allocatable.get('pods')) * 1.5)
                field_selector = ('status.phase!=Succeeded,status.phase!=Failed,' +
                                  'spec.nodeName=' + node_name)
                pods = self.clientCoreV1.list_pod_for_all_namespaces(limit=max_pods,
                                                                     field_selector=field_selector).items
                # compute the allocated resources
                cpureqs, cpulmts, memreqs, memlmts = [], [], [], []
                pod_count = 0
                for pod in pods:
                    for container in pod.spec.containers:
                        res = container.resources
                        reqs = defaultdict(lambda: 0, res.requests or {})
                        lmts = defaultdict(lambda: 0, res.limits or {})

                        # for cpu reqs for each container of a pod
                        if reqs.get('cpu') is 0 or reqs.get('cpu') is None:
                            # if the value is 0 or None
                            cpureqs.append(0)
                        elif quantity_obj(reqs.get('cpu')).unitless:
                            # if the value is only in string e.g. '1'
                            temp = quantity_obj('%sm' % eval(reqs.get('cpu') + '*1000'))
                            cpureqs.append(temp)
                        else:
                            # if the value is only in string e.g. '100m'
                            cpureqs.append(quantity_obj(reqs.get('cpu')))

                        # for cpu limits for each container of a pod
                        if lmts.get('cpu') is 0 or lmts.get('cpu') is None:
                            # if the value is 0 or None
                            cpulmts.append(0)
                        elif quantity_obj(lmts.get('cpu')).unitless:
                            # if the value is only in string e.g. '1'
                            temp = quantity_obj('%sm' % eval(lmts.get('cpu') + '*1000'))
                            cpulmts.append(temp)
                        else:
                            # if the value is only in string e.g. '100m'
                            cpulmts.append(quantity_obj(lmts.get('cpu')))

                        # for memory requests for each container of a pod
                        if reqs.get('memory') is 0 or reqs.get('memory') is None:
                            # if the value is 0 or None
                            memreqs.append(0)
                        elif quantity_obj(reqs.get('memory')).unitless:
                            # if the value is only in string e.g. '1'
                            temp = quantity_obj('%sm' % eval(reqs.get('memory') + '*1000'))
                            memreqs.append(temp)
                        else:
                            # if the value is only in string e.g. '100Mi'
                            memreqs.append(quantity_obj(reqs.get('memory')))

                        # for memory limits for each container of a pod
                        if lmts.get('memory') is 0 or lmts.get('memory') is None:
                            # if the value is 0 or None
                            memlmts.append(0)
                        elif quantity_obj(lmts.get('memory')).unitless:
                            # if the value is only in string e.g. '1'
                            temp = quantity_obj('%sm' % eval(lmts.get('memory') + '*1000'))
                            memlmts.append(temp)
                        else:
                            # if the value is only in string e.g. '100Mi'
                            memlmts.append(quantity_obj(lmts.get('memory')))

                    pod_count = pod_count + 1
                node_info.update({
                    'pod_count': pod_count,
                    'cpu_requests': str(sum(cpureqs)),
                    'cpu_limits': str(sum(cpulmts)),
                    'memory_requests': str(sum(memreqs)),
                    'memory_limits': str(sum(memlmts)),
                    'node_name': str(node_name)
                })
                node_list.append(node_info)

            response = node_list
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

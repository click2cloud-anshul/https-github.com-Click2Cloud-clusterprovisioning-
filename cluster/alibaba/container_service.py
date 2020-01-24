import json
import os

import yaml
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from cluster.kuberenetes.operations import Kubernetes_Operations
from cluster.others.miscellaneous_operation import get_db_info_using_cluster_id, create_cluster_config_file, \
    insert_or_update_cluster_details, get_cluster_config_details, insert_or_update_cluster_config_details
from clusterProvisioningClient.settings import BASE_DIR

config_dumps_path = os.path.join(BASE_DIR, 'config_dumps')


def get_labels_from_items(item_list):
    """
    This function will extracts all the labels from labels
    :param item_list:
    :return:
    """
    label_dict = {}
    for element in item_list:
        # if metadata is empty or not present then labels
        # will be empty dictionary {}
        if 'metadata' in element and element.get(
                'metadata') is not None:
            # if metadata is empty or not present then labels
            # will be empty dictionary {}
            if 'labels' in element.get('metadata') and \
                    element.get('metadata').get(
                        'labels') is not None:
                for key, value in element.get('metadata').get(
                        'labels').items():
                    if key in label_dict:
                        # Adding the label value
                        if not value in label_dict.get(
                                key):
                            label_dict.get(
                                key).append(value)
                    else:
                        label_dict.update(
                            {key: [value]})
    return label_dict


class Alibaba_CS:
    def __init__(self, ali_access_key, ali_secret_key, region_id):
        """
        constructor for the Alibab_CS classs
        :param ali_access_key:
        :param ali_secret_key:
        :param region_id:
        """
        self.access_key = ali_access_key
        self.secret_key = ali_secret_key
        self.region_id = region_id
        self.retry_counter = 0
        self.clusters_folder_directory = ''

    def create_cluster(self, request_body):
        """
        Create the cluster in the alibaba cloud
        :param request_body:
        :return:
        """
        error = False
        response = None
        try:
            client = AcsClient(self.access_key, self.secret_key, self.region_id)

            request = CommonRequest()
            request.set_accept_format('json')
            request.set_method('POST')
            request.set_protocol_type('https')  # https | http
            request.set_domain('cs.aliyuncs.com')
            request.set_version('2015-12-15')

            request.add_query_param('RegionId', "default")
            request.add_header('Content-Type', 'application/json')
            request.set_uri_pattern('/clusters')

            body = json.dumps(request_body)
            request.set_content(body.encode('utf-8'))

            result = client.do_action_with_exception(request)
            response = json.loads(result)

        except ServerException as e:
            error = True
            error_codes = [400]
            if e.http_status in error_codes:
                error_message_splitted = str(e.message).split('ServerResponseBody: ')
                response = '%s %s' % (
                    'Error while creating cluster.', json.loads(error_message_splitted[1]).get('message'))

            else:
                response = 'Unable to create the cluster'
        except Exception as e:
            error = True
            response = e.message

        finally:
            return error, response

    def delete_cluster(self, cluster_id):
        """
        Delete cluster
        :param cluster_id:
        :return:
        """
        error = False
        response = False
        try:
            client = AcsClient(self.access_key, self.secret_key, self.region_id)

            request = CommonRequest()
            request.set_accept_format('json')
            request.set_method('DELETE')
            request.set_protocol_type('https')  # https | http
            request.set_domain('cs.aliyuncs.com')
            request.set_version('2015-12-15')

            request.add_query_param('RegionId', "default")
            request.add_header('Content-Type', 'application/json')
            request.set_uri_pattern('/clusters/' + cluster_id)
            body = ''''''
            request.set_content(body.encode('utf-8'))

            result = client.do_action_with_exception(request)
            # response is None when cluster is deleted successfully
            if len(result) == 0:
                response = True
            else:
                response = False
        except ServerException as e:
            error = True
            # error_codes = [400]
            if e.http_status == 400:
                error_message_splitted = str(e.message).split('ServerResponseBody: ')
                if len(error_message_splitted) > 1:
                    response = '%s %s' % (
                        'Error while deleting the cluster.', json.loads(error_message_splitted[1]).get('message'))
                else:
                    response = '%s %s' % ('Error while deleting the cluster.', e.message)
            elif e.http_status == 404:
                response = '%s %s' % ('Error while deleting the cluster.', e.message)
            else:
                response = 'Unable to Delete the cluster'
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def check_database_state_and_update(self, cluster):
        """
        check the database state and update cluster info in the database
        :param cluster:
        :return:
        """
        cluster_details = {'cluster_info': cluster}
        error = False
        response = None
        cluster_id = cluster.get('cluster_id')
        try:
            error, response = get_db_info_using_cluster_id(cluster_id)
            if not error:
                # if no data is available for the cluster in db then skip
                if len(response) > 0:
                    if 'failed' in str(cluster.get('state')):
                        for cluster_info_db in response:
                            if 'Initiated' in str(cluster_info_db[5]):
                                cluster_detail = {}
                                cluster_detail.update({
                                    'is_insert': False,
                                    'user_id': cluster_info_db[1],
                                    'provider_id': cluster_info_db[2],
                                    'cluster_id': cluster_id,
                                    'cluster_details': json.dumps(cluster_details),
                                    'status': 'Failed',
                                    'operation': 'created from cloudbrain'
                                })
                                error, response = insert_or_update_cluster_details(cluster_detail)
                    elif 'running' in str(cluster.get('state')):
                        for cluster_info_db in response:
                            if 'Initiated' in str(cluster_info_db[5]):
                                cluster_detail = {}
                                cluster_detail.update({
                                    'is_insert': False,
                                    'user_id': cluster_info_db[1],
                                    'provider_id': cluster_info_db[2],
                                    'cluster_id': cluster_id,
                                    'cluster_details': json.dumps(cluster_details),
                                    'status': 'Running',
                                    'operation': 'created from cloudbrain'
                                })
                                error, response = insert_or_update_cluster_details(cluster_detail)
            else:
                raise Exception(response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def describe_all_clusters(self):
        """
        Describe all the clusters available on the alibaba cloud
        :return:
        """
        error = False
        response = None
        try:
            client = AcsClient(self.access_key, self.secret_key, 'default')

            request = CommonRequest()
            request.set_accept_format('json')
            request.set_method('GET')
            request.set_protocol_type('https')  # https | http
            request.set_domain('cs.aliyuncs.com')
            request.set_version('2015-12-15')

            request.add_query_param('RegionId', "default")
            request.add_header('Content-Type', 'application/json')
            request.set_uri_pattern('/clusters')
            body = ''''''
            request.set_content(body.encode('utf-8'))

            result = client.do_action_with_exception(request)
            response = json.loads(result)
        except ServerException as e:
            error = True
            error_codes = [400]
            if e.http_status in error_codes:
                error_message_splitted = str(e.message).split('ServerResponseBody: ')
                response = '%s %s' % (
                    'Error while creating cluster.', json.loads(error_message_splitted[1]).get('message'))

            else:
                response = 'Unable to access the cluster'
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def describe_cluster_config_token_endpoint(self, cluster_id):
        """
        get the single cluster config and token from cluster_id
        :param cluster_id:
        :return:
        """
        provider = 'Alibaba:Cloud'
        error = False
        response = None
        config_detail = {
            'cluster_id': cluster_id,
            'cluster_public_endpoint': None,
            'cluster_config': None,
            'cluster_token': None,
            'provider': provider,
            'is_insert': False,
            'k8s_object': None
        }
        try:
            error_get_cluster_config_details, response_get_cluster_config_details = get_cluster_config_details(
                provider, cluster_id)
            if not error_get_cluster_config_details:
                if response_get_cluster_config_details is not None:
                    if len(list(response_get_cluster_config_details)) > 0:
                        # if cluster config is present in database
                        config_path = os.path.join(config_dumps_path,
                                                   cluster_id,
                                                   'config')
                        error_create_cluster_config_file, response_create_cluster_config_file = create_cluster_config_file(
                            cluster_id, eval(response_get_cluster_config_details.get('cluster_config')))
                        if not error_create_cluster_config_file:
                            k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                            config_detail.update({'cluster_id': cluster_id,
                                                  'cluster_public_endpoint': response_get_cluster_config_details.get(
                                                      'cluster_public_endpoint'),
                                                  'cluster_config': eval(
                                                      response_get_cluster_config_details.get('cluster_config')),
                                                  'cluster_token': response_get_cluster_config_details.get(
                                                      'cluster_token'),
                                                  'k8s_object': k8_obj})
                        else:
                            raise Exception(response_create_cluster_config_file)
                    else:
                        #  if cluster config is not present in database
                        error_describe_cluster_endpoint, response_describe_cluster_endpoint \
                            = self.describe_cluster_endpoint(cluster_id)
                        if not error_describe_cluster_endpoint:
                            if 'api_server_endpoint' in response_describe_cluster_endpoint:
                                # if cluster has public api server endpoint details blank value can be received
                                if response_describe_cluster_endpoint.get(
                                        'api_server_endpoint') is not None and response_describe_cluster_endpoint.get(
                                    'api_server_endpoint') != '':
                                    # if cluster has public api server endpoint details
                                    error_describe_cluster_config, response_describe_cluster_config = self.describe_cluster_config(
                                        cluster_id)
                                    if not error_describe_cluster_config:
                                        # config is generated from Alibaba Cloud
                                        if 'config' in response_describe_cluster_config:
                                            # Dumping config file
                                            cluster_config = json.dumps(
                                                yaml.load(json.loads(response_describe_cluster_config).get('config'),
                                                          yaml.FullLoader))

                                            error_create_cluster_config_file, response_create_cluster_config_file = create_cluster_config_file(
                                                cluster_id,
                                                json.loads(cluster_config))
                                            if not error_create_cluster_config_file:
                                                # Dumping config file is successful
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error_get_token, response_get_token = k8_obj.get_token()
                                                if not error_get_token:
                                                    # If token is created
                                                    config_detail.update({
                                                        'cluster_public_endpoint': response_describe_cluster_endpoint.get(
                                                            'api_server_endpoint'),
                                                        'cluster_config': json.loads(cluster_config),
                                                        'cluster_token': response_get_token,
                                                        'is_insert': True,
                                                        'k8s_object': k8_obj
                                                    })
                                                    error_insert_or_update_cluster_config_details, \
                                                    response_insert_or_update_cluster_config_details = \
                                                        insert_or_update_cluster_config_details(
                                                            config_detail)
                                                    if error_insert_or_update_cluster_config_details:
                                                        raise Exception(
                                                            response_insert_or_update_cluster_config_details)
                                                else:
                                                    # If cluster's token can not be generated
                                                    raise Exception(response_get_token)
                                            else:
                                                # If cluster's config can not be generated
                                                raise Exception(response_create_cluster_config_file)
                                        else:
                                            # If cluster's config can not be generated
                                            raise Exception('Unable to find cluster config details')
                                    else:
                                        # if unable to generate config from Alibaba Cloud
                                        raise Exception(response_describe_cluster_config)
                                else:
                                    # If cluster api server endpoint key not present in Alibaba response
                                    raise Exception(
                                        'Unable to find cluster public api server endpoint details')
                            else:
                                # If cluster api server endpoint key not present in Alibaba response
                                raise Exception('Unable to find cluster public api server endpoint details')
                        else:
                            # If cluster api server endpoint key not present in Alibaba response
                            raise Exception(response_describe_cluster_endpoint)
                    response = config_detail
            else:
                raise Exception(response_get_cluster_config_details)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def describe_cluster_config(self, cluster_id):
        """
        get the single cluster configuration
        :param cluster_id:
        :return:
        """
        error = False
        response = None
        try:
            client = AcsClient(self.access_key, self.secret_key, 'default')
            request = CommonRequest()
            request.set_accept_format('json')
            request.set_method('GET')
            request.set_protocol_type('https')  # https | http
            request.set_domain('cs.aliyuncs.com')
            request.set_version('2015-12-15')
            request.add_query_param('RegionId', "default")
            request.add_header('Content-Type', 'application/json')
            request.set_uri_pattern('/api/v2/k8s/' + cluster_id + '/user_config')
            body = ''''''
            request.set_content(body.encode('utf-8'))
            response = client.do_action_with_exception(request)
        except ServerException as e:
            error = True
            error_codes = [400]
            if e.http_status in error_codes:
                error_message_splitted = str(e.message).split('ServerResponseBody: ')
                response = '%s %s' % (
                    'Error while creating cluster.', json.loads(error_message_splitted[1]).get('message'))

            else:
                response = 'Unable to access the cluster'
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def describe_cluster_endpoint(self, cluster_id):
        """
        Get the cluster endpoints
        :param cluster_id:
        :return:
        """
        error = False
        response = None
        try:
            client = AcsClient(self.access_key, self.secret_key, 'default')
            request = CommonRequest()
            request.set_accept_format('json')
            request.set_method('GET')
            request.set_protocol_type('https')  # https | http
            request.set_domain('cs.aliyuncs.com')
            request.set_version('2015-12-15')
            request.add_query_param('RegionId', "default")
            request.add_header('Content-Type', 'application/json')
            request.set_uri_pattern('/clusters/' + cluster_id + '/endpoints')
            body = ''''''
            request.set_content(body.encode('utf-8'))
            response = client.do_action_with_exception(request)
            response = json.loads(response)
        except ServerException as e:
            error = True
            error_codes = [400]
            if e.http_status in error_codes:
                error_message_splitted = str(e.message).split('ServerResponseBody: ')
                response = '%s %s' % (
                    'Error while creating cluster.', json.loads(error_message_splitted[1]).get('message'))

            else:
                response = 'Unable to access the cluster'
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_pod_details(self):
        """
        Get the detail of all the pods of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = None
        try:
            error_describe_all_clusters, response_describe_all_clusters = self.describe_all_clusters()
            if not error_describe_all_clusters:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'pod_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_pods, response_get_pods = k8s_obj.get_pods(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_pods:
                                            labels = get_labels_from_items(
                                                response_get_pods.get('items'))
                                            cluster_details.update({
                                                'pod_details': response_get_pods,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_pods})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_namespace_details(self):
        """
        Get the detail of all the namespaces of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error_describe_all_clusters, response_describe_all_clusters = self.describe_all_clusters()
            if not error_describe_all_clusters:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'namespace_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_namespaces, response_get_namespaces = k8s_obj.get_namespaces(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_namespaces:
                                            labels = get_labels_from_items(
                                                response_get_namespaces.get('items'))
                                            cluster_details.update({
                                                'namespace_details': response_get_namespaces,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({
                                                'error': response_get_namespaces})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update(
                                        {'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update(
                                    {'error':
                                         'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_role_details(self):
        """
        Get the detail of all the roles of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error_describe_all_clusters, response_describe_all_clusters = self.describe_all_clusters()
            if not error_describe_all_clusters:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'role_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_roles, response_get_roles = k8s_obj.get_roles(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_roles:
                                            roles_label_dict = get_labels_from_items(
                                                response_get_roles.get('role_list').get('items'))
                                            cluster_details.update({
                                                'role_details': response_get_roles.get('role_list'),
                                                'labels': roles_label_dict
                                            })
                                        else:
                                            cluster_details.update({
                                                'error': response_get_roles})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update(
                                        {'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update(
                                    {'error':
                                         'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_cluster_role_details(self):
        """
        Get the detail of all the roles of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error_describe_all_clusters, response_describe_all_clusters = self.describe_all_clusters()
            if not error_describe_all_clusters:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'cluster_role_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_roles, response_get_roles = k8s_obj.get_roles(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_roles:
                                            cluster_roles_label_dict = get_labels_from_items(
                                                response_get_roles.get('cluster_role_list').get('items'))
                                            cluster_details.update({
                                                'cluster_role_details': response_get_roles.get('cluster_role_list'),
                                                'labels': cluster_roles_label_dict
                                            })
                                        else:
                                            cluster_details.update({
                                                'error': response_get_roles})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update(
                                        {'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update(
                                    {'error':
                                         'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_persistent_volume_details(self):
        """
        Get the detail of all the persistent volumes of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error_describe_all_clusters, response_describe_all_clusters = self.describe_all_clusters()
            if not error_describe_all_clusters:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'persistent_volume_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_persistent_volumes, response_get_persistent_volumes = k8s_obj.get_persistent_volumes(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_persistent_volumes:
                                            labels = get_labels_from_items(
                                                response_get_persistent_volumes.get('items'))
                                            cluster_details.update({
                                                'persistent_volume_details': response_get_persistent_volumes,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_persistent_volumes})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_persistent_volume_claims_details(self):
        """
        Get the detail of all the persistent volume claims of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error_describe_all_clusters, response_describe_all_clusters = self.describe_all_clusters()
            if not error_describe_all_clusters:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'persistent_volume_claim_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_persistent_volume_claims, response_get_persistent_volume_claims = k8s_obj.get_persistent_volume_claims(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_persistent_volume_claims:
                                            labels = get_labels_from_items(
                                                response_get_persistent_volume_claims.get('items'))
                                            cluster_details.update({
                                                'persistent_volume_claim_details': response_get_persistent_volume_claims,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_persistent_volume_claims})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_deployment_details(self):
        """
        Get the detail of all the deployment of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error_describe_all_clusters, response_describe_all_clusters = self.describe_all_clusters()
            if not error_describe_all_clusters:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'deployment_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_deployments, response_get_deployments = k8s_obj.get_deployments(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_deployments:
                                            labels = get_labels_from_items(
                                                response_get_deployments.get('items'))
                                            cluster_details.update({
                                                'deployment_details': response_get_deployments,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_deployments})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_secret_details(self):
        """
        Get the detail of all the secret of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error_describe_all_clusters, response_describe_all_clusters = self.describe_all_clusters()
            if not error_describe_all_clusters:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'secret_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_secrets, response_get_secrets = k8s_obj.get_secrets(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_secrets:
                                            labels = get_labels_from_items(
                                                response_get_secrets.get('items'))
                                            cluster_details.update({
                                                'secret_details': response_get_secrets,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_secrets})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_node_details(self):
        """
        Get the detail of all the node of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error_describe_all_clusters, response_describe_all_clusters = self.describe_all_clusters()
            if not error_describe_all_clusters:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'node_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_nodes, response_get_nodes = k8s_obj.get_nodes(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_nodes:
                                            labels = get_labels_from_items(
                                                response_get_nodes.get('items'))
                                            error_compute_allocated_resources, response_compute_allocated_resources = k8s_obj.compute_allocated_resources()
                                            if not error_compute_allocated_resources:
                                                for node in response_get_nodes.get('items'):
                                                    for item in response_compute_allocated_resources:
                                                        if node.get('metadata').get('name') == item.get(
                                                                'node_name'):
                                                            node.update({'allocated_resources': item})
                                                cluster_details.update({
                                                    'node_details': response_get_nodes,
                                                    'labels': labels
                                                })
                                            else:
                                                cluster_details.update(
                                                    {'error': 'Unable to compute allocated resources'})
                                        else:
                                            cluster_details.update({'error': response_get_nodes})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_service_details(self):
        """
        Get the detail of all the service of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response_describe_all_clusters = self.describe_all_clusters()
            if not error:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'service_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_services, response_get_services = k8s_obj.get_services(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_services:
                                            labels = get_labels_from_items(
                                                response_get_services.get('items'))
                                            cluster_details.update({
                                                'service_details': response_get_services,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_services})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_cron_job_details(self):
        """
        Get the detail of all the cron jobs of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response_describe_all_clusters = self.describe_all_clusters()
            if not error:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'cron_job_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_cron_jobs, response_get_cron_jobs = k8s_obj.get_cron_jobs(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_cron_jobs:
                                            labels = get_labels_from_items(
                                                response_get_cron_jobs.get('items'))
                                            cluster_details.update({
                                                'cron_job_details': response_get_cron_jobs,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_cron_jobs})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_job_details(self):
        """
        Get the detail of all the jobs of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response_describe_all_clusters = self.describe_all_clusters()
            if not error:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'job_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_jobs, response_get_jobs = k8s_obj.get_jobs(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_jobs:
                                            labels = get_labels_from_items(
                                                response_get_jobs.get('items'))
                                            cluster_details.update({
                                                'job_details': response_get_jobs,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_jobs})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_storage_class_details(self):
        """
        Get the detail of all the storage class of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response_describe_all_clusters = self.describe_all_clusters()
            if not error:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'storage_class_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_storage_class, response_get_storage_class = k8s_obj.get_storage_classes(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_storage_class:
                                            labels = get_labels_from_items(
                                                response_get_storage_class.get('items'))
                                            cluster_details.update({
                                                'storage_class_details': response_get_storage_class,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_storage_class})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_replication_controller_details(self):
        """
        Get the detail of all the replication controllers of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response_describe_all_clusters = self.describe_all_clusters()
            if not error:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'replication_controller_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_replication_controllers, response_get_replication_controllers = k8s_obj.get_replication_controllers(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_replication_controllers:
                                            labels = get_labels_from_items(
                                                response_get_replication_controllers.get('items'))
                                            cluster_details.update({
                                                'replication_controller_details': response_get_replication_controllers,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_replication_controllers})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_stateful_set_details(self):
        """
        Get the detail of all the stateful sets of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error_describe_all_clusters, response_describe_all_clusters = self.describe_all_clusters()
            if not error_describe_all_clusters:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'stateful_set_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_stateful_sets, response_get_stateful_sets = k8s_obj.get_stateful_sets(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_stateful_sets:
                                            labels = get_labels_from_items(
                                                response_get_stateful_sets.get('items'))
                                            cluster_details.update({
                                                'stateful_set_details': response_get_stateful_sets,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_stateful_sets})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_replica_set_details(self):
        """
        Get the detail of all the replica sets of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response_describe_all_clusters = self.describe_all_clusters()
            if not error:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'replica_set_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_replica_sets, response_get_replica_sets = k8s_obj.get_replica_sets(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_replica_sets:
                                            labels = get_labels_from_items(
                                                response_get_replica_sets.get('items'))
                                            cluster_details.update({
                                                'replica_set_details': response_get_replica_sets,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_replica_sets})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_daemon_set_details(self):
        """
        Get the detail of all the daemon sets of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response_describe_all_clusters = self.describe_all_clusters()
            if not error:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'daemon_set_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_daemon_sets, response_get_daemon_sets = k8s_obj.get_daemon_sets(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_daemon_sets:
                                            labels = get_labels_from_items(
                                                response_get_daemon_sets.get('items'))
                                            cluster_details.update({
                                                'daemon_set_details': response_get_daemon_sets,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_daemon_sets})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_config_map_details(self):
        """
        Get the detail of all the config map of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response_describe_all_clusters = self.describe_all_clusters()
            if not error:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'config_map_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_config_maps, response_get_config_maps = k8s_obj.get_config_maps(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_config_maps:
                                            labels = get_labels_from_items(
                                                response_get_config_maps.get('items'))
                                            cluster_details.update({
                                                'config_map_details': response_get_config_maps,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_config_maps})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_ingress_details(self):
        """
        Get the detail of all the ingress of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response_describe_all_clusters = self.describe_all_clusters()
            if not error:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'ingress_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'running' in cluster.get(
                                        'state'):
                                    error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                        cluster_id)
                                    if not error_describe_cluster_config_token_endpoint:
                                        # Adding unique labels for the cluster_roles in a single cluster
                                        k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                        error_get_ingresses, response_get_ingresses = k8s_obj.get_ingresses(
                                            cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                'cluster_public_endpoint'),
                                            token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                                        if not error_get_ingresses:
                                            labels = get_labels_from_items(
                                                response_get_ingresses.get('items'))
                                            cluster_details.update({
                                                'ingress_details': response_get_ingresses,
                                                'labels': labels
                                            })
                                        else:
                                            cluster_details.update({'error': response_get_ingresses})
                                    else:
                                        cluster_details.update(
                                            {'error': response_describe_cluster_config_token_endpoint})
                                else:
                                    # If cluster is not in running state
                                    cluster_details.update({'error': 'Cluster is not in running state'})
                            else:
                                cluster_details.update({
                                    'error':
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state'
                                })
                        else:
                            raise Exception(response_check_database_state_and_update)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def create_k8s_object(self, cluster_id, data, namespace):
        """
        Create the kubernetes object on the cluster in alibaba console
        :param cluster_id:
        :param data:
        :param namespace:
        :return:
        """
        response = None
        error = False
        try:
            error, response_describe_all_clusters = self.describe_all_clusters()
            if not error:
                describe_clusters_response = response_describe_all_clusters
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster are present in the current cloud provider
                    cluster_accessed_flag = False
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                cluster_accessed_flag = True
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')

                                            error_create_k8s_object, response_create_k8s_object = k8s_obj.create_k8s_object(
                                                cluster_id=cluster_id,
                                                data=data,
                                                namespace=namespace)

                                            if error_create_k8s_object:
                                                # If any error occurred while
                                                # creating application using file
                                                raise Exception(response_create_k8s_object)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    if not cluster_accessed_flag:
                        # invalid cluster_id provided
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def describe_all_cluster_config(self):
        """
        get the list of all cluster configs present in alibaba provider
        :return:
        """
        response = None
        error = False
        cluster_details_list = []
        try:
            error, response_describe_all_clusters = self.describe_all_clusters()

            if not error:
                # access_key_secret_key['name']: cluster_details_list
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {
                            'cluster_id': cluster_id,
                            'config': {},
                            'error': None
                        }
                        if 'running' in cluster.get('state'):
                            error, response_check_database_state_and_update = self.check_database_state_and_update(
                                cluster)
                            if not error:
                                error, response_describe_cluster_config = self.describe_cluster_config(cluster_id)
                                if not error:
                                    cluster_config = json.loads(response_describe_cluster_config)
                                    if 'config' in cluster_config:
                                        cluster_config = yaml.load(cluster_config.get('config'), yaml.FullLoader)
                                        cluster_details.update({
                                            'config': cluster_config
                                        })
                                    else:
                                        cluster_details.update({
                                            'error': 'Unable to find cluster config details'
                                        })
                                else:
                                    cluster_details.update({
                                        'error': response_describe_cluster_config
                                    })
                            else:
                                cluster_details.update({
                                    'error': response
                                })
                        else:
                            cluster_details.update({
                                'error': 'Cluster is not in running state'
                            })
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                # skip if any error occurred for a particular key
                response = response_describe_all_clusters

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def is_cluster_exist(self, cluster_id):
        """
        Check whether cluster exist or not
        :param cluster_id:
        :return:
        """
        error = False
        response = False
        try:
            error, result = self.describe_all_clusters()
            if not error:
                for cluster in result:
                    if cluster_id == cluster.get('cluster_id'):
                        if 'running' == cluster.get('state'):
                            response = True
                        elif 'failed' == cluster.get('state'):
                            response = True
                        # if cluster is present response is true otherwise false
                        else:
                            #  Creating state or in deleting state
                            response = False
            else:
                raise Exception(result)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_pod(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_pods(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_persistent_volume_claim(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_persistent_volume_claims(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_cron_job(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_cron_jobs(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_daemon_set(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_daemon_sets(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_deployment(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_deployments(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_job(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_jobs(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_replica_set(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_replica_sets(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_replication_controller(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_replication_controllers(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_stateful_set(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_stateful_sets(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_service(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_services(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_persistent_volume(self, name, cluster_id):
        """
        Delete the kubernetes persistent volume on the cluster in Alibaba console which does not contain namespace
        :param name:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_persistent_volumes(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_without_namespace(
                                                    objects=response_objects, name=name,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_storage_class(self, name, cluster_id):
        """
        Delete the kubernetes persistent volume on the cluster in Alibaba console which does not contain namespace
        :param name:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_storage_classes(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_without_namespace(
                                                    objects=response_objects, name=name,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_config_map(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_config_maps(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_secret(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_secrets(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_ingress(self, name, namespace, cluster_id):
        """
        Delete the kubernetes object on the cluster in alibaba console
        :param name:
        :param namespace:
        :param cluster_id:
        :return:
        """
        response = None
        error = False
        try:
            error, describe_clusters_response = self.describe_all_clusters()
            if not error:
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster is present in the given provider
                    access_flag_for_cluster_id = True
                    for cluster in describe_clusters_response:
                        error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                            cluster)
                        if not error_check_database_state_and_update:
                            if cluster_id == cluster.get('cluster_id'):
                                access_flag_for_cluster_id = False
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_pods, response_objects = k8s_obj.get_ingresses(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))

                                            if not error_get_pods:
                                                error_delete_object_with_namespace, response_delete_object_with_namespace = k8s_obj.delete_object_with_namespace(
                                                    objects=response_objects, name=name, namespace=namespace,
                                                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_public_endpoint'),
                                                    token=response_describe_cluster_config_token_endpoint.get(
                                                        'cluster_token')
                                                )
                                                if error_delete_object_with_namespace:
                                                    # Unable to delete object
                                                    raise Exception(response_delete_object_with_namespace)
                                            else:
                                                # Unable to delete object
                                                raise Exception(response_objects)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                        else:
                            raise Exception(response_check_database_state_and_update)
                    # if invalid cluster_id is provided
                    if access_flag_for_cluster_id:
                        raise Exception('Invalid cluster_id provided.')
            else:
                raise Exception(describe_clusters_response)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_all_resources_list(self, cluster_id):
        """
        Get the detail of all the resources of the cluster in alibaba console
        :return:
        """
        error = False
        cluster_details = {}
        response = []
        cluster_access_flag = False
        try:
            error, response_describe_all_clusters = self.describe_all_clusters()
            if not error:
                if len(response_describe_all_clusters) == 0:
                    response = []
                else:
                    for cluster in response_describe_all_clusters:
                        if cluster_id == cluster.get('cluster_id'):
                            cluster_access_flag = True

                            error_check_database_state_and_update, response_check_database_state_and_update = self.check_database_state_and_update(
                                cluster)
                            if not error_check_database_state_and_update:
                                if 'parameters' in cluster and cluster.get('parameters') is not None:
                                    if 'running' in cluster.get(
                                            'state'):
                                        error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                                            cluster_id)
                                        if not error_describe_cluster_config_token_endpoint:
                                            # Adding unique labels for the cluster_roles in a single cluster
                                            k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                                            error_get_all_resources, response_get_all_resources = k8s_obj.get_all_resources(
                                                cluster_url=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_public_endpoint'),
                                                token=response_describe_cluster_config_token_endpoint.get(
                                                    'cluster_token'))
                                            if not error_get_all_resources:
                                                cluster_details = response_get_all_resources
                                            else:
                                                raise Exception(response_get_all_resources)
                                        else:
                                            raise Exception(response_describe_cluster_config_token_endpoint)
                                    else:
                                        # If cluster is not in running state
                                        raise Exception('Cluster is not in running state')
                                else:
                                    raise Exception(
                                        'Unable to find the parameter for cluster. Either it is in initial or failed state')
                            else:
                                raise Exception(response_check_database_state_and_update)
                    if not cluster_access_flag:
                        raise Exception('Please provide valid cluster_id')
                    response = cluster_details
            else:
                raise Exception(response_describe_all_clusters)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

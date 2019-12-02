import json
import os

import yaml
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from cluster.kuberenetes.operations import Kubernetes_Operations
from cluster.others.miscellaneous_operation import get_db_info_using_cluster_id, create_cluster_config_file, \
    insert_or_update_cluster_details
from clusterProvisioningClient.settings import BASE_DIR

config_dumps_path = os.path.join(BASE_DIR, 'config_dumps')


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
        response = []
        try:
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'pod_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_pods(cluster_url=cluster_url,
                                                                                          token=response)
                                                        if not error:
                                                            # Adding unique labels for the pods in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'pod_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch pod details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

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
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'namespace_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):

                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_namespaces(cluster_url=cluster_url,
                                                                                                token=response)
                                                        if not error:
                                                            # Adding unique labels for the namespace in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'namespace_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch namespace details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

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
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'role_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'cluster_role_labels': {},
                                           'role_labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_roles(cluster_url=cluster_url,
                                                                                           token=response)
                                                        if not error:
                                                            # Adding unique labels for the cluster_roles in a single cluster
                                                            cluster_roles_label_dict = {}
                                                            roles_label_dict = {}

                                                            for element in response.get('cluster_role_list').get(
                                                                    'items'):
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
                                                                            if key in cluster_roles_label_dict:
                                                                                # Adding the label value
                                                                                if not value in cluster_roles_label_dict.get(
                                                                                        key):
                                                                                    cluster_roles_label_dict.get(
                                                                                        key).append(value)
                                                                            else:
                                                                                cluster_roles_label_dict.update(
                                                                                    {key: [value]})

                                                            for element in response.get('role_list').get('items'):
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
                                                                            if key in roles_label_dict:
                                                                                # Adding the label value
                                                                                if not value in roles_label_dict.get(
                                                                                        key):
                                                                                    roles_label_dict.get(key).append(
                                                                                        value)
                                                                            else:
                                                                                roles_label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'role_details': response,
                                                                'cluster_role_labels': cluster_roles_label_dict,
                                                                'role_labels': roles_label_dict
                                                            })

                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch role details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

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
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'persistent_volume_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_persistent_volumes(
                                                            cluster_url=cluster_url,
                                                            token=response)
                                                        if not error:
                                                            # Adding unique labels for the pv in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'persistent_volume_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state so unable to fetch persistent volume details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

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
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'persistent_volume_claim_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_persistent_volume_claims(
                                                            cluster_url=cluster_url,
                                                            token=response)
                                                        if not error:
                                                            # Adding unique labels for the pvc in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'persistent_volume_claim_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch persistent volume claim details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

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
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'deployment_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_deployments(
                                                            cluster_url=cluster_url,
                                                            token=response)
                                                        if not error:
                                                            # Adding unique labels for the deployment in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'deployment_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch deployment details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

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
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'secret_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_secrets(cluster_url=cluster_url,
                                                                                             token=response)
                                                        if not error:
                                                            # Adding unique labels for the secrets in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'secret_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch secret details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

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
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'node_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_nodes(cluster_url=cluster_url,
                                                                                           token=response)
                                                        if not error:
                                                            # Adding unique labels for the nodes in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            node_details = response
                                                            error, response = k8_obj.compute_allocated_resources()

                                                            if not error:
                                                                for node in node_details.get('items'):
                                                                    for item in response:
                                                                        if node.get('metadata').get('name') == item.get(
                                                                                'node_name'):
                                                                            node.update({'allocated_resources': item})
                                                                cluster_details.update({
                                                                    'node_details': node_details,
                                                                    'labels': label_dict
                                                                })
                                                            else:
                                                                cluster_details.update(
                                                                    {'error': 'Unable to compute allocated resources'})

                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch node details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

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
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'service_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_services(cluster_url=cluster_url,
                                                                                              token=response)
                                                        if not error:
                                                            # Adding unique labels for the service in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'service_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch service details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

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
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'cron_job_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_cron_jobs(cluster_url=cluster_url,
                                                                                               token=response)
                                                        if not error:
                                                            # Adding unique labels for the cron jobs in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})
                                                            cluster_details.update({
                                                                'cron_job_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch cron job details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

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
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'job_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_jobs(cluster_url=cluster_url,
                                                                                          token=response)
                                                        if not error:
                                                            # Adding unique labels for the jobs in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'job_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch job details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_all_storage_class_details(self):
        """
        Get the detail of all the storage class of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'storage_class_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_storage_class(
                                                            cluster_url=cluster_url,
                                                            token=response)
                                                        if not error:
                                                            # Adding unique labels for the storage class deatails in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'storage_class_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch storage details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_all_replication_controller_details(self):
        """
        Get the detail of all the replication controllers of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'replication_controller_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_replication_controllers(
                                                            cluster_url=cluster_url,
                                                            token=response)
                                                        if not error:
                                                            # Adding unique labels for the replication controller  in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'replication_controller_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch replication controller details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_all_stateful_set_details(self):
        """
        Get the detail of all the stateful sets of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'stateful_set_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_stateful_sets(
                                                            cluster_url=cluster_url,
                                                            token=response)
                                                        if not error:
                                                            # Adding unique labels for the stateful sets in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'stateful_set_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch stateful set details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_all_replica_set_details(self):
        """
        Get the detail of all the replica sets of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'replica_set_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_replica_sets(
                                                            cluster_url=cluster_url,
                                                            token=response)
                                                        if not error:
                                                            # Adding unique labels for the replica set  in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'replica_set_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch replica set details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_all_daemon_set_details(self):
        """
        Get the detail of all the daemon sets of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'daemon_set_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_daemon_sets(
                                                            cluster_url=cluster_url,
                                                            token=response)
                                                        if not error:
                                                            # Adding unique labels for the daemon set in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'daemon_set_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch daemon set details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_all_config_map_details(self):
        """
        Get the detail of all the config map of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'config_map_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_config_maps(
                                                            cluster_url=cluster_url,
                                                            token=response)
                                                        if not error:
                                                            # Adding unique labels for the config map in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'config_map_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch config map details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_all_ingress_details(self):
        """
        Get the detail of all the ingress of all the clusters in alibaba console
        :return:
        """
        cluster_details_list = []
        error = False
        response = []
        try:
            error, response = self.describe_all_clusters()
            if not error:
                if len(response) == 0:
                    response = []
                else:
                    for cluster in response:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {'cluster_id': cluster_id,
                                           'ingress_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'labels': {},
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster and cluster.get('parameters') is not None:
                                if 'True' in str(cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                        'state'):
                                    error, response = self.describe_cluster_config(cluster_id)
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster_id,
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(config_dumps_path,
                                                                           cluster_id,
                                                                           'config')
                                                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                error, response = k8_obj.get_token()
                                                if not error:
                                                    # If token is created
                                                    cluster_url = None
                                                    cluster_config = json.loads(cluster_config)
                                                    for item in cluster_config.get('clusters'):
                                                        cluster_info_token = item.get('cluster')
                                                        cluster_url = cluster_info_token.get('server')
                                                    if cluster_url is not None:
                                                        error, response = k8_obj.get_ingress_details(
                                                            cluster_url=cluster_url,
                                                            token=response)
                                                        if not error:
                                                            # Adding unique labels for the ingress in a single cluster
                                                            label_dict = {}
                                                            for element in response.get('items'):
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
                                                                                if not value in label_dict.get(key):
                                                                                    label_dict.get(key).append(value)
                                                                            else:
                                                                                label_dict.update({key: [value]})

                                                            cluster_details.update({
                                                                'ingress_details': response,
                                                                'labels': label_dict
                                                            })
                                                        else:
                                                            cluster_details.update({'error': response})
                                                    else:
                                                        cluster_details.update(
                                                            {'error': 'Unable to find the cluster endpoint'})
                                                else:
                                                    # If token is not created
                                                    cluster_details.update({'error': response})
                                            else:
                                                # If error while generating config file for a particular cluster
                                                cluster_details.update({'error': response})
                                        else:
                                            # If config key not present in Alibaba response
                                            cluster_details.update({'error': 'Unable to find cluster config details'})
                                    else:
                                        cluster_details.update({'error': response})
                                else:
                                    # If Eip is not present in cluster
                                    cluster_details.update(
                                        {
                                            'error': 'Eip is not available or cluster is in failed state, unable to fetch all ingress details'})
                            else:
                                cluster_details.update(
                                    {
                                        'error': 'Unable to find the parameter for cluster. Either it is in initial or failed state'})
                        else:
                            raise Exception(response)
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                raise Exception(response)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def create_from_yaml(self, cluster_id, data, namespace):
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
            error, response = self.describe_all_clusters()
            if not error:
                describe_clusters_response = response
                if len(describe_clusters_response) == 0:
                    # If no cluster are present in the current cloud provider
                    raise Exception('No clusters are present in the current provider.')
                else:
                    # if cluster are present in the current cloud provider
                    for cluster in describe_clusters_response:
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                error, response = k8_obj.create_from_yaml(
                                                                    cluster_id=cluster_id, data=data,
                                                                    namespace=namespace)
                                                                if error:
                                                                    # If any error occurred while
                                                                    # creating application using file
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                            else:
                                # invalid cluster_id provided
                                raise Exception('Invalid cluster_id provided.')
                        else:
                            raise Exception(response)
            else:
                raise Exception(response)

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
            error, result = self.describe_all_clusters()

            if not error:
                # access_key_secret_key['name']: cluster_details_list
                if len(result) == 0:
                    response = []
                else:
                    for cluster in result:
                        cluster_id = cluster.get('cluster_id')
                        cluster_details = {
                            'cluster_id': cluster_id,
                            'config': {},
                            'error': None
                        }
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            error, response = self.describe_cluster_config(cluster_id)
                            if not error:
                                cluster_config = json.loads(response)
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
                                    'error': response
                                })
                        else:
                            cluster_details.update({
                                'error': response
                            })
                        cluster_details_list.append(cluster_details)
                    response = cluster_details_list
            else:
                # skip if any error occurred for a particular key
                response = result

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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_pods(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_with_namespace(
                                                                        items, name,
                                                                        namespace,
                                                                        cluster_url,
                                                                        token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_persistent_volume_claims(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_with_namespace(
                                                                        items, name,
                                                                        namespace,
                                                                        cluster_url,
                                                                        token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_cron_jobs(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_with_namespace(
                                                                        items, name,
                                                                        namespace,
                                                                        cluster_url,
                                                                        token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_daemon_sets(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_with_namespace(
                                                                        items, name,
                                                                        namespace,
                                                                        cluster_url,
                                                                        token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_deployments(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_with_namespace(
                                                                        items, name,
                                                                        namespace,
                                                                        cluster_url,
                                                                        token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_jobs(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_with_namespace(
                                                                        items, name,
                                                                        namespace,
                                                                        cluster_url,
                                                                        token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_replica_sets(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_with_namespace(
                                                                        items, name,
                                                                        namespace,
                                                                        cluster_url,
                                                                        token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_replication_controllers(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_with_namespace(
                                                                        items, name,
                                                                        namespace,
                                                                        cluster_url,
                                                                        token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_stateful_sets(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_with_namespace(
                                                                        items, name,
                                                                        namespace,
                                                                        cluster_url,
                                                                        token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_services(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_with_namespace(
                                                                        items, name,
                                                                        namespace,
                                                                        cluster_url,
                                                                        token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_persistent_volumes(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_without_namespace(
                                                                        items, name, cluster_url, token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_storage_class(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_without_namespace(
                                                                        items, name, cluster_url, token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_config_maps(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_with_namespace(
                                                                        items, name,
                                                                        namespace,
                                                                        cluster_url,
                                                                        token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if cluster_id == cluster.get('cluster_id'):
                                # valid cluster_id provided
                                access_flag_for_cluster_id = False
                                if 'running' in cluster.get('state'):
                                    # if cluster is in running state
                                    if 'parameters' in cluster and cluster.get('parameters') is not None:
                                        if 'True' in str(
                                                cluster.get('parameters').get('Eip')) and 'running' in cluster.get(
                                            'state'):
                                            error, response = self.describe_cluster_config(cluster_id)
                                            if not error:
                                                cluster_config = json.loads(response)
                                                if 'config' in cluster_config:
                                                    cluster_config = json.dumps(
                                                        yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                                    error, response = create_cluster_config_file(
                                                        cluster_id,
                                                        json.loads(cluster_config))
                                                    if not error:
                                                        config_path = os.path.join(config_dumps_path,
                                                                                   cluster_id,
                                                                                   'config')
                                                        k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                                                        error, response = k8_obj.get_token()
                                                        if not error:
                                                            # If token is created
                                                            cluster_url = None
                                                            cluster_config = json.loads(cluster_config)
                                                            for item in cluster_config.get('clusters'):
                                                                cluster_info_token = item.get('cluster')
                                                                cluster_url = cluster_info_token.get('server')
                                                            if cluster_url is not None:
                                                                token = response
                                                                error, response = k8_obj.get_secrets(
                                                                    cluster_url=cluster_url,
                                                                    token=token)
                                                                if not error:
                                                                    items = response
                                                                    error, response = k8_obj.delete_object_with_namespace(
                                                                        items, name,
                                                                        namespace,
                                                                        cluster_url,
                                                                        token)
                                                                    if error:
                                                                        # Unable to delete object
                                                                        raise Exception(response)
                                                                else:
                                                                    # Unable to fetch object details
                                                                    raise Exception(response)
                                                            else:
                                                                raise Exception('Unable to find the cluster endpoint')
                                                        else:
                                                            # If token is not created
                                                            raise Exception(response)
                                                    else:
                                                        # If error while generating config file for a particular cluster
                                                        raise Exception(response)
                                                else:
                                                    # If config key not present in Alibaba response
                                                    raise Exception('Unable to find cluster config details')
                                            else:
                                                raise Exception(response)
                                        else:
                                            raise Exception(
                                                'Eip is not available or cluster is in failed state, unable to fetch details')
                                    else:
                                        raise Exception(
                                            'Unable to find the parameter for cluster. '
                                            'Either it is in initial or failed state')
                                else:
                                    # if cluster is not in running state
                                    raise Exception('Cluster is not in running state.')
                        else:
                            raise Exception(response)
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

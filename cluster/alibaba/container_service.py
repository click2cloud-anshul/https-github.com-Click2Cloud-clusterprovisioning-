import json
import os
from os import path

import yaml
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkros.request.v20190910.GetStackRequest import GetStackRequest

from cluster.kuberenetes.operations import Kubernetes_Operations
from cluster.others.miscellaneous_operation import get_db_info_using_cluster_id, create_cluster_config_file, \
    insert_or_update_cluster_details

from clusterProvisioningClient.settings import BASE_DIR
from common.apps import file_operation


class Alibaba_CS:
    def __init__(self, ali_access_key=None, ali_secret_key=None, region_id=None):
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

    def cluster_details(self, cluster_id=None):
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
            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)
            cluster_info = {}
            access_flag = True
            if len(describe_clusters_response) == 0:
                return False, "No clusters are present in the current account"
            for cluster in describe_clusters_response:
                if cluster_id in cluster["cluster_id"]:
                    access_flag = False
                    cluster_info = {"cluster_info": cluster}
                    cluster_info.update(cluster_info)
                    request = GetStackRequest()
                    request.set_accept_format('json')
                    if str(cluster['state']).__contains__('failed'):
                        flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                        if flag:
                            for cluster_info_db in cluster_info_db_list:
                                if str(cluster_info_db[5]).__contains__('Initiated'):
                                    new_params = {}
                                    new_params['is_insert'] = False
                                    new_params['user_id'] = cluster_info_db[1]
                                    new_params['provider_id'] = cluster_info_db[2]
                                    new_params['cluster_id'] = cluster_info_db[3]
                                    new_params['cluster_details'] = json.dumps(cluster_info)
                                    new_params['status'] = 'Failed'
                                    new_params['operation'] = 'created from cloudbrain'
                                    insert_or_update_cluster_details(new_params)
                    parameters = cluster["parameters"]
                    request.set_StackId(str(parameters["ALIYUN::StackId"]))
                    client = AcsClient(ak=self.access_key, secret=self.secret_key, region_id=str(cluster["region_id"]))
                    get_stack_response = client.do_action_with_exception(request)
                    get_stack_json = json.loads(get_stack_response)
                    stack_info = {"stack_info": get_stack_json}
                    cluster_info.update(stack_info)
                    if str(cluster['state']).__contains__('running'):
                        flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                        if flag:
                            for cluster_info_db in cluster_info_db_list:
                                if str(cluster_info_db[5]).__contains__('Initiated'):
                                    new_params = {}
                                    new_params['is_insert'] = False
                                    new_params['user_id'] = cluster_info_db[1]
                                    new_params['provider_id'] = cluster_info_db[2]
                                    new_params['cluster_id'] = cluster_info_db[3]
                                    new_params['cluster_details'] = json.dumps(cluster_info)
                                    new_params['status'] = 'Running'
                                    new_params['operation'] = 'created from cloudbrain'
                                    insert_or_update_cluster_details(new_params)

            if access_flag:
                return False, 'Invalid cluster_id ' + cluster_id + ' provided.'
            return True, cluster_info
        except Exception as e:
            return False, e.message

    def create_cluster(self, request_body=None):
        # return True, {"created": "msg", "access_key": self.access_key, "secret_key": self.secret_key, "cluster_id":"fdsfdsfsdafdsf"}
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

            response = client.do_action_with_exception(request)
            create_clusters_response = json.loads(response)
            return True, create_clusters_response
        except Exception as e:
            return False, e.message

    def delete_cluster(self, cluster_id=None):
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

            response = client.do_action_with_exception(request)
            if len(str(response)) == 0:
                response = '{"message":"' + "Delete request accepted for cluster id " + cluster_id + '"}'
            delete_clusters_response = json.loads(response)
            return True, delete_clusters_response
        except Exception as e:
            return False, e.message

    def get_all_clusters(self):
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            cluster_details_list = []
            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                cluster_info = {"cluster_info": cluster}
                cluster_details.update(cluster_info)
                request = GetStackRequest()
                request.set_accept_format('json')
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('failed'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_info_db[4])
                                new_params['status'] = 'Failed'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if 'parameters' in cluster and cluster["parameters"] is not None:
                    parameters = cluster["parameters"]
                    if "ALIYUN::StackId" in parameters:
                        request.set_StackId(str(parameters["ALIYUN::StackId"]))
                        client = AcsClient(ak=self.access_key, secret=self.secret_key,
                                           region_id=str(cluster["region_id"]))
                        get_stack_response = client.do_action_with_exception(request)
                        get_stack_json = json.loads(get_stack_response)
                        stack_info = {"stack_info": get_stack_json}
                        cluster_details.update(stack_info)
                        cluster_details_list.append(cluster_details)
                    else:
                        stack_info = {"stack_info": 'Stack Not Created'}
                        cluster_details.update(stack_info)
                        cluster_details_list.append(cluster_details)
                else:
                    stack_info = {"stack_info": 'Stack Not Created'}
                    cluster_details.update(stack_info)
                    cluster_details_list.append(cluster_details)
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_all_cluster_config(self):
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            cluster_details_list = []
            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_id_list = {}
                cluster_info = {}
                if str(cluster['state']).__contains__('failed'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                cluster_details = {}
                                cluster_info = {"cluster_info": cluster}
                                cluster_details.update(cluster_info)
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Failed'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running'):
                    cluster_info = {"cluster_id": cluster['cluster_id'], "cluster_name": cluster['name']}
                    cluster_id_list.update(cluster_info)
                cluster_details_list.append(cluster_id_list)
            cluster_config_details_list = []
            if len(cluster_details_list) > 0:
                for cluster_info in cluster_details_list:
                    client = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')

                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster_info['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    if 'config' in cluster_config:
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        cluster_config_details_list.append(
                            {"cluster_id": cluster_info['cluster_id'], "cluster_name": cluster_info['cluster_name'],
                             "cluster_config": json.loads(cluster_config)}
                        )
            return True, cluster_config_details_list
        except Exception as e:
            return False, e.message

    def check_database_state_and_update(self, cluster=None):
        """
        check the database state and update cluster info in the database
        :param cluster:
        :return:
        """
        cluster_details = {'cluster_info': cluster}
        error = False
        response = None
        try:
            error, response = get_db_info_using_cluster_id(cluster.get('cluster_id'))
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
                                    'cluster_id': cluster_info_db[3],
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
                                    'cluster_id': cluster_info_db[3],
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

    def get_cluster_config(self):
        pass

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
                        cluster_details = {'cluster_id': cluster.get('cluster_id'),
                                           'pod_details': {},
                                           'cluster_name': cluster.get('name'),
                                           'error': None}
                        error, response = self.check_database_state_and_update(cluster)
                        if not error:
                            if 'parameters' in cluster:
                                if 'True' in str(cluster.get('parameters').get('Eip')):
                                    error, response = self.describe_cluster_config(cluster.get('cluster_id'))
                                    if not error:
                                        cluster_config = json.loads(response)
                                        if 'config' in cluster_config:
                                            cluster_config = json.dumps(
                                                yaml.load(cluster_config.get('config'), yaml.FullLoader))
                                            error, response = create_cluster_config_file(cluster.get('cluster_id'),
                                                                                         json.loads(cluster_config))
                                            if not error:
                                                config_path = os.path.join(BASE_DIR, 'cluster', 'dumps',
                                                                           cluster.get('cluster_id'),
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
                                                            cluster_details.update({
                                                                'pod_details': response
                                                            })
                                                        else:
                                                            return error, cluster_details
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
                                        {'error': 'Eip is not available, unable to fetch pod details'})
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

    def get_secrets(self):
        cluster_details_list = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                cluster_info = {"cluster_info": cluster}
                cluster_details.update(cluster_info)
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('failed'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Failed'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)

                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']
                            if cluster_url is not None:
                                flag, details = kube_one.get_secrets(cluster_url=cluster_url, token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "secret_list": details,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "secret_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_nodes(self):
        cluster_details_list = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                cluster_info = {"cluster_info": cluster}
                cluster_details.update(cluster_info)
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('failed'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Failed'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']
                            if cluster_url is not None:
                                flag, details = kube_one.get_nodes(cluster_url=cluster_url, token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "node_list": details,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "node_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_deployments(self):
        cluster_details_list = []
        try:
            cluster_list_for_pods = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                cluster_info = {"cluster_info": cluster}
                cluster_details.update(cluster_info)
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('failed'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Failed'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']
                            if cluster_url is not None:
                                flag, details = kube_one.get_deployments(cluster_url=cluster_url, token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "deployment_list": details,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "deployment_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_namespaces(self):
        cluster_details_list = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']
                            if cluster_url is not None:
                                # namespace_list
                                flag, details = kube_one.get_namespaces(cluster_url=cluster_url, token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "namespace_list": details,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "namespace_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_persistent_volume_claims(self):
        cluster_details_list = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                cluster_info = {"cluster_info": cluster}
                cluster_details.update(cluster_info)
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('failed'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Failed'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']
                            if cluster_url is not None:

                                flag, details = kube_one.get_persistent_volume_claims(cluster_url=cluster_url,
                                                                                      token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "persistent_volume_claims_list": details,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "persistent_volume_claims_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_persistent_volumes(self):
        cluster_details_list = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                cluster_info = {"cluster_info": cluster}
                cluster_details.update(cluster_info)
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('failed'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Failed'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']
                            if cluster_url is not None:
                                flag, details = kube_one.get_persistent_volumes(cluster_url=cluster_url,
                                                                                token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "persistent_volumes_list": details,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "persistent_volumes_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_services(self):
        cluster_details_list = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                cluster_info = {"cluster_info": cluster}
                cluster_details.update(cluster_info)
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('failed'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Failed'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']
                            if cluster_url is not None:
                                flag, details = kube_one.get_services(cluster_url=cluster_url,
                                                                      token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "services_list": details,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "services_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_roles(self):
        cluster_details_list = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                cluster_info = {"cluster_info": cluster}
                cluster_details.update(cluster_info)
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('failed'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Failed'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']

                            if cluster_url is not None:
                                flag, cluster_roles_list, roles_list = kube_one.get_roles(cluster_url=cluster_url,
                                                                                          token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "cluster_roles_list": cluster_roles_list,
                                                       "roles_list": roles_list,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "roles_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_storageclasses(self):
        cluster_details_list = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']
                            if cluster_url is not None:
                                flag, details = kube_one.get_storageclasses(cluster_url=cluster_url,
                                                                            token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "storageclasses_list": details,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "storageclasses_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_cronjobs(self):
        cluster_details_list = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                cluster_info = {"cluster_info": cluster}
                cluster_details.update(cluster_info)
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('failed'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Failed'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']
                            if cluster_url is not None:
                                flag, details = kube_one.get_cronjobs(cluster_url=cluster_url,
                                                                      token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "cronjob_list": details,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "cronjob_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_jobs(self):
        cluster_details_list = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                cluster_info = {"cluster_info": cluster}
                cluster_details.update(cluster_info)
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('failed'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Failed'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']
                            if cluster_url is not None:
                                flag, details = kube_one.get_jobs(cluster_url=cluster_url,
                                                                  token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "jobs_list": details,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "jobs_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_daemon_sets(self):
        cluster_details_list = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']
                            if cluster_url is not None:
                                # namespace_list
                                flag, details = kube_one.get_daemon_sets(cluster_url=cluster_url, token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "namespace_list": details,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "namespace_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_replica_sets(self):
        cluster_details_list = []
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

            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)

            if len(describe_clusters_response) == 0:
                return True, []
            for cluster in describe_clusters_response:
                cluster_details = {}
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                        'True'):
                    client1 = AcsClient(self.access_key, self.secret_key, 'default')
                    request = CommonRequest()
                    request.set_accept_format('json')
                    request.set_method('GET')
                    request.set_protocol_type('https')  # https | http
                    request.set_domain('cs.aliyuncs.com')
                    request.set_version('2015-12-15')
                    request.add_query_param('RegionId', "default")
                    request.add_header('Content-Type', 'application/json')
                    request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                    body = ''''''
                    request.set_content(body.encode('utf-8'))
                    response = client1.do_action_with_exception(request)
                    cluster_config = json.loads(response)
                    self.clusters_folder_directory = BASE_DIR
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = Kubernetes_Operations(
                            configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                               cluster['cluster_id'], r"config"))
                        flag, token = kube_one.get_token(self.clusters_folder_directory)
                        os.chdir(self.clusters_folder_directory)
                        if flag:
                            cluster_url = None
                            cluster_config = json.loads(cluster_config)
                            for p in cluster_config['clusters']:
                                cluster_info_token = p['cluster']
                                cluster_url = cluster_info_token['server']
                            if cluster_url is not None:
                                # namespace_list
                                flag, details = kube_one.get_replica_sets(cluster_url=cluster_url, token=token)
                                if flag:
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "namespace_list": details,
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                else:
                                    return flag, cluster_details
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "namespace_list": {}, "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def create_from_yaml(self, cluster_id=None, data=None):
        print 'll'
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
            response = client.do_action_with_exception(request)
            describe_clusters_response = json.loads(response)
            access_flag = True
            if len(describe_clusters_response) == 0:
                return False, "No clusters are present in the current account"
            for cluster in describe_clusters_response:
                cluster_details = {}
                cluster_info = {"cluster_info": cluster}
                cluster_details.update(cluster_info)
                if str(cluster['state']).__contains__('running'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_details)
                                new_params['status'] = 'Running'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if str(cluster['state']).__contains__('failed'):
                    flag, cluster_info_db_list = get_db_info_using_cluster_id(cluster['cluster_id'])
                    if flag:
                        for cluster_info_db in cluster_info_db_list:
                            if str(cluster_info_db[5]).__contains__('Initiated'):
                                new_params = {}
                                new_params['is_insert'] = False
                                new_params['user_id'] = cluster_info_db[1]
                                new_params['provider_id'] = cluster_info_db[2]
                                new_params['cluster_id'] = cluster_info_db[3]
                                new_params['cluster_details'] = json.dumps(cluster_info_db[4])
                                new_params['status'] = 'Failed'
                                new_params['operation'] = 'created from cloudbrain'
                                insert_or_update_cluster_details(new_params)
                if cluster_id in cluster["cluster_id"]:
                    if str(cluster['state']).__contains__('running') and str(cluster['parameters']['Eip']).__contains__(
                            'True'):
                        access_flag = False
                        client1 = AcsClient(self.access_key, self.secret_key, 'default')
                        request = CommonRequest()
                        request.set_accept_format('json')
                        request.set_method('GET')
                        request.set_protocol_type('https')  # https | http
                        request.set_domain('cs.aliyuncs.com')
                        request.set_version('2015-12-15')
                        request.add_query_param('RegionId', "default")
                        request.add_header('Content-Type', 'application/json')
                        request.set_uri_pattern('/api/v2/k8s/' + cluster['cluster_id'] + '/user_config')
                        body = ''''''
                        request.set_content(body.encode('utf-8'))
                        response = client1.do_action_with_exception(request)
                        cluster_config = json.loads(response)
                        self.clusters_folder_directory = BASE_DIR
                        if 'config' in cluster_config:
                            os.chdir(self.clusters_folder_directory)
                            # json.dumps(yaml.load(cluster_config['config']))
                            cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                            file_operation(cluster['cluster_id'], json.loads(cluster_config))
                            kube_one = Kubernetes_Operations(
                                configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
                                                                   cluster['cluster_id'], r"config"))
                            flag, exception_list, names_list = kube_one.create_from_yaml()
        except Exception as e:
            print e

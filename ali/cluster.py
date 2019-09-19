import json
import os
from os import path

import requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkros.request.v20190910.GetStackRequest import GetStackRequest
import yaml
from k8s.k8s import *

from common.apps import file_operation


class Alibaba_CS:
    def __init__(self, ali_access_key=None, ali_secret_key=None, region_id=None):
        """
                :param ali_access_key: access key of alibaba
                :param ali_secret_key: secret key of alibaba
                :param region_id: region id of alibaba
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
            if len(describe_clusters_response) == 0:
                return False, "No clusters are present in the current account"
            for cluster in describe_clusters_response:
                if cluster_id in cluster["cluster_id"]:
                    cluster_info = {"cluster_info": cluster}
                    cluster_info.update(cluster_info)
                    request = GetStackRequest()
                    request.set_accept_format('json')
                    parameters = cluster["parameters"]
                    request.set_StackId(str(parameters["ALIYUN::StackId"]))
                    client = AcsClient(ak=self.access_key, secret=self.secret_key, region_id=str(cluster["region_id"]))

                    get_stack_response = client.do_action_with_exception(request)
                    get_stack_json = json.loads(get_stack_response)
                    stack_info = {"stack_info": get_stack_json}
                    cluster_info.update(stack_info)
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
                parameters = cluster["parameters"]
                request.set_StackId(str(parameters["ALIYUN::StackId"]))
                client = AcsClient(ak=self.access_key, secret=self.secret_key, region_id=str(cluster["region_id"]))
                get_stack_response = client.do_action_with_exception(request)
                get_stack_json = json.loads(get_stack_response)
                stack_info = {"stack_info": get_stack_json}
                cluster_details.update(stack_info)
                cluster_details_list.append(cluster_details)
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

    def get_cluster_config(self, ):
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

    def get_cluster_status(self, cluster_id=None):
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
            if len(describe_clusters_response) == 0:
                return False, "No clusters are present in the current account"
            for cluster in describe_clusters_response:
                if cluster_id in cluster["cluster_id"]:
                    cluster_status = {}
                    if 'err_msg' in cluster:
                        cluster_status = {"cluster_status": cluster["err_msg"]}
                    else:
                        cluster_status = {"cluster_status": cluster["state"]}
                    cluster_info.update(cluster_status)
                    request = GetStackRequest()
                    request.set_accept_format('json')
                    parameters = cluster["parameters"]
                    request.set_StackId(str(parameters["ALIYUN::StackId"]))
                    client = AcsClient(ak=self.access_key, secret=self.secret_key, region_id=str(cluster["region_id"]))
                    get_stack_response = client.do_action_with_exception(request)
                    stack_json = json.loads(get_stack_response)
                    stack_status = []
                    if 'Status' in stack_json:
                        stack_status.append({"status": stack_json['Status']})
                    if 'StatusReason' in stack_json:
                        stack_status.append({"status_reason": stack_json['StatusReason']})
                    if 'StackId' in stack_json:
                        stack_status.append({"id": stack_json['StackId']})
                    cluster_info.update({"stack_status": stack_status})
            return True, cluster_info
        except Exception as e:
            return False, e.message

    def get_pods(self):
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
                if str(cluster['state']).__contains__('running'):
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
                    self.clusters_folder_directory = os.getcwd()
                    if 'config' in cluster_config:
                        os.chdir(self.clusters_folder_directory)
                        # json.dumps(yaml.load(cluster_config['config']))
                        cluster_config = json.dumps(yaml.load(cluster_config['config'], yaml.FullLoader))
                        file_operation(cluster['cluster_id'], json.loads(cluster_config))
                        kube_one = K8s(configuration_yaml=r"" + path.join(self.clusters_folder_directory, 'clusters',
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
                                try:
                                    url = cluster_url + "/api/v1/pods"
                                    headers = {
                                        'Authorization': "Bearer " + token,
                                    }
                                    response = requests.request("GET", url, headers=headers, verify=False)
                                    cluster_details = {"cluster_id": cluster['cluster_id'],
                                                       "pod_list": json.loads(response.text),
                                                       "cluster_name": cluster['name']}
                                    cluster_details_list.append(cluster_details)
                                except Exception as e:
                                    return False, 'Max retries exceeded with url ' + cluster_url
                        else:
                            cluster_details = {"cluster_id": cluster['cluster_id'],
                                               "pod_list": "", "cluster_name": cluster['name']}
                            cluster_details_list.append(cluster_details)
                    else:
                        return False, 'config not present in JSON for cluster_id ' + cluster['cluster_id']
                else:
                    cluster_details_list.append(cluster_details)
            return True, cluster_details_list
        except Exception as e:
            return False, e.message

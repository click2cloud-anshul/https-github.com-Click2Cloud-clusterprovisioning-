import json

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkros.request.v20190910.GetStackRequest import GetStackRequest
import yaml

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
                return False, "No clusters are present in the current account"
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

    def get_cluster_config(self, cluster_id=None):
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
            cluster_config = json.loads(response)
            if 'config' in cluster_config:
                # json.dumps(yaml.load(cluster_config['config']))
                cluster_config = json.dumps(yaml.load(cluster_config['config']))

            return True, cluster_config
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

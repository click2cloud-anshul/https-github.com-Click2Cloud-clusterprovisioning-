import json

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkros.request.v20190910.GetStackRequest import GetStackRequest


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
            for cluster in describe_clusters_response:
                if cluster_id in cluster["cluster_id"]:
                    test = {"cluster_info": cluster}
                    cluster_info.update(test)

                    request = GetStackRequest()
                    request.set_accept_format('json')
                    parameters = cluster["parameters"]
                    request.set_StackId(str(parameters["ALIYUN::StackId"]))
                    client = AcsClient(ak=self.access_key, secret=self.secret_key, region_id=str(cluster["region_id"]))

                    get_stack_response = client.do_action_with_exception(request)
                    get_stack_json = json.loads(get_stack_response)
                    test = {"stack_info": get_stack_json}
                    cluster_info.update(test)
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
                response = '{"message":"'+"Delete request accepted for cluster id " + cluster_id + '"}'
            delete_clusters_response = json.loads(response)
            return True, delete_clusters_response
        except Exception as e:
            return False, e.message

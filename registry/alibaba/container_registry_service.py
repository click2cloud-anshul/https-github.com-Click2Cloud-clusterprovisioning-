import json

from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcr.request.v20160607 import CreateNamespaceRequest, GetNamespaceListRequest, GetNamespaceRequest, \
    DeleteNamespaceRequest, UpdateNamespaceRequest


class Alibaba_CRS:
    def __init__(self, ali_access_key, ali_secret_key):
        """
        constructor for the Alibaba_CRS class
        :param ali_access_key:
        :param ali_secret_key:
        """
        self.access_key = ali_access_key
        self.secret_key = ali_secret_key
        self.region_id = "cr.ap-south-1.aliyuncs.com"

    def create_namespace_request(self, namespace):
        """
        Creates a namespace
        :param namespace:
        :return:
        """
        error = False
        response = None
        try:
            client = AcsClient(self.access_key, self.secret_key, self.region_id)

            client_create_namespace_request = CreateNamespaceRequest.CreateNamespaceRequest()
            client_create_namespace_request.set_endpoint(self.region_id)
            body = """{
                    "Namespace": {
                        "Namespace": '%s',
                    }
                }""" % (namespace)
            client_create_namespace_request.set_content(body)
            client_response = client.do_action_with_exception(client_create_namespace_request)
            response = json.loads(client_response)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                if response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                else:
                    response = e.message
        except ClientException as e:
            error = True
            if 'Max retries exceeded' in str(e.message):
                response = 'Max retries exceeded, Failed to establish a new connection'
            else:
                response = e.message
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def list_namespaces(self):
        """
        This method will return all namespaces present in alibaba
        :return:
        """
        error = False
        response = None

        try:
            client = AcsClient(self.access_key, self.secret_key, self.region_id)
            client_request = GetNamespaceListRequest.GetNamespaceListRequest()
            client_request.set_endpoint(self.region_id)
            namespace_list = []
            client_response = client.do_action_with_exception(client_request)
            response_namespace_list = json.loads(client_response)
            if 'data' in response_namespace_list:
                if 'namespaces' in response_namespace_list.get('data'):
                    response_list_of_namespaces = response_namespace_list.get('data').get('namespaces')
                    for response_namespace in response_list_of_namespaces:
                        namespace_request = GetNamespaceRequest.GetNamespaceRequest()
                        namespace_request.set_endpoint(self.region_id)
                        namespace_request.set_Namespace(response_namespace.get('namespace'))
                        namespace_response = client.do_action_with_exception(namespace_request)
                        namespace_response = json.loads(namespace_response)
                        namespace_list.append(namespace_response.get('data').get('namespace'))
            response = namespace_list
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                if response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                else:
                    response = e.message
        except ClientException as e:
            error = True
            if 'Max retries exceeded' in str(e.message):
                response = 'Max retries exceeded, failed to establish a new connection'
            else:
                response = e.message
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def delete_namespace_request(self, namespace):
        """
        This method will delete namespace present in alibaba
        :param namespace:
        :return:
        """
        error = False
        response = None
        try:
            client = AcsClient(self.access_key, self.secret_key, self.region_id)

            client_delete_namespace_request = DeleteNamespaceRequest.DeleteNamespaceRequest()
            client_delete_namespace_request.set_endpoint(self.region_id)
            client_delete_namespace_request.set_Namespace(namespace)

            response_delete_namespace = client.do_action_with_exception(client_delete_namespace_request)
            response = json.loads(response_delete_namespace)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                if response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                else:
                    response = e.message
        except ClientException as e:
            error = True
            if 'Max retries exceeded' in str(e.message):
                response = 'Max retries exceeded, Failed to establish a new connection'
            else:
                response = e.message
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def update_namespace_request(self, namespace, request_body):
        """
        This method will update namespace present in alibaba
        :param namespace:
        :param request_body:
        :return:
        """
        error = False
        response = None
        try:
            client = AcsClient(self.access_key, self.secret_key, self.region_id)

            request_update_namespace = UpdateNamespaceRequest.UpdateNamespaceRequest()
            request_update_namespace.set_endpoint(self.region_id)
            request_update_namespace.set_Namespace(namespace)
            request_update_namespace.set_content(json.dumps(request_body))
            response_update_namespace = client.do_action_with_exception(request_update_namespace)
            response = json.loads(response_update_namespace)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                if response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                else:
                    response = e.message
        except ClientException as e:
            error = True
            if 'Max retries exceeded' in str(e.message):
                response = 'Max retries exceeded, Failed to establish a new connection'
            else:
                response = e.message
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

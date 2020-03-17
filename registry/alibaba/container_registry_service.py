import json

from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcr.request.v20160607 import CreateNamespaceRequest, GetNamespaceListRequest, GetNamespaceRequest, \
    DeleteNamespaceRequest, UpdateNamespaceRequest, CreateRepoRequest, GetRepoListByNamespaceRequest, UpdateRepoRequest, \
    DeleteRepoRequest, GetRepoTagsRequest, GetRepoBuildListRequest, GetRepoWebhookRequest, CreateRepoWebhookRequest, \
    DeleteRepoWebhookRequest, UpdateRepoWebhookRequest, GetRepoSourceRepoRequest, DeleteImageRequest, \
    GetImageLayerRequest, GetImageManifestRequest

from cluster.alibaba.compute_service import Alibaba_ECS


class Alibaba_CRS:
    def __init__(self, ali_access_key, ali_secret_key):
        """
        constructor for the Alibaba_CRS class
        :param ali_access_key:
        :param ali_secret_key:
        """
        self.access_key = ali_access_key
        self.secret_key = ali_secret_key
        self.region_id = "cr.cn-beijing.aliyuncs.com"

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
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def create_repository_request(self, namespace, repository_name, repository_summary, repository_detail,
                                  repository_type, region_id):
        """
        Creates a repository
        :param namespace:
        :param repository_name:
        :param repository_summary:
        :param repository_detail:
        :param repository_type:
        :param region_id:
        :return:
        """
        error = False
        response = None
        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)

            client_create_repository_request = CreateRepoRequest.CreateRepoRequest()
            client_create_repository_request.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            body = """ {
    "repo": {   
        "RepoNamespace": "%s",   
        "RepoName": "%s",   
        "Summary": "%s",   
        "Detail": "%s",   
        "RepoType": "%s",   
    }   
}""" % (namespace, repository_name, repository_summary, repository_detail, repository_type)
            client_create_repository_request.set_content(body)
            client_response = client.do_action_with_exception(client_create_repository_request)
            response = json.loads(client_response)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def list_repository_by_provider(self):
        """
        This method will return all repository present in alibaba
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
            repo_list = []
            alibaba_ecs = Alibaba_ECS(
                ali_access_key=self.access_key,
                ali_secret_key=self.secret_key,
                region_id='default'
            )
            flag, region_list = alibaba_ecs.list_container_registry_regions()
            if flag:
                for namespace in namespace_list:
                    region_repository_list = []
                    repo_dict = {
                        'namespace': namespace.get('namespace'),
                        'region_list': region_repository_list
                    }
                    for region_id in region_list:
                        region_dict = {
                            'region_name': region_id,
                            'repository_list': []
                        }
                        request_get_repo_list_by_namespace = GetRepoListByNamespaceRequest.GetRepoListByNamespaceRequest()
                        request_get_repo_list_by_namespace.set_RepoNamespace(namespace.get('namespace'))
                        request_get_repo_list_by_namespace.set_endpoint("cr.%s.aliyuncs.com" % region_id)
                        response_get_repo_list_by_namespace = client.do_action_with_exception(
                            request_get_repo_list_by_namespace)
                        region_dict.update({
                            'repository_list': json.loads(response_get_repo_list_by_namespace).get('data').get('repos')
                        })
                        region_repository_list.append(region_dict)
                    repo_list.append(repo_dict)
                response = repo_list
            else:
                raise Exception('Error occurred while fetching the region list')
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def list_repository_by_namespace(self, namespace):
        """
        This method will return all repository present in alibaba
        :param namespace:
        :return:
        """
        error = False
        response = None

        try:
            alibaba_ecs = Alibaba_ECS(
                ali_access_key=self.access_key,
                ali_secret_key=self.secret_key,
                region_id='default'
            )
            flag, region_list = alibaba_ecs.list_container_registry_regions()
            if flag:
                region_repository_list = []
                repo_dict = {
                    'namespace': namespace,
                    'region_list': region_repository_list
                }
                for region_id in region_list:
                    region_dict = {
                        'region_name': region_id,
                        'repository_list': []
                    }
                    client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)
                    request_get_repo_list_by_namespace = GetRepoListByNamespaceRequest.GetRepoListByNamespaceRequest()
                    request_get_repo_list_by_namespace.set_RepoNamespace(namespace)
                    request_get_repo_list_by_namespace.set_endpoint("cr.%s.aliyuncs.com" % region_id)
                    response_get_repo_list_by_namespace = client.do_action_with_exception(
                        request_get_repo_list_by_namespace)
                    region_dict.update({
                        'repository_list': json.loads(response_get_repo_list_by_namespace).get('data').get('repos')
                    })
                    region_repository_list.append(region_dict)
                response = repo_dict
            else:
                raise Exception('Error occurred while fetching the region list')
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def update_repository(self, region_id, namespace, repository_name, repo_type, summary, detail):
        """
        This method will update repository
        :param region_id:
        :param namespace:
        :param repository_name:
        :param repo_type:
        :param summary:
        :param detail:
        :return:
        """
        error = False
        response = None

        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)
            request_update_repository = UpdateRepoRequest.UpdateRepoRequest()
            request_update_repository.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            request_update_repository.set_RepoNamespace(namespace)
            request_update_repository.set_RepoName(repository_name)
            body = """{
                    "Repo": {        
                    "RepoType": "%s",
                    "Summary": "%s",
                    "Detail": "%s"
                }
            }""" % (repo_type, summary, detail)
            request_update_repository.set_content(body.encode('utf-8'))
            response_update_repository = client.do_action_with_exception(request_update_repository)
            response = json.loads(response_update_repository)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def get_repository_source(self, namespace, repository_name, region_id):
        """
        Retrieve a repository source
        :param namespace:
        :param repository_name:
        :param region_id:
        :return:
        """
        error = False
        response = None
        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)

            client_get_repository_source_request = GetRepoSourceRepoRequest.GetRepoSourceRepoRequest()
            client_get_repository_source_request.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            client_get_repository_source_request.set_RepoName(repository_name)
            client_get_repository_source_request.set_RepoNamespace(namespace)

            client_response = client.do_action_with_exception(client_get_repository_source_request)
            response = json.loads(client_response)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                    if 'docker system error' in response:
                        error = False
                        response = None
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def delete_repository_request(self, namespace, repository_name, region_id):
        """
        Delete a repository
        :param namespace:
        :param repository_name:
        :param region_id:
        :return:
        """
        error = False
        response = None
        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)

            client_delete_repository_request = DeleteRepoRequest.DeleteRepoRequest()
            client_delete_repository_request.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            client_delete_repository_request.set_RepoName(repository_name)
            client_delete_repository_request.set_RepoNamespace(namespace)

            client_response = client.do_action_with_exception(client_delete_repository_request)
            response = json.loads(client_response)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                    if 'docker system error' in response:
                        error = False
                        response = None
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def list_all_tags_of_repository(self, region_id, namespace, repository_name):
        """
        This method will list all tags belongs to repository
        :param region_id:
        :param namespace:
        :param repository_name:
        :return:
        """
        error = False
        response = None

        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)
            request_get_repository_tags = GetRepoTagsRequest.GetRepoTagsRequest()
            request_get_repository_tags.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            request_get_repository_tags.set_RepoNamespace(namespace)
            request_get_repository_tags.set_RepoName(repository_name)
            response_get_repository_tags = client.do_action_with_exception(request_get_repository_tags)
            response = json.loads(response_get_repository_tags)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def list_all_repository_build(self, region_id, namespace, repository_name):
        """
        This method will list all builds belongs to repository
        :param region_id:
        :param namespace:
        :param repository_name:
        :return:
        """
        error = False
        response = None

        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)
            request_get_repo_build_list = GetRepoBuildListRequest.GetRepoBuildListRequest()
            request_get_repo_build_list.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            request_get_repo_build_list.set_RepoNamespace(namespace)
            request_get_repo_build_list.set_RepoName(repository_name)
            response_get_repo_build_list = client.do_action_with_exception(request_get_repo_build_list)
            response = json.loads(response_get_repo_build_list)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def get_repo_webhook_request(self, region_id, namespace, repository_name):
        """
        This method will return webhooks belongs to repository
        :param region_id:
        :param namespace:
        :param repository_name:
        :return:
        """
        error = False
        response = None

        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)
            request_get_repo_webhook_request = GetRepoWebhookRequest.GetRepoWebhookRequest()
            request_get_repo_webhook_request.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            request_get_repo_webhook_request.set_RepoNamespace(namespace)
            request_get_repo_webhook_request.set_RepoName(repository_name)
            response_get_repo_webhook_request = client.do_action_with_exception(request_get_repo_webhook_request)
            response = json.loads(response_get_repo_webhook_request)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def delete_repository_tag_request(self, namespace, repository_name, region_id, tag_name):
        """
        Delete a repository tag
        :param namespace:
        :param repository_name:
        :param region_id:
        :param tag_name:
        :return:
        """
        error = False
        response = None
        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)

            client_delete_repository_tag_request = DeleteImageRequest.DeleteImageRequest()
            client_delete_repository_tag_request.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            client_delete_repository_tag_request.set_RepoName(repository_name)
            client_delete_repository_tag_request.set_RepoNamespace(namespace)
            client_delete_repository_tag_request.set_Tag(tag_name)

            client_response = client.do_action_with_exception(client_delete_repository_tag_request)
            response = json.loads(client_response)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                    if 'docker system error' in response:
                        error = False
                        response = None
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def get_repository_image_layer_request(self, namespace, repository_name, region_id, tag_name):
        """
        Get a repository image layer
        :param namespace:
        :param repository_name:
        :param region_id:
        :param tag_name:
        :return:
        """
        error = False
        response = None
        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)

            client_get_repository_image_layer_request = GetImageLayerRequest.GetImageLayerRequest()
            client_get_repository_image_layer_request.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            client_get_repository_image_layer_request.set_RepoName(repository_name)
            client_get_repository_image_layer_request.set_RepoNamespace(namespace)
            client_get_repository_image_layer_request.set_Tag(tag_name)

            client_response = client.do_action_with_exception(client_get_repository_image_layer_request)
            response = json.loads(client_response)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                    if 'docker system error' in response:
                        error = False
                        response = None
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def create_repo_webhook_request(self, region_id, namespace, repository_name, trigger_type, webhook_url,
                                    webhook_name, trigger_tag_list):
        """
        This method will creates webhook to repository
        :param region_id:
        :param namespace:
        :param repository_name:
        :param trigger_type:
        :param webhook_url:
        :param webhook_name:
        :param trigger_tag_list:
        :return:
        """
        error = False
        response = None

        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)
            request_create_repo_webhook_request = CreateRepoWebhookRequest.CreateRepoWebhookRequest()
            request_create_repo_webhook_request.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            request_create_repo_webhook_request.set_RepoNamespace(namespace)
            request_create_repo_webhook_request.set_RepoName(repository_name)
            new_trigger_tag_list = []
            for tag in trigger_tag_list:
                new_trigger_tag_list.append(str(tag))
            body = """{
    "Webhook": {
        "WebhookName": "%s",
        "WebhookUrl": "%s",
        "TriggerType": "%s",
        "TriggerTag": %s
    }
}""" % (webhook_name, webhook_url, trigger_type, new_trigger_tag_list)
            request_create_repo_webhook_request.set_content(body.encode('utf-8'))
            response_create_repo_webhook_request = client.do_action_with_exception(request_create_repo_webhook_request)
            response = json.loads(response_create_repo_webhook_request)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def update_repo_webhook_request(self, region_id, namespace, repository_name, trigger_type, webhook_url,
                                    webhook_name, trigger_tag_list, webhook_id):
        """
        This method will updates webhook to repository
        :param region_id:
        :param namespace:
        :param repository_name:
        :param trigger_type:
        :param webhook_url:
        :param webhook_name:
        :param trigger_tag_list:
        :param webhook_id:
        :return:
        """
        error = False
        response = None

        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)
            request_update_repo_webhook_request = UpdateRepoWebhookRequest.UpdateRepoWebhookRequest()
            request_update_repo_webhook_request.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            request_update_repo_webhook_request.set_RepoNamespace(namespace)
            request_update_repo_webhook_request.set_RepoName(repository_name)
            request_update_repo_webhook_request.set_WebhookId(str(webhook_id))
            new_trigger_tag_list = []
            for tag in trigger_tag_list:
                new_trigger_tag_list.append(str(tag))
            body = """{
   "Webhook": {
      "WebhookName": "%s",
      "WebhookUrl": "%s",
      "TriggerType": "%s",
      "TriggerTag": %s
   }
}""" % (webhook_name, webhook_url, trigger_type, new_trigger_tag_list)
            request_update_repo_webhook_request.set_content(body.encode('utf-8'))
            response_update_repo_webhook_request = client.do_action_with_exception(request_update_repo_webhook_request)
            response = json.loads(response_update_repo_webhook_request)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def delete_repo_webhook_request(self, region_id, namespace, repository_name, webhook_id):
        """
        This method will delete webhook to repository
        :param region_id:
        :param namespace:
        :param repository_name:
        :param webhook_id:
        :return:
        """
        error = False
        response = None

        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)
            request_delete_repo_webhook_request = DeleteRepoWebhookRequest.DeleteRepoWebhookRequest()
            request_delete_repo_webhook_request.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            request_delete_repo_webhook_request.set_RepoNamespace(namespace)
            request_delete_repo_webhook_request.set_RepoName(repository_name)
            request_delete_repo_webhook_request.set_WebhookId(str(webhook_id))

            response_delete_repo_webhook_request = client.do_action_with_exception(request_delete_repo_webhook_request)
            response = json.loads(response_delete_repo_webhook_request)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

    def get_image_mainfest_request(self, region_id, namespace, repository_name, tag_name):
        """
        This method will return manifest information belongs to a particular image
        :param region_id:
        :param namespace:
        :param repository_name:
        :param tag_name:
        :return:
        """
        error = False
        response = None

        try:
            client = AcsClient(self.access_key, self.secret_key, "cr.%s.aliyuncs.com" % region_id)
            request_get_image_mainfest_request = GetImageManifestRequest.GetImageManifestRequest()
            request_get_image_mainfest_request.set_endpoint("cr.%s.aliyuncs.com" % region_id)
            request_get_image_mainfest_request.set_RepoNamespace(namespace)
            request_get_image_mainfest_request.set_RepoName(repository_name)
            request_get_image_mainfest_request.set_Tag(tag_name)
            response_get_image_mainfest_request = client.do_action_with_exception(request_get_image_mainfest_request)
            response = json.loads(response_get_image_mainfest_request)
        except ServerException as e:
            error = True
            if 'key is not found.' in str(e.message):
                response = e.message
            else:
                if 'ServerResponseBody' in e.message:
                    response = json.loads(str(e.message).split('ServerResponseBody: ')[1]).get('message')
                elif response == '':
                    response = 'Invalid request %s' % json.loads(str(e.message).split('ServerResponseBody: ')[1]).get(
                        'code')
                elif response is None:
                    response = e.error_code
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

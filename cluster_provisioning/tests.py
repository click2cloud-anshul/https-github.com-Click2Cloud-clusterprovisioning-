# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your tests here.
import base64
import json
import subprocess
import uuid

from aliyunsdkcr.request.v20160607 import GetNamespaceRequest, DeleteNamespaceRequest, CreateRepoRequest, \
    DeleteRepoRequest, GetRepoListByNamespaceRequest

access_key = ''
secret_key = ''
from cluster.kuberenetes.operations import Kubernetes_Operations


def all_resources():
    k8s_obj = Kubernetes_Operations(configuration_yaml='<config_file_path>')
    flag, token = k8s_obj.get_token()
    print token
    flag, result = k8s_obj.get_all_resources(cluster_url='<kubernetes_cluster_endpoint>',
                                             token=token)
    print result


def all_pods():
    k8s_obj = Kubernetes_Operations(configuration_yaml='<config_file_path>')
    flag, token = k8s_obj.get_token()
    print token
    flag, result = k8s_obj.get_pods(cluster_url='<kubernetes_cluster_endpoint>',
                                    token=token)
    print result


def all_deployments():
    k8s_obj = Kubernetes_Operations(configuration_yaml='<config_file_path>')
    flag, token = k8s_obj.get_token()
    print token
    flag, result = k8s_obj.get_deployments(cluster_url='<kubernetes_cluster_endpoint>',
                                           token=token)
    print result


def test_to_encode_and_decode():
    data = "text"
    encodedStr = str(base64.b64encode(data.encode("utf-8")))
    print encodedStr
    decoded = base64.b64decode(encodedStr)
    print decoded


def check_git_branch():
    github_username = ""
    github_password = ""
    git_url = ""
    branch_name = ""

    git_repo_name = 'https://%s:%s@%s' % (github_username, github_password, git_url)
    check_github_repo = subprocess.Popen(
        ['git', 'ls-remote', git_repo_name, '--tags', branch_name],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = check_github_repo.communicate()
    if not error and len(output) > 0:
        # if repository and branch exist present
        pass
    else:
        # if error is present
        pass


def s2i_git_branch():
    github_username = ""
    github_password = ""
    git_url = ""
    branch_name = ""
    builder_image = ""
    new_image_name = ""

    git_repo_name = 'https://%s:%s@%s' % (github_username, github_password, git_url)
    check_github_repo = subprocess.Popen(
        ['git', 'ls-remote', str(git_repo_name), '--tags', branch_name],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = check_github_repo.communicate()
    if not error and len(output) > 0:
        # if repository and branch exist present
        build_new_image = subprocess.Popen(
            ['s2i', 'build', 'https://%s:%s@%s' % (github_username, github_password, git_url), '-r',
             '%s' % branch_name, builder_image, new_image_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, info = build_new_image.communicate()
        print output
        print info
    else:
        # if error is present
        pass
    pass


def create_docker_secret():
    docker_username = ''
    docker_password = ''
    namespace = ''
    sceret_name = ''
    registry = 'https://index.docker.io/v1/'
    cred_payload = {
        "auths": {
            registry: {
                "Username": docker_username,
                "Password": docker_password,
                "auth": '%s' % (base64.b64encode('%s:%s' % (docker_username, docker_password)))
            }
        }
    }
    data = {
        ".dockerconfigjson": base64.b64encode(
            json.dumps(cred_payload).encode()
        ).decode()
    }
    config_file_path = "<config_file_path>"
    k8s_obj = Kubernetes_Operations(configuration_yaml=config_file_path)
    secret = k8s_obj.client.V1Secret(
        api_version="v1",
        data=data,
        kind="Secret",
        metadata=dict(name=sceret_name, namespace=namespace),
        type="kubernetes.io/dockerconfigjson",
    )
    output = k8s_obj.clientCoreV1.create_namespaced_secret(namespace=namespace, body=secret)
    print output


def generate_uuid():
    print str(uuid.uuid4()).split('-')[0]


def get_list_of_namespaces_alibaba_registry():
    # !/usr/bin/env python
    # coding=utf-8

    from aliyunsdkcore.acs_exception.exceptions import ClientException
    from aliyunsdkcore.acs_exception.exceptions import ServerException
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcr.request.v20160607 import GetNamespaceListRequest
    client = AcsClient(access_key, secret_key, 'cn-hangzhou')

    request = GetNamespaceListRequest.GetNamespaceListRequest()
    # Set the parameters
    # request.set_RepoNamespace("repoNamespaceName")
    # request.set_RepoName("repoName")
    # request.set_Tag("tag")
    request.set_endpoint("cr.cn-hangzhou.aliyuncs.com")
    # Make a request
    try:
        namespace_list = []
        response = client.do_action_with_exception(request)
        response = json.loads(response)
        if 'data' in response:
            if 'namespaces' in response.get('data'):
                response_list_of_namespaces = response.get('data').get('namespaces')
                for response_namespace in response_list_of_namespaces:
                    request = GetNamespaceRequest.GetNamespaceRequest()
                    request.set_endpoint("cr.cn-hangzhou.aliyuncs.com")
                    request.set_Namespace(response_namespace.get('namespace'))
                    response = client.do_action_with_exception(request)
                    response = json.loads(response)
                    namespace_list.append(response.get('data').get('namespace'))
        print namespace_list
    except ServerException as e:
        print(e)
    except ClientException as e:
        print(e)

    # request = CommonRequest()
    # request.set_accept_format('json')
    # request.set_domain('cr.cn-hangzhou.aliyuncs.com')
    # request.set_method('POST')
    # request.set_protocol_type('https')  # https | http
    # request.set_version('2018-12-01')
    # request.set_action_name('ListNamespace')
    # #
    # request.add_query_param('RegionId', "cn-hangzhou")
    #
    # response = client.do_action(request)
    # python2:  print(response)
    # print(str(response, encoding='utf-8'))


def create_namespace_request():
    from aliyunsdkcore.acs_exception.exceptions import ClientException
    from aliyunsdkcore.acs_exception.exceptions import ServerException
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcr.request.v20160607 import CreateNamespaceRequest
    client = AcsClient(access_key, secret_key, 'cn-hangzhou')

    request = CreateNamespaceRequest.CreateNamespaceRequest()
    # Set the parameters
    # request.set_RepoNamespace("repoNamespaceName")
    # request.set_RepoName("repoName")
    # request.set_Tag("tag")
    request.set_endpoint("cr.cn-hangzhou.aliyuncs.com")
    # Make a request
    body = """{
    "Namespace": {
        "Namespace": "test-c2c-namespace-123",
    }
}"""
    try:
        request.set_content(body)
        response = client.do_action_with_exception(request)
        response = json.loads(response)
        pass
    except ServerException as e:
        print(e)
    except ClientException as e:
        print(e)


def update_namespace_request():
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcr.request.v20160607 import UpdateNamespaceRequest
    client = AcsClient(access_key, secret_key, 'cn-hangzhou')

    request = UpdateNamespaceRequest.UpdateNamespaceRequest()
    # Set the parameters
    # request.set_RepoNamespace("repoNamespaceName")
    # request.set_RepoName("repoName")
    # request.set_Tag("tag")
    request.set_endpoint("cr.cn-hangzhou.aliyuncs.com")
    request.set_Namespace('test-c2c-namespace-123')
    # Make a request
    body = """{
         "Namespace": {
        "AutoCreate": true,
        "DefaultVisibility": "PUBLIC"
    }
}"""
    try:
        request.set_content(body.encode('utf-8'))
        response = client.do_action_with_exception(request)
        response = json.loads(response)
        pass
    except Exception as e:
        print e


def delete_namespace_request():
    from aliyunsdkcore.client import AcsClient
    client = AcsClient(access_key, secret_key, 'cn-hangzhou')

    request = DeleteNamespaceRequest.DeleteNamespaceRequest()
    # Set the parameters
    # request.set_RepoNamespace("repoNamespaceName")
    # request.set_RepoName("repoName")
    # request.set_Tag("tag")
    request.set_endpoint("cr.cn-hangzhou.aliyuncs.com")
    request.set_Namespace('test-c2c-namespace-123')
    # Make a request
    try:
        response = client.do_action_with_exception(request)
        response = json.loads(response)
        pass
    except Exception as e:
        print e


def create_repository():
    from aliyunsdkcore.client import AcsClient
    client = AcsClient(access_key, secret_key, 'cn-hangzhou')

    request = CreateRepoRequest.CreateRepoRequest()
    # Set the parameters
    # request.set_RepoNamespace("repoNamespaceName")
    # request.set_RepoName("repoName")
    # request.set_Tag("tag")
    request.set_endpoint("cr.cn-hangzhou.aliyuncs.com")
    # Make a request
    body = """ {
    "repo": {   
        "RepoNamespace": "test-c2c-namespace-123",   
        "RepoName": "testrepo-1",   
        "Summary": "tes-repo",   
        "Detail": "test-repo",   
        "RepoType": "PUBLIC",   
    }   
}"""
    try:
        request.set_content(body.encode('utf-8'))
        response = client.do_action_with_exception(request)
        response = json.loads(response)
        pass
    except Exception as e:
        print e


def delete_repo_request():
    from aliyunsdkcore.client import AcsClient
    client = AcsClient(access_key, secret_key, 'cn-hangzhou')

    request = DeleteRepoRequest.DeleteRepoRequest()
    request.set_endpoint("cr.cn-hangzhou.aliyuncs.com")
    request.set_RepoName('testrepo-1')
    request.set_RepoNamespace('test-c2c-namespace-123')
    # Make a request
    try:
        response = client.do_action_with_exception(request)
        response = json.loads(response)
        pass
    except Exception as e:
        print e


def get_repo_list_by_namespace():
    from aliyunsdkcore.acs_exception.exceptions import ClientException
    from aliyunsdkcore.acs_exception.exceptions import ServerException
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcr.request.v20160607 import GetNamespaceListRequest
    client = AcsClient(access_key, secret_key, 'cn-hangzhou')

    request = GetNamespaceListRequest.GetNamespaceListRequest()
    # Set the parameters
    # request.set_RepoNamespace("repoNamespaceName")
    # request.set_RepoName("repoName")
    # request.set_Tag("tag")
    request.set_endpoint("cr.cn-hangzhou.aliyuncs.com")
    # Make a request
    try:
        namespace_list = []
        response = client.do_action_with_exception(request)
        response = json.loads(response)
        if 'data' in response:
            if 'namespaces' in response.get('data'):
                response_list_of_namespaces = response.get('data').get('namespaces')
                for response_namespace in response_list_of_namespaces:
                    request = GetNamespaceRequest.GetNamespaceRequest()
                    request.set_endpoint("cr.cn-hangzhou.aliyuncs.com")
                    request.set_Namespace(response_namespace.get('namespace'))
                    response = client.do_action_with_exception(request)
                    response = json.loads(response)
                    namespace_list.append(response.get('data').get('namespace'))
        print namespace_list
        for namespace in namespace_list:
            request = GetRepoListByNamespaceRequest.GetRepoListByNamespaceRequest()
            request.set_RepoNamespace(namespace.get('namespace'))
            response = client.do_action_with_exception(request)

            response = json.loads(response)

        pass
    except ServerException as e:
        print(e)
    except ClientException as e:
        print(e)


get_repo_list_by_namespace()

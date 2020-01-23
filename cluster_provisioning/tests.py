# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your tests here.
import base64
import json
import subprocess
import uuid

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

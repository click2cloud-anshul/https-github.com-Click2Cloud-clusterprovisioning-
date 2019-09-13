from __future__ import unicode_literals

from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ali.ecs import *

from ali.cluster import *


@api_view(["GET"])
def alibaba_region_list(params):
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['access_key', 'secret_key']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({key: {"error": "key " + key + " is not found"}})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({key: {"error": "Value " + key + " is not found"}})
        if not error:
            access_key = json_request["access_key"]
            secret_key = json_request["secret_key"]

            alibaba_ecs = Alibaba_ECS(
                ali_access_key=access_key,
                ali_secret_key=secret_key,
                region_id=None,
            )

            flag, regions = alibaba_ecs.list_regions()

            if flag:
                response.update({"status": flag,
                                 "regionList": regions,
                                 "error": ""})
            else:
                response.update({"status": flag,
                                 "regionList": "",
                                 "error": regions})

        return JsonResponse(response, safe=False)
    except Exception as e:
        Response({"status": False,
                  "message": "",
                  "error": e.message})


@api_view(["GET"])
def alibaba_key_pair_list(params):
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['access_key', 'secret_key', 'region_id']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({key: {"error": "key " + key + " is not found"}})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({key: {"error": "Value " + key + " is not found"}})
        if not error:
            access_key = json_request["access_key"]
            secret_key = json_request["secret_key"]
            region_id = json_request["region_id"]
            alibaba_ecs = Alibaba_ECS(
                ali_access_key=access_key,
                ali_secret_key=secret_key,
                region_id=region_id,
            )

            flag, key_pairs = alibaba_ecs.key_pairs_list()

            if flag:
                response.update({"status": flag,
                                 "key_pairs_list": key_pairs,
                                 "error": ""})
            else:
                response.update({"status": flag,
                                 "key_pairs_list": "",
                                 "error": key_pairs})

        return JsonResponse(response, safe=False)
    except Exception as e:
        Response({"status": False,
                  "message": "",
                  "error": e.message})


@api_view(["GET"])
def get_vpc_list(params):
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['access_key', 'secret_key', 'region_id']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({key: {"error": "key " + key + " is not found"}})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({key: {"error": "Value " + key + " is not found"}})
        if not error:
            access_key = json_request["access_key"]
            secret_key = json_request["secret_key"]
            region_id = json_request["region_id"]
            alibaba_ecs = Alibaba_ECS(
                ali_access_key=access_key,
                ali_secret_key=secret_key,
                region_id=region_id,
            )

            flag, vpc_list = alibaba_ecs.vpc_list()

            if flag:
                response.update({"status": flag,
                                 "vpc_list": vpc_list,
                                 "error": ""})
            else:
                response.update({"status": flag,
                                 "vpc_list": "",
                                 "error": vpc_list})

        return JsonResponse(response, safe=False)
    except Exception as e:
        Response({"status": False,
                  "message": "",
                  "error": e.message})


@api_view(["GET"])
def get_cluster_details(params):
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['access_key', 'secret_key', 'cluster_id']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({key: {"error": "key " + key + " is not found"}})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({key: {"error": "Value " + key + " is not found"}})
        if not error:
            access_key = json_request["access_key"]
            secret_key = json_request["secret_key"]
            cluster_id = json_request["cluster_id"]
            alibaba_cs = Alibaba_CS(
                ali_access_key=access_key,
                ali_secret_key=secret_key,
                region_id='default'
            )

            flag, cluster_details = alibaba_cs.cluster_details(cluster_id)

            if flag:
                response.update({"status": flag,
                                 "cluster_details": cluster_details,
                                 "error": ""})
            else:
                response.update({"status": flag,
                                 "cluster_details": "",
                                 "error": cluster_details})

        return JsonResponse(response, safe=False)
    except Exception as e:
        Response({"status": False,
                  "message": "",
                  "error": e.message})


@api_view(["POST"])
def create_kubernetes_cluster(params):
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['access_key', 'secret_key', 'request_body']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({key: {"error": "key " + key + " is not found"}})
            else:
                if key.__contains__("request_body"):
                    continue
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({key: {"error": "Value " + key + " is not found"}})
        if not error:
            access_key = json_request["access_key"]
            secret_key = json_request["secret_key"]
            request_body = json_request["request_body"]
            alibaba_cs = Alibaba_CS(
                ali_access_key=access_key,
                ali_secret_key=secret_key,
                region_id='default'
            )

            flag, new_cluster_details = alibaba_cs.create_cluster(request_body)

            if flag:
                response.update({"status": flag,
                                 "new_cluster_details": new_cluster_details,
                                 "error": ""})
            else:
                split_str = str(new_cluster_details).split('ServerResponseBody: ')
                response.update({"status": flag,
                                 "new_cluster_details": "",
                                 "error": json.loads((split_str.__getitem__(1)))})

        return JsonResponse(response, safe=False)
    except Exception as e:
        Response({"status": False,
                  "message": "",
                  "error": e.message})


@api_view(["DELETE"])
def delete_kubernetes_cluster(params):
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['access_key', 'secret_key', 'cluster_id']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({key: {"error": "key " + key + " is not found"}})
            else:
                if key.__contains__("request_body"):
                    continue
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({key: {"error": "Value " + key + " is not found"}})
        if not error:
            access_key = json_request["access_key"]
            secret_key = json_request["secret_key"]
            cluster_id = json_request["cluster_id"]
            alibaba_cs = Alibaba_CS(
                ali_access_key=access_key,
                ali_secret_key=secret_key,
                region_id='default'
            )

            flag, deleted_cluster_details = alibaba_cs.delete_cluster(cluster_id)

            if flag:
                response.update({"status": flag,
                                 "message": deleted_cluster_details,
                                 "error": ""})
            else:
                split_str = str(deleted_cluster_details).split('ServerResponseBody: ')
                response.update({"status": flag,
                                 "message": "",
                                 "error": json.loads((split_str.__getitem__(1)))})

        return JsonResponse(response, safe=False)
    except Exception as e:
        print e.message
        Response({"status": False,
                  "message": "",
                  "error": e.message})


@api_view(["GET"])
def get_cluster_config(params):
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['access_key', 'secret_key', 'cluster_id']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({key: {"error": "key " + key + " is not found"}})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({key: {"error": "Value " + key + " is not found"}})
        if not error:
            access_key = json_request["access_key"]
            secret_key = json_request["secret_key"]
            cluster_id = json_request["cluster_id"]
            alibaba_cs = Alibaba_CS(
                ali_access_key=access_key,
                ali_secret_key=secret_key,
                region_id='default'
            )

            flag, cluster_config = alibaba_cs.get_cluster_config(cluster_id)

            if flag:
                response.update({"status": flag,
                                 "config": json.loads(cluster_config),
                                 "error": ""})
            else:
                response.update({"status": flag,
                                 "config": "",
                                 "error": cluster_config})

        return JsonResponse(response, safe=False)
    except Exception as e:
        Response({"status": False,
                  "message": "",
                  "error": e.message})


@api_view(["GET"])
def get_all_clusters(params):
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['access_key', 'secret_key']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({key: {"error": "key " + key + " is not found"}})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({key: {"error": "Value " + key + " is not found"}})
        if not error:
            access_key = json_request["access_key"]
            secret_key = json_request["secret_key"]
            alibaba_cs = Alibaba_CS(
                ali_access_key=access_key,
                ali_secret_key=secret_key,
                region_id='default'
            )

            flag, cluster_details_list = alibaba_cs.get_all_clusters()

            if flag:
                response.update({"status": flag,
                                 "cluster_details_list": cluster_details_list,
                                 "error": ""})
            else:
                response.update({"status": flag,
                                 "cluster_details_list": "",
                                 "error": cluster_details_list})

        return JsonResponse(response, safe=False)
    except Exception as e:
        Response({"status": False,
                  "message": "",
                  "error": e.message})


@api_view(["GET"])
def get_cluster_status(params):
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['access_key', 'secret_key', 'cluster_id']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({key: {"error": "key " + key + " is not found"}})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({key: {"error": "Value " + key + " is not found"}})
        if not error:
            access_key = json_request["access_key"]
            secret_key = json_request["secret_key"]
            cluster_id = json_request["cluster_id"]
            alibaba_cs = Alibaba_CS(
                ali_access_key=access_key,
                ali_secret_key=secret_key,
                region_id='default'
            )

            flag, cluster_status = alibaba_cs.get_cluster_status(cluster_id)

            if flag:
                response.update({"status": flag,
                                 "cluster_status": cluster_status,
                                 "error": ""})
            else:
                response.update({"status": flag,
                                 "cluster_status": "",
                                 "error": cluster_status})

        return JsonResponse(response, safe=False)
    except Exception as e:
        Response({"status": False,
                  "message": "",
                  "error": e.message})

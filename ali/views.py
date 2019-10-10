from __future__ import unicode_literals


from django.http import JsonResponse
from rest_framework.decorators import api_view
from ali.ecs import *

from ali.cluster import *


@api_view(["GET"])
def alibaba_instance_list(params):
    response = {}
    access_flag = True
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id', 'provider_id', 'region_id', 'zone_id_list']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                if key.__contains__("request_body"):
                    continue
                json_request[key] = str(str(json_request[key]).strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            provider_id = json_request["provider_id"]
            region_id = json_request["region_id"]
            try:
                user_id = int(user_id)
                provider_id = int(provider_id)
                user_id = str(user_id)
                provider_id = str(provider_id)
            except Exception:
                raise Exception('Please provide valid user_id and provider_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if flag:
                access_key_secret_key_list = json.loads(access_key_secret_key_list)
                unique_access_key_list = []
                if list(access_key_secret_key_list).__len__() > 0:
                    for access_key_secret_key in access_key_secret_key_list:

                        if access_key_secret_key['client_id'] in unique_access_key_list:
                            continue
                        else:
                            unique_access_key_list.append(access_key_secret_key['client_id'])
                for access_key in unique_access_key_list:

                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key['client_id'] is access_key and access_key_secret_key['id'] is int(
                                provider_id):
                            access_flag = False
                            alibaba_ecs = Alibaba_ECS(
                                ali_access_key=access_key_secret_key['client_id'],
                                ali_secret_key=access_key_secret_key['client_secret'],
                                region_id=region_id
                            )
                            zone_id_list = eval(json_request['zone_id_list'])

                            flag, instance_list = alibaba_ecs.instance_list(zone_id_list)

                            if flag:
                                if flag:
                                    response.update({"status": flag,
                                                     "instance_list": instance_list,
                                                     "error": ""})
                                else:
                                    response.update({"status": flag,
                                                     "instance_list": instance_list,
                                                     "error": "Cluster created but error in db"})
                            else:
                                if str(instance_list).__contains__('No such'):
                                    response.update({"status": flag,
                                                     "instance_list": "",
                                                     "error": instance_list})
                                    break
                                split_str = str(instance_list).split('ServerResponseBody: ')
                                response.update({"status": flag,
                                                 "instance_list": "",
                                                 "error": json.loads((split_str.__getitem__(1)))})
            else:
                response.update({"status": False,
                                 "instance_list": "",
                                 "error": access_key_secret_key_list})
        if access_flag:
            response.update({"status": False,
                             "instance_list": "",
                             "error": 'Please provide valid user_id and provider_id'})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "instance_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def alibaba_region_list(params):
    response = {}
    access_flag = True
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id', 'provider_id']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                if key.__contains__("request_body"):
                    continue
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            provider_id = json_request["provider_id"]
            try:
                user_id = int(user_id)
                provider_id = int(provider_id)
                user_id = str(user_id)
                provider_id = str(provider_id)
            except Exception:
                raise Exception('Please provide valid user_id and provider_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if flag:
                access_key_secret_key_list = json.loads(access_key_secret_key_list)
                unique_access_key_list = []
                if list(access_key_secret_key_list).__len__() > 0:
                    for access_key_secret_key in access_key_secret_key_list:

                        if access_key_secret_key['client_id'] in unique_access_key_list:
                            continue
                        else:
                            unique_access_key_list.append(access_key_secret_key['client_id'])
                for access_key in unique_access_key_list:

                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key['client_id'] is access_key and access_key_secret_key['id'] is int(
                                provider_id):
                            access_flag = False
                            alibaba_ecs = Alibaba_ECS(
                                ali_access_key=access_key_secret_key['client_id'],
                                ali_secret_key=access_key_secret_key['client_secret'],
                                region_id='default'
                            )
                            flag, region_list = alibaba_ecs.list_regions()

                            if flag:
                                if flag:
                                    response.update({"status": flag,
                                                     "region_list": region_list,
                                                     "error": ""})
                                else:
                                    response.update({"status": flag,
                                                     "region_list": region_list,
                                                     "error": "Cluster created but error in db"})
                            else:
                                if str(region_list).__contains__('No such'):
                                    response.update({"status": flag,
                                                     "instance_list": "",
                                                     "error": region_list})
                                    break
                                split_str = str(region_list).split('ServerResponseBody: ')
                                response.update({"status": flag,
                                                 "region_list": "",
                                                 "error": json.loads((split_str.__getitem__(1)))})
            else:
                response.update({"status": False,
                                 "region_list": "",
                                 "error": access_key_secret_key_list})
        if access_flag:
            response.update({"status": False,
                             "region_list": "",
                             "error": 'Please provide valid user_id and provider_id'})
        return JsonResponse(response, safe=False)

    except Exception as e:
        response.update({"status": False,
                         "region_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def alibaba_key_pair_list(params):
    response = {}
    access_flag = True
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id', 'provider_id', 'region_id']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                if key.__contains__("request_body"):
                    continue
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            provider_id = json_request["provider_id"]
            region_id = json_request["region_id"]
            try:
                user_id = int(user_id)
                provider_id = int(provider_id)
                user_id = str(user_id)
                provider_id = str(provider_id)
            except Exception as e:
                raise Exception('Please provide valid user_id and provider_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if flag:
                access_key_secret_key_list = json.loads(access_key_secret_key_list)
                unique_access_key_list = []
                if list(access_key_secret_key_list).__len__() > 0:
                    for access_key_secret_key in access_key_secret_key_list:

                        if access_key_secret_key['client_id'] in unique_access_key_list:
                            continue
                        else:
                            unique_access_key_list.append(access_key_secret_key['client_id'])
                for access_key in unique_access_key_list:

                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key['client_id'] is access_key and access_key_secret_key['id'] is int(
                                provider_id):
                            access_flag = False
                            alibaba_ecs = Alibaba_ECS(
                                ali_access_key=access_key_secret_key['client_id'],
                                ali_secret_key=access_key_secret_key['client_secret'],
                                region_id=region_id
                            )
                            flag, key_pairs_list = alibaba_ecs.key_pairs_list()

                            if flag:
                                if flag:
                                    response.update({"status": flag,
                                                     "key_pairs_list": key_pairs_list,
                                                     "error": ""})
                                else:
                                    response.update({"status": flag,
                                                     "key_pairs_list": key_pairs_list,
                                                     "error": "Cluster created but error in db"})
                            else:
                                if str(key_pairs_list).__contains__('No such'):
                                    response.update({"status": flag,
                                                     "instance_list": "",
                                                     "error": key_pairs_list})
                                    break
                                split_str = str(key_pairs_list).split('ServerResponseBody: ')
                                response.update({"status": flag,
                                                 "key_pairs_list": "",
                                                 "error": json.loads((split_str.__getitem__(1)))})
            else:
                response.update({"status": False,
                                 "key_pairs_list": "",
                                 "error": access_key_secret_key_list})
        if access_flag:
            response.update({"status": False,
                             "key_pairs_list": "",
                             "error": 'Please provide valid user_id and provider_id'})
        return JsonResponse(response, safe=False)

    except Exception as e:
        response.update({"status": False,
                         "key_pairs_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_vpc_list(params):
    response = {}
    access_flag = True
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id', 'provider_id', 'region_id']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                if key.__contains__("request_body"):
                    continue
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            provider_id = json_request["provider_id"]
            region_id = json_request["region_id"]
            try:
                user_id = int(user_id)
                provider_id = int(provider_id)
                user_id = str(user_id)
                provider_id = str(provider_id)
            except Exception:
                raise Exception('Please provide valid user_id and provider_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if flag:
                access_key_secret_key_list = json.loads(access_key_secret_key_list)
                unique_access_key_list = []
                if list(access_key_secret_key_list).__len__() > 0:
                    for access_key_secret_key in access_key_secret_key_list:

                        if access_key_secret_key['client_id'] in unique_access_key_list:
                            continue
                        else:
                            unique_access_key_list.append(access_key_secret_key['client_id'])
                for access_key in unique_access_key_list:

                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key['client_id'] is access_key and access_key_secret_key['id'] is int(
                                provider_id):
                            access_flag = False
                            alibaba_ecs = Alibaba_ECS(
                                ali_access_key=access_key_secret_key['client_id'],
                                ali_secret_key=access_key_secret_key['client_secret'],
                                region_id=region_id
                            )
                            flag, vpc_list = alibaba_ecs.vpc_list()

                            if flag:
                                if flag:
                                    response.update({"status": flag,
                                                     "vpc_list": vpc_list,
                                                     "error": ""})
                                else:
                                    response.update({"status": flag,
                                                     "vpc_list": vpc_list,
                                                     "error": "Cluster created but error in db"})
                            else:
                                if str(vpc_list).__contains__('No such'):
                                    response.update({"status": flag,
                                                     "instance_list": "",
                                                     "error": vpc_list})
                                    break
                                split_str = str(vpc_list).split('ServerResponseBody: ')
                                response.update({"status": flag,
                                                 "vpc_list": "",
                                                 "error": json.loads((split_str.__getitem__(1)))})
            else:
                response.update({"status": False,
                                 "vpc_list": "",
                                 "error": access_key_secret_key_list})
        if access_flag:
            response.update({"status": False,
                             "vpc_list": "",
                             "error": 'Please provide valid user_id and provider_id'})
        return JsonResponse(response, safe=False)

    except Exception as e:
        response.update({"status": False,
                         "vpc_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_cluster_details(params):
    response = {}
    access_flag = True
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id', 'provider_id', 'cluster_id']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                if key.__contains__("request_body"):
                    continue
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            cursor = None
            user_id = json_request["user_id"]
            provider_id = json_request["provider_id"]
            cluster_id = json_request["cluster_id"]
            try:
                user_id = int(user_id)
                provider_id = int(provider_id)
                user_id = str(user_id)
                provider_id = str(provider_id)
                cluster_id = str(cluster_id)
            except Exception:
                raise Exception('Please provide valid user_id and provider_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)

            if flag:
                access_key_secret_key_list = json.loads(access_key_secret_key_list)
                unique_access_key_list = []
                if list(access_key_secret_key_list).__len__() > 0:
                    for access_key_secret_key in access_key_secret_key_list:

                        if access_key_secret_key['client_id'] in unique_access_key_list:
                            continue
                        else:
                            unique_access_key_list.append(access_key_secret_key['client_id'])
                for access_key in unique_access_key_list:

                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key['client_id'] is access_key and access_key_secret_key['id'] is int(
                                provider_id):
                            access_flag = False
                            alibaba_cs = Alibaba_CS(
                                ali_access_key=access_key_secret_key['client_id'],
                                ali_secret_key=access_key_secret_key['client_secret'],
                                region_id='default'
                            )
                            flag, cluster_details = alibaba_cs.cluster_details(cluster_id)

                            if flag:
                                response.update({"status": flag,
                                                 "cluster_details": cluster_details,
                                                 "error": ""})
                            else:
                                if str(cluster_details).__contains__('Invalid cluster_id'):
                                    response.update({"status": flag,
                                                     "cluster_details": "",
                                                     "error": cluster_details})
                                    break
                                split_str = str(cluster_details).split('ServerResponseBody: ')
                                response.update({"status": flag,
                                                 "cluster_details": "",
                                                 "error": json.loads((split_str.__getitem__(1)))})
            else:
                response.update({"status": False,
                                 "cluster_details": "",
                                 "error": access_key_secret_key_list})
        if access_flag:
            response.update({"status": False,
                             "cluster_details": "",
                             "error": 'Please provide valid user_id and provider_id'})
        return JsonResponse(response, safe=False)

    except Exception as e:
        response.update({"status": False,
                         "cluster_details": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["POST"])
def create_kubernetes_cluster(params):
    response = {}
    access_flag = True
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id', 'provider_id', 'request_body']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                if key.__contains__("request_body"):
                    continue
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            provider_id = json_request["provider_id"]
            try:
                user_id = int(user_id)
                provider_id = int(provider_id)
                user_id = str(user_id)
                provider_id = str(provider_id)
            except Exception:
                raise Exception('Please provide valid user_id and provider_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if flag:
                access_key_secret_key_list = json.loads(access_key_secret_key_list)
                unique_access_key_list = []
                if list(access_key_secret_key_list).__len__() > 0:
                    for access_key_secret_key in access_key_secret_key_list:

                        if access_key_secret_key['client_id'] in unique_access_key_list:
                            continue
                        else:
                            unique_access_key_list.append(access_key_secret_key['client_id'])
                for access_key in unique_access_key_list:
                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key['client_id'] is access_key and access_key_secret_key['id'] is int(
                                provider_id):
                            access_flag = False
                            request_body = json_request["request_body"]
                            alibaba_cs = Alibaba_CS(
                                ali_access_key=access_key_secret_key['client_id'],
                                ali_secret_key=access_key_secret_key['client_secret'],
                                region_id='default'
                            )
                            flag, new_cluster_details = alibaba_cs.create_cluster(request_body)

                            if flag:
                                new_params = {}
                                new_params['is_insert'] = True
                                new_params['user_id'] = int(user_id)
                                new_params['provider_id'] = int(provider_id)
                                new_params['cluster_id'] = str(new_cluster_details['cluster_id'])
                                new_params['cluster_details'] = json.dumps(request_body)
                                new_params['status'] = 'Initiated'
                                new_params['operation'] = 'created from cloudbrain'
                                flag, msg = insert_or_update_cluster_details(new_params)
                                if flag:
                                    response.update({"status": flag,
                                                     "new_cluster_details": new_cluster_details,
                                                     "error": ""})
                                else:
                                    response.update({"status": flag,
                                                     "new_cluster_details": new_cluster_details,
                                                     "error": "Cluster created but error in db"})
                            else:
                                split_str = str(new_cluster_details).split('ServerResponseBody: ')
                                response.update({"status": flag,
                                                 "new_cluster_details": "",
                                                 "error": json.loads((split_str.__getitem__(1)))})
            else:
                response.update({"status": False,
                                 "new_cluster_details": "",
                                 "error": access_key_secret_key_list})
        if access_flag:
            response.update({"status": False,
                             "new_cluster_details": "",
                             "error": 'Please provide valid user_id and provider_id'})
        return JsonResponse(response, safe=False)

    except Exception as e:
        response.update({"status": False,
                         "new_cluster_details": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["DELETE"])
def delete_kubernetes_cluster(params):
    response = {}
    access_flag = True
    try:
        json_request = json.loads(params.body)
        error = False

        valid_keys_json = ['user_id', 'provider_id', 'cluster_id']

        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                if key.__contains__("request_body"):
                    continue
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            cluster_id = json_request["cluster_id"]
            user_id = json_request["user_id"]
            provider_id = json_request["provider_id"]
            try:
                user_id = int(user_id)
                provider_id = int(provider_id)
                user_id = str(user_id)
                provider_id = str(provider_id)
            except Exception as e:
                raise Exception('Please provide valid user_id and provider_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if flag:
                access_key_secret_key_list = json.loads(access_key_secret_key_list)
                unique_access_key_list = []
                if list(access_key_secret_key_list).__len__() > 0:
                    for access_key_secret_key in access_key_secret_key_list:

                        if access_key_secret_key['client_id'] in unique_access_key_list:
                            continue
                        else:
                            unique_access_key_list.append(access_key_secret_key['client_id'])
                for access_key in unique_access_key_list:
                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key['client_id'] is access_key and access_key_secret_key['id'] is int(
                                provider_id):
                            access_flag = False
                            alibaba_cs = Alibaba_CS(
                                ali_access_key=access_key_secret_key['client_id'],
                                ali_secret_key=access_key_secret_key['client_secret'],
                                region_id='default'
                            )
                            flag, cluster_details = alibaba_cs.cluster_details(cluster_id)
                            if flag:
                                flag, deleted_cluster_details = alibaba_cs.delete_cluster(cluster_id)
                                if flag:
                                    new_params = {}
                                    new_params['is_insert'] = True
                                    new_params['user_id'] = int(user_id)
                                    new_params['provider_id'] = int(provider_id)
                                    new_params['cluster_id'] = str(cluster_id)
                                    new_params['cluster_details'] = json.dumps(cluster_details)
                                    new_params['status'] = 'Deleted'
                                    new_params['operation'] = deleted_cluster_details['message']
                                    flag, msg = insert_or_update_cluster_details(new_params)
                                    if flag:
                                        response.update({"status": flag,
                                                         "deleted_cluster_details": deleted_cluster_details['message'],
                                                         "error": ""})
                                    else:
                                        response.update({"status": flag,
                                                         "deleted_cluster_details": deleted_cluster_details['message'],
                                                         "error": "Cluster deleted but error in db"})
                                else:
                                    split_str = str(deleted_cluster_details).split('ServerResponseBody: ')
                                    response.update({"status": flag,
                                                     "deleted_cluster_details": "",
                                                     "error": json.loads((split_str.__getitem__(1)))})
                            else:
                                if str(cluster_details).__contains__('Invalid cluster_id'):
                                    response.update({"status": flag,
                                                     "cluster_details": "",
                                                     "error": cluster_details})
                                    break
                                split_str = str(cluster_details).split('ServerResponseBody: ')
                                response.update({"status": flag,
                                                 "deleted_cluster_details": "",
                                                 "error": json.loads((split_str.__getitem__(1)))})
            else:
                response.update({"status": False,
                                 "deleted_cluster_details": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
        if access_flag:
            response.update({"status": False,
                             "deleted_cluster_details": "",
                             "error": 'Please provide valid user_id and provider_id'})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "deleted_cluster_details": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_cluster_config(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        provider_cluster_config_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                raise Exception(access_key_secret_key_list)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if len(access_key_secret_key_list) > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
                if len(unique_access_key_list) > 0:
                    for access_key in unique_access_key_list:
                        providers_cluster_config_info = {}
                        for access_key_secret_key in access_key_secret_key_list:
                            if access_key_secret_key['client_id'] is access_key:
                                alibaba_cs = Alibaba_CS(
                                    ali_access_key=access_key,
                                    ali_secret_key=access_key_secret_key['client_secret'],
                                    region_id='default'
                                )
                                flag, cluster_details_list = alibaba_cs.get_all_cluster_config()
                                if flag:
                                    providers_cluster_config_info.update(
                                        {"provider_name": access_key_secret_key['name'],
                                         "cluster_list": cluster_details_list})
                                else:
                                    raise Exception(cluster_details_list)
                        provider_cluster_config_list.append(providers_cluster_config_info)
            response.update({"status": True,
                             "provider_cluster_config_list": provider_cluster_config_list,
                             'error': ''})
            return JsonResponse(response, safe=False)
        else:
            response.update({"status": False,
                             "provider_cluster_config_list": provider_cluster_config_list})
            return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_config_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_clusters(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_all_clusters()
                        if flag:
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)
                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_pods(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_pods()
                        if flag:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_secrets(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_secrets()
                        if flag:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_nodes(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_nodes()
                        if flag:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         "error": ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_deployments(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_deployments()
                        if flag:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_namespaces(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_namespaces()
                        if flag:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_persistent_volume_claims(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_persistent_volume_claims()
                        if flag:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_persistent_volumes(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_persistent_volumes()
                        if flag:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_services(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_services()
                        if flag:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_roles(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_roles()
                        if flag:
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_storageclasses(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_storageclasses()
                        if flag:
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_cronjobs(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_cronjobs()
                        if flag:
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_jobs(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_jobs()
                        if flag:
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)

@api_view(["GET"])
def get_all_daemon_sets(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_daemon_sets()
                        if flag:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


@api_view(["GET"])
def get_all_replica_sets(params):
    response = {}
    try:
        json_request = json.loads(params.body)
        response = {}
        error = False
        valid_keys_json = ['user_id']
        providers_cluster_info_list = []
        for key in valid_keys_json:
            if key not in json_request:
                error = True
                response.update({"error": "key " + key + " is not found"})
            else:
                json_request[key] = str(json_request[key].strip())
                if (len(json_request[key])) == 0:
                    error = True
                    response.update({"error": "value " + key + " is not found"})
        if not error:
            user_id = json_request["user_id"]
            try:
                user_id = int(user_id)
                user_id = str(user_id)
            except Exception:
                raise Exception('Please provide valid user_id.')
            flag, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not flag:
                response.update({"status": False,
                                 "provider_cluster_list": "",
                                 "error": access_key_secret_key_list})
                return JsonResponse(response, safe=False)
            access_key_secret_key_list = json.loads(access_key_secret_key_list)
            unique_access_key_list = []
            if list(access_key_secret_key_list).__len__() > 0:
                for access_key_secret_key in access_key_secret_key_list:

                    if access_key_secret_key['client_id'] in unique_access_key_list:
                        continue
                    else:
                        unique_access_key_list.append(access_key_secret_key['client_id'])
            for access_key in unique_access_key_list:
                providers_cluster_info = {}
                for access_key_secret_key in access_key_secret_key_list:
                    if access_key_secret_key['client_id'] is access_key:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=access_key,
                            ali_secret_key=access_key_secret_key['client_secret'],
                            region_id='default'
                        )
                        flag, cluster_details_list = alibaba_cs.get_replica_sets()
                        if flag:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update(
                                {"provider_name": access_key_secret_key['name'], "cluster_list": cluster_details_list})
                        else:
                            raise Exception(cluster_details_list)

                providers_cluster_info_list.append(providers_cluster_info)
        else:
            response.update({"status": False,
                             "provider_cluster_list": providers_cluster_info_list})
            return JsonResponse(response, safe=False)
        response.update({"status": True,
                         "provider_cluster_list": providers_cluster_info_list,
                         'error': ''})
        return JsonResponse(response, safe=False)
    except Exception as e:
        response.update({"status": False,
                         "provider_cluster_list": "",
                         "error": e.message})
        return JsonResponse(response, safe=False)


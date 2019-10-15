import json

from django.http import JsonResponse
from rest_framework.decorators import api_view

from cluster.alibaba.compute_service import Alibaba_ECS
from cluster.alibaba.container_service import Alibaba_CS
from cluster.others.miscellaneous_operation import key_validations_cluster_provisioning, get_access_key_secret_key_list, \
    get_grouped_credential_list


@api_view(['GET'])
def alibaba_region_list(request):
    """
    get the list of the available regions
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'region_list': [],
                    'error': None}
    access_flag = True
    valid_json_keys = ['user_id',
                       'provider_id']
    try:
        json_request = json.loads(request.body)
        # key validations
        error, response = key_validations_cluster_provisioning(json_request, valid_json_keys)
        if error:
            api_response.update({
                'error': response.get('error'),
                'is_successful': False
            })
        else:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            # Fetching access keys and secret keys from db
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not error:
                access_key_secret_key_list = json.loads(access_key_secret_key_list)
                unique_access_key_list = []
                if len(list(access_key_secret_key_list)) > 0:
                    # creating unique list of access key
                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key.get('client_id') in unique_access_key_list:
                            continue
                        else:
                            unique_access_key_list.append(access_key_secret_key.get('client_id'))
                for access_key in unique_access_key_list:
                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key.get('client_id') == access_key and access_key_secret_key.get(
                                'id') == int(provider_id):
                            access_flag = False
                            alibaba_ecs = Alibaba_ECS(
                                ali_access_key=access_key_secret_key.get('client_id'),
                                ali_secret_key=access_key_secret_key.get('client_secret'),
                                region_id='default'
                            )
                            flag, region_list = alibaba_ecs.list_regions()

                            if flag:
                                api_response.update({'is_successful': flag,
                                                     'region_list': region_list,
                                                     'error': None})
                            else:
                                api_response.update({'is_successful': flag,
                                                     'error': 'Error occured while fetching the region list'})
                                break
                if access_flag:
                    api_response.update({'is_successful': False,
                                         'error': 'Invalid provider_id or no data available.'})
            else:
                api_response.update({'is_successful': False,
                                     'error': 'Invalid user_id or no data available.'})

    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['GET'])
def all_cluster_details(request):
    """
    get the details of all clusters
    :param request:
    :return:
    """
    api_response = {}
    access_flag = True
    try:
        pass
    except Exception as e:
        pass
    finally:
        return JsonResponse({'done': 'successfully'}, safe=False)


@api_view(['GET'])
def alibaba_ssh_key_pair_list(request):
    """
    get the list of names of ssh key pairs in a particular region
    :param request:
    :return:
    """
    api_response = {"is_successful": True,
                    "ssh_key_pairs_name_list": [],
                    "error": None}
    access_flag = True
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'region_id']
        # key validations
        error, response = key_validations_cluster_provisioning(json_request, valid_json_keys)
        if error:
            api_response.update({
                'error': response.get('error'),
                'is_successful': False
            })
        else:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            region_id = json_request.get('region_id')

            # Fetching access keys and secret keys from db
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not error:
                access_key_secret_key_list = json.loads(access_key_secret_key_list)
                unique_access_key_list = []
                if len(list(access_key_secret_key_list)) > 0:
                    # creating unique list of access key
                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key.get('client_id') in unique_access_key_list:
                            continue
                        else:
                            unique_access_key_list.append(access_key_secret_key.get('client_id'))
                for access_key in unique_access_key_list:
                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key.get('client_id') == access_key and access_key_secret_key.get(
                                'id') == int(provider_id):
                            access_flag = False
                            alibaba_ecs = Alibaba_ECS(
                                ali_access_key=access_key_secret_key.get('client_id'),
                                ali_secret_key=access_key_secret_key.get('client_secret'),
                                region_id=region_id
                            )
                            flag, result = alibaba_ecs.key_pairs_list()

                            if flag:
                                api_response.update({'is_successful': flag,
                                                     'ssh_key_pairs_name_list': result,
                                                     'error': None})
                            else:
                                api_response.update({'is_successful': flag,
                                                     'error': result})
                                break
                if access_flag:
                    api_response.update({'is_successful': False,
                                         'error': 'Invalid provider_id or no data available.'})
            else:
                api_response.update({'is_successful': False,
                                     'error': 'Invalid user_id or no data available.'})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['GET'])
def alibaba_network_details(request):
    """
    get the network details including vpc, vswitchId
    :param request:
    :return:
    """
    api_response = {"is_successful": True,
                    "vpc_list": [],
                    "error": None}
    access_flag = True
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'region_id']
        # key validations
        error, response = key_validations_cluster_provisioning(json_request, valid_json_keys)
        if error:
            api_response.update({
                'error': response.get('error'),
                'is_successful': False
            })
        else:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            region_id = json_request.get('region_id')

            # Fetching access keys and secret keys from db
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not error:
                access_key_secret_key_list = json.loads(access_key_secret_key_list)
                unique_access_key_list = []
                if len(list(access_key_secret_key_list)) > 0:
                    # creating unique list of access key
                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key.get('client_id') in unique_access_key_list:
                            continue
                        else:
                            unique_access_key_list.append(access_key_secret_key.get('client_id'))
                for access_key in unique_access_key_list:
                    for access_key_secret_key in access_key_secret_key_list:
                        if access_key_secret_key.get('client_id') == access_key and access_key_secret_key.get(
                                'id') == int(provider_id):
                            access_flag = False
                            alibaba_ecs = Alibaba_ECS(
                                ali_access_key=access_key_secret_key.get('client_id'),
                                ali_secret_key=access_key_secret_key.get('client_secret'),
                                region_id=region_id
                            )
                            flag, result = alibaba_ecs.network_details()

                            if flag:
                                api_response.update({'is_successful': flag,
                                                     'vpc_list': result,
                                                     'error': None})
                            else:
                                api_response.update({'is_successful': flag,
                                                     'error': result})
                                break
                if access_flag:
                    api_response.update({'is_successful': False,
                                         'error': 'Invalid provider_id or no data available.'})
            else:
                api_response.update({'is_successful': False,
                                     'error': 'Invalid user_id or no data available.'})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['GET'])
def all_pod_details(request):
    """
    get the details of all pods available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_provider_cluster_details': [],
                    'error': None}
    all_provider_cluster_details = []
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id']
        # key validations
        error, response = key_validations_cluster_provisioning(json_request, valid_json_keys)
        if error:
            api_response.update({
                'error': response.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                # groups the common credentials according to the access key
                error, response = get_grouped_credential_list(response)
                if not error:

                    for credential in response:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error, result = alibaba_cs.get_pod_details()

                        if not error:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_provider_cluster_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response})
            else:
                api_response.update({'is_successful': False,
                                     'error': response})


    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)

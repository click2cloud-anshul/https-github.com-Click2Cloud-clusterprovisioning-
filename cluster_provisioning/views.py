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
                    'all_pod_details': [],
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
                                    'all_pod_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_namespace_details(request):
    """
    get the details of all namespaces available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_namespace_details': [],
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
                        error, result = alibaba_cs.get_namespace_details()

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
                                    'all_namespace_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_role_details(request):
    """
    get the details of all roles available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_role_details': [],
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
                        error, result = alibaba_cs.get_role_details()

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
                                    'all_role_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_persistent_volume_details(request):
    """
    get the details of all persistent volumes available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_persistent_volume_details': [],
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
                        error, result = alibaba_cs.get_persistent_volume_details()

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
                                    'all_persistent_volume_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_persistent_volume_claim_details(request):
    """
    get the details of all persistent volume claims available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_persistent_volume_claims_details': [],
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
                        error, result = alibaba_cs.get_persistent_volume_claims_details()

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
                                    'all_persistent_volume_claims_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_deployment_details(request):
    """
    get the details of all persistent volume claims available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_deployment_details': [],
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
                        error, result = alibaba_cs.get_deployment_details()

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
                                    'all_deployment_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_secret_details(request):
    """
    get the details of all secret available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_secret_details': [],
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
                        error, result = alibaba_cs.get_secret_details()

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
                                    'all_secret_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_node_details(request):
    """
    get the details of all node available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_node_details': [],
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
                        error, result = alibaba_cs.get_node_details()

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
                                    'all_node_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_service_details(request):
    """
    get the details of all service available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_service_details': [],
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
                        error, result = alibaba_cs.get_service_details()

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
                                    'all_service_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_cron_job_details(request):
    """
    get the details of all cron jobs available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_cron_job_details': [],
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
                        error, result = alibaba_cs.get_cron_job_details()

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
                                    'all_cron_job_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_job_details(request):
    """
    get the details of all jobs available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_job_details': [],
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
                        error, result = alibaba_cs.get_job_details()

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
                                    'all_job_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_storage_class_details(request):
    """
    get the details of all storage class available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_storage_class_details': [],
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
                        error, result = alibaba_cs.get_all_storage_class_details()

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
                                    'all_storage_class_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_replication_controller_details(request):
    """
    get the details of all replication controllers available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_replication_controller_details': [],
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
                        error, result = alibaba_cs.get_all_replication_controller_details()

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
                                    'all_replication_controller_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_stateful_sets_details(request):
    """
    get the details of all stateful sets available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_stateful_sets_details': [],
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
                        error, result = alibaba_cs.get_all_stateful_set_details()

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
                                    'all_stateful_sets_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_replica_sets_details(request):
    """
    get the details of all replica sets available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_replica_set_details': [],
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
                        error, result = alibaba_cs.get_all_replica_set_details()

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
                                    'all_replica_set_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_daemon_set_details(request):
    """
    get the details of all daemon sets available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_daemon_set_details': [],
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
                        error, result = alibaba_cs.get_all_daemon_set_details()

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
                                    'all_replica_sets_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_config_map_details(request):
    """
    get the details of all config map available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_config_map_details': [],
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
                        error, result = alibaba_cs.get_all_config_map_details()

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
                                    'all_config_map_details': all_provider_cluster_details,
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


@api_view(['GET'])
def all_ingress_details(request):
    """
    get the details of all ingress available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_ingress_details': [],
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
                        error, result = alibaba_cs.get_all_ingress_details()

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
                                    'all_ingress_details': all_provider_cluster_details,
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

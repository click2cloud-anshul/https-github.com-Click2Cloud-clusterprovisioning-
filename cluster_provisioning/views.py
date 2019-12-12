import base64
import json

from django.http import JsonResponse
from rest_framework.decorators import api_view

from cluster.alibaba.compute_service import Alibaba_ECS
from cluster.alibaba.container_service import Alibaba_CS
from cluster.others.miscellaneous_operation import key_validations_cluster_provisioning, get_access_key_secret_key_list, \
    get_grouped_credential_list, check_for_provider_id, insert_or_update_cluster_details


@api_view(['POST'])
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


@api_view(['POST'])
def alibaba_instance_list(request):
    """
    get the list of the available instances
    :param request:
    :return:
    """
    instance_list = []
    api_response = {'is_successful': True,
                    'details': instance_list,
                    'error': None}
    access_flag = True
    zone_list_length = 0
    valid_json_keys = ['user_id',
                       'provider_id',
                       'region_id',
                       'zone_id_list']
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
            zone_id_temp = json_request.get('zone_id_list')
            region_id = json_request.get('region_id')
            zone_list = [str(item) for item in zone_id_temp]
            zone_list_length = len(zone_list)
            # Fetching access keys and secret keys from db
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id)
            if not error:
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
                            for zone_id in zone_list:
                                instances = {'zone_id': zone_id,
                                             'instances': None,
                                             'error': None}
                                error, response = alibaba_ecs.list_instances(zone_id)
                                if not error:
                                    instances.update({'instances': response})
                                #
                                else:
                                    instances.update({'error': response,
                                                      })
                                instance_list.append(instances.copy())

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
        # Update error and is_successful key  if all the zone ids are invalid
        error_count = 0
        error_msg = None
        for item in api_response.get('details'):
            error_msg = item.get('error')
            if error_msg is not None:
                error_count += 1
        if error_count == zone_list_length:
            api_response.update({'is_successful': False,
                                 'error': error_msg})
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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


@api_view(['POST'])
def alibaba_network_details(request):
    """
    get the network details including vpc, vswitchId
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'vpc_list': [],
                    'error': None}
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


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_pod_details, result_get_pod_details = alibaba_cs.get_pod_details()

                        if not error_get_pod_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_pod_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_pod_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_pod_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_namespace_details, result_get_namespace_details = alibaba_cs.get_namespace_details()

                        if not error_get_namespace_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_namespace_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_namespace_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_namespace_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_role_details, result_get_role_details = alibaba_cs.get_role_details()

                        if not error_get_role_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_role_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_role_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_role_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)

@api_view(['POST'])
def all_cluster_role_details(request):
    """
    get the details of all roles available in the alibaba
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_cluster_role_details': [],
                    'error': None}
    all_provider_cluster_details = []
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_role_details, result_get_role_details = alibaba_cs.get_cluster_role_details()

                        if not error_get_role_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_role_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_role_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_cluster_role_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)



@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_persistent_volume_details, result_get_persistent_volume_details = alibaba_cs.get_persistent_volume_details()

                        if not error_get_persistent_volume_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_persistent_volume_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_persistent_volume_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_persistent_volume_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_persistent_volume_claims_details, result_get_persistent_volume_claims_details = alibaba_cs.get_persistent_volume_claims_details()

                        if not error_get_persistent_volume_claims_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_persistent_volume_claims_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_persistent_volume_claims_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_persistent_volume_claims_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_deployment_details, result_get_deployment_details = alibaba_cs.get_deployment_details()

                        if not error_get_deployment_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_deployment_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_deployment_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_deployment_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_secret_details, result_get_secret_details = alibaba_cs.get_secret_details()

                        if not error_get_secret_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_secret_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_secret_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_secret_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_node_details, result_get_node_details = alibaba_cs.get_node_details()

                        if not error_get_node_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_node_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_node_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_node_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_service_details, result_get_service_details = alibaba_cs.get_service_details()

                        if not error_get_service_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_service_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_service_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_service_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_cron_job_details, result_get_cron_job_details = alibaba_cs.get_cron_job_details()

                        if not error_get_cron_job_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_cron_job_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_cron_job_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_cron_job_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_job_details, result_get_job_details = alibaba_cs.get_job_details()

                        if not error_get_job_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_job_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_job_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_job_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_storage_class_details, result_get_storage_class_details = alibaba_cs.get_storage_class_details()

                        if not error_get_storage_class_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_storage_class_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_storage_class_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_storage_class_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_replication_controller_details, result_get_replication_controller_details = alibaba_cs.get_replication_controller_details()

                        if not error_get_replication_controller_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_replication_controller_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_replication_controller_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_replication_controller_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_stateful_set_details, result_get_stateful_set_details = alibaba_cs.get_stateful_set_details()

                        if not error_get_stateful_set_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_stateful_set_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_stateful_set_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_stateful_sets_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_replica_set_details, result_get_replica_set_details = alibaba_cs.get_replica_set_details()

                        if not error_get_replica_set_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_replica_set_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_replica_set_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_replica_set_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_daemon_set_details, result_get_daemon_set_details = alibaba_cs.get_daemon_set_details()

                        if not error_get_daemon_set_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_daemon_set_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_daemon_set_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_daemon_set_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_config_map_details, result_get_config_map_details = alibaba_cs.get_config_map_details()

                        if not error_get_config_map_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_config_map_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_config_map_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_config_map_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
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
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })

        else:
            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:

                    for credential in response_get_grouped_credential_list:
                        providers_cluster_info = {}
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_ingress_details, result_get_ingress_details = alibaba_cs.get_ingress_details()

                        if not error_get_ingress_details:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': result_get_ingress_details})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'cluster_list': [],
                                'error': result_get_ingress_details})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response = {'is_successful': True,
                                    'all_ingress_details': all_provider_cluster_details,
                                    'error': None}
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
def create_application(request):
    """
    create application on kubernetes cluster on the alibaba
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'created_object_details': None,
        'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'application_body', 'namespace']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            cluster_id = json_request.get('cluster_id')
            application_body = json_request.get('application_body')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret'),
                        region_id='default'
                    )
                    error_create_from_yaml, response_create_from_yaml = alibaba_cs.create_k8s_object(
                        cluster_id=cluster_id, data=application_body,
                        namespace=namespace)
                    if not error_create_from_yaml:
                        # application successfully created.
                        api_response = {
                            'created_object_details': response_create_from_yaml
                        }
                    else:
                        # application creation failed.
                        raise Exception(response_create_from_yaml)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response_check_for_provider_id)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response_get_access_key_secret_key_list)
        else:
            raise Exception(response_key_validations_cluster_provisioning.get('error'))
    except Exception as e:
        api_response.update({
            'is_successful': False,
            'error': e.message
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
def all_cluster_details(request):
    """
    get the details of clusters in all providers
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_cluster_details': [],
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
                        error, result = alibaba_cs.describe_all_clusters()

                        if not error:
                            # access_key_secret_key['name']: cluster_details_list
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'clusters': result})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'clusters': [],
                                'error': result})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response.update({'all_cluster_details': all_provider_cluster_details})
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


@api_view(['POST'])
def all_cluster_config_details(request):
    """
    get the details of clusters config in all providers
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_cluster_config_details': [],
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
                        error, result = alibaba_cs.describe_all_cluster_config()

                        if not error:
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'clusters': result})
                        else:
                            # skip if any error occurred for a particular key
                            providers_cluster_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'clusters': [],
                                'error': result})
                        all_provider_cluster_details.append(providers_cluster_info)
                    api_response.update({'all_cluster_config_details': all_provider_cluster_details})
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


@api_view(['POST'])
def create_kubernetes_cluster(request):
    """
    Create the kubernetes cluster on the alibaba cloud
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'cluster_detail': {},
        'error': None
    }
    cluster_info_db = {}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'request_body']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            request_body = json_request.get('request_body')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret'),
                        region_id='default'
                    )
                    error_create_cluster, response_create_cluster = alibaba_cs.create_cluster(
                        request_body=request_body)
                    if not error_create_cluster:
                        # Database entry for Create
                        api_response.update({
                            'cluster_detail': response_create_cluster
                        })
                        cluster_info_db.update({
                            'is_insert': True,
                            'user_id': int(user_id),
                            'provider_id': int(provider_id),
                            'cluster_id': str(response_create_cluster.get('cluster_id')),
                            'cluster_details': json.dumps(request_body),
                            'status': 'Initiated',
                            'operation': 'created from cloudbrain', })
                        error_insert_or_update_cluster_details, response_insert_or_update_cluster_details = insert_or_update_cluster_details(
                            cluster_info_db)
                        if error_insert_or_update_cluster_details:
                            api_response.update({'is_successful': False,
                                                 'error': 'Cluster created but error while inserting data into database'})
                    else:
                        # application creation failed.
                        raise Exception(response_create_cluster)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response_check_for_provider_id)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response_get_access_key_secret_key_list)
        else:
            raise Exception(response_key_validations_cluster_provisioning.get('error'))
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })

    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def delete_kubernetes_cluster(request):
    """
    Delete the kubernetes cluster on the alibaba cloud
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'error': None}
    cluster_info_db = {}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id']
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
            cluster_id = json_request.get('cluster_id')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_cluster(cluster_id)
                            if not error:
                                if not response:
                                    raise Exception('Unable to delete the cluster')
                                else:
                                    # Database entry for delete
                                    cluster_info_db.update({
                                        'is_insert': True,
                                        'user_id': int(user_id),
                                        'provider_id': int(provider_id),
                                        'cluster_id': cluster_id,
                                        'cluster_details': {},
                                        'status': 'Deleted',
                                        'operation': 'Deleted from cloudbrain', })
                                    error, response = insert_or_update_cluster_details(cluster_info_db)
                                    if error:
                                        response.update({'is_successful': False,
                                                         'error': 'Cluster deleted but error while updating in database'})

                            else:
                                # Unable to delete the cluster
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_pod(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_pod(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_persistent_volume_claim(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_persistent_volume_claim(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_cron_job(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_cron_job(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_daemon_set(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_daemon_set(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_deployment(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_deployment(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_job(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_job(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_replica_set(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_replica_set(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_replication_controller(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_replication_controller(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_stateful_set(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_stateful_set(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_service(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_service(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_config_map(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_config_map(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_secret(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_secret(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_ingress(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name', 'namespace']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_ingress(name, namespace, cluster_id)
                            if error:
                                # Unable to delete the pod, otherwise pod gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_persistent_volume(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_persistent_volume(name, cluster_id)
                            if error:
                                # Unable to delete the persistent volumes, otherwise persistent volumes gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def alibaba_delete_storage_class(request):
    """
        Delete the object of the existing kubernetes cluster on Alibaba cloud
        :param request:
        :return:
        """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'name']
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
            cluster_id = json_request.get('cluster_id')
            name = json_request.get('name')
            # Fetching access keys and secret keys from db
            error, response = get_access_key_secret_key_list(user_id)
            if not error:
                error, response = check_for_provider_id(provider_id, response)
                if not error:
                    # if provider_id present in credentials from database
                    alibaba_cs = Alibaba_CS(
                        ali_access_key=response.get('client_id'),
                        ali_secret_key=response.get('client_secret'),
                        region_id='default'
                    )
                    error, response = alibaba_cs.is_cluster_exist(cluster_id)
                    if not error:
                        if response:
                            # If cluster exists
                            error, response = alibaba_cs.delete_storage_class(name, cluster_id)
                            if error:
                                # Unable to delete the persistent volumes, otherwise persistent volumes gets delete
                                raise Exception(response)
                        else:
                            raise Exception(
                                'Cluster does not exist in the current provider or it is in creating or deleting state.')
                    else:
                        # Cluster does not exist
                        raise Exception(response)
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response)
            else:
                # If user_id is incorrect or no user is found is database
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)

import base64
import json

from django.http import JsonResponse
from rest_framework.decorators import api_view

from cluster.alibaba.compute_service import Alibaba_ECS
from cluster.alibaba.container_service import Alibaba_CS
from cluster.azure.compute_service import Azure_Compute_Service
from cluster.azure.container_service import Azure_CS
from cluster.on_premises_cluster.container_service import On_Premises_Cluster
from cluster.others import miscellaneous_operation
from cluster.others.miscellaneous_operation import key_validations_cluster_provisioning, get_access_key_secret_key_list, \
    get_grouped_credential_list, check_for_provider_id, insert_or_update_cluster_details, \
    get_db_info_using_user_id_and_provider_id


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
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id,
                                                                               miscellaneous_operation.ALIBABA_CLOUD)
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
                            flag, region_list = alibaba_ecs.list_container_service_regions()

                            if flag:
                                api_response.update({'is_successful': flag,
                                                     'region_list': region_list,
                                                     'error': None})
                            else:
                                api_response.update({'is_successful': flag,
                                                     'error': 'Error occurred while fetching the region list'})
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
def alibaba_list_providers(request):
    """
    List the providers on the alibaba
    :param request:
    :return:
    """
    provider_name_list = []
    api_response = {
        'is_successful': True,
        'provider_list': [],
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)

        if not error_key_validations_cluster_provisioning:

            user_id = json_request.get('user_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)

                if not error_get_grouped_credential_list:
                    for grouped_credential_list in response_get_grouped_credential_list:
                        for credentials in grouped_credential_list.get('provider_name_list'):
                            provider_name_list.append(credentials)
                    api_response.update({'provider_list': provider_name_list})
                else:
                    # if provider_id is not present in credentials
                    raise Exception(response_get_grouped_credential_list)
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
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id,
                                                                               miscellaneous_operation.ALIBABA_CLOUD)
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
                                error_list_ecs_instances, response_list_ecs_instances = alibaba_ecs.list_ecs_instances(
                                    zone_id)
                                if not error_list_ecs_instances:
                                    instances.update({'instances': response_list_ecs_instances})
                                else:
                                    instances.update({'error': response_list_ecs_instances,
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
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id,
                                                                               miscellaneous_operation.ALIBABA_CLOUD)
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
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id,
                                                                               miscellaneous_operation.ALIBABA_CLOUD)
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
def alibaba_all_pod_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_pod_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_namespace_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_namespace_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_role_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_role_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_cluster_role_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_cluster_role_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_persistent_volume_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_persistent_volume_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_persistent_volume_claim_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_persistent_volume_claims_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_deployment_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_deployment_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_secret_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_secret_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_node_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_node_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_service_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_service_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_cron_job_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_cron_job_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_job_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_job_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_storage_class_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_storage_class_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_replication_controller_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_replication_controller_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_stateful_sets_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_stateful_sets_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_replica_sets_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_replica_set_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_daemon_set_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_daemon_set_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_config_map_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_config_map_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_all_ingress_details(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    api_response.update({'is_successful': True,
                                         'all_ingress_details': all_provider_cluster_details,
                                         'error': None})
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
def alibaba_create_application(request):
    """
    create application on kubernetes cluster on the alibaba
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                    if error_create_from_yaml:
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
def alibaba_all_cluster_details(request):
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
def alibaba_all_cluster_config_details(request):
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
def alibaba_create_kubernetes_cluster(request):
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
                        print(cluster_info_db)
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
def alibaba_delete_kubernetes_cluster(request):
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.ALIBABA_CLOUD)
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


@api_view(['POST'])
def azure_all_cluster_details(request):
    """
    This method will list all the kubernetes services running for that particular user_id
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
            error, response = get_access_key_secret_key_list(user_id, miscellaneous_operation.AZURE_CLOUD)
            if not error:
                # groups the common credentials according to the access key
                error, response = get_grouped_credential_list(response)
                if not error:

                    for credential in response:
                        providers_cluster_info = {}
                        azure_cs = Azure_CS(
                            azure_subscription_id=credential.get('subscription_id'),
                            azure_client_id=credential.get('access_key'),
                            azure_client_secret=credential.get('secret_key'),
                            azure_tenant_id=credential.get('tenant_id')
                        )

                        error, result = azure_cs.describe_all_clusters()

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
def azure_region_list(request):
    """
    get the list of the available regions
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'region_list': [],
                    'error': None}
    providerId_access_flag = True
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
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id,
                                                                               miscellaneous_operation.AZURE_CLOUD)
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
                            providerId_access_flag = False
                            azure_Compute_Service = Azure_Compute_Service(
                                azure_subscription_id=access_key_secret_key.get('subscription_id'),
                                azure_client_id=access_key_secret_key.get('client_id'),
                                azure_client_secret=access_key_secret_key.get('client_secret'),
                                azure_tenant_id=access_key_secret_key.get('tenant_id'))

                            flag, region_list = azure_Compute_Service.list_regions()

                            if flag:
                                api_response.update({'is_successful': flag,
                                                     'error': 'Error occurred while fetching the resource group list'})
                                break
                            else:
                                api_response.update({'is_successful': flag,
                                                     'region_list': region_list,
                                                     'error': None})
                if providerId_access_flag:
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
def azure_resource_group_list(request):
    """
    get the list of the available resource group
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'resource_group_list': [],
                    'error': None}
    providerId_access_flag = True
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
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id,
                                                                               miscellaneous_operation.AZURE_CLOUD)
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
                            providerId_access_flag = False
                            azure_Compute_Service = Azure_Compute_Service(
                                azure_subscription_id=access_key_secret_key.get('subscription_id'),
                                azure_client_id=access_key_secret_key.get('client_id'),
                                azure_client_secret=access_key_secret_key.get('client_secret'),
                                azure_tenant_id=access_key_secret_key.get('tenant_id'))
                            flag, resource_group_list = azure_Compute_Service.resource_group_list()
                            if flag:
                                api_response.update({'is_successful': flag,
                                                     'error': 'Error occurred while fetching the region list'})
                                break
                            else:
                                api_response.update({'is_successful': flag,
                                                     'resource_group_list': resource_group_list,
                                                     'error': None})
                if providerId_access_flag:
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
def azure_instance_type_list(request):
    """
    get the list of the available instance type
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'instance_type_list': [],
                    'error': None}
    providerId_access_flag = True
    valid_json_keys = ['user_id',
                       'provider_id',
                       'region_id']
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
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id,
                                                                               miscellaneous_operation.AZURE_CLOUD)
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
                            providerId_access_flag = False
                            azure_Compute_Service = Azure_Compute_Service(
                                azure_subscription_id=access_key_secret_key.get('subscription_id'),
                                azure_client_id=access_key_secret_key.get('client_id'),
                                azure_client_secret=access_key_secret_key.get('client_secret'),
                                azure_tenant_id=access_key_secret_key.get('tenant_id'))
                            flag, instance_type_list = azure_Compute_Service.instance_type(
                                location=json_request.get('region_id'))
                            if flag:
                                api_response.update({'is_successful': flag,
                                                     'error': 'Error occurred while fetching the instance type list'})
                                break
                            else:
                                api_response.update({'is_successful': flag,
                                                     'instance_type_list': instance_type_list,
                                                     'error': None})
                if providerId_access_flag:
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
def azure_virtual_network_details(request):
    """
    get the list of the available virtual network
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'virtual_network_details': [],
                    'error': None}
    providerId_access_flag = True
    valid_json_keys = ['user_id',
                       'provider_id',
                       'region_id']
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
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id,
                                                                               miscellaneous_operation.AZURE_CLOUD)
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
                            providerId_access_flag = False
                            azure_Compute_Service = Azure_Compute_Service(
                                azure_subscription_id=access_key_secret_key.get('subscription_id'),
                                azure_client_id=access_key_secret_key.get('client_id'),
                                azure_client_secret=access_key_secret_key.get('client_secret'),
                                azure_tenant_id=access_key_secret_key.get('tenant_id'))

                            flag, virtual_network_details = azure_Compute_Service.virtual_network(
                                location=json_request.get('region_id'))
                            if flag:
                                api_response.update({'is_successful': flag,
                                                     'error': 'Error occurred while fetching the virtual network details'})
                                break
                            else:
                                api_response.update({'is_successful': flag,
                                                     'virtual_network_details': virtual_network_details,
                                                     'error': None})
                if providerId_access_flag:
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
def alibaba_all_resources(request):
    """
    get the details of all resources count available in the alibaba
    :param request:
    :return:
    """
    all_provider_cluster_details = {}
    api_response = {'is_successful': True,
                    'all_resource_details': all_provider_cluster_details,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id']
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
            cluster_id = json_request.get('cluster_id')
            provider_id = json_request.get('provider_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                error, response = check_for_provider_id(provider_id, response_get_access_key_secret_key_list)
                if not error:
                    if not error_get_grouped_credential_list:
                        flag_for_provider = False
                        access_credentials = {}
                        for credential in response_get_grouped_credential_list:
                            for provider in credential.get('provider_name_list'):
                                if provider_id == provider.get('id'):
                                    flag_for_provider = True
                                    access_credentials = credential
                        if flag_for_provider:
                            alibaba_cs = Alibaba_CS(
                                ali_access_key=access_credentials.get('access_key'),
                                ali_secret_key=access_credentials.get('secret_key'),
                                region_id='default'
                            )
                            error_get_all_resources_list, result_get_all_resources_list = alibaba_cs.get_all_resources_list(
                                cluster_id)
                            if not error_get_all_resources_list:
                                # access_key_secret_key['name']: cluster_details_list
                                all_provider_cluster_details = result_get_all_resources_list
                            else:
                                # skip if any error occurred for a particular key
                                raise Exception(result_get_all_resources_list)
                        else:
                            raise Exception('Invalid provider_id provided')
                        api_response.update({
                            'all_resource_details': all_provider_cluster_details,
                        })
                    else:
                        raise Exception(response_get_grouped_credential_list)
                else:
                    raise Exception(response)
            else:
                raise Exception(response_get_access_key_secret_key_list)
    except Exception as e:
        resources = {
            'namespaces': 0,
            'pods': 0,
            'deployments': 0,
            'services': 0,
            'secrets': 0,
            'nodes': 0,
            'jobs': 0,
            'cron_jobs': 0,
            'config_maps': 0,
            'persistent_volume_claims': 0,
            'daemon_sets': 0,
            'ingress': 0,
            'persistent_volumes': 0,
            'replica_sets': 0,
            'replication_controller': 0,
            'roles': 0,
            'stateful_sets': 0,
            'cluster_roles': 0,
            'storage_class': 0
        }
        api_response.update({
            'error': e.message,
            'is_successful': False,
            'all_resource_details': resources
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
def on_premises_add_cluster(request):
    """
    add on premises kubernetes clusters in cloud brain
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'cluster_name', 'cluster_config']
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
            cluster_name = json_request.get('cluster_name')
            cluster_config = base64.b64decode(json_request.get('cluster_config'))
            on_prem_cluster = On_Premises_Cluster(user_id=user_id, cluster_name=cluster_name,
                                                  cluster_config=cluster_config)
            error_add_on_premises_cluster, response_add_on_premises_cluster = on_prem_cluster.add_on_premises_cluster()
            if not error_add_on_premises_cluster:
                # api_response.update({'cluster_detail':''})
                pass
            else:
                raise Exception(response_add_on_premises_cluster)
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
def on_premises_all_pod_details(request):
    """
    This method will list all pods for all on premises clusters
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_pod_details': [],
                    'error': None}
    cluster_list = []
    all_on_premises = []
    all_on_premises_cluster_details = {
        'provider_names': [
            {
                'name': 'On-premises',
                'id': 0
            }
        ],
        'cluster_list': cluster_list
    }
    provider_id = 0
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            raise Exception(response_key_validations_cluster_provisioning.get('error'))
        else:
            user_id = json_request.get('user_id')
            # Fetching cluster_id from db
            error_get_db_info, response_get_db_info = get_db_info_using_user_id_and_provider_id(user_id=user_id,
                                                                                                provider_id=provider_id)
            if not error_get_db_info:
                for response_from_db in response_get_db_info:
                    cluster_details = json.loads(base64.b64decode(response_from_db[4]))
                    on_premises_cluster = On_Premises_Cluster(user_id, cluster_details.get('cluster_name'),
                                                              json.loads(base64.b64decode(
                                                                  cluster_details.get('cluster_config'))))
                    result_get_pod = on_premises_cluster.get_pods(cluster_details)
                    cluster_list.append(result_get_pod)
                all_on_premises.append(all_on_premises_cluster_details)
            else:
                raise Exception(response_get_db_info)
            api_response.update({'is_successful': True,
                                 'all_pod_details': all_on_premises,
                                 'error': None})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
def on_premises_all_service_details(request):
    """
    This method will list all pods for all on premises clusters
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_service_details': [],
                    'error': None}
    cluster_list = []
    all_on_premises = []
    all_on_premises_cluster_details = {
        'provider_names': [
            {
                'name': 'On-premises',
                'id': 0
            }
        ],
        'cluster_list': cluster_list
    }
    provider_id = 0
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            raise Exception(response_key_validations_cluster_provisioning.get('error'))
        else:
            user_id = json_request.get('user_id')
            # Fetching cluster_id from db
            error_get_db_info, response_get_db_info = get_db_info_using_user_id_and_provider_id(user_id=user_id,
                                                                                                provider_id=provider_id)
            if not error_get_db_info:
                for response_from_db in response_get_db_info:
                    cluster_details = json.loads(base64.b64decode(response_from_db[4]))
                    on_premises_cluster = On_Premises_Cluster(user_id, cluster_details.get('cluster_name'),
                                                              json.loads(base64.b64decode(
                                                                  cluster_details.get('cluster_config'))))
                    result_get_services = on_premises_cluster.get_services(cluster_details)
                    cluster_list.append(result_get_services)
                all_on_premises.append(all_on_premises_cluster_details)
            else:
                raise Exception(response_get_db_info)
            api_response.update({'is_successful': True,
                                 'all_service_details': all_on_premises,
                                 'error': None})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
        print(e.message)
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
def on_premises_create_application(request):
    """
    create application on kubernetes cluster on the on_premises
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'application_body', 'namespace']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            provider_id = json_request.get('provider_id')
            cluster_id = json_request.get('cluster_id')
            application_body = json_request.get('application_body')
            namespace = json_request.get('namespace')
            user_id = json_request.get('user_id')
            # Fetching cluster_id from db
            error_get_db_info, response_get_db_info = get_db_info_using_user_id_and_provider_id(user_id=user_id,
                                                                                                provider_id=provider_id)
            if not error_get_db_info:
                is_cluster_accessed = False
                for response_from_db in response_get_db_info:
                    if cluster_id in response_from_db[3]:
                        is_cluster_accessed = True
                        cluster_details = json.loads(base64.b64decode(response_from_db[4]))
                        on_premises_cluster = On_Premises_Cluster(user_id, cluster_details.get('cluster_name'),
                                                                  json.loads(base64.b64decode(
                                                                      cluster_details.get('cluster_config'))))
                        error_create_k8s_object, response_create_k8s_object = on_premises_cluster.create_k8s_object(
                            cluster_id=cluster_id, data=application_body,
                            namespace=namespace)
                        if error_create_k8s_object:
                            raise Exception(response_create_k8s_object)
                if not is_cluster_accessed:
                    raise Exception('No cluster with cluster id %s found' % cluster_id)
            else:
                raise Exception(response_get_db_info)
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
def on_premises_get_all_resources(request):
    """
    This method will list all resources count for on premises clusters
    :param request:
    :return:
    """
    api_response = {'is_successful': True,
                    'all_resource_details': [],
                    'error': None}
    all_on_premises_cluster_details = {}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'cluster_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if error_key_validations_cluster_provisioning:
            api_response.update({
                'error': response_key_validations_cluster_provisioning.get('error'),
                'is_successful': False
            })
        else:
            provider_id = json_request.get('provider_id')
            cluster_id = json_request.get('cluster_id')
            user_id = json_request.get('user_id')
            # Fetching cluster_id from db
            error_get_db_info, response_get_db_info = get_db_info_using_user_id_and_provider_id(user_id=user_id,
                                                                                                provider_id=provider_id)
            if not error_get_db_info:
                cluster_access_flag = False
                for response_from_db in response_get_db_info:
                    if cluster_id == response_from_db[3]:
                        cluster_access_flag = True
                        cluster_details = json.loads(base64.b64decode(response_from_db[4]))
                        on_premises_cluster = On_Premises_Cluster(user_id, cluster_details.get('cluster_name'),
                                                                  json.loads(base64.b64decode(
                                                                      cluster_details.get('cluster_config'))))
                        error_get_all_resources_list, response_get_all_resources_list = on_premises_cluster.get_all_resources_list(
                            cluster_id)
                        if not error_get_all_resources_list:
                            all_on_premises_cluster_details = response_get_all_resources_list
                        else:
                            raise Exception(response_get_all_resources_list)
                if not cluster_access_flag:
                    raise Exception('No cluster_id %s found' % cluster_id)
            else:
                raise Exception(response_get_db_info)
            api_response.update({'is_successful': True,
                                 'all_resource_details': all_on_premises_cluster_details,
                                 'error': None})
    except Exception as e:
        resources = {
            'namespaces': 0,
            'pods': 0,
            'deployments': 0,
            'services': 0,
            'secrets': 0,
            'nodes': 0,
            'jobs': 0,
            'cron_jobs': 0,
            'config_maps': 0,
            'persistent_volume_claims': 0,
            'daemon_sets': 0,
            'ingress': 0,
            'persistent_volumes': 0,
            'replica_sets': 0,
            'replication_controller': 0,
            'roles': 0,
            'stateful_sets': 0,
            'cluster_roles': 0,
            'storage_class': 0
        }
        api_response.update({
            'error': e.message,
            'is_successful': False,
            'all_resource_details': resources
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['POST'])
def alibaba_get_widget_information(request):
    """
    This method will list all resources count for alibaba clusters with all providers
    :param request:
    :return:
    """
    all_provider_cluster_details = []
    api_response = {'is_successful': True,
                    'response': None,
                    'error': None}
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
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:
                    for credential in response_get_grouped_credential_list:
                        alibaba_cs = Alibaba_CS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key'),
                            region_id='default'
                        )
                        error_get_widget_information, result_get_widget_information = alibaba_cs.get_widget_information()
                        for credential_item in credential.get('provider_name_list'):
                            providers_cluster_info = {'provider_name': credential_item.get('name'),
                                                      'id': credential_item.get('id'),
                                                      'subscription_id': credential.get('subscription_id'),
                                                      'error': None,
                                                      'cluster_list': None
                                                      }
                            if not error_get_widget_information:
                                if len(result_get_widget_information) > 0:
                                    providers_cluster_info.update({
                                        'cluster_list': result_get_widget_information})
                            else:
                                # skip if any error occurred for a particular key
                                providers_cluster_info.update({
                                    'error': result_get_widget_information})
                            all_provider_cluster_details.append(providers_cluster_info)
                    response = {
                        'widget_details': all_provider_cluster_details
                    }
                    api_response.update({'is_successful': True,
                                         'response': response,
                                         'error': None})
                else:
                    api_response.update({'is_successful': False,
                                         'error': response_get_grouped_credential_list})
            else:
                api_response.update({'is_successful': False,
                                     'error': response_get_access_key_secret_key_list})
    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False,
        })
    finally:
        return JsonResponse(api_response, safe=False)



# -------------------------New---Development-----------------





@api_view(['POST'])
def alibaba_describe_zones(request):
    """
    get the list of the available instances
    :param request:
    :return:
    """
    system_disk = {}
    api_response = {'is_successful': True,
                    'details': system_disk,
                    'error': None}
    access_flag = True
    valid_json_keys = ['user_id',
                       'provider_id',
                       'region_id',
                       'zone_id']
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
            region_id = json_request.get('region_id')
            zone_id= json_request.get('zone_id')
            # Fetching access keys and secret keys from db
            error, access_key_secret_key_list = get_access_key_secret_key_list(user_id,
                                                                               miscellaneous_operation.ALIBABA_CLOUD)
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
                            error_describe_zones, response_list_ecs_zones = alibaba_ecs.list_zones(region_id)

                            zone_info = list(filter(lambda x: x.get("ZoneId") in zone_id, response_list_ecs_zones))
                            print(zone_info)

                            if not error_describe_zones:
                                system_disk.update({'ZoneDetails': zone_info})
                            else:
                                system_disk.update({'error': response_list_ecs_zones})
                if access_flag:
                    system_disk.update({'is_successful': False,
                                         'error': 'Invalid provider_id or no data available.'})
            else:
                system_disk.update({'is_successful': False,
                                     'error': 'Invalid user_id or no data available.'})
    except Exception as e:
        api_response.update({
            'error': e,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)

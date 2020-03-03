from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.utils import json

from cluster.alibaba.compute_service import Alibaba_ECS
from cluster.others import miscellaneous_operation
from cluster.others.miscellaneous_operation import key_validations_cluster_provisioning, get_access_key_secret_key_list, \
    check_for_provider_id, insert_or_update_namespace_details, get_grouped_credential_list, \
    insert_or_update_repository_details
from registry.alibaba.container_registry_service import Alibaba_CRS


# list regions
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
                            flag, region_list = alibaba_ecs.list_container_registry_regions()

                            if flag:
                                api_response.update({'is_successful': flag,
                                                     'region_list': region_list,
                                                     'error': None})
                            else:
                                raise Exception('Error occurred while fetching the region list')
                if access_flag:
                    raise Exception('Invalid provider_id or no data available.')
            else:
                raise Exception('Invalid user_id or no data available.')

    except Exception as e:
        api_response.update({
            'error': e.message,
            'is_successful': False
        })
    finally:
        return JsonResponse(api_response, safe=False)


# list providers
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


# create namespace
@api_view(['POST'])
def alibaba_create_namespace(request):
    """
    Create the namespace on the alibaba container registry
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'namespace_id': None,
        'error': None
    }
    namespace_info_db = {}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_create_namespace, response_create_namespace = alibaba_crs.create_namespace_request(
                        namespace=namespace)
                    if not error_create_namespace:
                        # Database entry for Create
                        namespace_id = response_create_namespace.get('data').get('namespaceId')
                        api_response.update({
                            'namespace_id': namespace_id
                        })

                        namespace_info_db.update({
                            'is_insert': True,
                            'user_id': int(user_id),
                            'provider_id': int(provider_id),
                            'namespace_id': namespace_id,
                            'namespace_details': json.dumps(
                                dict(response_create_namespace).update({'namespace_name': namespace})),
                            'status': 'Created',
                            'operation': 'created from cloudbrain', })
                        error_insert_or_update_namespace_details, response_insert_or_update_namespace_details = insert_or_update_namespace_details(
                            namespace_info_db)
                        if error_insert_or_update_namespace_details:
                            raise Exception('Namespace created but error while inserting data into database')
                    else:
                        raise Exception(response_create_namespace)
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


# delete namespace
@api_view(['DELETE'])
def alibaba_delete_namespace(request):
    """
    Delete the namespace on the alibaba container registry
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'error': None
    }
    namespace_info_db = {}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')

            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_delete_namespace, response_delete_namespace = alibaba_crs.delete_namespace_request(
                        namespace=namespace)
                    if not error_delete_namespace:
                        # Database entry for Delete

                        namespace_info_db.update({
                            'is_insert': True,
                            'user_id': int(user_id),
                            'provider_id': int(provider_id),
                            'namespace_id': '',
                            'namespace_details': json.dumps(
                                dict(response_delete_namespace).update({'namespace_name': namespace})),
                            'status': 'Deleted',
                            'operation': 'deleted from cloudbrain', })
                        error_insert_or_update_namespace_details, response_insert_or_update_namespace_details = insert_or_update_namespace_details(
                            namespace_info_db)
                        if error_insert_or_update_namespace_details:
                            raise Exception('Namespace deleted but error while inserting data into database')
                    else:
                        raise Exception(response_delete_namespace)
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


# list namespaces
@api_view(['POST'])
def alibaba_list_namespace(request):
    """
    List the namespace on the alibaba container registry
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'namespace_list': [],
        'error': None
    }
    all_provider_container_registry_details = []
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
                    for credential in response_get_grouped_credential_list:
                        provider_container_registry_info = {}
                        alibaba_crs = Alibaba_CRS(
                            ali_access_key=credential.get('access_key'),
                            ali_secret_key=credential.get('secret_key')
                        )
                        error_list_namespaces, response_list_namespaces = alibaba_crs.list_namespaces()
                        if not error_list_namespaces:
                            # Database entry for Delete
                            provider_container_registry_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'namespace_list': response_list_namespaces})
                        else:
                            # skip if any error occurred for a particular key
                            provider_container_registry_info.update({
                                'provider_names': credential.get('provider_name_list'),
                                'namespace_list': [],
                                'error': response_list_namespaces})
                        all_provider_container_registry_details.append(provider_container_registry_info)
                    api_response = {'namespace_list': all_provider_container_registry_details}
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


# update namespace
@api_view(['POST'])
def alibaba_update_namespace(request):
    """
    Update the namespace on the alibaba container registry
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'request_body']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            request_body = json_request.get('request_body')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_update_namespace_request, response_update_namespace_request = alibaba_crs.update_namespace_request(
                        namespace,
                        request_body)
                    if error_update_namespace_request:
                        raise Exception(response_update_namespace_request)
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


# create repository
@api_view(['POST'])
def alibaba_create_repository(request):
    """
    Create the repository on the alibaba container registry
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'repository_id': None,
        'error': None
    }
    repository_info_db = {}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'repository_name', 'repository_summary',
                           'repository_detail', 'repository_type', 'region_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            repository_name = json_request.get('repository_name')
            repository_summary = json_request.get('repository_summary')
            repository_detail = json_request.get('repository_detail')
            repository_type = json_request.get('repository_type')
            region_id = json_request.get('region_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_create_repository_request, response_create_repository_request = alibaba_crs.create_repository_request(
                        namespace=namespace, repository_name=repository_name, repository_summary=repository_summary,
                        repository_detail=repository_detail,
                        repository_type=repository_type, region_id=region_id)
                    if not error_create_repository_request:
                        # Database entry for Create

                        repository_id = response_create_repository_request.get('data').get('repoId')

                        api_response.update({
                            'repository_id': repository_id
                        })
                        repository_info_db.update({
                            'is_insert': True,
                            'user_id': int(user_id),
                            'provider_id': int(provider_id),
                            'repository_id': repository_id,
                            'repository_details': json.dumps(
                                dict(response_create_repository_request).update({'namespace_name': namespace,
                                                                                 'repository_name': repository_name,
                                                                                 'repository_summary': repository_summary,
                                                                                 'repository_detail': repository_detail,
                                                                                 'repository_type': repository_type,
                                                                                 'region_id': region_id})),
                            'status': 'Created',
                            'operation': 'created from cloudbrain', })
                        error_insert_or_update_repository_details, response_insert_or_update_repository_details = insert_or_update_repository_details(
                            repository_info_db)
                        if error_insert_or_update_repository_details:
                            raise Exception('Repository created but error while inserting data into database')
                    else:
                        raise Exception(response_create_repository_request)
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


# list repository
@api_view(['POST'])
def alibaba_list_repository_by_provider(request):
    """
    List the repository on the alibaba container registry by provider
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'all_repository_list': [],
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)

        if not error_key_validations_cluster_provisioning:

            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')

            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:
                    error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                        provider_id, response_get_access_key_secret_key_list)
                    if not error_check_for_provider_id:
                        # if provider_id present in credentials from database
                        alibaba_crs = Alibaba_CRS(
                            ali_access_key=response_check_for_provider_id.get('client_id'),
                            ali_secret_key=response_check_for_provider_id.get('client_secret')
                        )
                        error_list_repository, response_list_repository = alibaba_crs.list_repository_by_provider()
                        if not error_list_repository:
                            # Database entry for Delete
                            api_response.update({
                                'all_repository_list': response_list_repository})
                        else:
                            # skip if any error occurred for a particular key
                            raise Exception(response_list_repository)
                    else:
                        # if provider_id is not present in credentials
                        raise Exception(response_check_for_provider_id)
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


# list repository
@api_view(['POST'])
def alibaba_list_repository_by_namespace(request):
    """
    List the repository on the alibaba container registry by namespace
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'all_repository_list': [],
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)

        if not error_key_validations_cluster_provisioning:

            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                # groups the common credentials according to the access key
                error_get_grouped_credential_list, response_get_grouped_credential_list = get_grouped_credential_list(
                    response_get_access_key_secret_key_list)
                if not error_get_grouped_credential_list:
                    error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                        provider_id, response_get_access_key_secret_key_list)
                    if not error_check_for_provider_id:
                        # if provider_id present in credentials from database
                        alibaba_crs = Alibaba_CRS(
                            ali_access_key=response_check_for_provider_id.get('client_id'),
                            ali_secret_key=response_check_for_provider_id.get('client_secret')
                        )
                        error_list_repository, response_list_repository = alibaba_crs.list_repository_by_namespace(
                            namespace)
                        if not error_list_repository:
                            # Database entry for Delete
                            api_response.update({
                                'all_repository_list': response_list_repository})
                        else:
                            # skip if any error occurred for a particular key
                            raise Exception(response_list_repository)
                    else:
                        # if provider_id is not present in credentials
                        raise Exception(response_check_for_provider_id)
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


# delete repository
@api_view(['DELETE'])
def alibaba_delete_repository(request):
    """
    Delete the repository on the alibaba container registry
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'repository_name', 'region_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            repository_name = json_request.get('repository_name')
            region_id = json_request.get('region_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_delete_repository_request, response_delete_repository_request = alibaba_crs.delete_repository_request(
                        namespace=namespace, repository_name=repository_name, region_id=region_id)
                    if not error_delete_repository_request:
                        repository_info_db = {
                            'is_insert': True,
                            'user_id': int(user_id),
                            'provider_id': int(provider_id),
                            'repository_id': '',
                            'repository_details': {'namespace_name': namespace,
                                                   'repository_name': repository_name,
                                                   'region_id': region_id,
                                                   'repository_id': ''},
                            'status': 'Deleted',
                            'operation': 'deleted from cloudbrain'}
                        error_insert_or_update_repository_details, response_insert_or_update_repository_details = insert_or_update_repository_details(
                            repository_info_db)
                        if error_insert_or_update_repository_details:
                            raise Exception('Repository created but error while inserting data into database')

                    else:
                        raise Exception(response_delete_repository_request)

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


# delete repository tag
@api_view(['DELETE'])
def alibaba_delete_repository_tag(request):
    """
    Delete the repository of tag on the alibaba container registry
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'repository_name', 'region_id', 'tag_name']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            repository_name = json_request.get('repository_name')
            region_id = json_request.get('region_id')
            tag_name = json_request.get('tag_name')

            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_delete_repository_request, response_delete_repository_request = alibaba_crs.delete_repository_tag_request(
                        namespace=namespace, repository_name=repository_name, region_id=region_id, tag_name=tag_name)
                    if error_delete_repository_request:
                        raise Exception(response_delete_repository_request)

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


# get repository image layer
@api_view(['POST'])
def alibaba_get_repository_image_layer(request):
    """
    Delete the repository of tag on the alibaba container registry
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'image_layers': None,
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'repository_name', 'region_id', 'tag_name']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            repository_name = json_request.get('repository_name')
            region_id = json_request.get('region_id')
            tag_name = json_request.get('tag_name')

            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_get_repository_image_layer_request, response_get_repository_image_layer_request = alibaba_crs.get_repository_image_layer_request(
                        namespace=namespace, repository_name=repository_name, region_id=region_id, tag_name=tag_name)
                    if not error_get_repository_image_layer_request:
                        api_response.update({'image_layers': response_get_repository_image_layer_request})
                    else:
                        raise Exception(response_get_repository_image_layer_request)

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


# get repository source
@api_view(['POST'])
def alibaba_get_repository_source(request):
    """
    get the repository source repo on the alibaba container registry
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'repository_name', 'region_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            repository_name = json_request.get('repository_name')
            region_id = json_request.get('region_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_get_repository_source_request, response_get_repository_source_request = alibaba_crs.get_repository_source(
                        namespace=namespace, repository_name=repository_name, region_id=region_id)
                    if error_get_repository_source_request:
                        raise Exception(response_get_repository_source_request)

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


# update repository
@api_view(['POST'])
def alibaba_update_repository(request):
    """
    Updates the repository on the alibaba container registry
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'repository_name', 'repository_summary',
                           'repository_detail', 'repository_type', 'region_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            repository_name = json_request.get('repository_name')
            summary = json_request.get('repository_summary')
            detail = json_request.get('repository_detail')
            repo_type = json_request.get('repository_type')
            region_id = json_request.get('region_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_create_repository_request, response_create_repository_request = alibaba_crs.update_repository(
                        namespace=namespace, repository_name=repository_name, summary=summary,
                        detail=detail,
                        repo_type=repo_type, region_id=region_id)

                    if error_create_repository_request:
                        # update creation failed.
                        raise Exception(response_create_repository_request)
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


# list of all tags belongs to repository
@api_view(['POST'])
def alibaba_list_all_tags_of_repository(request):
    """
    Provides repository tags
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'tag_list_details': None,
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'repository_name', 'region_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            repository_name = json_request.get('repository_name')
            region_id = json_request.get('region_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_list_all_tags_of_repository, response_list_all_tags_of_repository = alibaba_crs.list_all_tags_of_repository(
                        namespace=namespace, repository_name=repository_name, region_id=region_id)

                    if not error_list_all_tags_of_repository:
                        api_response.update({'tag_list_details': response_list_all_tags_of_repository})
                    else:
                        raise Exception(response_list_all_tags_of_repository)

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


# create webhook
@api_view(['POST'])
def alibaba_create_repository_webhook_request(request):
    """
    Creates repository webhook
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'webhook_id': None,
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'repository_name', 'region_id', 'webhook_name',
                           'trigger_type', 'webhook_url', 'trigger_tag_list']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            repository_name = json_request.get('repository_name')
            region_id = json_request.get('region_id')
            trigger_type = json_request.get('trigger_type')
            webhook_url = json_request.get('webhook_url')
            webhook_name = json_request.get('webhook_name')
            trigger_tag_list = json_request.get('trigger_tag_list')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_create_repo_webhook, response_create_repo_webhook = alibaba_crs.create_repo_webhook_request(
                        namespace=namespace, repository_name=repository_name, region_id=region_id,
                        trigger_type=trigger_type, webhook_url=webhook_url, webhook_name=webhook_name,
                        trigger_tag_list=trigger_tag_list)

                    if not error_create_repo_webhook:
                        api_response.update({'webhook_id': response_create_repo_webhook.get('data').get('webhookId')})
                    else:
                        raise Exception(response_create_repo_webhook)

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


# list webhook
@api_view(['POST'])
def alibaba_get_repository_webhook_request(request):
    """
    Provides repository webhook
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'webhook_details': None,
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'repository_name', 'region_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            repository_name = json_request.get('repository_name')
            region_id = json_request.get('region_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_get_repo_webhook_request, response_get_repo_webhook_request = alibaba_crs.get_repo_webhook_request(
                        namespace=namespace, repository_name=repository_name, region_id=region_id)

                    if not error_get_repo_webhook_request:
                        api_response.update({'webhook_details': response_get_repo_webhook_request})
                    else:
                        raise Exception(response_get_repo_webhook_request)

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


# update webhook
@api_view(['POST'])
def alibaba_update_repository_webhook_request(request):
    """
    Creates repository webhook
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'repository_name', 'region_id', 'webhook_name',
                           'trigger_type', 'webhook_url', 'trigger_tag_list', 'webhook_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            repository_name = json_request.get('repository_name')
            region_id = json_request.get('region_id')
            trigger_type = json_request.get('trigger_type')
            webhook_url = json_request.get('webhook_url')
            webhook_name = json_request.get('webhook_name')
            trigger_tag_list = json_request.get('trigger_tag_list')
            webhook_id = json_request.get('webhook_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_create_repo_webhook, response_create_repo_webhook = alibaba_crs.update_repo_webhook_request(
                        namespace=namespace, repository_name=repository_name, region_id=region_id,
                        trigger_type=trigger_type, webhook_url=webhook_url, webhook_name=webhook_name,
                        trigger_tag_list=trigger_tag_list, webhook_id=webhook_id)
                    if error_create_repo_webhook:
                        raise Exception(response_create_repo_webhook)
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


# delete webhook
@api_view(['DELETE'])
def alibaba_delete_repository_webhook_request(request):
    """
    Delete repository webhook
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'repository_name', 'region_id', 'webhook_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            repository_name = json_request.get('repository_name')
            region_id = json_request.get('region_id')
            webhook_id = json_request.get('webhook_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_delete_repo_webhook, response_delete_repo_webhook = alibaba_crs.delete_repo_webhook_request(
                        namespace=namespace, repository_name=repository_name, region_id=region_id,
                        webhook_id=webhook_id)

                    if error_delete_repo_webhook:
                        raise Exception(response_delete_repo_webhook)
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


# list build list for repository
@api_view(['POST'])
def alibaba_get_repo_build_list(request):
    """
    Provides repository build list
    :param request:
    :return:
    """
    api_response = {
        'is_successful': True,
        'build_list_details': None,
        'error': None
    }
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'provider_id', 'namespace', 'repository_name', 'region_id']
        # key validations
        error_key_validations_cluster_provisioning, response_key_validations_cluster_provisioning = key_validations_cluster_provisioning(
            json_request, valid_json_keys)
        if not error_key_validations_cluster_provisioning:
            user_id = json_request.get('user_id')
            provider_id = json_request.get('provider_id')
            namespace = json_request.get('namespace')
            repository_name = json_request.get('repository_name')
            region_id = json_request.get('region_id')
            # Fetching access keys and secret keys from db
            error_get_access_key_secret_key_list, response_get_access_key_secret_key_list = get_access_key_secret_key_list(
                user_id, miscellaneous_operation.ALIBABA_CLOUD)
            if not error_get_access_key_secret_key_list:
                error_check_for_provider_id, response_check_for_provider_id = check_for_provider_id(
                    provider_id, response_get_access_key_secret_key_list)
                if not error_check_for_provider_id:
                    # if provider_id present in credentials from database
                    alibaba_crs = Alibaba_CRS(
                        ali_access_key=response_check_for_provider_id.get('client_id'),
                        ali_secret_key=response_check_for_provider_id.get('client_secret')
                    )
                    error_list_all_build_of_repository, response_list_all_build_of_repository = alibaba_crs.list_all_repository_build(
                        namespace=namespace, repository_name=repository_name, region_id=region_id)

                    if not error_list_all_build_of_repository:
                        api_response.update({'build_list_details': response_list_all_build_of_repository})
                    else:
                        raise Exception(response_list_all_build_of_repository)

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

from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.utils import json

from cluster.others import miscellaneous_operation
from cluster.others.miscellaneous_operation import key_validations_cluster_provisioning, get_access_key_secret_key_list, \
    check_for_provider_id, insert_or_update_namespace_details, get_grouped_credential_list, \
    insert_or_update_repository_details
from registry.alibaba.container_registry_service import Alibaba_CRS


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
                        # application creation failed.
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


@api_view(['POST'])
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
                        # application creation failed.
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
                        # application creation failed.
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
                        # application creation failed.
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
                            api_response.update({
                                'all_repository_list': [],
                                'error': response_list_repository})
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
                            api_response.update({
                                'all_repository_list': [],
                                'error': response_list_repository})
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


@api_view(['POST'])
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

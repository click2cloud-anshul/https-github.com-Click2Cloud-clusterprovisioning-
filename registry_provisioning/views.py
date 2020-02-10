from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.utils import json

from cluster.others import miscellaneous_operation
from cluster.others.miscellaneous_operation import key_validations_cluster_provisioning, get_access_key_secret_key_list, \
    check_for_provider_id, insert_or_update_namespace_details, get_grouped_credential_list
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
        'namespace_detail': {},
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
                        api_response.update({
                            'namespace_detail': response_create_namespace.get('data')
                        })
                        namespace_id = response_create_namespace.get('data').get('namespaceId')
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

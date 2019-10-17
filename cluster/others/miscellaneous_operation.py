import json
import os
import time

from django.db import connection

from clusterProvisioningClient.settings import BASE_DIR


def get_access_key_secret_key_list(user_id=None):
    """
    retrieve the list of access keys and secrete keys from db
    :param user_id:
    :return:
    """
    cursor = None
    error = False
    response = None
    try:
        # create cursor for calling stored procedure
        cursor = connection.cursor()
        cmd = "SELECT public._cb_cp_sp_access_key_secret_key('%s')" % user_id
        cursor.execute(cmd)
        rows = cursor.fetchall()
        result = rows[0][0]
        response = json.dumps(result)
        if result is None:
            error = True
            response = 'Invalid user_id or no data available.'

    except Exception as ex:
        error = True
        response = ex.message
    finally:
        if cursor is not None:
            cursor.close()
        return error, response


def key_validations_cluster_provisioning(request_keys=None, validation_keys=None):
    """
    validate the keys from request parameter
    :param request_keys: keys receieved from request which need to validate
    :param validation_keys: referenced keys for validation
    :return:
    """
    error = False
    response = {}
    missing_key_flag = False
    missing_value_flag = False
    try:
        missing_keys = []
        missing_values = []
        for key in validation_keys:
            if key not in request_keys:
                missing_key_flag = True
                missing_keys.append(key)
            elif key in ['provider_id', 'user_id']:
                # checking the type of value is int only
                if not isinstance(request_keys.get(key), int):
                    missing_value_flag = True
                    missing_values.append(key)
            elif key in ['region_id', 'cluster_id', 'application_body']:
                # checking string length and checking the type of value is string only
                if (len(str(request_keys.get(key)).strip())) == 0 or not isinstance(request_keys.get(key), unicode):
                    missing_value_flag = True
                    missing_values.append(key)
            elif key in ['request_body']:
                # checking dict length and checking the type of value is dict only
                if not isinstance(request_keys.get(key), dict) or len(request_keys.get(key)) == 0:
                    missing_value_flag = True
                    missing_values.append(key)
            elif key in ['zone_id_list']:
                # checking dict length and checking the type of value is dict only
                if not isinstance(request_keys.get(key), list) or len(request_keys.get(key)) == 0:
                    missing_value_flag = True
                    missing_values.append(key)

        if missing_key_flag or missing_value_flag:
            response = {
                'error':
                    {
                        'message': 'Following keys and/or values are missing in request parameter or value type is invalid.',
                        'keys_info': {
                            'keys': missing_keys,
                            'values': missing_values,
                        }
                    }
            }
            if len(missing_keys) == 0 and len(missing_values) == 0:
                response.get('error').get('keys_info').update({'keys': []})
                response.get('error').get('keys_info').update({'values': []})
            elif len(missing_keys) == 0:
                response.get('error').get('keys_info').update({'keys': []})
            elif len(missing_keys) == 0:
                response.get('error').get('missing').update({'values': []})
    except Exception as e:
        error = True
        return error, response.update({
            'message': e.message
        })
    finally:
        if len(response) == 0:
            # return error=False if response is empty
            error = False
            return error, response
        else:
            # return error=True if response is not empty
            error = True
            return error, response


def insert_or_update_cluster_details(params=None):
    """
    insert or update the cluster details in the database
    :param params:
    :return:
    """
    cursor = None
    error = False
    response = None
    try:
        cursor = connection.cursor()
        user_id = int(params.get('user_id'))
        provider_id = int(params.get('provider_id'))
        cluster_id = str(params.get('cluster_id'))
        cluster_details = params.get('cluster_details')
        status = params.get('status')
        operation = params.get('operation')
        if params.get('is_insert'):
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            cmd = "INSERT INTO public._cb_cp_cluster_details(user_id, provider_id, cluster_id, cluster_details, " \
                  "status, created_at, operation) VALUES ({user_id},{provider_id},'{cluster_id}','{cluster_details}'" \
                  ",'{status}','{created_at}','{operation}')".format(
                user_id=int(user_id), provider_id=int(provider_id),
                cluster_id=cluster_id,
                cluster_details=cluster_details,
                status=status, created_at=created_at,
                operation=operation)
            cursor.execute(cmd)
            connection.commit()
            response = 'Success'
        else:
            # update operation
            cmd = "UPDATE public._cb_cp_cluster_details SET status = '{status}', cluster_details = " \
                  "'{cluster_details}', operation = '{operation}' " \
                  "where user_id = {user_id} and provider_id = {provider_id} and cluster_id = '{cluster_id}' ".format(
                status=status,
                cluster_details=cluster_details,
                operation=operation,
                user_id=user_id,
                provider_id=provider_id,
                cluster_id=cluster_id
            )
            cursor.execute(cmd)
            connection.commit()
            response = 'Success'
    except Exception as e:
        error = True
        response = e.message
    finally:
        if cursor is not None:
            cursor.close()
        return error, response


def get_db_info_using_cluster_id(cluster_id=None):
    """
    retrieve the data of cluster from db
    :param cluster_id:
    :return:
    """
    cursor = None
    error = False
    response = None
    try:
        cursor = connection.cursor()
        sql_cmd = "SELECT * FROM public._cb_cp_cluster_details where cluster_id = '{cluster_id}'".format(
            cluster_id=cluster_id)
        cursor.execute(sql_cmd)
        response = cursor.fetchall()
    except Exception as e:
        error = True
        response = e.message
    finally:
        if cursor is not None:
            cursor.close()
        return error, response


def create_cluster_config_file(cluster_id=None, config_details=None):
    """
    create the folder for the config file of kubernetes cluster with its id as a directory name
    :param cluster_id:
    :param config_details:
    :return:
    """
    error = False
    response = None
    try:
        path = os.path.join(BASE_DIR, 'cluster', 'dumps', cluster_id)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, 'config'), 'w+') as outfile:
            json.dump(config_details, outfile)
        response = 'Success'
    except Exception as e:
        error = True
        response = e.message
    finally:
        return error, response


def get_grouped_credential_list(credentials):
    """
    groups the common credentials according to the access key
    :param credentials:
    :return:
    """
    error = False
    response = None
    try:
        credentials = json.loads(credentials)
        credential_list = []
        unique_access_keys = set(item.get('client_id') for item in credentials)
        for access_key in unique_access_keys:
            provider_name_list = []
            credential_json = {}
            secret_key = None
            for element in credentials:
                if element.get('client_id') == access_key:
                    provider_name_list.append(element.get('name'))
                    secret_key = element.get('client_secret')
            credential_json.update({
                'provider_name_list': provider_name_list,
                'access_key': access_key,
                'secret_key': secret_key
            })
            credential_list.append(credential_json)
        response = credential_list
    except Exception as e:
        error = True
        response = e.message
    finally:
        return error, response


def check_for_provider_id(provider_id, credentials):
    """
    checks for the provider_id present in credentials
    :param provider_id:
    :param credentials:
    :return:
    """
    error = False
    response = None
    try:
        credentials = json.loads(credentials)
        for item in credentials:
            if item.get('id') == provider_id:
                error = False
                response = item
                break
            else:
                error = True
        if error:
            response = 'provider does not exists'
    except Exception as e:
        error = True
        response = e.message
    finally:
        return error, response

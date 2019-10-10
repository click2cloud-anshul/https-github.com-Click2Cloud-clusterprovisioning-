import json

from django.db import connection


def get_access_key_secret_key_list(user_id=None):
    """
    retrieve the list of access keys and secrete keys from db
    :param user_id:
    :return:
    """
    cursor = None
    error = False
    try:
        # create cursor for calling stored procedure
        cursor = connection.cursor()
        cmd = "SELECT public._cb_cp_sp_access_key_secret_key('%s')" % user_id
        cursor.execute(cmd)
        rows = cursor.fetchall()
        result = rows[0][0]
        result_json = json.dumps(result)
        if result is None:
            error = True
            return error, 'No data found for access key and secret key. Please check the  user id.'
        return error, result_json
    except Exception as ex:
        error = True
        return error, ex.message
    finally:
        if cursor is not None:
            cursor.close()


def key_validations_cluster_provisioning(request_keys, validation_keys):
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
            elif not isinstance(request_keys.get(key), int):
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

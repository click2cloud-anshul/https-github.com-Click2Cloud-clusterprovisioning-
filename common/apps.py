# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import time

from django.apps import AppConfig

from django.db import connection
import json


class CommonConfig(AppConfig):
    name = 'common'


def test_db():
    result = False
    cursor = None

    try:

        # create cursor for calling stored procedure
        cursor = connection.cursor()

        # create command to execute stored procedure
        # cmd = "EXEC [dbo].[test_connection] @guid = 'test'"
        cmd = "SELECT * FROM cb_dr_sp_test_connection()"

        # execute command and getting the result
        cursor.execute(cmd)
        # connection.commit()

        rows = cursor.fetchall()
        result = rows[0][0]
        json.loads(str(result).lower())

        return result
    except Exception as ex:
        # add exception details to logger
        print(ex)
        pass
        return result

    finally:
        #  if cursor is not None close the cursor
        if cursor is not None:
            cursor.close()


def get_access_key_secret_key_list(user_id=None):
    result = False
    cursor = None

    try:

        # create cursor for calling stored procedure
        cursor = connection.cursor()

        # create command to execute stored procedure
        # cmd = "EXEC [dbo].[test_connection] @guid = 'test'"
        cmd = 'SELECT public._cb_cp_sp_access_key_secret_key(' + user_id + ')'

        # execute command and getting the result
        cursor.execute(cmd)
        # connection.commit()

        rows = cursor.fetchall()
        result = rows[0][0]
        result_json = json.dumps(result)
        if result is None:
            return False, "Please provide valid user_id"
        return True, result_json
    except Exception as ex:
        # add exception details to logger
        return False, ex.message

    finally:
        #  if cursor is not None close the cursor
        if cursor is not None:
            cursor.close()


def get_cluster_id_list(user_id=None, provider_id=None):
    cluster_list = []
    cursor = None

    try:

        # create cursor for calling stored procedure
        cursor = connection.cursor()

        # create command to execute stored procedure
        # cmd = "EXEC [dbo].[test_connection] @guid = 'test'"
        cmd = 'SELECT cluster_id FROM public._cb_cp_cluster_details where provider_id =' + user_id + ' and user_id = ' + provider_id + ')'

        # execute command and getting the result
        cursor.execute(cmd)
        connection.commit()
        rows = cursor.fetchall()
        rows = list(rows)
        cluster_list = []
        for row in rows:
            cluster_list.append(row[0])
        print cluster_list

        return True, cluster_list
    except Exception as ex:
        # add exception details to logger
        return False, cluster_list

    finally:
        #  if cursor is not None close the cursor
        if cursor is not None:
            cursor.close()


def insert_or_update_cluster_details(params=None):
    try:
        if params['is_insert']:
            cursor = connection.cursor()
            user_id = int(params['user_id'])
            provider_id = int(params['provider_id'])
            cluster_id = str(params['cluster_id'])
            cluster_details = params['cluster_details']
            status = params['status']
            operation = params['operation']
            created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            cmd = "INSERT INTO public._cb_cp_cluster_details(user_id, provider_id, cluster_id, cluster_details, status, created_at, operation) VALUES ({user_id},{provider_id},'{cluster_id}','{cluster_details}','{status}','{created_at}','{operation}')".format(
                user_id=int(user_id), provider_id=int(provider_id),
                cluster_id=cluster_id,
                cluster_details=cluster_details,
                status=status, created_at=created_at,
                operation=operation)
            cursor.execute(cmd)
            connection.commit()
            return True, "Success"
        else:
            # update operation
            cursor = connection.cursor()
            user_id = int(params['user_id'])
            provider_id = int(params['provider_id'])
            cluster_id = str(params['cluster_id'])
            cluster_details = params['cluster_details']
            status = params['status']
            operation = params['operation']
            cmd = '''UPDATE public._cb_cp_cluster_details SET status = '{status}', cluster_details = '{cluster_details}', operation = '{operation}' where user_id = {user_id} and provider_id = {provider_id} and cluster_id = '{cluster_id}' '''.format(
                status=status,
                cluster_details=cluster_details,
                operation=operation,
                user_id=user_id,
                provider_id=provider_id,
                cluster_id=cluster_id
            )
            cursor.execute(cmd)
            connection.commit()

            return True, "Success"

    except Exception as e:
        return False, e.message


def file_operation(cluster_id=None, string_to_append=None):
    path = get_path(cluster_id)
    if os.path.exists(path):
        return True
    os.makedirs(path, True)
    try:
        with open(os.path.join(path, "config"), "w+") as outfile:
            json.dump(string_to_append, outfile)
        return True
    except Exception:
        return False


def get_path(cluster_id):
    path = "./"
    if get_platform().__contains__('Linux') or get_platform().__contains__('OS X'):
        # for linux
        path = "/var/www/html/clusterProvisioningClient/"
    directory = os.path.join(path, 'clusters', cluster_id)
    return directory


def get_platform():
    platforms = {
        'linux1': 'Linux',
        'linux2': 'Linux',
        'darwin': 'OS X',
        'win32': 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]


def get_db_info_using_cluster_id(cluster_id=None):
    cursor = None
    record = None
    try:

        # create cursor for calling stored procedure
        cursor = connection.cursor()

        # create command to execute stored procedure
        # cmd = "EXEC [dbo].[test_connection] @guid = 'test'"
        sql_cmd = "SELECT * FROM public._cb_cp_cluster_details where cluster_id = '{cluster_id}'".format(
            cluster_id=cluster_id)

        record = None
        cursor.execute(sql_cmd)
        record = cursor.fetchall()
        if record is not None:
            if len(list(record)) > 0:
                return True, record
            return False, record
        else:
            return False, record
    except Exception:
        return False, record

    finally:
        if cursor is not None:
            cursor.close()

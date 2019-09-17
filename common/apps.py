# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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

        return result_json
    except Exception as ex:
        # add exception details to logger
        print(ex)
        pass
        return result

    finally:
        #  if cursor is not None close the cursor
        if cursor is not None:
            cursor.close()

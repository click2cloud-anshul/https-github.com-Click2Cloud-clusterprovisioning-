import base64
import json
import os
import uuid

import yaml

from cluster.alibaba.container_service import get_labels_from_items
from cluster.kuberenetes.operations import Kubernetes_Operations
from cluster.others.miscellaneous_operation import insert_or_update_cluster_details, create_cluster_config_file, \
    get_db_info_using_user_id_and_provider_id, insert_or_update_cluster_config_details, \
    get_cluster_config_details
from clusterProvisioningClient.settings import BASE_DIR

config_dumps_path = os.path.join(BASE_DIR, 'config_dumps')


class On_Premises_Cluster:
    def __init__(self, user_id, cluster_name, cluster_config):
        """
        constructor for the On_Premises_Cluster classs
        :param user_id:
        :param cluster_config:
        :param cluster_config:
        """
        self.cluster_name = cluster_name
        self.user_id = user_id
        self.cluster_config = cluster_config

    def add_on_premises_cluster(self):
        """
        This method will add On_Premises_Cluster
        :return:
        """

        error = False
        response = None
        provider_id = 0
        cluster_info_db = {}
        cluster_id = str(uuid.uuid4())
        cluster_config = yaml.safe_load(self.cluster_config)
        cluster_details = {
            'cluster_id': cluster_id,
            'cluster_name': self.cluster_name,
            'cluster_config': cluster_config
        }
        try:
            error_get_db_info_using_provider_id, response_get_db_info_using_provider_id = get_db_info_using_user_id_and_provider_id(
                self.user_id, provider_id)

            flag_for_already_exists = False
            if not error_get_db_info_using_provider_id:
                for response_using_provider_id in response_get_db_info_using_provider_id:
                    response_using_provider_id_cluster_details = response_using_provider_id[4]
                    response_using_provider_id_cluster_details = base64.b64decode(
                        response_using_provider_id_cluster_details)
                    response_using_provider_id_cluster_details = json.loads(
                        response_using_provider_id_cluster_details)
                    if self.cluster_name == response_using_provider_id_cluster_details.get('cluster_name'):
                        flag_for_already_exists = True
            else:
                raise Exception(response_get_db_info_using_provider_id)
            if flag_for_already_exists:
                raise Exception('Cluster already exists')
            else:
                create_cluster_config_file(cluster_id=cluster_id, config_details=cluster_config)
                config_path = os.path.join(config_dumps_path,
                                           cluster_id,
                                           'config')
                k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                # check for accessibility
                error_check_cluster_accessibility, response_check_cluster_accessibility = k8_obj.check_cluster_accessibility()
                if not error_check_cluster_accessibility:

                    # if cluster is accessible
                    cluster_details.update({'cluster_config': base64.b64encode((json.dumps(cluster_config)))})
                    cluster_info_db.update({
                        'is_insert': True,
                        'user_id': int(self.user_id),
                        'provider_id': int(provider_id),
                        'cluster_id': '%s' % cluster_id,
                        'cluster_details': cluster_details,
                        'status': 'Running',
                        'operation': 'Added On Premises Cluster on Cloudbrain', })
                    error_insert_or_update_cluster_details, response_insert_or_update_cluster_details = insert_or_update_cluster_details(
                        cluster_info_db)

                    if not error_insert_or_update_cluster_details:
                        response = 'Cluster added successfully'
                    else:
                        raise Exception('Cluster is accessible but error while inserting data into database')
                else:
                    # if cluster is not accessible
                    raise Exception(response_check_cluster_accessibility)

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def get_pods(self, cluster_details):
        """
        This method will provide pod details
        :param cluster_details:
        :return:
        """
        cluster_id = cluster_details.get('cluster_id')
        response_cluster_details = {
            'cluster_name': self.cluster_name,
            'cluster_id': cluster_details.get('cluster_id'),
            'pod_details': {},
            'error': None,
            'labels': {}
        }

        try:
            error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                cluster_id)
            if not error_describe_cluster_config_token_endpoint:
                # Adding unique labels for the cluster_roles in a single cluster
                k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')
                error_get_pods, response_get_pods = k8s_obj.get_pods(
                    cluster_url=response_describe_cluster_config_token_endpoint.get(
                        'cluster_public_endpoint'),
                    token=response_describe_cluster_config_token_endpoint.get('cluster_token'))
                if not error_get_pods:
                    labels = get_labels_from_items(
                        response_get_pods.get('items'))
                    response_cluster_details.update({
                        'pod_details': response_get_pods,
                        'labels': labels
                    })
                else:
                    response_cluster_details.update({'error': response_get_pods})
            else:
                response_cluster_details.update(
                    {'error': response_describe_cluster_config_token_endpoint})

        except Exception as e:
            response_cluster_details.update({'error': e.message})
        finally:
            return response_cluster_details

    def describe_cluster_config_token_endpoint(self, cluster_id):
        """
        This method will provide config, token, and enpoint details from db or config
        :param cluster_id:
        :return:
        """
        provider = 'Alibaba:Cloud'
        error = False
        response = None
        config_detail = {
            'cluster_id': cluster_id,
            'cluster_public_endpoint': None,
            'cluster_config': None,
            'cluster_token': None,
            'provider': provider,
            'is_insert': False,
            'k8s_object': None
        }
        try:
            error_get_cluster_config_details, response_get_cluster_config_details = get_cluster_config_details(
                provider, cluster_id)
            if not error_get_cluster_config_details:
                if response_get_cluster_config_details is not None:
                    if len(list(response_get_cluster_config_details)) > 0:
                        # if cluster config is present in database
                        config_path = os.path.join(config_dumps_path,
                                                   cluster_id,
                                                   'config')
                        error_create_cluster_config_file, response_create_cluster_config_file = create_cluster_config_file(
                            cluster_id, eval(response_get_cluster_config_details.get('cluster_config')))
                        if not error_create_cluster_config_file:
                            k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                            config_detail.update({'cluster_id': cluster_id,
                                                  'cluster_public_endpoint': response_get_cluster_config_details.get(
                                                      'cluster_public_endpoint'),
                                                  'cluster_config': eval(
                                                      response_get_cluster_config_details.get('cluster_config')),
                                                  'cluster_token': response_get_cluster_config_details.get(
                                                      'cluster_token'),
                                                  'k8s_object': k8_obj})
                        else:
                            raise Exception(response_create_cluster_config_file)
                    else:
                        #  if cluster config is not present in database
                        error_describe_cluster_endpoint, response_describe_cluster_endpoint \
                            = self.describe_cluster_endpoint()
                        if not error_describe_cluster_endpoint:
                            config_path = os.path.join(config_dumps_path,
                                                       cluster_id,
                                                       'config')
                            k8_obj = Kubernetes_Operations(configuration_yaml=config_path)
                            error_get_token, response_get_token = k8_obj.get_token()
                            if not error_get_token:
                                # If token is created
                                config_detail.update({
                                    'cluster_public_endpoint': response_describe_cluster_endpoint,
                                    'cluster_config': json.dumps(self.cluster_config),
                                    'cluster_token': response_get_token,
                                    'is_insert': True,
                                    'k8s_object': k8_obj
                                })
                                error_insert_or_update_cluster_config_details, \
                                response_insert_or_update_cluster_config_details = \
                                    insert_or_update_cluster_config_details(
                                        config_detail)
                                if error_insert_or_update_cluster_config_details:
                                    raise Exception(
                                        response_insert_or_update_cluster_config_details)
                        else:
                            # If cluster api server endpoint key not present in config
                            raise Exception(
                                'Unable to find cluster public api server endpoint details')
                    response = config_detail
            else:
                raise Exception(response_get_cluster_config_details)
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def describe_cluster_endpoint(self):
        """
        This method will provide cluster endpoint
        :return:
        """
        error = False
        response = None

        try:
            response = self.cluster_config.get('clusters')[0].get('cluster').get('server')
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def create_k8s_object(self, cluster_id, data, namespace):
        """
        This method will create k8s_object
        :param cluster_id:
        :param data:
        :param namespace:
        :return:
        """
        response = None
        error = False
        try:
            error_describe_cluster_config_token_endpoint, response_describe_cluster_config_token_endpoint = self.describe_cluster_config_token_endpoint(
                cluster_id)
            if not error_describe_cluster_config_token_endpoint:
                # Adding unique labels for the cluster_roles in a single cluster
                k8s_obj = response_describe_cluster_config_token_endpoint.get('k8s_object')

                error_create_k8s_object, response_create_k8s_object = k8s_obj.create_k8s_object(
                    cluster_id=cluster_id,
                    data=data,
                    namespace=namespace)

                if error_create_k8s_object:
                    # If any error occurred while
                    # creating application using file
                    raise Exception(response_create_k8s_object)
            else:
                response.update(
                    {'error': response_describe_cluster_config_token_endpoint})

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

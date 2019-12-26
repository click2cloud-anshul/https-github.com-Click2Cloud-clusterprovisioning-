from azure.mgmt.subscription import SubscriptionClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute.v2019_03_01 import ComputeManagementClient


class Azure_EC2:
    def __init__(self, azure_subscription_id, azure_client_id, azure_client_secret, azure_tenant_id, azure_region):
        """
        constructor for the Azure_CS classs
        :param azure_subscription_id:
        :param azure_client_id:
        :param azure_client_secret:
        :param azure_tenant_id:
        """
        self.azure_subscription_id = azure_subscription_id
        self.azure_client_id = azure_client_id
        self.azure_client_secret = azure_client_secret
        self.azure_tenant_id = azure_tenant_id
        self.azure_region = azure_region
        self.clusters_folder_directory = ''

        def list_regions(self):
            """
            list the available regions in the alibaba
            :return:
            """
            try:

                subscription_id = self.azure_subscription_id  # your Azure Subscription Id

                credentials = ServicePrincipalCredentials(
                    client_id=self.azure_client_id,
                    secret=self.azure_client_secret,
                    tenant=self.azure_tenant_id,
                )
                region_list = []
                subscription_client = SubscriptionClient(credentials)
                result = subscription_client.subscriptions.list_locations(subscription_id)
                for region in result:
                    region_list.append(region.name)

                return True, region_list

            except Exception as e:
                return False, e.message

        def resource_group_list(self):
            try:

                subscription_id = self.azure_subscription_id  # your Azure Subscription Id

                credentials = ServicePrincipalCredentials(
                    client_id=self.azure_client_id,
                    secret=self.azure_client_secret,
                    tenant=self.azure_tenant_id,
                )
                resource_group_list = []

                resource_client = ResourceManagementClient(credentials, subscription_id)

                result = resource_client.resource_groups.list()
                for resource_group in result:
                    resource_group_list.append(resource_group.name)

                return True, resource_group_list

            except Exception as e:
                return False, e.message

        def cluster_object_to_dict(vm_size):
            """
            This method will convert vm_size object to dict
            :param vm_size:
            :return:
            """
            error = False
            response = None

            item = {
                'name': '',
                'number_of_cores': 0,
                'resource_disk_size_in_mb': 0,
                'memory_in_mb': 0,
                'max_data_disk_count': 0,
                'os_disk_size_in_mb': 0,
            }
            try:

                 if vm_size.name:
                     item['id'] = vm_size.name
                 if vm_size.number_of_cores:
                     item['number_of_cores'] = vm_size.number_of_cores
                 if vm_size.resource_disk_size_in_mb:
                     item['resource_disk_size_in_mb'] = vm_size.resource_disk_size_in_mb
                 if vm_size.memory_in_mb:
                     item['memory_in_mb'] = vm_size.memory_in_mb
                 if vm_size.max_data_disk_count:
                     item['max_data_disk_count'] = vm_size.max_data_disk_count
                 if vm_size.os_disk_size_in_mb:
                     item['os_disk_size_in_mb'] = vm_size.os_disk_size_in_mb

                 response = item

            except Exception as e:
                error = True
                response = e.message

            finally:
                return error, response

        def instance_type(self):
            try:

                subscription_id = self.azure_subscription_id  # your Azure Subscription Id

                credentials = ServicePrincipalCredentials(
                    client_id=self.azure_client_id,
                    secret=self.azure_client_secret,
                    tenant=self.azure_tenant_id,
                )
                virtual_machine_size_list = []

                compute_client = ComputeManagementClient(credentials, subscription_id)

                result = compute_client.virtual_machine_sizes.list(location='centralindia')
                for virtual_machine_size in result:
                    # virtual_machine_size.name
                    cluster_object_to_dict(virtual_machine_size)
                return True, resource_group_list

            except Exception as e:
                return False, e.message


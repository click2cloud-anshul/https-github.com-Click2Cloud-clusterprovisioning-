from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute.v2019_03_01 import ComputeManagementClient
from azure.mgmt.network._network_management_client import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient


def vm_size_object_to_dict(vm_size):
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
        if hasattr(vm_size, 'name'):
            item['name'] = vm_size.name
        if hasattr(vm_size, 'number_of_cores'):
            item['number_of_cores'] = vm_size.number_of_cores
        if hasattr(vm_size, 'resource_disk_size_in_mb'):
            item['resource_disk_size_in_mb'] = vm_size.resource_disk_size_in_mb
        if hasattr(vm_size, 'memory_in_mb'):
            item['memory_in_mb'] = vm_size.memory_in_mb
        if hasattr(vm_size, 'max_data_disk_count'):
            item['max_data_disk_count'] = vm_size.max_data_disk_count
        if hasattr(vm_size, 'os_disk_size_in_mb'):
            item['os_disk_size_in_mb'] = vm_size.os_disk_size_in_mb
        response = item
    except Exception as e:
        error = True
        response = e.message
        print(e.message)
    finally:
        return error, response


class Azure_Compute_Service:
    def __init__(self, azure_subscription_id, azure_client_id, azure_client_secret, azure_tenant_id):
        """
        constructor for the Azure_Compute_Service class
        :param azure_subscription_id:
        :param azure_client_id:
        :param azure_client_secret:
        :param azure_tenant_id:
        """
        self.azure_subscription_id = azure_subscription_id
        self.azure_client_id = azure_client_id
        self.azure_client_secret = azure_client_secret
        self.azure_tenant_id = azure_tenant_id
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
                if hasattr(region, 'name'):
                    region_list.append(region.name)
            return False, region_list
        except Exception as e:
            return True, e.message

    def resource_group_list(self):
        """
        Describe all the resource group on the Azure cloud
        :return:
        """
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
                if hasattr(resource_group, 'name'):
                    resource_group_list.append(resource_group.name)
            return False, resource_group_list
        except Exception as e:
            return True, e.message

    def instance_type(self, location):
        """
        Describe all the instance type on the Azure cloud
        :param location:
        :return:
        """
        error = False
        response = None
        try:
            subscription_id = self.azure_subscription_id  # your Azure Subscription Id
            credentials = ServicePrincipalCredentials(
                client_id=self.azure_client_id,
                secret=self.azure_client_secret,
                tenant=self.azure_tenant_id,
            )
            virtual_machine_size_list = []
            compute_client = ComputeManagementClient(credentials, subscription_id)
            result = compute_client.virtual_machine_sizes.list(location=location)
            for virtual_machine_size in result:
                # virtual_machine_size.name
                error_vm_size_object_to_dict, response_vm_size_object_to_dict = vm_size_object_to_dict(
                    virtual_machine_size)
                if error_vm_size_object_to_dict:
                    raise Exception(response_vm_size_object_to_dict)
                else:
                    virtual_machine_size_list.append(response_vm_size_object_to_dict)
            response = virtual_machine_size_list

        except Exception as e:
            error = True
            response = e.message
            print(e.message)
        finally:
            return error, response

    def virtual_network(self, location):
        """
        Describe all the virtual network on the Azure cloud
        :param location:
        :return:
        """
        error = False
        response = None
        virtual_network = {'name': '',
                           'subnet': []}
        try:
            subscription_id = self.azure_subscription_id
            credentials = ServicePrincipalCredentials(
                client_id=self.azure_client_id,
                secret=self.azure_client_secret,
                tenant=self.azure_tenant_id,
            )
            virtual_networks_client = NetworkManagementClient(credentials, subscription_id)
            virtual_network_list = []
            for vn in virtual_networks_client.virtual_networks.list_all():
                subnet_list = []
                if vn.location:
                    if vn.location == location:
                        if hasattr(vn, 'name'):
                            virtual_network = {}
                            virtual_network['name'] = vn.name
                        for s in vn.subnets:
                            subnet = {}
                            if hasattr(s, 'name') and hasattr(s, 'address_prefix'):
                                subnet = {'name': '%s(%s)' % (s.name, s.address_prefix)}
                                subnet_list.append(subnet)
                        virtual_network.update({'subnet': subnet_list})
                        virtual_network_list.append(virtual_network)
            response = virtual_network_list
        except Exception as e:
            error = True
            response = e.message
            print(e.message)
        finally:
            return error, response

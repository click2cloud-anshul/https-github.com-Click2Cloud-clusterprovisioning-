from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.containerservice.v2019_11_01 import ContainerServiceClient


class Azure_CS:
    def __init__(self, azure_subscription_id, azure_client_id, azure_client_secret, azure_tenant_id):
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
        self.clusters_folder_directory = ''

    def cluster_object_to_dict(self, cluster):
        """
        This method will convert cluster object to dict
        :param cluster:
        :return:
        """
        error = False
        response = None

        # agentpool ={
        #                 'name': '',
        #                 'count': 0,
        #                 'vmSize': '',
        #                 'maxPods': 0,
        #                 'osType': '',
        #                 'provisioningState': '',
        #                 'orchestratorVersion': ''
        #             }
        #
        # ssh_key= {'keyData': ''}
        item = {
            'id': '',
            'location': '',
            'name': '',
            'type': '',
            'tags': {},
            'properties': {
                'enableRBAC': False,
                'provisioningState': '',
                'kubernetesVersion': '',
                'maxAgentPools': 0,
                'dnsPrefix': '',
                'fqdn': '',
                'agentPoolProfiles': [

                ],
                'linuxProfile': {
                    'adminUsername': '',
                    'ssh': {
                        'publicKeys': [

                        ]
                    }
                },
                'networkProfile': {
                    'networkPlugin': '',
                    'podCidr': '',
                    'serviceCidr': '',
                    'dnsServiceIP': '',
                    'dockerBridgeCidr': '',
                },
                'nodeResourceGroup': ''
            }
        }

        try:

            if hasattr(cluster, 'id1'):
                item['id'] = cluster.id
            if hasattr(cluster, 'location'):
                item['location'] = cluster.location
            if hasattr(cluster, 'name'):
                item['name'] = cluster.name
            if hasattr(cluster, 'type'):
                item['type'] = cluster.type
            if hasattr(cluster, 'tags'):
                item['tags'] = cluster.tags
            if hasattr(cluster, 'enable_rbac'):
                item['properties']['enableRBAC'] = cluster.enable_rbac
            if hasattr(cluster, 'provisioning_state'):
                item['properties']['provisioningState'] = cluster.provisioning_state
            if hasattr(cluster, 'kubernetes_version'):
                item['properties']['kubernetesVersion'] = cluster.kubernetes_version
            if hasattr(cluster, 'max_agent_pools'):
                item['properties']['maxAgentPools'] = cluster.max_agent_pools
            if hasattr(cluster, 'dns_prefix'):
                item['properties']['dnsPrefix'] = cluster.dns_prefix
            if hasattr(cluster, 'fqdn'):
                item['properties']['fqdn'] = cluster.fqdn
            if hasattr(cluster, 'agent_pool_profiles'):
                if cluster.agent_pool_profiles is not None:
                    for agent_profile in cluster.agent_pool_profiles:
                        agent_pool = {}
                        if hasattr(agent_profile, 'name'):
                            agent_pool['name'] = agent_profile.name
                        if hasattr(agent_profile, 'count'):
                            agent_pool['count'] = agent_profile.count
                        if hasattr(agent_profile, 'vm_size'):
                            agent_pool['vmSize'] = agent_profile.vm_size
                        if hasattr(agent_profile, 'max_pods'):
                            agent_pool['maxPods'] = agent_profile.max_pods
                        if hasattr(agent_profile, 'os_type'):
                            agent_pool['osType'] = agent_profile.os_type
                        if hasattr(agent_profile, 'provisioning_state'):
                            agent_pool['provisioningState'] = agent_profile.provisioning_state
                        if hasattr(agent_profile, 'orchestrator_version'):
                            agent_pool['orchestratorVersion'] = agent_profile.orchestrator_version
                        item['properties']['agentPoolProfiles'].append(agent_pool)
            if hasattr(cluster, 'network_profile'):
                if cluster.network_profile is not None:
                    if hasattr(cluster.network_profile, 'network_plugin'):
                        item['properties']['networkProfile']['networkPlugin'] = cluster.network_profile.network_plugin
                    if hasattr(cluster.network_profile, 'pod_cidr'):
                        item['properties']['networkProfile']['podCidr'] = cluster.network_profile.pod_cidr
                    if hasattr(cluster.network_profile, 'service_cidr'):
                        item['properties']['networkProfile']['serviceCidr'] = cluster.network_profile.service_cidr
                    if hasattr(cluster.network_profile, 'dns_service_ip'):
                        item['properties']['networkProfile']['dnsServiceIP'] = cluster.network_profile.dns_service_ip
                    if hasattr(cluster.network_profile, 'docker_bridge_cidr'):
                        item['properties']['networkProfile'][
                            'dockerBridgeCidr'] = cluster.network_profile.docker_bridge_cidr

            if hasattr(cluster, 'node_resource_group'):
                item['properties']['nodeResourceGroup'] = cluster.node_resource_group

            if hasattr(cluster, 'linux_profile'):
                if cluster.linux_profile is not None:
                    if hasattr(cluster.linux_profile, 'admin_username'):
                        item['properties']['linuxProfile']['adminUsername'] = cluster.linux_profile.admin_username
                    if hasattr(cluster.linux_profile, 'ssh'):
                        if cluster.linux_profile.ssh is not None:
                            if hasattr(cluster.linux_profile.ssh, 'public_keys'):
                                if cluster.linux_profile.ssh.public_keys is not None:
                                    for publickey in cluster.linux_profile.ssh.public_keys:
                                        ssh_key = {}
                                        ssh_key['keyData'] = publickey.key_data
                                        item['properties']['linuxProfile']['ssh']['publicKeys'].append(ssh_key)

            response = item
        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    def describe_all_clusters(self):
        """
        Describe all the clusters available on the Azure cloud
        :return:
        """
        error = False
        response = None
        try:
            subscription_id = self.azure_subscription_id

            credentials = ServicePrincipalCredentials(
                client_id=self.azure_client_id,
                secret=self.azure_client_secret,
                tenant=self.azure_tenant_id,
            )
            client = ContainerServiceClient(credentials, subscription_id)
            cluster_list = []
            for cluster in client.managed_clusters.list():
                error_cluster_object_to_dict, response_cluster_object_to_dict = self.cluster_object_to_dict(
                    cluster)
                if error_cluster_object_to_dict:
                    raise Exception(response_cluster_object_to_dict)
                else:
                    cluster_list.append(response_cluster_object_to_dict)
            response = cluster_list

        except Exception as e:
            error = True
            response = e.message
        finally:
            return error, response

    # def azure_test(request):
    #
    #     json_request = json.loads(request.body)
    #
    #     username = json_request['username']
    #     password = json_request['password']
    #     resource_group = json_request['resource_group']
    #     resource_name = json_request['resource_name']
    #     file_path = json_request['file_path']
    #
    #     az_login = subprocess.Popen(
    #         ['az', 'login', '-u', '%s' % (username), '-p', '%s' % (password)],
    #         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     output, error = az_login.communicate()
    #
    #     print output
    #     print error
    #
    #     # az aks get - credentials - -resource - group test - resource - group - k8s - -name test1 - -file C:\D_drive\Tathagat\kubeConfig_azure1\config
    #
    #     az_ = subprocess.Popen(
    #         ['az', 'aks', 'get', '--credentials', '--resource-group', '%s' % (resource_group), '--name',
    #          '%s' % (resource_name), '--file' '%s' % (file_path)],
    #         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     output1, error1 = az_login.communicate()
    #
    #     print output1
    #     print error1

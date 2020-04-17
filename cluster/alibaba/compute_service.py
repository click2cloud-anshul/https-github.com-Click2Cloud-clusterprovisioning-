import json

from aliyunsdkcore import client
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkecs.request.v20140526.DescribeInstanceTypesRequest import DescribeInstanceTypesRequest
from aliyunsdkecs.request.v20140526.DescribeKeyPairsRequest import DescribeKeyPairsRequest
from aliyunsdkecs.request.v20140526.DescribeVSwitchesRequest import DescribeVSwitchesRequest
from aliyunsdkecs.request.v20140526.DescribeVpcsRequest import DescribeVpcsRequest
from aliyunsdkecs.request.v20140526.DescribeZonesRequest import DescribeZonesRequest

from cluster.others.miscellaneous_operation import get_instance_details, ALIBABA_CLOUD, \
    insert_or_update_instance_details


class Alibaba_ECS:
    def __init__(self, ali_access_key, ali_secret_key, region_id):
        """
        Constructor for alibaba ecs operation class
        :param ali_access_key:
        :param ali_secret_key:
        :param region_id:
        """
        self.access_key = ali_access_key
        self.secret_key = ali_secret_key
        self.region_id = region_id
        self.retry_counter = 0

    def list_container_service_regions(self):
        """
        list the available regions in the alibaba
        :return:
        """
        try:
            conn = client.AcsClient(
                ak=self.access_key,
                secret=self.secret_key
            )

            request = CommonRequest()
            request.set_accept_format('json')
            request.set_domain('ecs.aliyuncs.com')
            request.set_method('POST')
            request.set_version('2014-05-26')
            request.set_action_name('DescribeRegions')

            regions = conn.do_action_with_exception(request)
            regions = json.loads(regions)
            result = regions.get('Regions')
            region_list = []
            # skip regions {'cn-qingdao', 'cn-huhehaote', 'cn-chengdu'} because container service not supported in
            # these regions
            for region in result.get('Region'):
                if 'cn-qingdao' in str(region.get('RegionId')) or 'cn-huhehaote' in str(
                        region.get('RegionId')) or 'cn-chengdu' in str(region.get('RegionId')):
                    continue
                region_list.append(str(region.get('RegionId')))
            return True, region_list
        except Exception as e:
            return False, e.message

    def list_container_registry_regions(self):
        """
        list the available regions in the alibaba
        :return:
        """
        try:
            conn = client.AcsClient(
                ak=self.access_key,
                secret=self.secret_key
            )

            request = CommonRequest()
            request.set_accept_format('json')
            request.set_domain('ecs.aliyuncs.com')
            request.set_method('POST')
            request.set_version('2014-05-26')
            request.set_action_name('DescribeRegions')

            regions = conn.do_action_with_exception(request)
            regions = json.loads(regions)
            result = regions.get('Regions')
            region_list = []
            # skip regions {'cn-qingdao', 'cn-huhehaote', 'cn-chengdu'} because container service not supported in
            # these regions
            for region in result.get('Region'):
                if 'cn-heyuan' in str(region.get('RegionId')) or 'cn-chengdu' in str(region.get('RegionId')):
                    continue
                region_list.append(str(region.get('RegionId')))
            return True, region_list
        except Exception as e:
            return False, e.message

    def key_pairs_list(self):
        """
        Returns the name list of ssh key pairs available in the Alibaba in a particular region
        :return:
        """
        try:
            conn = client.AcsClient(
                ak=self.access_key,
                secret=self.secret_key,
                region_id=self.region_id,
            )
            request = DescribeKeyPairsRequest()
            request.set_accept_format('json')

            response = conn.do_action_with_exception(request)
            key_pair_response = json.loads(response)

            result = key_pair_response.get('KeyPairs').get('KeyPair')
            key_pair_list = []
            for key_pair in result:
                key_pair_list.append(str(key_pair.get('KeyPairName')))
            return True, key_pair_list
        except Exception as e:
            return False, e.message

    def network_details(self):
        """
        Fetched the network details of the particular region in alibaba
        :return:
        """
        try:
            conn = client.AcsClient(
                ak=self.access_key,
                secret=self.secret_key,
                region_id=self.region_id,
            )
            request = DescribeVpcsRequest()
            request.set_accept_format('json')

            response = conn.do_action_with_exception(request)
            vpc_list_response = json.loads(response)

            result = vpc_list_response.get('Vpcs').get('Vpc')
            vpc_list = []

            vswitch_id_requests = DescribeVSwitchesRequest()
            vswitch_id_requests.set_accept_format('json')

            vswitch_id_response = AcsClient(ak=self.access_key, secret=self.secret_key,
                                            region_id=self.region_id, ).do_action_with_exception(vswitch_id_requests)
            vswitch_id_response = json.loads(vswitch_id_response)
            vswitch_list = []
            vswitch_result = vswitch_id_response.get('VSwitches').get('VSwitch')
            for vswitchId in vswitch_result:
                vswitch_info = {
                    'VSwitchName': str(vswitchId.get('VSwitchName')),
                    'VSwitchId': str(vswitchId.get('VSwitchId')),
                    'ZoneId': str(vswitchId.get('ZoneId')),
                    'VSwitchCidrBlock': str(vswitchId.get('CidrBlock'))
                }
                vswitch_list.append(vswitch_info)

            for vpc in result:
                vswitch_id_list = list(vpc.get('VSwitchIds').get('VSwitchId'))
                string_list = []
                for vswitch_id in vswitch_id_list:
                    for vswitch in vswitch_list:
                        if vswitch.get('VSwitchId') in vswitch_id:
                            string_list.append(vswitch)
                vpc_info = {
                    'VpcName': str(vpc.get('VpcName')),
                    'VpcCidrBlock': str(vpc.get('CidrBlock')),
                    'VpcId': str(vpc.get('VpcId')),
                    'RegionId': str(vpc.get('RegionId')),
                    'Status': str(vpc.get('Status')),
                    'VSwitchIds': string_list
                }
                vpc_list.append(vpc_info)
            return True, vpc_list
        except Exception as e:
            return False, e.message

    def list_instances(self, zone_id):
        """
        list the instances of the zone
        :param zone_id:
        :return:
        """
        error = False
        response = None
        instance_zone_list = []
        instance_size = []
        try:
            client = AcsClient(self.access_key, self.secret_key, self.region_id)

            request = DescribeZonesRequest()
            request.set_accept_format('json')
            response = client.do_action_with_exception(request)
            instance_type_family_list = []
            instance_type_list = []

            if response is not None:
                json_response = json.loads(response)
                zones = json_response.get('Zones')
                if 'Zone' in zones:
                    zone_list = zones.get('Zone')
                    for zone in zone_list:
                        if zone.get('ZoneId') in zone_id:
                            available_instances = zone.get('AvailableInstanceTypes')
                            if 'InstanceTypes' in available_instances:
                                available_instances_types = available_instances.get('InstanceTypes')
                                if available_instances_types is not None:
                                    for instance_type in available_instances_types:
                                        if not instance_type in instance_type_list:
                                            instance_type_list.append(instance_type)

                                        temp = str(instance_type).split(".")
                                        instance_type_family = temp[1]

                                        if not instance_type_family in instance_type_family_list:
                                            instance_type_family_list.append(instance_type_family)
                                        if not temp[2] in instance_size:
                                            instance_size.append(temp[2])
                            instance_list = []
                            for instance_type_family in instance_type_family_list:
                                Instance = []
                                for instance_type in instance_type_list:

                                    if instance_type_family in str(instance_type):
                                        temp = str(instance_type).split(".")
                                        instance_family = temp[1]
                                        if len(instance_type_family) == len(instance_family):
                                            Instance.append(str(instance_type))
                                instance_list.append(
                                    {'instance_type_family': instance_type_family, 'instance_list': Instance})
                            instance_zone_list.append(
                                {'zone_id': zone.get('ZoneId'), 'instance_zone_list': instance_list})
            instance_new_zone_list = []
            for instance_zone in instance_zone_list:
                for instance_type_family_zone in instance_zone.get('instance_zone_list'):
                    instance_type_family = instance_type_family_zone.get('instance_type_family')
                    client = AcsClient(self.access_key, self.secret_key, self.region_id)

                    request = DescribeInstanceTypesRequest()
                    request.set_accept_format('json')

                    request.set_InstanceTypeFamily('ecs.%s' % instance_type_family)

                    response = client.do_action_with_exception(request)
                    instance_new_list = []
                    if response is not None:
                        json_response = json.loads(response)
                        if 'InstanceTypes' in json_response:
                            instances_types_info_from_describe_family = json_response.get('InstanceTypes')
                            instances_types_info_from_describe_family = instances_types_info_from_describe_family.get(
                                'InstanceType')
                            for instances_types_from_describe_family in instances_types_info_from_describe_family:
                                if instances_types_from_describe_family.get(
                                        'InstanceTypeId') in instance_type_family_zone.get('instance_list'):
                                    instance_info = {}
                                    if int(instances_types_from_describe_family.get('CpuCoreCount') > 1) and int(
                                            instances_types_from_describe_family.get('MemorySize')) > 3:
                                        instance_info.update(
                                            {'instance_type': instances_types_from_describe_family.get(
                                                'InstanceTypeId'),
                                                'CpuCoreCount': instances_types_from_describe_family.get(
                                                    'CpuCoreCount'),
                                                'MemorySize': instances_types_from_describe_family.get('MemorySize')})
                                        if len(instance_info) > 0:
                                            instance_new_list.append(instance_info)
                    instance_new_zone_list.append(
                        {'instance_type_family': instance_type_family_zone.get('instance_type_family'),
                         'instance_spec': instance_new_list})
            if len(instance_new_zone_list) is 0:
                raise Exception('No such zones exist.')
            response = instance_new_zone_list
        except Exception as e:
            error = True
            response = e.message
            print e.message
        finally:
            return error, response

    def list_ecs_instances(self, zone_id):
        """
        list the instances of the zone
        :param zone_id:
        :return:
        """
        error = False
        response = None

        try:
            error_get_instance_details, response_get_instance_details = get_instance_details(ALIBABA_CLOUD, zone_id)
            flag = False
            if not error_get_instance_details:
                if len(response_get_instance_details) > 0:
                    response = json.loads(response_get_instance_details)
                    if 'instance_type_list' in response_get_instance_details:
                        response = response.get('instance_type_list')
                    else:
                        flag = True
                else:
                    flag = True
            else:
                raise Exception(response_get_instance_details)
            if flag:
                error_list_instances, response_list_instances = self.list_instances(zone_id)
                if error_list_instances:
                    raise Exception(response_list_instances)
                else:
                    response = response_list_instances
                    params = {
                        'is_insert': True,
                        'zone_id': zone_id,
                        'instance_details': response_list_instances,
                        'provider_name': ALIBABA_CLOUD}
                    error_insert_or_update_instance_details, response_insert_or_update_instance_details = insert_or_update_instance_details(
                        params)
                    if error_insert_or_update_instance_details:
                        raise Exception(response_insert_or_update_instance_details)
        except Exception as e:
            error = True
            response = e.message
            print e.message
        finally:
            return error, response

    def list_zones(self):
        """
        This Function will list all the zones for all the regions of alibaba cloud
        """
        error = False
        response = None
        region_and_zones_list = []
        try:
            is_sucessful, response_list_container_service_regions = self.list_container_service_regions()
            if is_sucessful:
                for region in response_list_container_service_regions:
                    region_and_zones = {}
                    zone_list = []
                    client = AcsClient(self.access_key, self.secret_key, region)
                    request = DescribeZonesRequest()
                    request.set_accept_format('json')
                    response = client.do_action_with_exception(request)
                    if response is not None:
                        json_response = json.loads(response)
                        zones = json_response.get('Zones')
                        if 'Zone' in zones:
                            zone_list_alibaba = zones.get('Zone')
                            for zone in zone_list_alibaba:
                                zone_list.append(zone.get('ZoneId'))
                    region_and_zones.update({"region_id": region, "zone_list": zone_list})
                    region_and_zones_list.append(region_and_zones)
            response = region_and_zones_list
        except Exception as e:
            error = True
            response = e.message
            print e.message
        finally:
            return error, response

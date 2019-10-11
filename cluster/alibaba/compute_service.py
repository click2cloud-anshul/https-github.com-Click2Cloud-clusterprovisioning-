import json

from aliyunsdkcore import client
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkecs.request.v20140526.DescribeKeyPairsRequest import DescribeKeyPairsRequest
from aliyunsdkecs.request.v20140526.DescribeVSwitchesRequest import DescribeVSwitchesRequest
from aliyunsdkecs.request.v20140526.DescribeVpcsRequest import DescribeVpcsRequest


class Alibaba_ECS:
    def __init__(self, ali_access_key, ali_secret_key, region_id):
        """

        :param ali_access_key:
        :param ali_secret_key:
        :param region_id:
        """
        self.access_key = ali_access_key
        self.secret_key = ali_secret_key
        self.region_id = region_id
        self.retry_counter = 0

    # def instance_list(self, zone_id_list):
    #     instance_zone_list = []
    #     instance_size = []
    #     try:
    #         client = AcsClient(self.access_key, self.secret_key, self.region_id)
    #
    #         request = DescribeZonesRequest()
    #         request.set_accept_format('json')
    #         response = client.do_action_with_exception(request)
    #         instance_type_family_list = []
    #         instance_type_list = []
    #
    #         if response is not None:
    #             json_response = json.loads(response)
    #             zone_list = json_response['Zones']['Zone']
    #             request_zone_list = []
    #             for zone in zone_id_list:
    #                 request_zone_list.append(zone['zone_id'])
    #             for zone in zone_list:
    #                 if zone['ZoneId'] in request_zone_list:
    #                     available_instances_types = zone['AvailableInstanceTypes']['InstanceTypes']
    #                     if available_instances_types is not None:
    #                         for instance_type in available_instances_types:
    #                             if not instance_type_list.__contains__(instance_type):
    #                                 instance_type_list.append(instance_type)
    #
    #                             temp = str(instance_type).split(".")
    #                             instance_type_family = temp[1]
    #
    #                             if not instance_type_family_list.__contains__(instance_type_family):
    #                                 instance_type_family_list.append(instance_type_family)
    #                             # else:
    #                             if not instance_size.__contains__(temp[2]):
    #                                 instance_size.append(temp[2])
    #
    #                     instance_list = []
    #                     for instance_type_family in instance_type_family_list:
    #                         Instance = []
    #                         for instance_type in instance_type_list:
    #
    #                             if str(instance_type).__contains__(instance_type_family):
    #                                 temp = str(instance_type).split(".")
    #                                 instance_family = temp[1]
    #                                 if len(instance_type_family) == len(instance_family):
    #                                     Instance.append(str(instance_type))
    #                         # instance_list.update({instance_type_family: str(Instance)})
    #                         instance_list.append(
    #                             {"instance_type_family": instance_type_family, "instance_list": Instance})
    #                     # instance_zone_list.update({zone['ZoneId']: instance_list})
    #                     instance_zone_list.append({"zone_id": zone['ZoneId'], "instance_zone_list": instance_list})
    #         # print instance_zone_list
    #         instance_new_zone_list = []
    #         for instance_zone in instance_zone_list:
    #             instance_info_list = []
    #             for instance_type_family_zone in instance_zone['instance_zone_list']:
    #                 instance_type_family = instance_type_family_zone['instance_type_family']
    #                 client = AcsClient(self.access_key, self.secret_key, self.region_id)
    #
    #                 request = DescribeInstanceTypesRequest()
    #                 request.set_accept_format('json')
    #
    #                 request.set_InstanceTypeFamily("ecs." + instance_type_family)
    #
    #                 response = client.do_action_with_exception(request)
    #                 instance_new_list = []
    #                 if response is not None:
    #                     json_response = json.loads(response)
    #                     if 'InstanceTypes' in json_response:
    #                         instances_types_info_from_describe_family = json_response['InstanceTypes']
    #                         instances_types_info_from_describe_family = instances_types_info_from_describe_family[
    #                             'InstanceType']
    #                         for instances_types_from_describe_family in instances_types_info_from_describe_family:
    #                             if instances_types_from_describe_family['InstanceTypeId'] in instance_type_family_zone[
    #                                 'instance_list']:
    #                                 instance_info = {}
    #                                 if int(instances_types_from_describe_family['CpuCoreCount'] > 1) and int(
    #                                         instances_types_from_describe_family['MemorySize']) > 3:
    #                                     instance_info.update(
    #                                         {"instance_type": instances_types_from_describe_family['InstanceTypeId'],
    #                                          "CpuCoreCount": instances_types_from_describe_family['CpuCoreCount'],
    #                                          "MemorySize": instances_types_from_describe_family['MemorySize']})
    #                                     if len(instance_info) > 0:
    #                                         instance_new_list.append(instance_info)
    #
    #                 instance_info_list.append(
    #                     {"instance_type_family": instance_type_family_zone['instance_type_family'],
    #                      "instance_info_list": instance_new_list})
    #             instance_new_zone_list.append(
    #                 {"zone_id": instance_zone['zone_id'], "instance_info_list": instance_info_list})
    #         if len(instance_new_zone_list) is 0:
    #             return False, 'No such zones exist.'
    #         return True, instance_new_zone_list
    #     except Exception as e:
    #         return False, e.args[0]

    def list_regions(self):
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
            # skip regions {"cn-qingdao", "cn-huhehaote", "cn-chengdu"} because container service not supported in
            # these regions
            for region in result.get('Region'):
                if 'cn-qingdao' in str(region.get('RegionId')) or 'cn-huhehaote' in str(
                        region.get('RegionId')) or 'cn-chengdu' in str(region.get('RegionId')):
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

            result = key_pair_response.get("KeyPairs").get("KeyPair")
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

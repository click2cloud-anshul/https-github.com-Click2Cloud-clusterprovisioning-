# !/usr/bin/env python
# coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526.DescribeKeyPairsRequest import DescribeKeyPairsRequest
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeVpcsRequest
import json
from aliyunsdkcore.request import CommonRequest
from aliyunsdkecs.request.v20140526.DescribeVpcsRequest import DescribeVpcsRequest
from aliyunsdkecs.request.v20140526.DescribeVSwitchesRequest import DescribeVSwitchesRequest
from aliyunsdkecs.request.v20140526.DescribeZonesRequest import DescribeZonesRequest
from aliyunsdkecs.request.v20140526.DescribeInstanceTypesRequest import DescribeInstanceTypesRequest


class Alibaba_ECS:

    def __init__(self, ali_access_key, ali_secret_key, region_id):
        """
        :param ali_access_key: access key of alibaba
        :param ali_secret_key: secret key of alibaba
        :param ali_ecs_endpoint: alibaba ecs endpoint
        :param ali_oss_endpoint: alibaba oss endpoint
        :param ali_region_id: alibaba region id
        :param ali_bucket_name: alibaba bucket name
        :param ali_object_name: alibaba object name
        """
        self.access_key = ali_access_key
        self.secret_key = ali_secret_key
        self.region_id = region_id
        self.retry_counter = 0

    def instance_list(self, zone_id_list):
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
                zone_list = json_response['Zones']['Zone']
                request_zone_list = []
                for zone in zone_id_list:
                    request_zone_list.append(zone['zone_id'])
                for zone in zone_list:
                    if zone['ZoneId'] in request_zone_list:
                        available_instances_types = zone['AvailableInstanceTypes']['InstanceTypes']
                        if available_instances_types is not None:
                            for instance_type in available_instances_types:
                                if not instance_type_list.__contains__(instance_type):
                                    instance_type_list.append(instance_type)

                                temp = str(instance_type).split(".")
                                instance_type_family = temp[1]

                                if not instance_type_family_list.__contains__(instance_type_family):
                                    instance_type_family_list.append(instance_type_family)
                                # else:
                                if not instance_size.__contains__(temp[2]):
                                    instance_size.append(temp[2])

                        instance_list = []
                        for instance_type_family in instance_type_family_list:
                            Instance = []
                            for instance_type in instance_type_list:

                                if str(instance_type).__contains__(instance_type_family):
                                    temp = str(instance_type).split(".")
                                    instance_family = temp[1]
                                    if len(instance_type_family) == len(instance_family):
                                        Instance.append(str(instance_type))
                            # instance_list.update({instance_type_family: str(Instance)})
                            instance_list.append({"instance_type_family": instance_type_family, "instance_list": Instance})
                        # instance_zone_list.update({zone['ZoneId']: instance_list})
                        instance_zone_list.append({"zone_id": zone['ZoneId'], "instance_zone_list": instance_list})
            # print instance_zone_list
            instance_new_zone_list = []
            for instance_zone in instance_zone_list:
                instance_info_list = []
                for instance_type_family_zone in instance_zone['instance_zone_list']:
                    instance_type_family = instance_type_family_zone['instance_type_family']
                    client = AcsClient(self.access_key, self.secret_key, self.region_id)

                    request = DescribeInstanceTypesRequest()
                    request.set_accept_format('json')

                    request.set_InstanceTypeFamily("ecs." + instance_type_family)

                    response = client.do_action_with_exception(request)
                    instance_new_list = []
                    if response is not None:
                        json_response = json.loads(response)
                        if 'InstanceTypes' in json_response:
                            instances_types_info_from_describe_family = json_response['InstanceTypes']
                            instances_types_info_from_describe_family = instances_types_info_from_describe_family[
                                'InstanceType']
                            for instances_types_from_describe_family in instances_types_info_from_describe_family:
                                if instances_types_from_describe_family['InstanceTypeId'] in instance_type_family_zone[
                                    'instance_list']:
                                    instance_info = {}
                                    if int(instances_types_from_describe_family['CpuCoreCount'] > 1) and int(
                                            instances_types_from_describe_family['MemorySize']) > 3:
                                        instance_info.update(
                                            {"instance_type": instances_types_from_describe_family['InstanceTypeId'],
                                             "CpuCoreCount": instances_types_from_describe_family['CpuCoreCount'],
                                             "MemorySize": instances_types_from_describe_family['MemorySize']})
                                        if len(instance_info) > 0:
                                            instance_new_list.append(instance_info)

                    instance_info_list.append(
                        {"instance_type_family": instance_type_family_zone['instance_type_family'],
                         "instance_info_list": instance_new_list})
                instance_new_zone_list.append(
                    {"zone_id": instance_zone['zone_id'], "instance_info_list": instance_info_list})
            return True, instance_new_zone_list
        except Exception as e:
            return False, e.message

    def list_regions(self):
        """
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
            result = regions["Regions"]
            region_list = []
            # {"cn-qingdao", "cn-huhehaote", "cn-chengdu"}
            for region in result["Region"]:
                if "cn-qingdao" in str(region['RegionId']) or "cn-huhehaote" in str(
                        region['RegionId']) or "cn-chengdu" in str(region['RegionId']):
                    continue
                region_list.append(str(region['RegionId']))
            return True, region_list
        except Exception as e:
            return False, e.message

    def key_pairs_list(self):
        """
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

            result = key_pair_response["KeyPairs"]["KeyPair"]
            key_pair_list = []
            for key_pair in result:
                key_pair_list.append(str(key_pair['KeyPairName']))
            return True, key_pair_list
        except Exception as e:
            return False, e.message

    def vpc_list(self):
        """
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

            result = vpc_list_response["Vpcs"]["Vpc"]
            vpc_list = []

            vswitch_id_requests = DescribeVSwitchesRequest()
            vswitch_id_requests.set_accept_format('json')

            vswitch_id_response = AcsClient(ak=self.access_key, secret=self.secret_key,
                                            region_id=self.region_id, ).do_action_with_exception(vswitch_id_requests)
            vswitch_id_response = json.loads(vswitch_id_response)
            vswitch_list = []
            var = vswitch_id_response["VSwitches"]["VSwitch"]
            for vswitchId in var:
                vswitch_info = {
                    "VSwitchName": str(vswitchId['VSwitchName']),
                    "VSwitchId": str(vswitchId['VSwitchId']),
                    "ZoneId": str(vswitchId['ZoneId']),
                    "VSwitchCidrBlock": str(vswitchId['CidrBlock'])
                }
                vswitch_list.append(vswitch_info)

            for vpc in result:
                vswitch_id_list = list(vpc['VSwitchIds']["VSwitchId"])
                string_list = []
                for vswitch_id in vswitch_id_list:
                    for vswitch in vswitch_list:
                        if vswitch["VSwitchId"] in vswitch_id:
                            string_list.append(vswitch)
                vpc_info = {
                    "VpcName": str(vpc['VpcName']),
                    "VpcCidrBlock": str(vpc['CidrBlock']),
                    "VpcId": str(vpc['VpcId']),
                    "RegionId": str(vpc['RegionId']),
                    "Status": str(vpc['Status']),
                    "VSwitchIds": string_list
                }
                vpc_list.append(vpc_info)
            return True, vpc_list
        except Exception as e:
            return False, e.message

    # def instance_type_list(self):
    #     try:
    #         instance_type_list = {}
    #         conn = client.AcsClient(
    #             ak=self.access_key,
    #             secret=self.secret_key,
    #             region_id=self.region_id,
    #         )
    #
    #
    #         return True
    #     except Exception as e:
    #         return False, e.message

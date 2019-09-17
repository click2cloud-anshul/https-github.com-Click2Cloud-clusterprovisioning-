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

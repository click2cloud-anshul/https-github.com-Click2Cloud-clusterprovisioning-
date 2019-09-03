package ali

import (
	"encoding/json"
	"github.com/Click2Cloud/clusterprovisioning"
	"github.com/Click2Cloud/clusterprovisioning/utils"
	"github.com/aliyun/alibaba-cloud-sdk-go/services/ecs"
	"net/http"
)

func GetVPCList(httpResponse http.ResponseWriter, httpRequest *http.Request) {

	accessKeyId := httpRequest.Header.Get("accessKeyId")
	accessKeySecret := httpRequest.Header.Get("accessKeySecret")
	regionId := httpRequest.Header.Get("regionId")

	if len(accessKeyId) == 0 {
		utils.Respond(httpResponse, utils.Message(false, "accessKeyId not found"), http.StatusBadRequest)
		return
	}

	if len(accessKeySecret) == 0 {
		utils.Respond(httpResponse, utils.Message(false, "accessKeySecret not found"), http.StatusBadRequest)
		return
	}
	if len(regionId) == 0 {
		utils.Respond(httpResponse, utils.Message(false, "regionId not found"), http.StatusBadRequest)
		return
	}

	client, err := ecs.NewClientWithAccessKey(regionId, accessKeyId, accessKeySecret)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}
	request := ecs.CreateDescribeVpcsRequest()
	request.Scheme = "https"

	response, err := client.DescribeVpcs(request)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}
	var VPCList []string
	for _, vpc := range response.Vpcs.Vpc {
		VPCList = append(VPCList, vpc.VpcName)
	}
	httpResponse.Header().Add("Content-Type", "application/json")
	byteArray, err := json.Marshal(VPCList)
	_, err = httpResponse.Write(byteArray)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, "Internal Server Error"), http.StatusInternalServerError)
		return
	}
	return
}

//func GetInstances(httpResponse http.ResponseWriter, httpRequest *http.Request) {
//
//}

func GetKeyPairList(httpResponse http.ResponseWriter, httpRequest *http.Request) {
	accessKeyId := httpRequest.Header.Get("accessKeyId")
	accessKeySecret := httpRequest.Header.Get("accessKeySecret")
	regionId := httpRequest.Header.Get("regionId")

	if len(accessKeyId) == 0 {
		utils.Respond(httpResponse, utils.Message(false, "accessKeyId not found"), http.StatusBadRequest)
		return
	}

	if len(accessKeySecret) == 0 {
		utils.Respond(httpResponse, utils.Message(false, "accessKeySecret not found"), http.StatusBadRequest)
		return
	}
	if len(regionId) == 0 {
		utils.Respond(httpResponse, utils.Message(false, "regionId not found"), http.StatusBadRequest)
		return
	}

	client, err := ecs.NewClientWithAccessKey(regionId, accessKeyId, accessKeySecret)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}
	request := ecs.CreateDescribeKeyPairsRequest()
	request.Scheme = "https"

	response, err := client.DescribeKeyPairs(request)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}
	var keyPairList []string
	keyPairs := response.KeyPairs.KeyPair
	for _, keyPair := range keyPairs {
		keyPairList = append(keyPairList, keyPair.KeyPairName)
	}
	httpResponse.Header().Add("Content-Type", "application/json")
	byteArray, err := json.Marshal(keyPairList)
	_, err = httpResponse.Write(byteArray)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, "Internal Server Error"), http.StatusInternalServerError)
		return
	}
	return
}

func GetRegionList(httpResponse http.ResponseWriter, httpRequest *http.Request) {
	accessKeyId := httpRequest.Header.Get("accessKeyId")
	accessKeySecret := httpRequest.Header.Get("accessKeySecret")

	if len(accessKeyId) == 0 {
		utils.Respond(httpResponse, utils.Message(false, "accessKeyId not found"), http.StatusBadRequest)
		return
	}

	if len(accessKeySecret) == 0 {
		utils.Respond(httpResponse, utils.Message(false, "accessKeySecret not found"), http.StatusBadRequest)
		return
	}

	client, err := ecs.NewClientWithAccessKey("default", accessKeyId, accessKeySecret)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}
	request := ecs.CreateDescribeRegionsRequest()
	request.Scheme = "https"
	request.ConnectTimeout = 10
	request.ReadTimeout = 10
	response, err := client.DescribeRegions(request)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}
	var regionList clusterprovisioning.RegionList
	for _, region := range response.Regions.Region {
		regionId := region.RegionId
		regionList.RegionId = append(regionList.RegionId, regionId)
	}
	httpResponse.Header().Add("Content-Type", "application/json")
	byteArray, err := json.Marshal(regionList)
	_, err = httpResponse.Write(byteArray)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, "Internal Server Error"), http.StatusInternalServerError)
		return
	}
	return
}

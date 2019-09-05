package ali

import (
	"encoding/json"
	"fmt"
	"github.com/Click2Cloud/clusterprovisioning"
	"github.com/Click2Cloud/clusterprovisioning/utils"
	"github.com/aliyun/alibaba-cloud-sdk-go/services/ecs"
	"net/http"
	"strings"
)

func GetVPCList(httpResponse http.ResponseWriter, httpRequest *http.Request) {
	var resp map[string]interface{}
	accessKeyId := httpRequest.Header.Get("accessKeyId")
	accessKeySecret := httpRequest.Header.Get("accessKeySecret")
	regionId := httpRequest.Header.Get("regionId")
	if len(accessKeyId) == 0 {
		resp = utils.Message(false)
		resp["error"] = "accessKeyId not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}
	if len(accessKeySecret) == 0 {
		resp = utils.Message(false)
		resp["error"] = "accessKeySecret not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}
	if len(regionId) == 0 {
		resp = utils.Message(false)
		resp["error"] = "regionId not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}

	client, err := ecs.NewClientWithAccessKey(regionId, accessKeyId, accessKeySecret)
	if err != nil {
		str := err.Error()
		if strings.Contains(str, "ConnectTimeout") {
			resp = utils.Message(false)
			resp["error"] = "Connection Timeout Issue"
			utils.Respond(httpResponse, resp, http.StatusRequestTimeout)
			return
		}
		if strings.Contains(str, "Message") {
			splitedString := strings.Split(str, "Message:")
			trim := strings.Trim(splitedString[1], " ")
			jsonString := strings.Replace(trim, "\\", "", -1)
			var raw map[string]interface{}
			err := json.Unmarshal([]byte(jsonString), &raw)
			if err != nil {
				resp = utils.Message(false)
				resp["error"] = "Internal Server Error"
				utils.Respond(httpResponse, resp, http.StatusInternalServerError)
				return
			}
			resp = utils.Message(false)
			resp["error"] = fmt.Sprintf("%v", raw["message"])
			utils.Respond(httpResponse, resp, http.StatusBadRequest)
			return
		}
	}
	request := ecs.CreateDescribeVpcsRequest()
	request.Scheme = "https"

	response, err := client.DescribeVpcs(request)
	if err != nil {
		str := err.Error()
		if strings.Contains(str, "ConnectTimeout") {
			resp = utils.Message(false)
			resp["error"] = "Connection Timeout Issue"
			utils.Respond(httpResponse, resp, http.StatusRequestTimeout)
			return
		}
		if strings.Contains(str, "Message") {
			splitedString := strings.Split(str, "Message:")
			trim := strings.Trim(splitedString[1], " ")
			jsonString := strings.Replace(trim, "\\", "", -1)
			var raw map[string]interface{}
			err := json.Unmarshal([]byte(jsonString), &raw)
			if err != nil {
				resp = utils.Message(false)
				resp["error"] = "Internal Server Error"
				utils.Respond(httpResponse, resp, http.StatusInternalServerError)
				return
			}
			resp = utils.Message(false)
			resp["error"] = fmt.Sprintf("%v", raw["message"])
			utils.Respond(httpResponse, resp, http.StatusBadRequest)
			return
		}
	}
	var regionWithVpc clusterprovisioning.RegionWithVPCList

	for _, vpc := range response.Vpcs.Vpc {
		var vpcCP clusterprovisioning.Vpcs
		vpcCP.VpcName = vpc.VpcName
		vpcCP.RegionId = vpc.RegionId
		vpcCP.Status = vpc.Status
		vpcCP.VpcId = vpc.VpcId
		vpcCP.CidrBlock = vpc.CidrBlock
		for _, vSwitch := range vpc.VSwitchIds.VSwitchId {
			vpcCP.VSwitchIds.VSwitchId = append(vpcCP.VSwitchIds.VSwitchId, vSwitch)
		}
		regionWithVpc.Vpcs = append(regionWithVpc.Vpcs, vpcCP)
	}
	resp = utils.Message(true)
	resp["vpcList"] = regionWithVpc
	utils.Respond(httpResponse, resp, http.StatusOK)
	return
}

func GetInstances(httpResponse http.ResponseWriter, httpRequest *http.Request) {

	accessKeyId := httpRequest.Header.Get("accessKeyId")
	accessKeySecret := httpRequest.Header.Get("accessKeySecret")
	var resp map[string]interface{}
	if len(accessKeyId) == 0 {
		resp = utils.Message(false)
		resp["error"] = "accessKeyId not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}

	if len(accessKeySecret) == 0 {
		resp = utils.Message(false)
		resp["error"] = "accessKeySecret not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}

}

func GetKeyPairList(httpResponse http.ResponseWriter, httpRequest *http.Request) {
	var resp map[string]interface{}
	accessKeyId := httpRequest.Header.Get("accessKeyId")
	accessKeySecret := httpRequest.Header.Get("accessKeySecret")
	regionId := httpRequest.Header.Get("regionId")

	if len(accessKeyId) == 0 {
		resp = utils.Message(false)
		resp["error"] = "accessKeyId not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}

	if len(accessKeySecret) == 0 {
		resp = utils.Message(false)
		resp["error"] = "accessKeySecret not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}
	if len(regionId) == 0 {
		resp = utils.Message(false)
		resp["error"] = "regionId not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}

	client, err := ecs.NewClientWithAccessKey(regionId, accessKeyId, accessKeySecret)
	if err != nil {
		str := err.Error()
		if strings.Contains(str, "ConnectTimeout") {
			resp = utils.Message(false)
			resp["error"] = "Connection Timeout Issue"
			utils.Respond(httpResponse, resp, http.StatusRequestTimeout)
			return
		}
		if strings.Contains(str, "Message") {
			splitedString := strings.Split(str, "Message:")
			trim := strings.Trim(splitedString[1], " ")
			jsonString := strings.Replace(trim, "\\", "", -1)
			var raw map[string]interface{}
			err := json.Unmarshal([]byte(jsonString), &raw)
			if err != nil {
				resp = utils.Message(false)
				resp["error"] = "Internal Server Error"
				utils.Respond(httpResponse, resp, http.StatusInternalServerError)
				return
			}
			resp = utils.Message(false)
			resp["error"] = fmt.Sprintf("%v", raw["message"])
			utils.Respond(httpResponse, resp, http.StatusBadRequest)
			return
		}
	}
	request := ecs.CreateDescribeKeyPairsRequest()
	request.Scheme = "https"
	response, err := client.DescribeKeyPairs(request)
	if err != nil {
		str := err.Error()
		if strings.Contains(str, "ConnectTimeout") {
			resp = utils.Message(false)
			resp["error"] = "Connection Timeout Issue"
			utils.Respond(httpResponse, resp, http.StatusRequestTimeout)
			return
		}
		if strings.Contains(str, "Message") {
			splitedString := strings.Split(str, "Message:")
			trim := strings.Trim(splitedString[1], " ")
			jsonString := strings.Replace(trim, "\\", "", -1)
			var raw map[string]interface{}
			err := json.Unmarshal([]byte(jsonString), &raw)
			if err != nil {
				resp = utils.Message(false)
				resp["error"] = "Internal Server Error"
				utils.Respond(httpResponse, resp, http.StatusInternalServerError)
				return
			}
			resp = utils.Message(false)
			resp["error"] = fmt.Sprintf("%v", raw["message"])
			utils.Respond(httpResponse, resp, http.StatusBadRequest)
			return
		}
	}
	var keyPairList []string
	keyPairs := response.KeyPairs.KeyPair
	for _, keyPair := range keyPairs {
		keyPairList = append(keyPairList, keyPair.KeyPairName)
	}
	resp = utils.Message(true)
	resp["keyPairList"] = keyPairList
	utils.Respond(httpResponse, resp, http.StatusOK)
	return
}

func GetRegionList(httpResponse http.ResponseWriter, httpRequest *http.Request) {
	var resp map[string]interface{}
	accessKeyId := httpRequest.Header.Get("accessKeyId")
	accessKeySecret := httpRequest.Header.Get("accessKeySecret")

	if len(accessKeyId) == 0 {
		resp = utils.Message(false)
		resp["error"] = "accessKeyId not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}
	if len(accessKeySecret) == 0 {
		resp = utils.Message(false)
		resp["error"] = "accessKeySecret not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}

	client, err := ecs.NewClientWithAccessKey("cn-beijing", accessKeyId, accessKeySecret)
	if err != nil {
		str := err.Error()
		if strings.Contains(str, "ConnectTimeout") {
			resp = utils.Message(false)
			resp["error"] = "Connection Timeout Issue"
			utils.Respond(httpResponse, resp, http.StatusRequestTimeout)
			return
		}
		if strings.Contains(str, "Message") {
			splitedString := strings.Split(str, "Message:")
			trim := strings.Trim(splitedString[1], " ")
			jsonString := strings.Replace(trim, "\\", "", -1)
			var raw map[string]interface{}
			err := json.Unmarshal([]byte(jsonString), &raw)
			if err != nil {
				resp = utils.Message(false)
				resp["error"] = "Internal Server Error"
				utils.Respond(httpResponse, resp, http.StatusInternalServerError)
				return
			}
			resp = utils.Message(false)
			resp["error"] = fmt.Sprintf("%v", raw["message"])
			utils.Respond(httpResponse, resp, http.StatusBadRequest)
			return
		}
	}
	request := ecs.CreateDescribeRegionsRequest()
	request.Scheme = "https"
	response, err := client.DescribeRegions(request)
	if err != nil {
		str := err.Error()
		if strings.Contains(str, "ConnectTimeout") {
			resp = utils.Message(false)
			resp["error"] = "Connection Timeout Issue"
			utils.Respond(httpResponse, resp, http.StatusRequestTimeout)
			return
		}
		if strings.Contains(str, "Message") {
			splitedString := strings.Split(str, "Message:")
			trim := strings.Trim(splitedString[1], " ")
			jsonString := strings.Replace(trim, "\\", "", -1)
			var raw map[string]interface{}
			err := json.Unmarshal([]byte(jsonString), &raw)
			if err != nil {
				resp = utils.Message(false)
				resp["error"] = "Internal Server Error"
				utils.Respond(httpResponse, resp, http.StatusInternalServerError)
				return
			}
			resp = utils.Message(false)
			resp["error"] = fmt.Sprintf("%v", raw["message"])
			utils.Respond(httpResponse, resp, http.StatusBadRequest)
			return
		}
	}

	avoidClusterCreationRegion := []string{"cn-qingdao", "cn-huhehaote", "cn-chengdu"}
	var regionList clusterprovisioning.RegionList
	for _, region := range response.Regions.Region {
		regionId := region.RegionId
		if utils.Contains(avoidClusterCreationRegion, regionId) {
			continue
		}
		regionList.RegionId = append(regionList.RegionId, regionId)
	}
	resp = utils.Message(true)
	resp["regionList"] = regionList
	utils.Respond(httpResponse, resp, http.StatusOK)
	return
}

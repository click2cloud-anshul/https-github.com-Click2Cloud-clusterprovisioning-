package ali

import (
	"encoding/json"
	"fmt"
	"github.com/Click2Cloud/clusterprovisioning"
	"github.com/Click2Cloud/clusterprovisioning/utils"
	"github.com/aliyun/alibaba-cloud-sdk-go/sdk"
	"github.com/aliyun/alibaba-cloud-sdk-go/sdk/requests"
	"github.com/aliyun/alibaba-cloud-sdk-go/services/cs"
	"github.com/aliyun/alibaba-cloud-sdk-go/services/ros"
	"io/ioutil"
	"net/http"
	"strings"
)

func CreateKubernetesCluster(httpResponse http.ResponseWriter, httpRequest *http.Request) {

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

	client, err := sdk.NewClientWithAccessKey("default", accessKeyId, accessKeySecret)
	if err != nil {
		panic(err)
	}

	request := requests.NewCommonRequest()
	request.Method = "POST"
	request.Scheme = "https" // https | http
	request.Domain = "cs.aliyuncs.com"
	request.Version = "2015-12-15"
	request.PathPattern = "/clusters"
	request.Headers["Content-Type"] = "application/json"
	request.QueryParams["RegionId"] = "default"

	body, err := ioutil.ReadAll(httpRequest.Body)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, "can't read body"), http.StatusBadRequest)
		return
	}
	request.Content = body

	response, err := client.ProcessCommonRequest(request)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}

	contentStringResponse := response.GetHttpContentString()
	httpResponse.Header().Add("Content-Type", "application/json")
	_, err = httpResponse.Write([]byte(contentStringResponse))
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, "Internal Server Error"), http.StatusInternalServerError)
		return
	}
	return
}

func GetClusterConfig(httpResponse http.ResponseWriter, httpRequest *http.Request) {

	clusterId := httpRequest.Header.Get("clusterId")
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
	if len(clusterId) == 0 {
		utils.Respond(httpResponse, utils.Message(false, "clusterId not found"), http.StatusBadRequest)
		return
	}

	client, err := sdk.NewClientWithAccessKey("default", accessKeyId, accessKeySecret)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}

	request := requests.NewCommonRequest()
	request.Method = "GET"
	request.Scheme = "https" // https | http
	request.Domain = "cs.aliyuncs.com"
	request.Version = "2015-12-15"
	request.PathPattern = "/api/v2/k8s/" + clusterId + "/user_config"
	request.Headers["Content-Type"] = "application/json"
	request.QueryParams["RegionId"] = "default"
	request.QueryParams["PrivateIpAddress"] = ""
	body := ``
	request.Content = []byte(body)

	cs.CreateDescribeClusterUserKubeconfigRequest()
	response, err := client.ProcessCommonRequest(request)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}
	str := response.GetHttpContentString()
	var raw map[string]interface{}
	err = json.Unmarshal([]byte(str), &raw)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, "Internal Server Error"), http.StatusInternalServerError)
		return
	}
	config := raw["config"]
	configString := fmt.Sprintf("%v", config)
	httpResponse.Header().Add("Content-Type", "application/json")
	_, err = httpResponse.Write([]byte(configString))
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, "Internal Server Error"), http.StatusInternalServerError)
		return
	}
	return
}

func GetClusterStatus(httpResponse http.ResponseWriter, httpRequest *http.Request) {
	clusterId := httpRequest.Header.Get("clusterId")
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
	if len(clusterId) == 0 {
		utils.Respond(httpResponse, utils.Message(false, "clusterId not found"), http.StatusBadRequest)
		return
	}

	client, err := sdk.NewClientWithAccessKey("default", accessKeyId, accessKeySecret)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}

	request := requests.NewCommonRequest()
	request.Method = "GET"
	request.Scheme = "https" // https | http
	request.Domain = "cs.aliyuncs.com"
	request.Version = "2015-12-15"
	request.PathPattern = "/clusters/" + clusterId
	request.Headers["Content-Type"] = "application/json"
	request.QueryParams["RegionId"] = "default"
	request.QueryParams["Name"] = ""
	request.QueryParams["clusterType"] = ""
	body := ``
	request.Content = []byte(body)

	response, err := client.ProcessCommonRequest(request)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}
	contentStringResponse := response.GetHttpContentString()
	var clusterDetail clusterprovisioning.ClusterDetail
	err = json.Unmarshal([]byte(contentStringResponse), &clusterDetail)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, "Internal Server Error"), http.StatusInternalServerError)
		return
	}

	if len(clusterDetail.ErrMsg) == 0 {

		client2, err := ros.NewClientWithAccessKey(clusterDetail.RegionID, accessKeyId, accessKeySecret)
		if err != nil {
			utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
			return
		}
		request := ros.CreateGetStackRequest()
		request.Scheme = "https"
		request.StackId = clusterDetail.Parameters.ALIYUNStackID
		var response, _ = client2.GetStack(request)
		contentString := response.GetHttpContentString()
		httpResponse.Header().Add("Content-Type", "application/json")

		_, err = httpResponse.Write([]byte(contentString))
		if err != nil {
			utils.Respond(httpResponse, utils.Message(false, "Internal Server Error"), http.StatusInternalServerError)
			return
		}
		return

	} else {
		httpResponse.Header().Add("Content-Type", "application/json")
		_, err = httpResponse.Write([]byte(contentStringResponse))
		if err != nil {
			utils.Respond(httpResponse, utils.Message(false, "Internal Server Error"), http.StatusInternalServerError)
			return
		}
		return
	}

}

func GetAllClusters(httpResponse http.ResponseWriter, httpRequest *http.Request) {

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

	client, err := sdk.NewClientWithAccessKey("default", accessKeyId, accessKeySecret)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}

	request := requests.NewCommonRequest()
	request.Method = "GET"
	request.Scheme = "https" // https | http
	request.Domain = "cs.aliyuncs.com"
	request.Version = "2015-12-15"
	request.PathPattern = "/clusters"
	request.Headers["Content-Type"] = "application/json"
	request.QueryParams["RegionId"] = "default"
	request.QueryParams["Name"] = ""
	request.QueryParams["clusterType"] = ""
	body := ``
	request.Content = []byte(body)

	response, err := client.ProcessCommonRequest(request)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}
	contentStringResponse := response.GetHttpContentString()

	httpResponse.Header().Add("Content-Type", "application/json")
	_, err = httpResponse.Write([]byte(contentStringResponse))
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, "Internal Server Error"), http.StatusInternalServerError)
		return
	}
	return
}

func DeleteCluster(httpResponse http.ResponseWriter, httpRequest *http.Request) {

	clusterId := httpRequest.Header.Get("clusterId")
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
	if len(clusterId) == 0 {
		utils.Respond(httpResponse, utils.Message(false, "clusterId not found"), http.StatusBadRequest)
		return
	}

	client, err := sdk.NewClientWithAccessKey("default", accessKeyId, accessKeySecret)
	if err != nil {
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}

	request := requests.NewCommonRequest()
	request.Method = "DELETE"
	request.Scheme = "https" // https | http
	request.Domain = "cs.aliyuncs.com"
	request.Version = "2015-12-15"
	request.PathPattern = "/clusters/" + clusterId
	request.Headers["Content-Type"] = "application/json"
	request.QueryParams["RegionId"] = "default"
	body := ``
	request.Content = []byte(body)

	response, err := client.ProcessCommonRequest(request)
	if err != nil {
		str := err.Error()
		if strings.Contains(str, "cluster") {
			splitedString := strings.Split(str, "cluster")
			for _, split := range splitedString {
				if strings.Contains(split, ", Error code:") {
					splitedString2 := strings.Split(split, ", Error code:")
					utils.Respond(httpResponse, utils.Message(false, "Cluster"+splitedString2[0]), http.StatusBadRequest)
					return
				}
			}
		}
		utils.Respond(httpResponse, utils.Message(false, err.Error()), http.StatusBadRequest)
		return
	}

	contentStringResponse := response.GetHttpContentString()

	if len(contentStringResponse) == 0 {
		httpResponse.Header().Add("Content-Type", "application/json")
		_, err = httpResponse.Write([]byte(contentStringResponse))
		if err != nil {
			utils.Respond(httpResponse, utils.Message(true, "Delete Successful"), http.StatusAccepted)
			return
		}
	} else {
		httpResponse.Header().Add("Content-Type", "application/json")
		utils.Respond(httpResponse, utils.Message(false, contentStringResponse), http.StatusInternalServerError)
		return
	}
	return
}

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
	"github.com/ghodss/yaml"
	"io/ioutil"
	"net/http"
	"strings"
)

type CreateClusterType struct {
	ClusterType       string        `json:"cluster_type"`
	Name              string        `json:"name"`
	RegionID          string        `json:"region_id"`
	DisableRollback   bool          `json:"disable_rollback"`
	TimeoutMins       int           `json:"timeout_mins"`
	KubernetesVersion string        `json:"kubernetes_version"`
	SnatEntry         bool          `json:"snat_entry"`
	PublicSlb         bool          `json:"public_slb"`
	SSHFlags          bool          `json:"ssh_flags"`
	CloudMonitorFlags bool          `json:"cloud_monitor_flags"`
	NodeCidrMask      string        `json:"node_cidr_mask"`
	ProxyMode         string        `json:"proxy_mode"`
	Tags              []interface{} `json:"tags"`
	Addons            []struct {
		Name   string `json:"name"`
		Config string `json:"config,omitempty"`
	} `json:"addons"`
	LoginPassword            string   `json:"login_password"`
	MasterCount              int      `json:"master_count"`
	MasterVswitchIds         []string `json:"master_vswitch_ids"`
	MasterInstanceTypes      []string `json:"master_instance_types"`
	MasterSystemDiskCategory string   `json:"master_system_disk_category"`
	MasterSystemDiskSize     int      `json:"master_system_disk_size"`
	WorkerInstanceTypes      []string `json:"worker_instance_types"`
	NumOfNodes               int      `json:"num_of_nodes"`
	WorkerSystemDiskCategory string   `json:"worker_system_disk_category"`
	WorkerSystemDiskSize     int      `json:"worker_system_disk_size"`
	Vpcid                    string   `json:"vpcid"`
	ContainerCidr            string   `json:"container_cidr"`
	ServiceCidr              string   `json:"service_cidr"`
}

func CreateKubernetesCluster(httpResponse http.ResponseWriter, httpRequest *http.Request) {

	var resp map[string]interface{}
	accessKeyId := httpRequest.Header.Get("accessKeyId")
	accessKeySecret := httpRequest.Header.Get("accessKeySecret")
	tenant_id := httpRequest.Header.Get("tenant_id")
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
	if len(tenant_id) == 0 {
		resp = utils.Message(false)
		resp["error"] = "tenant_id not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}
	client, err := sdk.NewClientWithAccessKey("default", accessKeyId, accessKeySecret)
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
		resp = utils.Message(false)
		resp["error"] = "Can't read body"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}
	request.Content = body
	response, err := client.ProcessCommonRequest(request)
	if err != nil {
		str := err.Error()
		if strings.Contains(str, "ConnectTimeout") {
			resp = utils.Message(false)
			resp["error"] = "Connection Timeout Issue"
			utils.Respond(httpResponse, resp, http.StatusRequestTimeout)
			return
		}
		var clusterType CreateClusterType
		err1 := json.Unmarshal(body, &clusterType)
		if err1 != nil {
			resp = utils.Message(false)
			resp["error"] = "Internal Server Error"
			utils.Respond(httpResponse, resp, http.StatusInternalServerError)
			return
		}
		clusterId := IsClusterCreated(clusterType.Name, accessKeyId, accessKeySecret, str)
		if len(clusterId) == 0 {
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
		} else {
			resp = utils.Message(true)
			resp["clusterId"] = clusterId
			//rand.Seed(time.Now().UnixNano())
			//hashstring := clusterId
			//job_id := api.Hash(hashstring)
			//api.InsertStatus(job_id, fmt.Sprintf("%v", clusterId), "Creation Request has been Submitted", "Alibaba Cloud", "", "")
			//resp["jobId"] = job_id
			utils.Respond(httpResponse, resp, http.StatusCreated)
			return
		}
	}
	contentStringResponse := response.GetHttpContentString()
	httpResponse.Header().Add("Content-Type", "application/json")
	var raw map[string]interface{}
	err1 := json.Unmarshal([]byte(contentStringResponse), &raw)
	if err1 != nil {
		resp = utils.Message(false)
		resp["error"] = "Internal Server Error"
		utils.Respond(httpResponse, resp, http.StatusInternalServerError)
		return
	}

	//resp["clusterId"] = raw["cluster_id"]
	//api.InsertStatus( "",fmt.Sprintf("%v", raw["cluster_id"]), "Creation Request has been Submitted", "Alibaba Cloud", "", "")

	utils.Respond(httpResponse, resp, http.StatusCreated)
	return
}

func GetClusterConfig(httpResponse http.ResponseWriter, httpRequest *http.Request) {
	clusterId := httpRequest.Header.Get("clusterId")
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
	if len(clusterId) == 0 {
		resp = utils.Message(false)
		resp["error"] = "clusterId not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}
	client, err := sdk.NewClientWithAccessKey("default", accessKeyId, accessKeySecret)
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
	str := response.GetHttpContentString()
	var raw map[string]interface{}
	err = json.Unmarshal([]byte(str), &raw)
	if err != nil {
		resp = utils.Message(false)
		resp["error"] = "Internal Server Error"
		utils.Respond(httpResponse, resp, http.StatusInternalServerError)
		return
	}
	config := raw["config"]
	configString := fmt.Sprintf("%v", config)
	bytesArray, err := yaml.YAMLToJSON([]byte(configString))
	if err != nil {
		resp = utils.Message(false)
		resp["error"] = "Internal Server Error"
		utils.Respond(httpResponse, resp, http.StatusInternalServerError)
		return
	}
	var configMap map[string]interface{}
	err = json.Unmarshal(bytesArray, &configMap)
	if err != nil {
		resp = utils.Message(false)
		resp["error"] = "Internal Server Error"
		utils.Respond(httpResponse, resp, http.StatusInternalServerError)
		return
	}
	resp = utils.Message(true)
	resp["config"] = configMap
	utils.Respond(httpResponse, resp, http.StatusOK)
	return
}

func GetClusterStatus(httpResponse http.ResponseWriter, httpRequest *http.Request) {
	var resp map[string]interface{}
	clusterId := httpRequest.Header.Get("clusterId")
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
	if len(clusterId) == 0 {
		resp = utils.Message(false)
		resp["error"] = "clusterId not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}
	client, err := sdk.NewClientWithAccessKey("default", accessKeyId, accessKeySecret)
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
	contentStringResponse := response.GetHttpContentString()
	var clusterDetail clusterprovisioning.ClusterDetail
	err = json.Unmarshal([]byte(contentStringResponse), &clusterDetail)
	if err != nil {
		resp = utils.Message(false)
		resp["error"] = "Internal Server Error"
		utils.Respond(httpResponse, resp, http.StatusInternalServerError)
		return
	}
	if len(clusterDetail.ErrMsg) == 0 {
		client2, err := ros.NewClientWithAccessKey(clusterDetail.RegionID, accessKeyId, accessKeySecret)
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
		request := ros.CreateGetStackRequest()
		request.Scheme = "https"
		request.StackId = clusterDetail.Parameters.ALIYUNStackID
		var stackResponse, _ = client2.GetStack(request)
		contentString := stackResponse.GetHttpContentString()

		var stackJSON map[string]interface{}
		err1 := json.Unmarshal([]byte(contentString), &stackJSON)
		if err1 != nil {
			resp = utils.Message(false)
			resp["error"] = "Internal Server Error"
			utils.Respond(httpResponse, resp, http.StatusInternalServerError)
			return
		}
		if stackJSON["Status"] != 0 {
			resp = utils.Message(true)
			resp["clusterStatus"] = fmt.Sprintf("%v", stackJSON["Status"])
			utils.Respond(httpResponse, resp, http.StatusOK)
			return
		}
		return
	} else {
		resp = utils.Message(true)
		resp["clusterStatus"] = clusterDetail.ErrMsg
		utils.Respond(httpResponse, resp, http.StatusOK)
		return
	}
}

func GetAllClusters(httpResponse http.ResponseWriter, httpRequest *http.Request) {
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
	client, err := sdk.NewClientWithAccessKey("default", accessKeyId, accessKeySecret)
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
	contentStringResponse := response.GetHttpContentString()
	httpResponse.Header().Add("Content-Type", "application/json")
	var raw []map[string]interface{}
	err = json.Unmarshal([]byte(contentStringResponse), &raw)
	if err != nil {
		resp = utils.Message(false)
		resp["error"] = "Internal Server Error"
		utils.Respond(httpResponse, resp, http.StatusInternalServerError)
		return
	}
	resp = utils.Message(true)
	resp["clusters"] = raw
	utils.Respond(httpResponse, resp, http.StatusOK)
	return
}

func DeleteCluster(httpResponse http.ResponseWriter, httpRequest *http.Request) {

	var resp map[string]interface{}
	clusterId := httpRequest.Header.Get("clusterId")
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
	if len(clusterId) == 0 {
		resp = utils.Message(false)
		resp["error"] = "clusterId not found"
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}
	client, err := sdk.NewClientWithAccessKey("default", accessKeyId, accessKeySecret)
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
		resp = utils.Message(false)
		resp["error"] = fmt.Sprintf("%v", err.Error())
		utils.Respond(httpResponse, resp, http.StatusBadRequest)
		return
	}
	contentStringResponse := response.GetHttpContentString()
	if len(contentStringResponse) == 0 {
		resp = utils.Message(true)
		resp["clusterStatus"] = "Delete Request Accepted"
		utils.Respond(httpResponse, resp, http.StatusAccepted)
		return
	} else {
		resp = utils.Message(true)
		resp["status"] = contentStringResponse
		utils.Respond(httpResponse, resp, http.StatusAccepted)
		return
	}
}

func IsClusterCreated(name string, accessKeyId string, accessKeySecret string, errorString string) string {

	if strings.Contains(errorString, "ClusterNameAlreadyExist") || strings.Contains(errorString, "TimeoutError") {
		return ""
	}
	client, err := sdk.NewClientWithAccessKey("default", accessKeyId, accessKeySecret)
	if err != nil {
		return ""
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
		return ""
	}
	contentStringResponse := response.GetHttpContentString()
	var clusterDetails []clusterprovisioning.ClusterDetail
	err1 := json.Unmarshal([]byte(contentStringResponse), &clusterDetails)
	if err1 != nil {
		return ""
	}
	for _, clusterInfo := range clusterDetails {
		if name == clusterInfo.Name {
			return clusterInfo.ClusterID
		}
	}
	return ""
}

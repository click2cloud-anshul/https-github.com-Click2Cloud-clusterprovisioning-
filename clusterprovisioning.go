package clusterprovisioning

import "time"

type RegionList struct {
	RegionId []string `json:"RegionId" xml:"RegionId"`
}

type RegionWithVPCList struct {
	Vpcs []Vpcs `json:"Vpcs" xml:"Vpcs"`
}

type Vpcs struct {
	CidrBlock  string     `json:"CidrBlock" xml:"CidrBlock"`
	VpcId      string     `json:"VpcId" xml:"VpcId"`
	RegionId   string     `json:"RegionId" xml:"RegionId"`
	Status     string     `json:"Status" xml:"Status"`
	VpcName    string     `json:"VpcName" xml:"VpcName"`
	VSwitchIds VSwitchIds `json:"VSwitchIds" xml:"VSwitchIds"`
}

type VSwitchIds struct {
	VSwitchId []string `json:"VSwitchId" xml:"VSwitchId"`
}

type ClusterDetail struct {
	InstanceType           string        `json:"instance_type"`
	VpcID                  string        `json:"vpc_id"`
	VswitchID              string        `json:"vswitch_id"`
	VswitchCidr            string        `json:"vswitch_cidr"`
	DataDiskSize           int           `json:"data_disk_size"`
	DataDiskCategory       string        `json:"data_disk_category"`
	SecurityGroupID        string        `json:"security_group_id"`
	Tags                   []interface{} `json:"tags"`
	ZoneID                 string        `json:"zone_id"`
	NAMING_FAILED          string        `json:"-"`
	Name                   string        `json:"name"`
	ClusterID              string        `json:"cluster_id"`
	Size                   int           `json:"size"`
	RegionID               string        `json:"region_id"`
	NetworkMode            string        `json:"network_mode"`
	SubnetCidr             string        `json:"subnet_cidr"`
	State                  string        `json:"state"`
	MasterURL              string        `json:"master_url"`
	ExternalLoadbalancerID string        `json:"external_loadbalancer_id"`
	Created                time.Time     `json:"created"`
	Updated                time.Time     `json:"updated"`
	Port                   int           `json:"port"`
	ErrMsg                 string        `json:"err_msg"`
	NodeStatus             string        `json:"node_status"`
	ClusterHealthy         string        `json:"cluster_healthy"`
	DockerVersion          string        `json:"docker_version"`
	ClusterType            string        `json:"cluster_type"`
	SwarmMode              bool          `json:"swarm_mode"`
	InitVersion            string        `json:"init_version"`
	CurrentVersion         string        `json:"current_version"`
	MetaData               string        `json:"meta_data"`
	GwBridge               string        `json:"gw_bridge"`
	UpgradeComponents      struct {
		Kubernetes struct {
			ComponentName  string      `json:"component_name"`
			Version        string      `json:"version"`
			NextVersion    string      `json:"next_version"`
			Changed        string      `json:"changed"`
			CanUpgrade     bool        `json:"can_upgrade"`
			Force          bool        `json:"force"`
			Policy         string      `json:"policy"`
			ExtraVars      interface{} `json:"ExtraVars"`
			ReadyToUpgrade string      `json:"ready_to_upgrade"`
			Message        string      `json:"message"`
			Exist          bool        `json:"exist"`
		} `json:"Kubernetes"`
	} `json:"upgrade_components"`
	ResourceGroupID    string      `json:"resource_group_id"`
	PrivateZone        bool        `json:"private_zone"`
	Profile            string      `json:"profile"`
	DeletionProtection bool        `json:"deletion_protection"`
	Capabilities       interface{} `json:"capabilities"`
	EnabledMigration   bool        `json:"enabled_migration"`
	NeedUpdateAgent    bool        `json:"need_update_agent"`
	Outputs            []struct {
		Description string      `json:"Description"`
		OutputKey   string      `json:"OutputKey"`
		OutputValue interface{} `json:"OutputValue"`
	} `json:"outputs"`
	Parameters struct {
		ALIYUNAccountID          string `json:"ALIYUN::AccountId"`
		ALIYUNNoValue            string `json:"ALIYUN::NoValue"`
		ALIYUNRegion             string `json:"ALIYUN::Region"`
		ALIYUNStackID            string `json:"ALIYUN::StackId"`
		ALIYUNStackName          string `json:"ALIYUN::StackName"`
		AdjustmentType           string `json:"AdjustmentType"`
		AuditFlags               string `json:"AuditFlags"`
		BetaVersion              string `json:"BetaVersion"`
		CA                       string `json:"CA"`
		ClientCA                 string `json:"ClientCA"`
		CloudMonitorFlags        string `json:"CloudMonitorFlags"`
		CloudMonitorVersion      string `json:"CloudMonitorVersion"`
		ContainerCIDR            string `json:"ContainerCIDR"`
		DisableAddons            string `json:"DisableAddons"`
		DockerVersion            string `json:"DockerVersion"`
		Eip                      string `json:"Eip"`
		EipAddress               string `json:"EipAddress"`
		ElasticSearchHost        string `json:"ElasticSearchHost"`
		ElasticSearchPass        string `json:"ElasticSearchPass"`
		ElasticSearchPort        string `json:"ElasticSearchPort"`
		ElasticSearchUser        string `json:"ElasticSearchUser"`
		EtcdVersion              string `json:"EtcdVersion"`
		ExecuteVersion           string `json:"ExecuteVersion"`
		Finance                  string `json:"Finance"`
		GPUFlags                 string `json:"GPUFlags"`
		HealthCheckType          string `json:"HealthCheckType"`
		ImageID                  string `json:"ImageId"`
		K8SMasterPolicyDocument  string `json:"K8SMasterPolicyDocument"`
		K8SWorkerPolicyDocument  string `json:"K8sWorkerPolicyDocument"`
		Key                      string `json:"Key"`
		KeyPair                  string `json:"KeyPair"`
		KubernetesVersion        string `json:"KubernetesVersion"`
		LoggingType              string `json:"LoggingType"`
		MasterAmounts            string `json:"MasterAmounts"`
		MasterAutoRenew          string `json:"MasterAutoRenew"`
		MasterAutoRenewPeriod    string `json:"MasterAutoRenewPeriod"`
		MasterCount              string `json:"MasterCount"`
		MasterDataDisk           string `json:"MasterDataDisk"`
		MasterDataDisks          string `json:"MasterDataDisks"`
		MasterDeletionProtection string `json:"MasterDeletionProtection"`
		MasterDeploymentSetID    string `json:"MasterDeploymentSetId"`
		MasterHpcClusterID       string `json:"MasterHpcClusterId"`
		MasterImageID            string `json:"MasterImageId"`
		MasterInstanceChargeType string `json:"MasterInstanceChargeType"`
		MasterInstanceTypes      string `json:"MasterInstanceTypes"`
		MasterKeyPair            string `json:"MasterKeyPair"`
		MasterLoginPassword      string `json:"MasterLoginPassword"`
		MasterPeriod             string `json:"MasterPeriod"`
		MasterPeriodUnit         string `json:"MasterPeriodUnit"`
		MasterSlbSShHealthCheck  string `json:"MasterSlbSShHealthCheck"`
		MasterSystemDiskCategory string `json:"MasterSystemDiskCategory"`
		MasterSystemDiskSize     string `json:"MasterSystemDiskSize"`
		MasterVSwitchIds         string `json:"MasterVSwitchIds"`
		NatGateway               string `json:"NatGateway"`
		NatGatewayID             string `json:"NatGatewayId"`
		Network                  string `json:"Network"`
		NodeCIDRMask             string `json:"NodeCIDRMask"`
		NodeNameMode             string `json:"NodeNameMode"`
		NumOfNodes               string `json:"NumOfNodes"`
		Password                 string `json:"Password"`
		PodVswitchIds            string `json:"PodVswitchIds"`
		ProtectedInstances       string `json:"ProtectedInstances"`
		PublicSLB                string `json:"PublicSLB"`
		RemoveInstanceIds        string `json:"RemoveInstanceIds"`
		SLBDeletionProtection    string `json:"SLBDeletionProtection"`
		SLSProjectName           string `json:"SLSProjectName"`
		SNatEntry                string `json:"SNatEntry"`
		SSHFlags                 string `json:"SSHFlags"`
		SecurityGroupID          string `json:"SecurityGroupId"`
		ServiceCIDR              string `json:"ServiceCIDR"`
		SetUpArgs                string `json:"SetUpArgs"`
		SnatTableID              string `json:"SnatTableId"`
		Tags                     string `json:"Tags"`
		UserCA                   string `json:"UserCA"`
		VpcID                    string `json:"VpcId"`
		WillReplace              string `json:"WillReplace"`
		WorkerAutoRenew          string `json:"WorkerAutoRenew"`
		WorkerAutoRenewPeriod    string `json:"WorkerAutoRenewPeriod"`
		WorkerDataDisk           string `json:"WorkerDataDisk"`
		WorkerDataDisks          string `json:"WorkerDataDisks"`
		WorkerDeletionProtection string `json:"WorkerDeletionProtection"`
		WorkerDeploymentSetID    string `json:"WorkerDeploymentSetId"`
		WorkerHpcClusterID       string `json:"WorkerHpcClusterId"`
		WorkerImageID            string `json:"WorkerImageId"`
		WorkerInstanceChargeType string `json:"WorkerInstanceChargeType"`
		WorkerInstanceTypes      string `json:"WorkerInstanceTypes"`
		WorkerKeyPair            string `json:"WorkerKeyPair"`
		WorkerLoginPassword      string `json:"WorkerLoginPassword"`
		WorkerPeriod             string `json:"WorkerPeriod"`
		WorkerPeriodUnit         string `json:"WorkerPeriodUnit"`
		WorkerSystemDiskCategory string `json:"WorkerSystemDiskCategory"`
		WorkerSystemDiskSize     string `json:"WorkerSystemDiskSize"`
		WorkerVSwitchIds         string `json:"WorkerVSwitchIds"`
		ZoneID                   string `json:"ZoneId"`
	} `json:"parameters"`
}

type KeyPair struct {
	KeyPairs []string `json:"KeyPairs" xml:"KeyPairs"`
}

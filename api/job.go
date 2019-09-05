package api

//
//func InsertStatus(tenant_id, cluster_id, cluster_status, cloud_provider, cluster_name, cluster_kube_config string) {
//	var sqlStatement = `INSERT INTO public.__cb_cluster_provisioning_details(tenant_id, cluster_id, cluster_status, cloud_provider, cluster_name, cluster_kube_config) VALUES ( $1, $2, $3, $4, $5, $6);`
//	_, err := db.DB.Exec(sqlStatement, tenant_id, cluster_id, cluster_status, cloud_provider, cluster_name, cluster_kube_config)
//	if err != nil {
//		fmt.Print(err)
//	}
//	//cmd := "SELECT * FROM cb_dr_sp_insert_or_update_job_status('{token}','{dr_type}',{progress},'{start_time}','{end_time}','{stat}','{err}','{job_id}')"
//
//}

//func Hash(key string) string {
//	hasher := md5.New()
//	hasher.Write([]byte(key))
//	return hex.EncodeToString(hasher.Sum(nil))
//}

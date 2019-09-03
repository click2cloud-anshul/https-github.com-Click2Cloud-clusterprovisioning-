package api

//
//func InsertStatus(cluster_id, job_id, cluster_status, cloud_provider,cluster_name string) {
//	var sqlStatement = `INSERT INTO public._cb_cp_details(cluster_id, job_id, cluster_status, cloud_provider, cluster_name) VALUES ( $1, $2, $3, $4, $5);`
//	_, err := db.DB.Exec(sqlStatement, cluster_id, job_id, cluster_status, cloud_provider, cluster_name)
//	if err != nil {
//		fmt.Print(err)
//	}
//	//cmd := "SELECT * FROM cb_dr_sp_insert_or_update_job_status('{token}','{dr_type}',{progress},'{start_time}','{end_time}','{stat}','{err}','{job_id}')"
//
//}
//
//func create_dir(user_id string) (string, string, error) {
//	rand.Seed(time.Now().UnixNano())
//	hashstring := user_id + randomString(10)
//	job_id := hash(hashstring)
//
//	basepath := "." + string(filepath.Separator) + "Jobs" + string(filepath.Separator) + string(job_id)
//	//InsertStatus(user_id, job_id, "InProgress", "Started template creation and application")
//	//InsertStatus()
//	if _, err := os.Stat(basepath); os.IsNotExist(err) {
//		err := os.MkdirAll(basepath, 0777)
//		if err != nil {
//			return "", "", nil
//		}
//	}
//	return job_id, basepath, nil
//}
//func randomInt(min, max int) int {
//	return min + rand.Intn(max-min)
//}
//func randomString(len int) string {
//	bytesrand := make([]byte, len)
//	for i := 0; i < len; i++ {
//		bytesrand[i] = byte(randomInt(65, 90))
//	}
//	return string(bytesrand)
//}
//func hash(key string) string {
//	hasher := md5.New()
//	hasher.Write([]byte(key))
//	return hex.EncodeToString(hasher.Sum(nil))
//}

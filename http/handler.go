package http

import (
	"log"
	"net/http"

	"github.com/Click2Cloud/clusterprovisioning/api/ali"
	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
)

func ServeHttp() {
	router := mux.NewRouter()

	router.HandleFunc("/ali/clusterprovisiong/getVPCList", ali.GetVPCList).Methods("GET")
	router.HandleFunc("/ali/clusterprovisiong/getKeyPairList", ali.GetKeyPairList).Methods("GET")
	router.HandleFunc("/ali/clusterprovisiong/getRegionList", ali.GetRegionList).Methods("GET")
	router.HandleFunc("/ali/clusterprovisiong/getClusterStatus", ali.GetClusterStatus).Methods("GET")
	router.HandleFunc("/ali/clusterprovisiong/getClusterConfig", ali.GetClusterConfig).Methods("GET")
	//router.HandleFunc("/ali/clusterprovisiong/getInstances", ali.GetInstances).Methods("GET")
	router.HandleFunc("/ali/clusterprovisiong/createKubernetesCluster", ali.CreateKubernetesCluster).Methods("POST")
	router.HandleFunc("/ali/clusterprovisiong/getAllClusters", ali.GetAllClusters).Methods("GET")
	router.HandleFunc("/ali/clusterprovisiong/deleteCluster", ali.DeleteCluster).Methods("DELETE")

	log.Fatal(http.ListenAndServe("0.0.0.0:8000", handlers.CORS(handlers.AllowedHeaders([]string{"X-Requested-With", "Content-Type", "Authorization"}), handlers.AllowedMethods([]string{"GET", "DELETE", "PUT", "POST", "PUT", "HEAD", "OPTIONS"}), handlers.AllowedOrigins([]string{"*"}))(router)))
}

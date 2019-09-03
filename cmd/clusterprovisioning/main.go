package main

import (
	"github.com/Click2Cloud/clusterprovisioning/http"
	//"encoding/json"
	"github.com/gorilla/mux"
	"github.com/jinzhu/gorm"
	_ "github.com/lib/pq"
	//"io/ioutil"
	//"net/http"
)

type App struct {
	Router *mux.Router
	DB     *gorm.DB
}

func main() {
	http.ServeHttp()
}

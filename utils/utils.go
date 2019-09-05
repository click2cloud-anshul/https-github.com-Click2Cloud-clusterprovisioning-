package utils

import (
	"encoding/json"
	"net/http"
)

func Message(status bool) map[string]interface{} {
	return map[string]interface{}{"status": status}
}

func Respond(w http.ResponseWriter, data map[string]interface{}, responseCode int) {
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(responseCode)
	_ = json.NewEncoder(w).Encode(data)
}

func Contains(slice []string, item string) bool {
	set := make(map[string]struct{}, len(slice))
	for _, s := range slice {
		set[s] = struct{}{}
	}

	_, ok := set[item]
	return ok
}

# cluster-provisioning

## Environment Variables Accepted:
- **DB_User** (Default: `root`)
- **DB_Host**
- **DB_Name** (Default: `vmdb_development`)
- **DB_Password**
- **DB_Port** (Default: `5432`)
- **CB_Node_Service** (For credentials decryption)
- **ENCRYPTION_KEY** (For Cluster Configuration encryption and decryption)

### Note: Also supports dotenv (.env) file to load environment variables at path clusterProvisioningClient/.


## Build Docker Image
```
docker build --build-arg=COMMIT=$(git rev-parse --short HEAD) --build-arg=BRANCH=$(git rev-parse --abbrev-ref HEAD) -t registry.click2cloud.com:5000/click2cloud/cluster-provisioner:production .
```
## Run Docker Image
```
docker run --name clusterpro -d -p 8080:8000 -v $(pwd):/var/log/cluster-provisioner/ --env-file ./clusterProvisioningClient/.env registry.click2cloud.com:5000/click2cloud/cluster-provisioner:production -v /var/run/docker.sock:/var/run/docker.sock:z
```
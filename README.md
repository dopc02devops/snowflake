
https://docs.airbyte.com/using-airbyte/getting-started/oss-quickstart
https://clickhouse.com/docs/knowledgebase/how-to-set-up-ch-on-docker-odbc-connect-mssql

### DOWNLOAD AIRBYTE ###
brew tap airbytehq/tap
brew install abctl
brew upgrade abctl

### INSATLL AIRBYTE ###
abctl local install --insecure-cookies
abctl local install --low-resource-mode
abctl local install --low-resource-mode --insecure-cookies

### PASSWORD ###
abctl local credentials

### CHANGE PASSWORD ###
abctl local credentials --password YourStrongPasswordExample

### UNINSATLL AIRBYTE ###
abctl local uninstall
abctl local uninstall --persisted
rm -rf ~/.airbyte/abctl



docker stop airbyte-abctl-control-plane


# snowflake

https://signup.snowflake.com/#


https://home.openweathermap.org/

### EMAIL ###
USER_EMAIL=dopc02devops1@gmail.com
ORGANISATION: NSN


docker-compose up --build -d
docker-compose up -d --force-recreate
docker-compose down

host.docker.internal





export KUBECONFIG=~/.airbyte/abctl/abctl.kubeconfig

kubectl delete namespace airbyte-abctl
kubectl delete deployment --all -n airbyte-abctl




kubectl describe pod replication-job-2-attempt-1 -n airbyte-abctl

kubectl top nodes
kubectl top pods -n airbyte-abctl

kubectl edit deployment airbyte-abctl-worker -n airbyte-abctl

##########
edit-  deployment file 
kubectl get deployment airbyte-abctl-worker -n airbyte-abctl -o yaml > airbyte-worker-deployment.yaml

kubectl apply -f airbyte-worker-deployment.yaml -n airbyte-abctl
kubectl rollout restart deployment airbyte-abctl-worker -n airbyte-abctl
###############

kubectl get pod replication-job-2-attempt-2 -n airbyte-abctl -o yaml > replication-job-pod.yaml
kubectl delete pod replication-job-2-attempt-3 -n airbyte-abctl

kubectl apply -f replication-job-pod.yaml -n airbyte-abctl
kubectl rollout restart deployment replication-job-2-attempt-2 -n airbyte-abctl


install metric server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl get pods -n kube-system | grep metrics-server

kubectl describe pod metrics-server-75bf97fcc9-q588j -n kube-system
kubectl logs -n kube-system metrics-server-75bf97fcc9-q588j


### To use Context ####
- kubectl config get-contexts
- kubectl config use-context kind-airbyte-abctl
- kubectl get all -n airbyte-abctl
- kubectl get pods -n airbyte-abctl
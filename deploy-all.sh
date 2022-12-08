#!/bin/sh
kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml

kubectl apply -f rest/rest-deployment.yaml
kubectl apply -f rest/rest-service.yaml

kubectl apply -f sql/mysql-secret.yaml
kubectl apply -f sql/mysql-storage.yaml
kubectl apply -f sql/mysql-deployment.yaml

kubectl apply -f logs/logs-deployment.yaml

kubectl apply -f worker/worker-deployment.yaml


# for deployment deletion:

# kubectl delete deployment,svc mysql
# kubectl delete pvc mysql-pv-claim
# kubectl delete pv mysql-pv-volume
# kubectl delete secret mysql-secret
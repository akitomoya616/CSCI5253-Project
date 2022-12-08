#!/bin/sh
kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml

kubectl apply -f rest/rest-deployment.yaml
kubectl apply -f rest/rest-service.yaml
kubectl apply -f rest/rest-ingress-gke.yaml # or kubectl apply -f rest/rest-ingress.yaml

kubectl apply -f sql/mysql-secret.yaml
kubectl apply -f sql/mysql-storage.yaml
kubectl apply -f sql/mysql-deployment.yaml

kubectl apply -f logs/logs-deployment.yaml

kubectl apply -f worker/worker-deployment.yaml

# run the following command on GKE to start the client. Use python instead of python3 for local environment testing
# python3 rest-client.py
# or this to drop the table been created
# python3 rest-client-drop-table.py

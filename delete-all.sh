# DELETION

# for redis:
kubectl delete deployment redis
kubectl delete service redis

# for rest:
kubectl delete deployment rest
kubectl delete service rest-svc
kubectl delete ingress frontend-ingress

# for mysql:
kubectl delete deployment,svc mysql
kubectl delete pvc mysql-pv-claim
kubectl delete pv mysql-pv-volume
kubectl delete secret mysql-secret

# for logs:
kubectl delete deployment logs

# for worker
kubectl delete deployment worker
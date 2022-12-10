# Redis Database

Database that stores the temperary data pushed form REST server (with tag `sql_command`) and from Worker node (with tag `sql_result`).

ONLY do `lpush` and `rpop` for maintaining Message Queue.

For running the redis pod on the local environment, please do `kubectl port-forward service/mysql 3306:3306` in terminal after setting up and deploying the pod first and then you can connect with database on rest server.


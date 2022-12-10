# MySQL Database

sql setup referenced from: https://phoenixnap.com/kb/kubernetes-mysql

For running the MySQL pod on the local environment, please do `kubectl port-forward service/mysql 3306:3306` in terminal after setting up and deploying the pod first and then you can connect with database on rest server.

Stores all the data uploaded by the user and communicates with Worker node through SQL query ONLY.
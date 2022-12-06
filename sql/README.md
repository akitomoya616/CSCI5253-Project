# MySQL Database

sql setup referenced from: https://phoenixnap.com/kb/kubernetes-mysql

Do kubectl port-forward service/mysql 3306:3306 after setting up the pod and then you can connect with database on rest server

Stores all the data uploaded by the user and communicates with Worker node through SQL query ONLY.
# SQL & Dataframes Processing Worker

Worker node is the only place that can communicate with MySQL Database.

Connect to REDIS and MySQL db, create db from MySQL if not exists, wait till command received in REDIS with tag `sql_command` which is pushed by REST server. Process the command and return the result back to REDIS with tag `sql_result` for REST server to grab from.

Worker node also support dataframes generation based on the SQL result by importing Pandas. It can generate a diagram representing the relationship between Date and Price of the product, encode it and pass it back to REST client so the latter one can decode it and save the diagram somewhere locally.
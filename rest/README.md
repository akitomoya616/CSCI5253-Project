# REST API and interface

REST server that take requests and data from REST client, grab all the necessary data for forming the SQL query needed by the request and lpush it to REDIS with tag `sql_command`.

Wait until there's no value in REDIS with tag `sql_command` (which means Worker has finished processing it and already returned result to REDIS with tag `sql_result` if there's a returnable result), grab ALL the result left from REDIS with tag `sql_result`, clean them up (since there's gonna have a `b\` or `b\\` right in front of the result) and return them back to REST client as a response.
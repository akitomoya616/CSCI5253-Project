# REST API & Interface

REST server that take requests and data from REST client, grab all the necessary data for forming the SQL query needed by the request and lpush it to REDIS with tag `sql_command`.

Wait until there's no value in REDIS with tag `sql_command` (which means Worker has finished processing it and already returned result to REDIS with tag `sql_result` if there's a returnable result), grab ALL the result left from REDIS with tag `sql_result`, clean them up (since there's gonna have a `b\` or `b\\` right in front of the result) and return them back to REST client as a response.

Please following this [tutorial for installing ingress extension based on nginx](https://kubernetes.github.io/ingress-nginx/deploy/#docker-for-mac)  before applying the ingress file (use [rest-ingress-gke.yaml](rest-ingress-gke.yaml) if you are doing this on GKE, and use [rest-ingress.yaml](rest-ingress.yaml) if you are simply doing this on local environment)
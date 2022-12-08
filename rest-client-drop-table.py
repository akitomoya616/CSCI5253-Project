#!/usr/bin/env python3

import requests
import json, jsonpickle
import os
import sys

#
# Use localhost & port 5000 if not specified by environment variable REST
#

# localhost for connection on pod, and localhost:5000 for connection to local test (so we run python rest-server.py on terminal)
REST = os.getenv("REST") or "*" #"localhost:5000"

##
# The following routine makes a JSON REST query of the specified type
# and if a successful JSON reply is made, it pretty-prints the reply
##

def mkReq(reqmethod, endpoint, data, verbose=True):
    print(f"Response to http://{REST}/{endpoint} request is {type(data)}")
    jsonData = jsonpickle.encode(data)
    if verbose and data != None:
        print(f"Make request http://{REST}/{endpoint} with json {data.keys()}")
    response = reqmethod(f"http://{REST}/{endpoint}", data=jsonData,
                         headers={'Content-type': 'application/json'})
    if response.status_code == 200:
        jsonResponse = json.dumps(response.json(), indent=4, sort_keys=True)
        print(jsonResponse)
        return
    else:
        print(
            f"response code is {response.status_code}, raw response is {response.text}")
        return response.text

# delete the table from sql database - WILL NOT BE USED BY USER since they do not have the rights to elimiate a general table
print('\ndelete the current tables.')
mkReq(requests.get, "apiv1/deleteTable", data=None)

sys.exit(0)
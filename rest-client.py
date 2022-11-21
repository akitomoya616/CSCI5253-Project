#!/usr/bin/env python3

import requests
import json, jsonpickle
import os
import sys
import base64
import glob
import time

#
# Use localhost & port 5000 if not specified by environment variable REST
#

# localhost for connection on pod, and localhost:5000 for connection to local test (so we run python rest-server.py on terminal)
REST = os.getenv("REST") or "localhost:5000" #"localhost:5000"

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

for shopping_data in glob.glob("data/*json"):
    print(f"Grab {shopping_data}")
    print('sending shopping data to REST server...')
    # send the json data here
    mkReq(requests.post, "apiv1/send",
        data={
            "shopping": base64.b64encode( open(shopping_data, "rb").read() ).decode('utf-8'),
            "callback": {
                "url": "http://localhost:5000",
                "data": {"shopping": 'this is the shopping data under callback!', 
                         "data": "to be returned"}
            }
        },
        verbose=True
        )
    # check current data in redis
    # print('current REDIS database contains the following data:')
    # mkReq(requests.get, "apiv1/queue", data=None)
    
    # send the next data after 1 second
    time.sleep(1)

# check current data in table
print('\ncurrent table in SQL database contains the following data:')
mkReq(requests.get, "apiv1/sqlqueue", data=None)

# get all data sorted by date
print('\nall data from newest to oldest:')
mkReq(requests.get, "apiv1/sort/date/DESC", data=None)

# delete specific data by its id from the table in sql database
print('\ndelete the current data from the table.')
mkReq(requests.get, "apiv1/deleteByID/4", data=None)
mkReq(requests.get, "apiv1/sqlqueue", data=None)

# return the total cost of all the products listed in the current table
print('\ntotal price of the products listed above is: ')
mkReq(requests.get, "apiv1/sumPrice", data=None)






# delete the table from sql database - WILL NOT BE USED BY USER since they do not have the rights to elimiate a general table
# print('\ndelete the current table.')
# mkReq(requests.get, "apiv1/deleteTable", data=None)

# do two more requests:
# now we can only do the following 2 tests in short but not in sample-requests.py
# because the hash for each file is just the filename but not the actual hashed bits
# the full length file name contains space and cannot be used under this situation

# mkReq(requests.get, "apiv1/track/short-hop/drums.wav", data=None)
# mkReq(requests.get, "apiv1/remove/short-hop/drums.wav", data=None)

sys.exit(0)
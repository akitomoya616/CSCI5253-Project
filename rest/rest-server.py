#!/usr/bin/env python3

##
## Sample Flask REST server implementing two methods
##
## Endpoint /api/image is a POST method taking a body containing an image
## It returns a JSON document providing the 'width' and 'height' of the
## image that was provided. The Python Image Library (pillow) is used to
## proce#ss the image
##
## Endpoint /api/add/X/Y is a post or get method returns a JSON body
## containing the sum of 'X' and 'Y'. The body of the request is ignored
##
##
from flask import Flask, request, Response
import jsonpickle
import base64

# extra library
import json

# extra libray imported by Sitong Lu
import redis
import os
import time

# Initialize the Flask application
app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)

# set redis host and port for connection
redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379
redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
print("Successfully connected to the REDIS server!\n")

# set sql database and table value for later use
sqldatabasename = 'TEST_DB' #'project_database'
deleteTableName = 'DELETED_DATA'
tableName = 'customer'

# method definition: by mentioning "GET", "POST", "DELETE" in methods=[], we allow the client side (in our case it is the rest-client.py)
# to have the corresponding ability to call requests.get/post/delete
# route http posts to this method

# ALL the methods created below will just take the necessary parameter for processing the SQL query to REDIS
# and let worker grab the data from REDIS, process it, and return the result back to REDIS if necessary
# REST server will then grab the result from there, beautify the result a little bit through editing
# and return it back to client as response

@app.route('/apiv1/add', methods=['POST'])
def addData():
    r = request
    try:
        shopping_data_encoded = json.loads(r.data)['shopping']
        shopping_data_decoded = base64.b64decode(shopping_data_encoded) 
        # this decoded data from above is in bytes but not in dict since we used json.loads on the encoded file but not the decoded one
        # therefore we need to load it again to get dict type file
        shopping_data = json.loads(shopping_data_decoded) 
        
        print("pushing into redis!")
        # pass the necessary parmeters for forming the correspnding SQL query to REDIS
        sql_command_list = ["INSERT", str(shopping_data['name']), str(shopping_data['product']), str(float(shopping_data['price'])), str(shopping_data['date'])]
        sql_command_string = ','.join(sql_command_list) # turn the list type data into string with comma to seperate each value
        print("current command is: " + sql_command_string + "\n")
        redisClient.lpush("sql_command", str(sql_command_string)) 
        
        print("length right now at lpush stage is: " + str(redisClient.llen("sql_command")) + "\n")
        
        # wait till worker finishing process this sql query and pop it out from redis
        # in general, there's only gonna have 1 query in redis between the following process 
        # rest post data to redis - worker process it and upload result back to redis
        # - worker pop it out from redis - rest post another data to redis
        while (redisClient.llen("sql_command") != 0):
            print("Waiting for Worker to finish processing this SQL queury...")
            print()
            time.sleep(1)

        response = {
            'status' : "got it!",
            'shopping data' : shopping_data
        }

    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'Failed to take data! Error: ' + str(e)}

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/sqlqueue', methods=['GET'])
def showSQLQueue():
    # get the list of data stored in sql database's table now
    # and return it back to client
    r = request
    try:
        print("pushing into redis!")
        sql_command_list = ["QUEUE"]
        sql_command_string = ','.join(sql_command_list) # turn the list type data into string with comma to seperate each value
        print("current command is: " + sql_command_string + "\n")
        redisClient.lpush("sql_command", str(sql_command_string)) 

        while (redisClient.llen("sql_command") != 0):
            print("Waiting for Worker to finish processing this SQL queury...")
            print()
            time.sleep(1)

        # grab the result from REDIS and form them back into a list type
        element = []
        while (redisClient.llen("sql_result") != 0): # will return 1 row in 1 REDIS storage, so we need to add them all
            row = redisClient.rpop("sql_result") # get the current row from REDIS
            row = str(row).replace("b\"", '').replace("\"",'') # clean out the extra chars added from REDIS
            element.append(row)

        response = element

    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'Failed to load data from the table in SQL database.'}

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/sumPrice', methods=['GET'])
def sumPrice():
    # get the list of data stored in sql database's table now
    # and return it back to client
    r = request
    try:
        print("pushing into redis!")
        sql_command_list = ["SUM"]
        sql_command_string = ','.join(sql_command_list) # turn the list type data into string with comma to seperate each value
        print("current command is: " + sql_command_string + "\n")
        redisClient.lpush("sql_command", str(sql_command_string)) 

        while (redisClient.llen("sql_command") != 0):
            print("Waiting for Worker to finish processing this SQL queury...")
            print()
            time.sleep(1)

        sum = redisClient.rpop("sql_result")

        # clean out extra value added during process from REDIS
        print("sum received: ")
        print(sum)
        print("after cleaning:")
        sum = float(str(sum).replace("b'", '').replace("'",'')) 
        print(str(sum) + "\n")

        response = {
            f'total price: ${sum}' 
        }

    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'Failed to load data from the table in SQL database.'}

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/sort/<string:orderByValue>/<string:asc_desc>', methods=['GET'])
def sortSQLQueue(orderByValue, asc_desc):
    # get the list of data stored in sql database's table now
    # and return it back to client in sorted order
    r = request
    try:
        print("pushing into redis!")
        sql_command_list = ["SORT", orderByValue, asc_desc]
        sql_command_string = ','.join(sql_command_list) # turn the list type data into string with comma to seperate each value
        print("current command is: " + sql_command_string + "\n")
        redisClient.lpush("sql_command", str(sql_command_string)) 

        while (redisClient.llen("sql_command") != 0):
            print("Waiting for Worker to finish processing this SQL queury...")
            print()
            time.sleep(1)

        element = []
        while (redisClient.llen("sql_result") != 0): # will return 1 row in 1 REDIS storage, so we need to add them all
            row = redisClient.rpop("sql_result") # get the current row from REDIS
            row = str(row).replace("b\"", '').replace("\"",'') # clean out the extra chars added from REDIS
            element.append(row)

        response = element

    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'Failed to load & sort data from the table in SQL database.'}

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/deleteByID/<string:id_to_delete>', methods=['GET'])
def deleteByID(id_to_delete):
    # get the list of data stored in sql database's table now
    # and return it back to client in sorted order
    r = request
    try:
        # drop the row we created in table
        print("pushing delete command into redis!")
        sql_command_list = ["DELETE", tableName, id_to_delete]
        sql_command_string = ','.join(sql_command_list) # turn the list type data into string with comma to seperate each value
        print("current command is: " + sql_command_string + "\n")
        redisClient.lpush("sql_command", str(sql_command_string)) 

        while (redisClient.llen("sql_command") != 0):
            print("Waiting for Worker to finish processing this SQL queury...")
            print()
            time.sleep(1)

        response = {f"Successfully deleted the row with id {id_to_delete} from SQL database!"}

    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'Failed to delete row in table.'}

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/deleteTable', methods=['GET'])
def deleteTable():
    # get the list of data stored in sql database's table now
    # and return it back to client in sorted order
    r = request
    try:
        # drop the two tables we created
        sql_command_list = ["DROP", tableName]
        sql_command_string = ','.join(sql_command_list) # turn the list type data into string with comma to seperate each value
        print("current command is: " + sql_command_string + "\n")
        redisClient.lpush("sql_command", str(sql_command_string)) 

        while (redisClient.llen("sql_command") != 0):
            print("Waiting for Worker to finish processing this SQL queury...")
            print()
            time.sleep(1)
        
        response = {"Successfully deleted all tables from SQL database!"}

    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'Failed to delete table in SQL database.'}

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/extra', methods=['GET'])
def extra():
    # get the list of data stored in sql database's table now
    # and return it back to client
    r = request
    try:
        print("pushing into redis!")
        sql_command_list = ["EXTRA"]
        sql_command_string = ','.join(sql_command_list) # turn the list type data into string with comma to seperate each value
        print("current command is: " + sql_command_string + "\n")
        redisClient.lpush("sql_command", str(sql_command_string)) 

        while (redisClient.llen("sql_command") != 0):
            print("Waiting for Worker to finish processing this SQL queury...")
            print()
            time.sleep(1)
        
        pic_encoded = redisClient.rpop("sql_result") # get the current encoded pic data from REDIS
        # clean out encoded data that has extra b' values added during transition from REDIS
        pic_encoded = str(pic_encoded).replace("b'", '').replace("'",'')

        # just pass this encoded pic data to client
        # DO NOT pass the decoded one cause the long byte will be somehow limited by the time client get it
        response = pic_encoded
    
    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'Failed to load & sort data from the table in SQL database.'}

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")





@app.route('/apiv1/queue', methods=['GET'])
def showQueue(): # dump the queued entries from the Redis database
    # get the list of files stored in radis now
    # and return it back to client
    r = request

    element = []
    length = redisClient.llen("hash_for_worker")
    print("length right now at response stage is: " + str(length))
    for i in range(0,length):
        element.append(str(redisClient.lindex("hash_for_worker", i)))

    try:
        response = element

    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'failed to load cache from server'}

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/a', methods=['GET'])
def a():
    # get the list of data stored in sql database's table now
    # and return it back to client in sorted order
    r = request
    try:
        
        response = {"Successfully connect to it!"}

    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'Failed to delete table in SQL database.'}

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# start flask app
app.run(host="0.0.0.0", port=5000)
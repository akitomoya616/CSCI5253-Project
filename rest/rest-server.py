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
from minio import Minio
import time
import io

import mysql.connector
from mysql.connector import Error
import pandas as pd

pw = 'test1234' # password created in MySQL server

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

# set minio host and port for connection
minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

minioClient = Minio(minioHost,
               secure=False,
               access_key=minioUser,
               secret_key=minioPasswd)
print("Successfully connected to the minIO server!\n")

bucketname='CSCI5253-Project' # for minio bucket setup and referenc

# set sql database and table value for later use
sqldatabasename = 'TEST_DB' #'project_database'
deleteTableName = 'DELETED_DATA'
tableName = 'customer'

# connect to SQL server
print("connecting to MySQL server...\n")
mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="test1234")
mycursor = mydb.cursor() # mycursor now reference to the whole sql server
print("Successfully connected to the SQL database!\n")

# create a database in this SQL server
mycursor.execute("CREATE DATABASE IF NOT EXISTS " + sqldatabasename)
print("Current databases in the SQL server are:")
mycursor.execute("SHOW DATABASES")
for x in mycursor:
  print(x)
print()

# connect to the specific database
mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="test1234",
        database=sqldatabasename)
print("Successfully connected to: " + sqldatabasename + "!\n")

mycursor = mydb.cursor() # mycursor now reference to the database we pointed to

# create the table we need if it does not exist with all column names and data types
# remember to DELETE THE WHOLE TABLE AND RECREATE IT if datatype for an EXISTING column has been changed
mycursor.execute(f"CREATE TABLE if not exists {tableName} (ID INT, Name VARCHAR(255), Product VARCHAR(255), Price DECIMAL(9,3), Date VARCHAR(255))") # DECIMAL(9,3) means we can have up to 6 places before the decimal and a decimal of up to 3 places
mycursor.execute(f"CREATE TABLE if not exists {deleteTableName} (ID INT)") # only stores deleted id

print("Tables in the current database:")
mycursor.execute("SHOW TABLES")
for x in mycursor:
  print(x)
print()

# method definition: by mentioning "GET", "POST", "DELETE" in methods=[], we allow the client side (in our case it is the rest-client.py)
# to have the corresponding ability to call requests.get/post/delete
# route http posts to this method
@app.route('/apiv1/add', methods=['POST'])
def addData():
    r = request
    try:
        shopping_data_encoded = json.loads(r.data)['shopping']
        shopping_data_decoded = base64.b64decode(shopping_data_encoded) 
        # this decoded data from above is in bytes but not in dict since we used json.loads on the encoded file but not the decoded one
        # therefore we need to load it again to get dict type file
        shopping_data = json.loads(shopping_data_decoded) 
        
        # intert data into the table
        print("Now start adding value into the table!")
        # # why use %s but not %d for integer values id and price as placeholder: https://stackoverflow.com/questions/20818155/not-all-parameters-were-used-in-the-sql-statement-python-mysql
        # sql = f"INSERT INTO {tableName} (ID, Name, Product, Price, Date) VALUES (%s, %s, %s, %s, %s)"
        # val = [
        #     (id, shopping_data['name'], shopping_data['product'], float(shopping_data['price']), shopping_data['date'])
        # ]
        # mycursor.executemany(sql, val) # use mycursor.execute(sql, val) if we have one line of val to put
        # mydb.commit()
        # print(mycursor.rowcount, "record inserted.\n")
        
        print("pushing into redis!")
        sql_command_list = [str(shopping_data['name']), str(shopping_data['product']), str(float(shopping_data['price'])), str(shopping_data['date'])]
        sql_command_string = ','.join(sql_command_list)
        print("current command is: " + sql_command_string + "\n")
        redisClient.lpush("sql_command", str(sql_command_string)) 
        
        # use the following command to delete all value related to the given key
        # redisClient.delete("hash_for_worker")
        
        print("length right now at lpush stage is: " + str(redisClient.llen("sql_command")) + "\n")
        
        # wait till worker finishing process this mp3 file and pop it out from redis
        # in general, there's only gonna have 1 file in redis between the following process 
        # rest post data to redis - worker process it and upload everything to minio 
        # - worker pop it out from redis - rest post another data to redis
        while (redisClient.llen("sql_command") != 0):
            print("Waiting for Worker to finish processing this mp3 file...")
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
        # add all data in the table to element array
        mycursor.execute(f"SELECT * FROM {tableName}")
        myresult = mycursor.fetchall()
        element = []
        for x in myresult:
            element.append(str(x))
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
        # add all data in the table to element array
        mycursor.execute(f"SELECT SUM(Price) FROM {tableName}")
        myresult = mycursor.fetchall() # return in form as [(value,)]
        sum = myresult[0][0] # [0][0] to get that value from returned list, which is the total price
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
        # add all data in the table to element array
        mycursor.execute(f"SELECT * FROM {tableName} ORDER BY {orderByValue} {asc_desc}")
        myresult = mycursor.fetchall()
        element = []
        for x in myresult:
            element.append(str(x))
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
        print(f"drop the current row with id {id_to_delete} from table!\n")
        sql = f"DELETE FROM {tableName} WHERE ID = {id_to_delete}"
        mycursor.execute(sql)
        response = {f"Successfully deleted the row with id {id_to_delete} from SQL database!"}

        # add the id of the row we want to delete to deleted table
        # DO NOT ADD SAME VALUE MUTIPLE TIMES, otherwise the comming id for new values in data table will increase as well
        print(f"add the id: {id_to_delete} of the data we want to delete to deleted table!\n")
        # normal INSERT INTO but with WHERE NOT EXISTS to check duplications
        # reference: https://stackoverflow.com/questions/3164505/mysql-insert-record-if-not-exists-in-table
        sql = f"INSERT INTO {deleteTableName} SELECT * FROM (SELECT ({int(id_to_delete)}) ) AS tmp WHERE NOT EXISTS (SELECT ID FROM {deleteTableName} WHERE ID = {int(id_to_delete)}) LIMIT 1"
        mycursor.execute(sql)
        mydb.commit()
        print("add into deleted table successfully! Now deleted table contains:")
        # add all data in the table to element array
        mycursor.execute(f"SELECT * FROM {deleteTableName}")
        myresult = mycursor.fetchall()
        element = []
        for x in myresult:
            print(str(x))
        print()

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
        print("drop the current table!\n")
        sql = f"DROP TABLE {tableName}, {deleteTableName}"
        mycursor.execute(sql)
        response = {"Successfully deleted all tables from SQL database!"}

    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'Failed to delete table in SQL database.'}

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

@app.route('/apiv1/track/<string:songName>/<string:instrumentName>', methods=['GET']) # <string:songhash>
def retrieveTrack(songName, instrumentName): # retrieve the track ( any of bass.mp3, vocals.mp3, drums.mp3, other.mp3) as a binary download
    r = request

    file_to_download = "data/output/mdx_extra_q/" + songName + '/' + instrumentName

    try:
        # download the file here
        minioClient.fget_object(bucketname, file_to_download, "data/downloadForTrack/"+ songName + '/' + instrumentName)
        response = {'Download success! Now Playing the music.'}

    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'Failed to download the track from MinIO, target file in the corresponding does not exist'}

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/remove/<string:songName>/<string:instrumentName>', methods=['GET'])
def removeTrack(songName, instrumentName): # remove the corresponding track
    r = request
    file_to_remove = "data/output/mdx_extra_q/" + songName + '/' + instrumentName

    try:
        minioClient.remove_object(bucketname, file_to_remove)
        response = {'Remove success!'}

    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'Failed to remove the track from MinIO, target file in the corresponding does not exist'}

    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# start flask app
app.run(host="0.0.0.0", port=5000)
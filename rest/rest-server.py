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

# set minio host and port for connection
minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

minioClient = Minio(minioHost,
               secure=False,
               access_key=minioUser,
               secret_key=minioPasswd)

bucketname='CSCI5253-Project'
sqldatabasename = 'TEST_DB'#'project_database'


print("connecting to MySQL server...\n")

mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="test1234")

mycursor = mydb.cursor() # mycursor now reference to the whole sql server
print("Successfully connected to the SQL database!\n")

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

# create the table we need if it not exits
mycursor.execute("CREATE TABLE if not exists customers (name VARCHAR(255), address VARCHAR(255))")

print("Tables in the current database:")
mycursor.execute("SHOW TABLES")
for x in mycursor:
  print(x)
print()

# intert data into the table
print("Now start adding value into the table!")
sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
val = [
  ('Peter', 'Lowstreet 4'),
  ('Amy', 'Apple st 652'),
  ('Hannah', 'Mountain 21'),
  ('Michael', 'Valley 345'),
  ('Sandy', 'Ocean blvd 2'),
  ('Betty', 'Green Grass 1'),
  ('Richard', 'Sky st 331'),
  ('Susan', 'One way 98'),
  ('Vicky', 'Yellow Garden 2'),
  ('Ben', 'Park Lane 38'),
  ('William', 'Central st 954'),
  ('Chuck', 'Main Road 989'),
  ('Viola', 'Sideway 1633')
]
mycursor.executemany(sql, val) # use mycursor.execute(sql, val) if we only have 1 line val
mydb.commit()
print(mycursor.rowcount, "record inserted.\n")

# print all data in the table
mycursor.execute("SELECT * FROM customers")
myresult = mycursor.fetchall()
print("Now value in the table are:")
for x in myresult:
  print(x)
print()

# drop the table we created
print("drop the current table!\n")
sql = "DROP TABLE customers"
mycursor.execute(sql)

print("Tables in the current database:")
mycursor.execute("SHOW TABLES")
for x in mycursor:
  print(x)
print()























# method definition: by mentioning "GET", "POST", "DELETE" in methods=[], we allow the client side (in our case it is the rest-client.py)
# to have the corresponding ability to call requests.get/post/delete
# route http posts to this method
@app.route('/apiv1/separate', methods=['POST'])
def takeMp3():
    r = request
    try:
        mp3_string = json.loads(r.data)['mp3'] # get the mp3 hash value from disctionary file transferred from JSON file
        mp3_data = base64.b64decode(mp3_string) # decode the music here that was encoded in client side
        mp3_filename = json.loads(r.data)['callback']['data']['mp3'] # actual hash for the mp3 file
        len_of_mp3 = len(mp3_string)


    except Exception as e:
        print(e) # print the error report if we faced the exception
        response = {'not working!, error: ' + str(e)}

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
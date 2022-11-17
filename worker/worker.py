import sys
import redis
import os
import platform
from minio import Minio

import glob

import mysql.connector
from mysql.connector import Error
import pandas as pd

pw = 'test1234' # password created in MySQL server
infoKey = "{}.rest.info".format(platform.node())
debugKey = "{}.rest.debug".format(platform.node())

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379
redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"
bucketname='CSCI5253-Project'

def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def log_debug(message, key=debugKey):
    print("DEBUG:", message, file=sys.stdout)
    redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
    redisClient.lpush('logging', f"{debugKey}:{message}")



def log_info(message, key=infoKey):
    print("INFO:", message, file=sys.stdout)
    redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
    redisClient.lpush('logging', f"{infoKey}:{message}")

try:

    log_debug("minio client setup")
    minioClient = Minio(minioHost,
                secure=False,
                access_key=minioUser,
                secret_key=minioPasswd)
    log_debug("connecting with MySQL server")
    connection = create_server_connection("localhost", "root", pw)
    log_debug("successfully connected with MySQL server!")

        

except Exception as e:
    print(e) # print the error report if we faced the exception
    log_info("exception raised: " + str(e))


#!/usr/bin/python3

import os
import sys
import logging
from pymongo import MongoClient

log = logging.getLogger("mongodb")

class MongoDB:
    """ class to manipule mongodb database """

    def __init__(self):
        """ init MongoDB class """
        try:
            self.client = MongoClient(
                host=os.environ["MONGODB_HOST"],
                port=int(os.environ["MONGODB_PORT"]),
                username=os.environ["MONGODB_USER"],
                password=os.environ["MONGODB_PWD"],
                authSource="admin",
                authMechanism='SCRAM-SHA-256')
        except Exception:
            log.error("environment variable to access mongodb not found!")
            sys.exit(1)
        #access database
        self.db = self.client['twitter-app']
        #create  collection
        self.tweets = self.db["tweets"]

    def mongo_insert_one(self, value):
        """ mongo insert one value by dict obj """
        try:
            return self.tweets.insert_one(dict(value))
        except Exception as e:
            log.error("mongo_insert_one method error: {}".format(e))

    def mongo_drop_collection(self):
        """ mongo drop tweets collection """
        try:
            self.tweets.drop()
        except Exception as e:
            log.error("mongo_drop_collection method error: {}".format(e))

if __name__ == '__main__':
    pass
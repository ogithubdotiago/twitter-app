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

    def mongo_find_all(self):
        """ mongo find all obj """
        try:
            _all = self.tweets.find({})
            return _all
        except Exception as e:
            log.error("mongo_find_all method error: {}".format(e))

    def mongo_find_sort(self):
        """ mongo query, top five users of the collected, 
            who have more followers. 
        """
        try:
            sort_list = list()
            sort = self.tweets.find({}).sort('followers', -1).limit(5)
            for s in sort:
                new_dict = dict()
                new_dict["name"] = s["name"]
                new_dict["followers"] = s["followers"]
                sort_list.append(new_dict)
            return sort_list
        except Exception as e:
            log.error("mongo_find_sort method error: {}".format(e))

    def mongo_total_post_by_hour(self):
        """ mongo query, total posts grouped by hour of day """
        try:
            def edit_dict(d):
                convert = dict()
                for k,v in d.items():
                    if k == "_id":
                        convert['hour'] = v
                    convert[k] = v
                del convert['_id']
                return convert
            result_list = list()
            query = [{"$group":{"_id":"$hour","count":{"$sum":1}}}]
            for r in self.tweets.aggregate(query):
                result_list.append(edit_dict(r))
            return result_list
        except Exception as e:
            log.error("mongo_total_post_by_hour method error: {}".format(e))

    def mongo_total_tag_by_location(self):
        """ mongo query, total posts for each #tag by language """
        try:
            result_list = list()
            query = [{"$group":{"_id":{"tag":"$tag","location":"$location"},"count":{"$sum":1}}}]
            for r in self.tweets.aggregate(query):
                new_dict = dict()
                new_dict["tag"] = r["_id"]["tag"]
                new_dict["location"] = r["_id"]["location"]
                new_dict["count"] = r["count"]
                result_list.append(new_dict)
            return result_list
        except Exception as e:
            log.error("mongo_total_tag_by_location method error: {}".format(e))

if __name__ == '__main__':
    pass

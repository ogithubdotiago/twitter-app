#!/usr/bin/python3

import os
import sys
import time
import logging
import urllib.parse
from datetime import datetime
from modules.database import MongoDB
from modules.gettweet import GetTweets

#config log
file_log = os.path.basename(__file__).replace('.py', '.log')
fmt=("{'time':'%(asctime)s','name':'%(name)s','level':'%(levelname)s','message':'%(message)s'}")
formatter = logging.Formatter(fmt)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

#log main
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(stream_handler)

#log gettweets
log_gettweets = logging.getLogger("gettweets")
log_gettweets.setLevel(logging.INFO)
log_gettweets.addHandler(stream_handler)

#log mongodb
log_mongodb = logging.getLogger("mongodb")
log_mongodb.setLevel(logging.INFO)
log_mongodb.addHandler(stream_handler)

#log path
try:
    path_log = os.environ["LOG_PATH"]
except KeyError:
    log.error("environment variable to config log not found!")
    sys.exit(1)
if os.environ["LOG_FILE"] == "true":
    file_handler = logging.FileHandler("{}/{}".format(path_log, file_log))
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    log_gettweets.addHandler(file_handler)
    log_mongodb.addHandler(file_handler)

#intance class
db = MongoDB()
tweets = GetTweets()

class Backend():
    """ backend responsible for collecting tweets 
        by tag and saving to the database. 
    """

    def __init__(self):
        """ init Backend class. """
        self.tweet_hashtags = [
            "#openbanking" , "#remediation", "#devops",
            "#microservices", "#observability", "#oauth",
            "#metrics", "#logmonitoring", "#opentracing",
            "#sre"]
        self.tweet_counts = 100

    def build_json_tweets(self, text, date, hour, name, follow, location, tag):
        """ builds json obj. """
        data = dict()
        data["text"] = text
        data["date"] = date
        data["hour"] = hour
        data["name"] = name
        data["followers"] = follow
        data["location"] = location
        data["tag"] = tag
        return data

    def create_obj_tweets(self):
        """ creates a list with all tweets filtered by tag
            in json format to input on mongodb database. 
        """
        try:
            tweet_list = list()
            tweets_access_token = tweets.get_access_token()
            for tag in self.tweet_hashtags:
                t = tweets.get_tweet_data(tweets_access_token, tag, self.tweet_counts)
                for s in t["statuses"]:
                    d = datetime.strptime(
                        s.get("created_at"), '%a %b %d %H:%M:%S +0000 %Y')
                    tweet_list.append(self.build_json_tweets(
                        s.get("text"),
                        s.get("created_at"),
                        d.hour,
                        s["user"].get("name"),
                        s["user"].get("followers_count"),
                        s.get("lang"),
                        urllib.parse.unquote(t["search_metadata"].get("query"))))
            return tweet_list
        except Exception as e:
            log.error(e)

    def insert_tweet_to_bd(self, tweets):
        """ insert tweets in mongodb database. """
        try:
            for tweet in tweets:
                db.mongo_insert_one(tweet)
        except Exception as e:
            log.error(e)

if __name__ == '__main__':

    backend = Backend()

    while True:
        """ runs the script every 5 minutes. """
        try:
            start = time.time()
            backend.insert_tweet_to_bd(backend.create_obj_tweets())
            end = time.time()
            log.info("tweet collection completed in {:f} seconds".format(end - start))
            time.sleep(300)
            if os.environ["MONGODB_DROP"] == "true":
                db.mongo_drop_collection()
        except KeyError:
            log.erro("environment variable to state database not found!")
        except KeyboardInterrupt:
            print("  Bye!")
            sys.exit(1)
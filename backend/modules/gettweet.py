#!/usr/bin/python3

import os
import sys
import base64
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

log = logging.getLogger("gettweets")

class GetTweets():
    """ class to connect in twitter api to collect tweets """

    def __init__(self):
        """ init GetTweets class """
        try:
            self.api_client_key = os.environ["TWITTER_API_CLIENT_KEY"]
            self.api_client_secret = os.environ["TWITTER_API_CLIENT_SECRET"]
        except Exception:
            log.error("environment variable to access api not found")
            sys.exit(1)

    def get_access_token(self):
        """ creates token to access api"""
        try:
            api_key_secret = "{}:{}".format(
                self.api_client_key, self.api_client_secret).encode("ascii")
            api_key_encoded_b64 = base64.b64encode(api_key_secret).decode("ascii")
            auth_url = "https://api.twitter.com/"
            auth_uri = "{}oauth2/token".format(auth_url)
            auth_headers = {
                "Authorization": "Basic {}".format(api_key_encoded_b64),
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
            }
            auth_data = {
                "grant_type": "client_credentials"
            }
            auth_resp = requests.post(auth_uri, 
                headers=auth_headers, data=auth_data, timeout=30)
            if auth_resp.status_code == 200:
                log.info("token created successfully")

            return auth_resp.json()['access_token']
        except Exception as e:
            log.error("error method get_access_token: {}".format(e))

    def get_tweet_data(self, token, tag, count):
        """ get tweets in twitter api by query tag and count """
        try:
            search_url = "https://api.twitter.com/"
            search_uri = "{}1.1/search/tweets.json".format(search_url)
            
            search_headers = {
                "Authorization": "Bearer {}".format(token)    
            }
            search_params = {
                "q": tag,
                "result_type": "recent",
                "count": count
            }
            search_resp = requests.get(search_uri, 
                headers=search_headers, params=search_params, timeout=30)
            if search_resp.status_code == 200:
                log.info("tweets tagged {} imported successfully".format(tag))
            return search_resp.json()
        except Exception as e:
            log.error("error method get_tweet_data: {}".format(e))

if __name__ == '__main__':
    pass
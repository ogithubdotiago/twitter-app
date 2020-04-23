#!/usr/bin/python3

import os
import sys
import json
import time
import socket
import logging
from bson import json_util
from modules.datebase import MongoDB
from flask_httpauth import HTTPBasicAuth
from flask import Flask, jsonify, make_response, render_template, url_for
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics

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

#log flask_werkzeug
log_flask = logging.getLogger('werkzeug')
log_flask.addHandler(stream_handler)

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
    log_flask.addHandler(file_handler)
    log_mongodb.addHandler(file_handler)

#obj mondodb
db = MongoDB()

#instance flask app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

#instance auth
auth = HTTPBasicAuth()

#metrics by prometheus
metrics = GunicornPrometheusMetrics(app)

@auth.get_password
def get_password(username):
    if username == 'admin':
        return 'admin'
    return None

@app.route('/')
def follow():
    return render_template('follow.html', 
        title='Tweets by Followers', 
        follow=db.mongo_find_sort())

@app.route('/hour')
def hour():
    return render_template('hour.html', 
        title='Tweets by Time', 
        hour=db.mongo_total_post_by_hour())

@app.route('/location')
def location():
    return render_template('location.html', 
        title='Tweets by Location', 
        location=db.mongo_total_tag_by_location())

@app.route('/health')
def probe():
    try:
        host = os.environ["MONGODB_HOST"]
        port = int(os.environ["MONGODB_PORT"])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try :
            s.connect((host, port))
            return jsonify({'database': 'up'}), 200
        except :
            return jsonify({'database': 'down'}), 500
    except KeyError:
        log.error("environment variable to access mongodb not found!")
        sys.exit(1)
    except Exception as e:
        log.error(e)

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify( { 'error': 'Bad Request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not Found' } ), 404)

@app.errorhandler(500)
def server_error(error):
    return make_response(jsonify( { 'error': 'Internal Server' } ), 500)

@app.route('/api/v1/tweets', methods = ['GET'])
@auth.login_required
def get_tweets():
    try:
        t = list()
        tweets = db.mongo_find_all()
        for tweet in tweets:
            t.append(tweet)
        return jsonify(json.loads(json_util.dumps(t)))
    except Exception as e:
        log.error(e)

@app.route('/api/v1/tweets/followers', methods = ['GET'])
@auth.login_required
def get_followers():
    try:
        follow = db.mongo_find_sort()
        return jsonify(json.loads(json_util.dumps(follow)))
    except Exception as e:
        log.error(e)

@app.route('/api/v1/tweets/posts', methods = ['GET'])
@auth.login_required
def get_posts():
    try:
        posts = db.mongo_total_post_by_hour()
        return jsonify(posts)
    except Exception as e:
        log.error(e)

@app.route('/api/v1/tweets/location', methods = ['GET'])
@auth.login_required
def get_location():
    try:
        location = db.mongo_total_tag_by_location()
        return jsonify(location)
    except Exception as e:
        log.error(e)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
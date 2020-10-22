import os

import jsonlines
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_basicauth import BasicAuth

from main import TwitterBot

load_dotenv()

COMPLAINTS_FILE = 'complaints.jsonl'
TWEET_ID_FILE = 'last_tweet_id.txt'

BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")
BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = BASIC_AUTH_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = BASIC_AUTH_PASSWORD

basic_auth = BasicAuth(app)

def createFileIfNotExist(filename):
    with open(filename, 'a+') as outfile:
        outfile.close()

# Create a cron job like so crontab -e add this username and password from .env
# * * * * * /opt/local/bin/curl -X GET https://falken:joshua@YOUR_WEB_LINK/cron/tweets
@app.route('/cron/tweets', methods=['GET'])
@basic_auth.required
def get_new_tweets():
    createFileIfNotExist(TWEET_ID_FILE)
    with open(TWEET_ID_FILE, 'r') as tweet_id_file:
        last_tweet_id = tweet_id_file.read()
    try:
        last_tweet_id_int = int(last_tweet_id)
    except:
        last_tweet_id_int = 1
    twitterBot = TwitterBot()
    latest_tweet_id = twitterBot.get_statuses(since_id=last_tweet_id_int)
    with open(TWEET_ID_FILE, 'w') as tweet_id_file:
        tweet_id_file.write(str(latest_tweet_id))
    return "success"

@app.route('/tweets', methods=['GET'])
@basic_auth.required
def tweets():
    createFileIfNotExist(COMPLAINTS_FILE)
    complaints_list = []
    with jsonlines.open(COMPLAINTS_FILE, mode='r') as reader:
        for obj in reader.iter(type=dict, skip_empty=True, skip_invalid=True):
            complaints_list.append(obj)
    if os.path.exists(COMPLAINTS_FILE):
        os.remove(COMPLAINTS_FILE)
    return jsonify(complaints_list)

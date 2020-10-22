import os
import tweepy
import jsonlines

from dotenv import load_dotenv

load_dotenv()

COMPLAINTS_FILE = "complaints.jsonl"

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

def createFileIfNotExist(filename):
    with open(filename, 'a+') as outfile:
        outfile.close()

class TwitterBot:

    def __init__(self):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth,  wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def get_statuses(self, since_id=1):
        statuses = []
        statuses = self.api.mentions_timeline(since_id=since_id)
        createFileIfNotExist(COMPLAINTS_FILE)
        if len(statuses) > 0:
            with jsonlines.open(COMPLAINTS_FILE, mode='a') as writer:
                new_since_id = since_id
                for status in statuses:
                    writer.write(status._json)
                    new_since_id = max(new_since_id, status.id)
            return new_since_id
        return since_id


if __name__ == "__main__":
    twitterBot = TwitterBot()
    print(twitterBot.get_statuses(since_id=1195871282102820864))
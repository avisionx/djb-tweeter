import os

import jsonlines
import tweepy
from dotenv import load_dotenv

from helpers import ComplaintParser

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
        self.api = tweepy.API(auth,  wait_on_rate_limit=True,
                              wait_on_rate_limit_notify=True)

    def get_statuses(self, since_id=1):
        statuses = []
        statuses = self.api.mentions_timeline(since_id=since_id)
        createFileIfNotExist(COMPLAINTS_FILE)
        if len(statuses) > 0:
            with jsonlines.open(COMPLAINTS_FILE, mode='a') as writer:
                new_since_id = since_id
                for status in statuses:
                    jsonTweet = status._json
                    data, reply_need_help = ComplaintParser().parse(status.text)
                    if reply_need_help:
                        reply = """
                        Thank you for contacting Delhi Jal Board! You're requested to reply in the 
below given pattern ONLY for speedy redressal:

NAME:
ADDRESS:
CONTACT NO.:
KNO:
ISSUE:

Alternatively, you can DM the above sought details in our inbox.
                        """
                    else:
                        jsonTweet["formated_data"] = data
                        reply = "Thank you for contacting Delhi Jal Board! Your complaint has been registered with us. We'll try and resolve it as soon as possible."
                    writer.write(jsonTweet)
                    self.reply_to_status(reply, status.id)
                    new_since_id = max(new_since_id, status.id)
            return new_since_id
        return since_id

    def reply_to_status(self, reply, in_reply_to_status_id):
        try:
            status = self.api.update_status(
                status=reply, in_reply_to_status_id=in_reply_to_status_id, auto_populate_reply_metadata=True)
        except Exception as inst:
            return None
        return status


if __name__ == "__main__":
    twitterBot = TwitterBot()
    print(twitterBot.reply_to_status())

#from PyQt5 import QtCore
import profile
import webbrowser
import json
import tweepy
import requests
from PyQt5.QtWidgets import QInputDialog

class StreamListener(tweepy.StreamListener):
    """receive streaming and classify messages"""
    def __init__(self, callback):
        super(StreamListener, self).__init__()
        self.callback = callback

    def on_status(self, status):
        """send tweets to main gui"""
        self.callback(status.text)

    def on_error(self, status_code):
        """print error code when receive error"""
        print(status_code)
        if status_code == 420:
            print(str(status_code))
            return False

def openstream(api, callback):
    """
    create and start stream with async mode which enables parallel
    processing of gui event loop and stream wait loop
    """
    stream = tweepy.Stream(auth=api.auth, listener=StreamListener(callback))
    stream.userstream(async=True)
    return stream

def connect(accesstoken, accesssecret):
    """create api object from saved keys"""
    auth = tweepy.OAuthHandler(profile.CONSUMER_KEY, profile.CONSUMER_SECRET)
    auth.set_access_token(accesstoken, accesssecret)
    api = tweepy.API(auth)
    return api

def authentication():
    """register new account and save AT and AS to local file"""
    consumerkey = profile.CONSUMER_KEY
    consumersecret = profile.CONSUMER_SECRET
    auth = tweepy.OAuthHandler(consumerkey, consumersecret)

    redirect_url = auth.get_authorization_url()
    webbrowser.open(redirect_url)

    verifier, ok = QInputDialog.getText(None, 'PIN code', 'input pin code') # PINコード入力用ダイアログ
    if not verifier:
        return
    verifier = verifier.strip()

    auth.get_access_token(verifier)
    accesstoken = auth.access_token
    accesssecret = auth.access_token_secret

    auth.set_access_token(accesstoken, accesssecret)
    api = tweepy.API(auth)
    screen_name = api.me().screen_name

    with open('auth.json', 'r') as f:
        authkeys = json.load(f)
    if not screen_name in authkeys["Twitter"]:
        authkeys["Twitter"][screen_name] = {"ACCESS_TOKEN":accesstoken, "ACCESS_SECRET":accesssecret}
    with open('auth.json', 'w')as f:
        json.dump(authkeys, f, indent=2)
    return api, screen_name

def geticon(api, screen_name):
    """get icon image with api and screen_name and save it to local"""
    url = api.me().profile_image_url_https

    response = requests.get(url, allow_redirects=False)
    image = response.content

    imagename = 'images/' + screen_name + '.jpg'
    with open(imagename, 'wb') as f:
        f.write(image)

if __name__ == "__main__":
    authentication()

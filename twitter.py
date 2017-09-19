import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import profile
import webbrowser
import tweepy
import json
import os
import requests

def connect():
    auth = tweepy.OAuthHandler(profile.CONSUMER_KEY, profile.CONSUMER_SECRET)
    auth.set_access_token(self.auth["Twitter"][""]["ACCESS_TOKEN"], self.auth["Twitter"][""]["ACCESS_SECRET"])

def authentication():
    #app = QApplication(sys.argv)

    CONSUMER_KEY = profile.CONSUMER_KEY
    CONSUMER_SECRET = profile.CONSUMER_SECRET
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

    redirect_url = auth.get_authorization_url()
    webbrowser.open(redirect_url) # 認証画面を表示する

    verifier, ok = QInputDialog.getText(None, 'PIN code', 'input pin code') # PINコード入力用ダイアログ
    if not verifier:
        return
    verifier = verifier.strip()

    auth.get_access_token(verifier)
    ACCESS_TOKEN = auth.access_token
    ACCESS_SECRET = auth.access_token_secret

    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    SCREEN_NAME = api.me().screen_name

    with open('auth.json', 'r') as f:
        authkeys = json.load(f)
    if not SCREEN_NAME in authkeys["Twitter"]:
        authkeys["Twitter"][SCREEN_NAME] = {"ACCESS_TOKEN":ACCESS_TOKEN, "ACCESS_SECRET":ACCESS_SECRET}
    with open('auth.json', 'w')as f:
        json.dump(authkeys, f, indent=2)

def geticon(auth):
    api = tweepy.API(auth)
    url = api.me().profile_image_url_https

    response = requests.get(url, allow_redirects=False)
    image = response.content
    imagename = api.me().screen_name + '.jpg'
    with open(imagename, 'wb') as f:
        f.write(image)

if __name__ == "__main__":
    authentication()
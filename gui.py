#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QScrollArea, QLabel)
from PyQt5.QtCore import QTimer, QSize, QByteArray
import PyQt5.QtGui
import twitter

class MyWindow(QWidget):
    """main window"""
    def __init__(self):
        super().__init__()
        self.auths = {}
        self.activeaccounts = []
        self.streams = []
        self.tweets = []

        self.init_main()
        self.init_accounts()
        self.init_tweets()
        self.init_widgets()

        self.show()
        sys.exit(app.exec_())

    def init_main(self):
        """options of main window"""
        self.setGeometry(300, 100, 300, 650)
        self.setWindowTitle("tomoebi")
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timeline)
        self.timer.start(500)

    def init_tweets(self):
        """create initial tweet"""
        self.tweets = ["start"]

    #initialize widgets
    def init_widgets(self):
        """initialize widgets"""
        #upper half of main window consists of accounts, composer and buttons
        self.imageviewer = QLabel()
        self.compose_vbox = QVBoxLayout()
        self.accounts_hbox = QHBoxLayout()
        self.accbuttons = []
        for a in self.auths:
            accbutton = QPushButton(self)
            accbutton.setWhatsThis(a)
            accbutton.setCheckable(True)
            accbutton.toggled.connect(self.choose_account)
            accbutton.setIcon(PyQt5.QtGui.QIcon('images/'+a+'.jpg'))
            accbutton.setIconSize(QSize(48, 48))
            self.accounts_hbox.addWidget(accbutton)
        self.addaccbutton = QPushButton("+", self)
        self.addaccbutton.clicked.connect(self.add_account)
        self.accounts_hbox.addWidget(self.addaccbutton)
        self.composer = QTextEdit(self)
        #self.composer.setPlaceholderText("いまなにしてる？")
        self.composer.setMaximumHeight(100)

        self.compose_hbox = QHBoxLayout()
        self.imagebutton = QPushButton("image", self)
        self.submitbutton = QPushButton("tweet", self)
        self.submitbutton.clicked.connect(self.submit)

        self.compose_hbox.addWidget(self.imagebutton)
        self.compose_hbox.addWidget(self.submitbutton)
        self.compose_vbox.addWidget(self.imageviewer)
        self.compose_vbox.addLayout(self.accounts_hbox)
        self.compose_vbox.addWidget(self.composer)
        self.compose_vbox.addLayout(self.compose_hbox)

        #lower half of main window consists of timeline
        l = QTextEdit()
        l.setPlainText(self.tweets[0])
        l.setReadOnly(True)
        self.inner = QWidget()
        self.timeline_vbox = QVBoxLayout(self.inner)
        self.timeline_vbox.addWidget(l)
        self.tweets = []
        self.timeline_vbox.addStretch()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.inner)

        #integrate upper and lower part of main window
        self.whole_vbox = QVBoxLayout()
        self.whole_vbox.addLayout(self.compose_vbox)
        self.whole_vbox.addWidget(self.scroll)
        self.setLayout(self.whole_vbox)

    #initialize registered accounts
    def init_accounts(self):
        """load account AT and AS from local and create api object and stream"""
        if not os.path.exists("images"):
            os.mkdir("images")
        if os.path.isfile("auth.json"):
            with open('auth.json', 'r') as f:
                authdic = json.load(f)
            for k, v in authdic["Twitter"].items():
                api = twitter.connect(v["ACCESS_TOKEN"], v["ACCESS_SECRET"])
                self.auths[k] = api
                self.streams.append(twitter.openstream(api, self.receive_tweet))
                if not os.path.isfile("images/"+k+".jpg"):
                    twitter.geticon(api, k)

        else:
            default = {
                "Twitter"  : {},
                "Mastodon" : {}
            }
            with open('auth.json', 'w') as f:
                json.dump(default, f, indent=2)
            self.authdic = {}

    def add_account(self):
        """add account and register it to local file"""
        api, screen_name = twitter.authentication()
        self.auths[screen_name] = api
        self.streams.append(twitter.openstream(api, self.receive_tweet))
        twitter.geticon(api, screen_name)
        accbutton = QPushButton(self)
        accbutton.setWhatsThis(screen_name)
        accbutton.setCheckable(True)
        accbutton.toggled.connect(self.choose_account)
        accbutton.setIcon(PyQt5.QtGui.QIcon('images/'+screen_name+'.jpg'))
        accbutton.setIconSize(QSize(48, 48))
        self.accounts_hbox.insertWidget(self.accounts_hbox.count() - 1, accbutton)

    def choose_account(self):
        """
        called when accbutton are toggled.
        add or remove active accounts
        """
        acc = self.sender()
        if acc.isChecked():
            self.activeaccounts.append(acc.whatsThis())
        else:
            self.activeaccounts.remove(acc.whatsThis())

    def receive_tweet(self, status):
        """called when stream receive a tweet"""
        self.tweets.append(status)

    def update_timeline(self):
        """called every 500ms and update gui timeline according to self.tweets"""
        for t in self.tweets:
            tweet = self.create_tweet(t)
            self.timeline_vbox.insertWidget(0, tweet)
            if "media" in t.entities:
                image = twitter.getimage(t.entities["media"][0]["media_url_https"])
                pixmap = PyQt5.QtGui.QPixmap()
                pixmap.loadFromData(QByteArray(image))
                self.imageviewer.setPixmap(pixmap)
        self.tweets = []
    
    def create_tweet(self, t):
        text = "@" + t.user.screen_name + "\n" + t.text      
        tweettext = QTextEdit()
        tweettext.setPlainText(text)
        tweettext.setReadOnly(True)
        return tweettext

    def submit(self):
        """called when tweet button is pressed and submit tweet"""
        submittext = self.composer.toPlainText()
        for a in self.activeaccounts:
            self.auths[a].update_status(submittext)
        self.composer.setPlainText("")

    def closeEvent(self, event):
        """called when gui window is closed and terminate all streams and thread"""
        for s in self.streams:
            s.disconnect()
        os._exit(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MyWindow()

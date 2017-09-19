#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os , json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import PyQt5.QtGui
import twitter

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.auths = []
        self.screen_names = []

        self.init_main()
        self.init_accounts()
        self.init_tweets()
        self.init_widgets()

        self.show()
        sys.exit(app.exec_())

    #options of main window
    def init_main(self):
        self.setGeometry(300, 100, 300, 500)
        self.setWindowTitle("tomoebi")

    #create test tweets
    def init_tweets(self):
        self.tweets = ["one", "two", "three"]

    #initialize widgets
    def init_widgets(self):
        #upper half of main window consists of accounts, composer and buttons
        self.compose_vbox = QVBoxLayout()
        self.accounts_hbox = QHBoxLayout()
        self.accountButtons = []
        for a in self.screen_names:
            accountButton = QPushButton(self)
            accountButton.setIcon(PyQt5.QtGui.QIcon('images/'+a+'.jpg'))
            accountButton.setIconSize(QSize(48, 48))
            self.accounts_hbox.addWidget(accountButton)
        self.addAccountButton = QPushButton("+", self)
        self.addAccountButton.clicked.connect(self.addaccount)
        self.accounts_hbox.addWidget(self.addAccountButton)
        self.composer = QTextEdit(self)
        self.composer.setPlaceholderText("いまなにしてる？")
        self.composer.setMaximumHeight(100)

        self.compose_hbox = QHBoxLayout()
        self.imageButton = QPushButton("image", self)
        self.submitButton = QPushButton("tweet", self)
        self.submitButton.clicked.connect(self.submit)

        self.compose_hbox.addWidget(self.imageButton)
        self.compose_hbox.addWidget(self.submitButton)
        self.compose_vbox.addLayout(self.accounts_hbox)
        self.compose_vbox.addWidget(self.composer)
        self.compose_vbox.addLayout(self.compose_hbox)

        #lower half of main window consists of timeline
        self.tweetboxes = []
        for t in self.tweets:
            l = QTextEdit(self)
            l.setPlainText(t)
            l.setReadOnly(True)
            self.tweetboxes.append(l)
        self.inner = QWidget()
        self.timeline_vbox = QVBoxLayout(self.inner)
        for tbox in reversed(self.tweetboxes):
            self.timeline_vbox.addWidget(tbox)
        self.timeline_vbox.addStretch()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.inner)

        #integrate upper and lower part of mwin window
        self.whole_vbox = QVBoxLayout()
        self.whole_vbox.addLayout(self.compose_vbox)
        self.whole_vbox.addWidget(self.scroll)
        self.setLayout(self.whole_vbox)

    #initialize registered accounts
    def init_accounts(self):
        if not os.path.exists("images"):
            os.mkdir("images")
        if os.path.isfile("auth.json"):
            with open('auth.json', 'r') as f:
                authdic = json.load(f)
            for k, v in authdic["Twitter"].items():
                self.screen_names.append(k)
                api = twitter.connect(v["ACCESS_TOKEN"], v["ACCESS_SECRET"])
                self.auths.append(api)
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

    def addaccount(self):
        api, screen_name = twitter.authentication()
        self.auths.append(api)
        self.screen_names.append(screen_name)
        twitter.geticon(api, screen_name)
        accountButton = QPushButton(self)
        accountButton.setIcon(PyQt5.QtGui.QIcon('images/'+screen_name+'.jpg'))
        accountButton.setIconSize(QSize(48, 48))
        self.accounts_hbox.insertWidget(self.accounts_hbox.count() - 1, accountButton)

    def update_timeline(self, text):
        l = QTextEdit(self)
        l.setPlainText(text)
        l.setReadOnly(True)
        self.timeline_vbox.insertWidget(0, l)

    def submit(self):
        submittext = self.composer.toPlainText()
        self.update_timeline(submittext)
        self.composer.setPlainText("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MyWindow()

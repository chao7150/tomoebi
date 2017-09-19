#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os , json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import twitter

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_main()
        self.account_names = self.init_accounts()
        self.init_tweets()
        self.init_widgets()

        self.show()
        sys.exit(app.exec_())

    def init_main(self):
        self.setGeometry(300, 100, 300, 500)
        self.setWindowTitle("tomoebi")

    def init_tweets(self):
        self.tweets = ["one", "two", "three"]

    def init_widgets(self):
        self.compose_vbox = QVBoxLayout()
        self.accounts_hbox = QHBoxLayout()
        self.accountButtons = []
        for a in self.account_names:
            self.accountButtons.append(QPushButton(a, self))
            self.accounts_hbox.addWidget(self.accountButtons[-1])
        self.addAccountButton = QPushButton("+", self)
        self.addAccountButton.clicked.connect(twitter.authentication)
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

        self.whole_vbox = QVBoxLayout()
        self.whole_vbox.addLayout(self.compose_vbox)
        self.whole_vbox.addWidget(self.scroll)
        self.setLayout(self.whole_vbox)

    def init_accounts(self):
        accounts = []
        if os.path.isfile("auth.json"):
            with open('auth.json', 'r') as f:
                self.auth = json.load(f)
            accounts = list(self.auth["Twitter"].keys())
            accounts.extend(list(self.auth["Mastodon"].keys()))
            self.twitter_apis = {}
            for t in self.auth["Twitter"].values():
                twitter.connect(self.auth["Twitter"])
        else:
            default = {
                    "Twitter"  : {},
                    "Mastodon" : {}
            }
            with open('auth.json', 'w') as f:
                json.dump(default, f, indent=2)


        return accounts

    def update_timeline(self, text):
        l = QTextEdit(self)
        l.setPlainText(text)
        l.setReadOnly(True)
        print(l.document().size().height())
        self.timeline_vbox.insertWidget(0, l)

    def submit(self):
        submittext = self.composer.toPlainText()
        self.update_timeline(submittext)
        self.composer.setPlainText("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MyWindow()

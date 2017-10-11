#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QScrollArea, QMenu,
                             QLabel, QLineEdit, QSizePolicy)
from PyQt5.QtCore import QTimer, QSize, QByteArray, Qt
import PyQt5.QtGui
import twitter
import glob

class IconLabel(QLabel):
    def __init__(self, id, account, RTcallback, replycallback):
        QLabel.__init__(self)
        self.id = id
        self.account = account
        self.RTcallback = RTcallback
        self.replycallback = replycallback

    def contextMenuEvent(self, event):
        menu = QMenu()
        rtAction = menu.addAction("RT")
        replyAction = menu.addAction("Reply")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == rtAction:
            self.RTcallback(self.id, self.account)
        elif action == replyAction:
            self.replycallback(self.id, self.account)

class MyWindow(QWidget):
    """main window"""
    def __init__(self):
        super().__init__()
        self.auths = {}
        self.activeaccounts = []
        self.streams = []
        self.tweets = []
        self.tagarray = []
        self.tweettags = []
        self.receivetags = []
        self.following = []
        self.searchstream = None

        self.init_main()
        self.init_accounts()
        self.init_tweets()
        self.init_widgets()

        self.show()
        sys.exit(app.exec_())

    def init_main(self):
        """options of main window"""
        self.setGeometry(300, 100, 1000, 600)
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
        self.composer = QTextEdit()
        #self.composer.setPlaceholderText("いまなにしてる？")
        self.composer.setMaximumHeight(60)

        self.compose_hbox = QHBoxLayout()
        self.imagebutton = QPushButton("image", self)
        self.submitbutton = QPushButton("tweet", self)
        self.submitbutton.clicked.connect(self.submit)

        self.hashtag_hbox = QHBoxLayout()
        self.hashtagedit = QLineEdit(self)
        self.hashtagedit.setPlaceholderText("hashtags")
        self.hashtagbutton = QPushButton("set")
        self.hashtagbutton.setCheckable(True)
        self.hashtagbutton.toggled.connect(self.sethashtag)
        self.hashtag_hbox.addWidget(self.hashtagedit)
        self.hashtag_hbox.addWidget(self.hashtagbutton)

        self.compose_hbox.addWidget(self.imagebutton)
        self.compose_hbox.addWidget(self.submitbutton)
        self.compose_vbox.addLayout(self.accounts_hbox)
        self.compose_vbox.addWidget(self.composer)
        self.compose_vbox.addLayout(self.compose_hbox)
        self.compose_vbox.addLayout(self.hashtag_hbox)

        #lower half of main window consists of timeline
        l = QTextEdit()
        l.setPlainText(self.tweets[0])
        l.setReadOnly(True)
        l.setFixedHeight(350)
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

        #right half of the main window
        self.image_collumn = QVBoxLayout()
        self.imageinner = QWidget()
        self.imagetimeline = QVBoxLayout(self.imageinner)
        self.imagescroll = QScrollArea()
        self.imagescroll.setWidgetResizable(True)
        self.imagescroll.setWidget(self.imageinner)
        self.imagetext = QTextEdit()
        self.imagetext.setMaximumHeight(60)
        self.imagetext.setReadOnly(True)
        self.image_collumn.addWidget(self.imagetext)
        self.image_collumn.addWidget(self.imagescroll)

        self.whole_hbox = QHBoxLayout()
        self.whole_hbox.addLayout(self.whole_vbox)
        self.whole_hbox.addLayout(self.image_collumn)
        self.setLayout(self.whole_hbox)

    #initialize registered accounts
    def init_accounts(self):
        """load account AT and AS from local and create api object and stream"""
        if not os.path.exists("images"):
            os.mkdir("images")
        if os.path.isfile("auth.json"):
            with open('auth.json', 'r') as f:
                authdic = json.load(f)
            for name, keys in authdic["Twitter"].items():
                api = twitter.connect(keys["ACCESS_TOKEN"], keys["ACCESS_SECRET"])
                self.auths[name] = api
                #self.following = self.following + api.friends_ids(k)
                self.streams.append(twitter.open_userstream(api, self.receive_tweet, name))
                if not os.path.isfile("images/"+name+".jpg"):
                    twitter.getmyicon(api, name)
            #twitter.open_filterstream(self.auths["XXXX"], self.receive_tweet,
            #  "XXXX", [str(x) for x in self.following])
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
        self.streams.append(twitter.open_userstream(api, self.receive_tweet, screen_name))
        twitter.getmyicon(api, screen_name)
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

    def receive_tweet(self, status, name, icon):
        """called when stream receive a tweet"""
        self.tweets.append((status, name, icon))

    def update_timeline(self):
        """called every 500ms and update gui timeline according to self.tweets"""
        for t, name, icon in self.tweets:
            rtby = None
            if hasattr(t, "retweeted_status"):
                rtby = [t.user.profile_image_url_https, t.user.screen_name]
                t = t.retweeted_status
            tweet = self.create_tweet(t)
            tweet_hbox = QHBoxLayout()
            if icon:
                if not glob.glob("images/" + t.user.screen_name + ".*"):
                    twitter.geticon(t.user.profile_image_url_https, t.user.screen_name)
                icon = PyQt5.QtGui.QPixmap(glob.glob("images/" + t.user.screen_name + ".*")[0])
                scaled_icon = icon.scaled(QSize(48, 48), 1, 1)
                iconviewer = IconLabel(t.id, name, self.retweet, self.reply)
                iconviewer.setPixmap(scaled_icon)
                icon_vbox = QVBoxLayout()
                icon_vbox.addWidget(iconviewer, alignment=Qt.AlignTop)
                if rtby:
                    if not glob.glob("images/" + rtby[1] + ".*"):
                        twitter.geticon(*rtby)
                    icon = PyQt5.QtGui.QPixmap(glob.glob("images/" + rtby[1] + ".*")[0])
                    scaled_icon = icon.scaled(QSize(24, 24), 1, 1)
                    rticonviewer = QLabel()
                    rticonviewer.setPixmap(scaled_icon)
                    rticon_hbox = QHBoxLayout()
                    #rticon_hbox.addStretch()
                    rticon_hbox.addWidget(rticonviewer, alignment=(Qt.AlignRight|Qt.AlignTop))
                    icon_vbox.addLayout(rticon_hbox)
                    icon_vbox.addStretch()
                tweet_hbox.addLayout(icon_vbox)
            tweet_hbox.addWidget(tweet)
            favbutton = QPushButton("fav")
            favbutton.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
            favbutton.setCheckable(True)
            favbutton.toggled.connect(lambda: self.fav(t.id, name))
            tweet_hbox.addWidget(favbutton)
            self.timeline_vbox.insertLayout(0, tweet_hbox)
            #not working yet
            '''print(self.timeline_vbox.count())
            if self.timeline_vbox.count() > 15:
                deleteitem = self.timeline_vbox.itemAt(self.timeline_vbox.count() - 1)
                print(deleteitem)
                self.timeline_vbox.removeItem(deleteitem)'''
            if "media" in t.entities:
                images = twitter.get_allimages(self.auths[name], t.id)
                self.imagetext.setPlainText("@" + t.user.screen_name + "\n" + t.text)
                for n, _ in enumerate(images):
                    pixmap = PyQt5.QtGui.QPixmap()
                    pixmap.loadFromData(QByteArray(images[n]))
                    scaled = pixmap.scaled(QSize(320, 180), 1, 1)
                    imageviewer = QLabel()
                    imageviewer.setPixmap(scaled)
                    self.imagetimeline.insertWidget(0, imageviewer)
        self.tweets = []

    def create_tweet(self, t):
        """create tweet widget"""
        text = "@" + t.user.screen_name + "\n" + t.text
        tweetdocument = PyQt5.QtGui.QTextDocument()
        tweetdocument.setTextWidth(300) #this line is not working so it needs to be fixed someday
        tweetdocument.setPlainText(text)
        tweettext = QTextEdit()
        tweettext.setDocument(tweetdocument)
        tweettext.setReadOnly(True)
        tweettext.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tweettext.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tweettext.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tweettext.setAttribute(103)
        tweettext.show()
        tweettext.setFixedHeight(tweettext.document().size().height()
                                 + tweettext.contentsMargins().top()*2)
        return tweettext

    def submit(self):
        """called when tweet button is pressed and submit tweet"""
        if not self.activeaccounts:
            return
        submittext = self.composer.toPlainText()
        for t in self.tweettags:
            submittext = submittext + " " + t
        if not submittext:
            return
        for a in self.activeaccounts:
            self.auths[a].update_status(submittext)
        self.composer.setPlainText("")

    def fav(self, tweetid, name):
        '''favor or unfavor a tweet from an account from which the tweet was obtained'''
        switch = self.sender()
        if switch.isChecked():
            try:
                self.auths[name].create_favorite(tweetid)
            except:
                print("already favored")
        else:
            try:
                self.auths[name].destroy_favorite(tweetid)
            except:
                print("not favored")
    
    def retweet(self, id, account):
        self.auths[account].retweet(id)

    def reply(self, id, account):
        if not self.activeaccounts:
            return
        submittext = self.composer.toPlainText()
        if not submittext:
            return
        self.auths[account].update_status(submittext, in_reply_to_status_id=id, auto_populate_reply_metadata=True)
        self.composer.setPlainText("")

    def sethashtag(self):
        """set hashtab for receive and tweet"""
        switch = self.sender()
        if switch.isChecked():
            htinput = self.hashtagedit.text()
            htlist = htinput.strip().split()
            for t in htlist:
                if not t[0] == "*":
                    self.receivetags.append(t)
                    self.tweettags.append(t)
                else:
                    self.receivetags.append(t[1:])
            repl_screen_name = list(self.auths.keys())[0]
            self.searchstream = twitter.open_filterstream(
                self.auths[repl_screen_name], self.receive_tweet, repl_screen_name, self.receivetags
                )
        else:
            self.receivetags = []
            self.tweettags = []
            self.searchstream.disconnect()

    def closeEvent(self, event):
        """called when gui window is closed and terminate all streams and thread"""
        for s in self.streams:
            s.disconnect()
        os._exit(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MyWindow()

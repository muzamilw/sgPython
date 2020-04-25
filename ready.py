from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.clock import Clock
import os
from threading import Thread
import logging
import threading
import time
import datetime
from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
from botLogic import Bot

class Ready(Screen):

    t = None
    StartTime = None
    botThread = None
    botStop = False

    def on_enter(self):
        app = App.get_running_app()
        lblusername = self.ids['lblusername'] #Label(text="showing the log here")
        lblusername.text = app.api.authenticated_user_id
        app.api.feed_timeline()
        # try:
        #     from instagram_private_api import (
        #         Client, ClientError, ClientLoginError,
        #         ClientCookieExpiredError, ClientLoginRequiredError,
        #         __version__ as client_version)
        # except ImportError:
        #     import sys
        #     sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        #     from instagram_private_api import (
        #         Client, ClientError, ClientLoginError,
        #         ClientCookieExpiredError, ClientLoginRequiredError,
        #         __version__ as client_version)

   

    def startBot(self):
        app = App.get_running_app()
        label = self.ids['logLabel'] #Label(text="showing the log here")

        self.lblFollow =  self.ids['lblFollow']
        self.lblUnFollow =  self.ids['lblUnFollow']
        self.lblLike =  self.ids['lblLike']
        self.lblStoryView =  self.ids['lblStoryView']
        self.lblComments =  self.ids['lblComments']
        self.lblLikeExchange =  self.ids['lblLikeExchange']
        self.lblFollowExchange =  self.ids['lblFollowExchange']
        self.lblCommentExchange =  self.ids['lblCommentExchange']
        self.lblTotalTime =  self.ids['lblTotalTime']
        

        log = logging.getLogger("my.logger")
        log.level = logging.DEBUG
        log.addHandler(MyLabelHandler(label, logging.DEBUG))

        oBot = Bot(Client,log,self,self.botStop)
        self.botThread = Thread(target=oBot.RunBot)
        self.botThread.start()
        self.StartTime = datetime.datetime.now()
        Clock.schedule_interval(self.updateTime, 1)
        self.ids['btnStart'].text = "Sequence started"
        
        # t = threading.Thread(target=self.my_thread, args=(log,))
        #thread.start_new(self.my_thread, (log,))
        # t.start()

    def updateTime(self,dt):

        secs = (datetime.datetime.now()-self.StartTime).total_seconds()
        self.lblTotalTime.text = str(datetime.timedelta(seconds= int(secs)))

    def my_thread(self,log):

        for i in range(2**20):
            time.sleep(1)
            log.info("WOO %s", i)

    def disconnect(self):
        self.botStop = True
        self.ids['btnStart'].text = "Start Sequence"
        #self.t.join()
        #self.manager.transition = SlideTransition(direction="right")
        # app = App.get_running_app()
        # app.AppLogout()
        # self.manager.current = 'login'
        # self.manager.get_screen('login').resetForm()

class MyLabelHandler(logging.Handler):

    def __init__(self, label, level=logging.NOTSET):
        logging.Handler.__init__(self, level=level)
        self.label = label

    def emit(self, record):
        "using the Clock module for thread safety with kivy's main loop"
        def f(dt=None):
            self.label.text += "\n" + self.format(record) #"use += to append..."
        Clock.schedule_once(f)
       
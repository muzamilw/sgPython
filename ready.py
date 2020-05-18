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
import traceback
import sys
import os
os.environ['KIVY_IMAGE'] = 'sdl2,gif'
from threading import Thread
import logging
import threading
import time
import datetime
from alert import Alert
from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
from botLogic import Bot

class Ready(Screen):

    t = None
    StartTime = None
    botThread = None
    botStop_event = threading.Event()
    log = None

    def on_enter(self):
        app = App.get_running_app()
        try:
            lblusername = self.ids['lblusername'] #Label(text="showing the log here")
            lblusername.text += app.api.authenticated_user_name
            # app.api.feed_timeline()
            pass
            
        
        except ClientLoginError as e:
            Alert(title='Error', text='IG Login Error, full error : ' + str(e))
        except ClientCookieExpiredError as e:
            Alert(title='Error', text='Client cookie has been expired, relogin to IG needed , full error : ' + str(e))
        except ClientLoginRequiredError as e:
             Alert(title='Error', text='Challenge received from IG,remove challenge by visiting IG manually. , full error : ' + str(e))
        except ClientError as e:
            Alert(title='Error', text='General Client error. , full error : ' + str(e))

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
        self.log = log

        oBot = Bot(Client,log,self,self.botStop_event)
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
        #self.botThread.join()
        self.botStop_event.set()
        self.ids['btnStart'].text = "Start Sequence"
        self.log.info("Stop Signal Sent")
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
       
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
import SPButton 
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem


class Ready(Screen):

    t = None
    StartTime = None
    botThread = None
    botStop_event = threading.Event()
    Logout_alert_dialog = None
    log = None

    # def __init__(self, **kwargs):
    #     self.ids['btnStop'].disabled = True

    

    def showLog(self):
        label = self.ids['logLabel']
        if label.opacity == 0 :
            label.opacity = 1
            
        else:
            label.opacity = 0
            
        # self.ids['btnShowLog'].disabled = True
        # self.ids['btnShowLog'].text = "Hiding Log"
        #self.h_widget(label)
        #self.log.info("Stop Signal Sent")
    
    def h_widget(wid, dohide=True):
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True

    def on_enter(self):
        app = App.get_running_app()
        try:
            lblusername = self.ids['lblusername'] #Label(text="showing the log here")
            lblusername.text = app.api.authenticated_user_name
            # app.api.feed_timeline()

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

            
           
            if self.log is None :
                log = logging.getLogger("my.logger")
                log.level = logging.DEBUG
                log.addHandler(MyLabelHandler(label, logging.DEBUG))
                self.log = log
            
            
        
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
        

        oBot = Bot(Client,self.log,self,self.botStop_event,self.ids['logLabel'])
        self.botThread = Thread(target=oBot.RunBot)
        self.botThread.start()
        self.StartTime = datetime.datetime.now()
        Clock.schedule_interval(self.updateTime, 1)

        self.ids['btnStart'].text = "Sequence started"
        self.ids['btnStart'].disabled = True
        self.ids['btnStop'].disabled = False
        
        self.ids['spinner'].active = True

        
        
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

    def navToHome(self):
        self.manager.current = 'home'


    def stop(self):
        #self.botThread.join()
        Clock.unschedule(self.updateTime)
        self.botStop_event.set()
        self.ids['btnStart'].text = "Start Sequence"
        self.ids['btnStart'].disabled = False
        self.ids['btnStop'].disabled = True
        self.log.info("Stop Signal Sent")
        self.ids['spinner'].active = False
        #self.t.join()
        #self.manager.transition = SlideTransition(direction="right")
        # app = App.get_running_app()
        # app.AppLogout()
        # self.manager.current = 'login'
        # self.manager.get_screen('login').resetForm()

    def logoutConfirm(self):
        app = App.get_running_app()
        self.Logout_alert_dialog = MDDialog(
                title="Confirm Logout",
                text="This will reset your logins for both server and API",
                type = "confirmation",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        text_color=app.theme_cls.primary_color,
                        on_release=self.on_cancelDialog
                    ),
                    MDFlatButton(
                        text="OK",
                        text_color=app.theme_cls.primary_color,
                        on_release=self.logout
                    ),
                ],
            )
        res = self.Logout_alert_dialog.open()

    def on_cancelDialog(self, *args):
        self.Logout_alert_dialog.dismiss(force=True)
        

    def logout(self,*args):

        app = App.get_running_app()
        #self.botThread.join()
        Clock.unschedule(self.updateTime)
        self.botStop_event.set()
        self.ids['btnStart'].text = "Start Sequence"
        self.ids['btnStart'].disabled = False
        self.ids['btnStop'].disabled = True
        self.log.info("Logging out")
        self.ids['spinner'].active = False
        #self.t.join()
        #self.manager.transition = SlideTransition(direction="right")
        # app = App.get_running_app()
        app.AppLogout()
        self.Logout_alert_dialog.dismiss(force=True)
        self.manager.current = 'home'
        

class MyLabelHandler(logging.Handler):

    def __init__(self, label, level=logging.NOTSET):
        logging.Handler.__init__(self, level=level)
        self.label = label

    def emit(self, record):
        "using the Clock module for thread safety with kivy's main loop"
        def f(dt=None):
            self.label.text += "\n" + self.format(record) #"use += to append..."
        Clock.schedule_once(f)
       
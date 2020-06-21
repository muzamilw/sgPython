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
import kivy.utils as util
import traceback
import sys
import os
os.environ['KIVY_IMAGE'] = 'sdl2,gif'
from threading import Thread
import logging
import threading
import schedule
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
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.bottomsheet import MDCustomBottomSheet
import customFunctions as cf
from progressbar import CircularProgressBar


class Ready(Screen):

    t = None
    StartTime = None
    botThread = None
    botStop_event = threading.Event()
    Logout_alert_dialog = None
    log = None
    RunScheduled = False
    TotalTime = 0
    ElapsedTime = 0
    processJobEvent = None
    

    # def __init__(self, **kwargs):
    #     self.ids['btnStop'].disabled = True

    def hide_widget(self,wid, dohide=True):
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled,wid.width, wid.size_hint_x = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled, wid.width, wid.size_hint_x
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled,wid.width, wid.size_hint_x = 0, None, 0, True,0,0

    def showLog(self):
        label = self.ids['logLabel']
        bLabel = self.ids['bLabel']
        
        # if label.opacity == 0 :
        #     label.opacity = 1
            
        # else:
        #     label.opacity = 0
        if label.height == 0:
            self.hide_widget(label,False)
            self.hide_widget(bLabel)
        else:
            self.hide_widget(label)
            self.hide_widget(bLabel,False)

    
    def processjobs(self,dt):
        schedule.run_pending()

    def animate(self, dt):
        bar = self.ids['pbar']
        if bar.value < bar.max:
            bar.value += 1
        else:
            bar.value = bar.min
    
    def on_enter(self):
        app = App.get_running_app()
        try:
            lblusername = self.ids['lblusername'] #Label(text="showing the log here")
            
            lblusername.text = app.api.username

            label = self.ids['logLabel'] #Label(text="showing the log here")
            self.hide_widget(label)
            self.lblFollow =  self.ids['lblFollow']
            self.lblUnFollow =  self.ids['lblUnFollow']
            self.lblLike =  self.ids['lblLike']
            self.lblStoryView =  self.ids['lblStoryView']
            self.lblComments =  self.ids['lblComments']
            self.lblLikeExchange =  self.ids['lblLikeExchange']
            self.lblFollowExchange =  self.ids['lblFollowExchange']
            self.lblCommentExchange =  self.ids['lblCommentExchange']
            self.lblTotalTime =  self.ids['lblTotalTime']
            self.tbar =  self.ids['tbar']
            self.pnlNotStarted =  self.ids['pnlNotStarted']
            self.pnlStarted =  self.ids['pnlStarted']
            self.lblAutoStartLabel =  self.ids['lblAutoStartLabel']
            self.lblStartTime =  self.ids['lblStartTime']
            

            if app.gVars.SequenceRunning == True:
                self.hide_widget(self.pnlNotStarted)
                self.hide_widget(self.pnlStarted,False)
                
            else:
                self.hide_widget(self.pnlNotStarted, False)
                self.hide_widget(self.pnlStarted)
                

            if hasattr(app.gVars, 'SequenceRunning'):
                if app.gVars.SequenceRunning is None:
                    app.gVars.SequenceRunning = False
            else:
                app.gVars.SequenceRunning = False
           
            if self.log is None :
                log = logging.getLogger("my.logger")
                log.level = logging.DEBUG
                log.addHandler(MyLabelHandler(label, logging.DEBUG))
                self.log = log

            if app.gVars.manifestObj is None:
                app.gVars.manifestJson = cf.GetManifest(app.gVars.loginResult["SocialProfileId"],app.gVars)
                app.gVars.manifestObj = cf.LoadManifest(app.gVars.manifestJson)

            
            self.tbar.title = "Instagram Status - Subscription (" + app.gVars.manifestObj.PlanName +")"
            self.ids['lblAutoStart'].text = app.gVars.manifestObj.starttime


            if (datetime.datetime.now().time()  < datetime.datetime.strptime(app.gVars.manifestObj.starttime,"%H:%M").time()) :
                self.lblAutoStartLabel.text = "Next growth session will start today at : "
            else:
                self.lblAutoStartLabel.text = "Next growth session will start tomorrow at : "

            if self.RunScheduled == False:
                schedule.every().day.at(app.gVars.manifestObj.starttime).do(self.startBot).tag('daily-run')
                self.RunScheduled = True
                self.processJobEvent = Clock.schedule_interval(self.processjobs, 1)
            
            
        
        except ClientLoginError as e:
            Alert(title='Error', text='IG Login Error, full error : ' + str(e))
        except ClientCookieExpiredError as e:
            Alert(title='Error', text='Client cookie has been expired, relogin to IG needed , full error : ' + str(e))
        except ClientLoginRequiredError as e:
             Alert(title='Error', text='Challenge received from IG,remove challenge by visiting IG manually. , full error : ' + str(e))
        except ClientError as e:
            Alert(title='Error', text='General  error. , full error : ' + str(e))

    def RefreshManifest(self):
        
        app = App.get_running_app()

        if app.gVars.SequenceRunning != True:

            app.ManifestRefreshed = True
            app.ResetGlobalVars()
            self.ElapsedTime = 0

            app.gVars.manifestJson = cf.GetManifest(app.gVars.loginResult["SocialProfileId"],app.gVars)
            app.gVars.manifestObj = cf.LoadManifest(app.gVars.manifestJson)
                
            self.tbar.title = "Instagram Status - Subscription (" + app.gVars.manifestObj.PlanName +")"
            self.ids['lblAutoStart'].text = app.gVars.manifestObj.starttime

            if (datetime.datetime.now().time()  < datetime.datetime.strptime(app.gVars.manifestObj.starttime,"%H:%M").time()) :
                self.lblAutoStartLabel.text = "Next growth session will start today at : "
            else:
                self.lblAutoStartLabel.text = "Next growth session will start tomorrow at : "

            self.processJobEvent.cancel()
            schedule.clear('daily-run')

            schedule.every().day.at(app.gVars.manifestObj.starttime).do(self.startBot).tag('daily-run')
            self.RunScheduled = True
            Clock.schedule_interval(self.processjobs, 1)
        else:
            self.ShowErrorMessage("Growth Session is already running, cannot refresh!.")


    def startBot(self):
        app = App.get_running_app()

        if app.gVars.manifestObj.PaymentPlanId is None or app.gVars.manifestObj.PaymentPlanId == 1:
            self.ShowErrorMessage("Please upgrade your subscription to start the sequence")
            return

        self.ElapsedTime = app.gVars.ElapsedTime

        if app.gVars.LastSuccessfulSequenceRunDate is None or app.gVars.LastSuccessfulSequenceRunDate != datetime.datetime.today() :
            # if app.gVars.SequenceRunning != True: #if sequence is already not in progress then proceed otherwise skip
                oBot = Bot(Client,self.log,self,self.botStop_event,self.ids['logLabel'])
                self.botThread = Thread(target=oBot.RunBot)
                self.botThread.start()

                # if app.gVars.SequenceRunning == True:
                self.hide_widget(self.pnlNotStarted)
                self.hide_widget(self.pnlStarted,False)
                    
                # else:
                # self.hide_widget(self.pnlNotStarted, False)
                # self.hide_widget(self.pnlStarted)
                
                Clock.schedule_interval(self.updateTime, 1)

               
                
                # Clock.schedule_interval(self.animate, 0.05)
            # else:
            #     self.log.info("Sequence is already running, skipping re-launch")
        else:
            self.log.info("Sequence has been completed successfully for today. Next run is possible tomorrow.")
        
        
        # t = threading.Thread(target=self.my_thread, args=(log,))
        #thread.start_new(self.my_thread, (log,))
        # t.start()

    def updateTime(self,dt):
        app = App.get_running_app()

        bar = self.ids['pbar']
        
        
        if app.gVars.TotalActionsLoaded != 0 or app.gVars.RequiredActionPerformed  != 0:
            loadingProgress = (app.gVars.ActionLoaded / app.gVars.TotalActionsLoaded) * 100
            loadingWeight = 10 / (10 + 30) #app.gVars.TotalActionsLoaded / ( app.gVars.TotalActionsLoaded + app.gVars.RequiredActionPerformed)

            actionProgress = (app.gVars.ActionPerformed / app.gVars.RequiredActionPerformed ) * 100
            actionsWeight = 30 / (10 + 30)#app.gVars.RequiredActionPerformed / ( app.gVars.TotalActionsLoaded + app.gVars.RequiredActionPerformed)
            
            bvalue = int((loadingProgress * loadingWeight) + (actionProgress * actionsWeight))
            if bvalue > 100:
                bvalue = 100 

            bar.value = bvalue
        else:
            bar.value = 1
        
        # secs = (datetime.datetime.now()-self.StartTime).total_seconds()
        # self.lblTotalTime.text = str(datetime.timedelta(seconds= int(secs)))
        self.ElapsedTime = self.ElapsedTime + 1
        app.gVars.ElapsedTime = self.ElapsedTime

        secsleft = self.TotalTime - self.ElapsedTime
        if self.TotalTime != 0:
            self.lblTotalTime.text = str(datetime.timedelta(seconds= int(secsleft)))
        else:
            self.lblTotalTime.text = "Calculating ..."

        if app.gVars.RunStartTime is not None:
            self.lblStartTime.text = app.gVars.RunStartTime.strftime("%b %d %Y %H:%M")



    def my_thread(self,log):

        for i in range(2**20):
            time.sleep(1)
            log.info("WOO %s", i)

    def navToHome(self):
        self.manager.current = 'home'


    def stop(self):
        app = App.get_running_app()
        Clock.unschedule(self.updateTime)
        self.botStop_event.set()

        app.gVars.SequenceRunning = False

        if app.gVars.SequenceRunning == True:
            self.hide_widget(self.pnlNotStarted)
            self.hide_widget(self.pnlStarted,False)
            
        else:
            self.hide_widget(self.pnlNotStarted, False)
            self.hide_widget(self.pnlStarted)
        

    def ShowErrorMessage(self, ErrorMsg):
        app = App.get_running_app()
        self.dialog = MDDialog(
                title="Error!",
                text=ErrorMsg,
                
                buttons=[
                        MDFlatButton(
                            text="Ok",
                            text_color=app.theme_cls.primary_color,
                        ),
                    ],
            )

        # self.Logout_alert_dialog.buttons.append ("Close me!",action=lambda *x: self.dismiss_callback())
        # self.dialog.set_normal_height()
        self.dialog.open()

    # def dismiss_callback(self, *args):
    #     self.dialog.dismiss()

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
                        on_release=self.dismiss_callback
                    ),
                    MDFlatButton(
                        text="ACCEPT",
                        text_color=app.theme_cls.primary_color,
                        on_release=self.logout
                    ),
                ],
            )

        # self.Logout_alert_dialog.buttons.append ("Close me!",action=lambda *x: self.dismiss_callback())
        self.Logout_alert_dialog.set_normal_height()
        self.Logout_alert_dialog.open()

    def dismiss_callback(self, *args):
        self.Logout_alert_dialog.dismiss()

    def on_cancelDialog(self, *args):
        if self.Logout_alert_dialog is not None:
            self.Logout_alert_dialog.dismiss(force=True)
        

    def logout(self,*args):

        app = App.get_running_app()
        #self.botThread.join()
        Clock.unschedule(self.updateTime)
        self.botStop_event.set()
        # self.ids['btnStart'].text = "Start Sequence"
        # self.ids['btnStart'].disabled = False
        # self.ids['btnStop'].disabled = True
        self.log.info("Logging out")
        # self.ids['spinner'].active = False
        #self.t.join()
        #self.manager.transition = SlideTransition(direction="right")
        # app = App.get_running_app()
        app.AppLogout()
        app.gVars.loginResult = None
        app.api = None
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
       
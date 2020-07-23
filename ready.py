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
import platform
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
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import customFunctions as cf
from progressbar import CircularProgressBar
import matplotlib.pyplot as plt
import numpy as np


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
    graph = None
    graph2 = None
    xval = 1

    fig1 = None
    ax1 = None
    figRen = None

    fig2 = None
    ax2= None
    figRenSec = None
    

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

    def hide_widgetGraph(self,wid, dohide=True):
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled,wid.width, wid.size_hint_x = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled, wid.width, wid.size_hint_x
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled,wid.width, wid.size_hint_x = 1, 1, 0, True,1,1

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

    def drawGraphMain(self,Req = None,Loaded = None,Done = None):

        if (self.figRen is not None):
            plt.close(self.figRen)
            
        plt.rcParams.update({
                    "figure.facecolor":  (1.0, 0.0, 0.0, 0),  # red   with alpha = 30%
                    })

        x = ['F', 'U', 'L', 'S','C']
        if Req is None:
            Req = [300, 330, 150, 100, 100]
        if Loaded is None:
            Loaded = [290, 310, 140, 90,80 ]
        if Done is None:
            Done = [1, 1, 1, 1,1 ]

        self.fig1 , self.ax1 = plt.subplots()

        plt.fill_between(x, Req, color="#a5a5a5",
                        alpha=1, label='Done')
      
        plt.fill_between(x, Loaded, color="#55cadd",
                        alpha=1, label='Loaded')

        plt.fill_between(x, Done, color="#006ad8",
                        alpha=1, label='Required')
       
       
        self.ax1.spines['top'].set_visible(False)
        self.ax1.spines['right'].set_visible(False)
        self.ax1.spines['bottom'].set_visible(False)
        self.ax1.spines['left'].set_visible(False)
        self.ax1.patch.set_alpha(0)

        if ( self.graph is None):
            self.figRen = plt.gcf()
            self.graph = FigureCanvasKivyAgg(self.figRen)
            self.graphContainerMain.add_widget(self.graph)
        else:
            self.graphContainerMain.remove_widget(self.graph)
            self.figRen = plt.gcf()
            self.graph = FigureCanvasKivyAgg(self.figRen)
            self.graphContainerMain.add_widget(self.graph)

    def drawGraphSecondary(self,Req = None,Loaded = None,Done = None):

        try:
            if (self.figRenSec is not None):
                plt.close(self.figRenSec)
                
            plt.rcParams.update({
                        "figure.facecolor":  (1.0, 0.0, 0.0, 0),  # red   with alpha = 30%
                        })

            x = ['LX', 'FX', 'CX']
            if Req is None:
                Req = [15, 15, 15 ]
            if Loaded is None:
                Loaded = [13, 12, 10 ]
            if Done is None:
                Done = [1, 1, 1 ]

            self.fig2 , self.ax2 = plt.subplots()
            
            plt.fill_between(x, Req, color="#a5a5a5",
                            alpha=1, label='Done')
            
            plt.fill_between(x, Loaded, color="#7edcad",
                            alpha=1, label='Loaded')

            plt.fill_between(x, Done, color="#009856",
                            alpha=1, label='Required')
        
            self.ax2.spines['top'].set_visible(False)
            self.ax2.spines['right'].set_visible(False)
            self.ax2.spines['bottom'].set_visible(False)
            self.ax2.spines['left'].set_visible(False)
            self.ax2.patch.set_alpha(0)

            if ( self.graph2 is None):
                self.figRenSec = plt.gcf()
                self.graph2 = FigureCanvasKivyAgg(self.figRenSec)
                self.graphContainerSecondary.add_widget(self.graph2)
            else:
                self.graphContainerSecondary.remove_widget(self.graph2)
                self.figRenSec = plt.gcf()
                self.graph2 = FigureCanvasKivyAgg(self.figRenSec)
                self.graphContainerSecondary.add_widget(self.graph2)
        except Exception as e:
            pass
        
    def processjobs(self,dt):
        schedule.run_pending()

    def animate(self, dt):
        # bar = self.ids['pbar']
        # if bar.value < bar.max:
        #     bar.value += 1
        # else:
        #     bar.value = bar.min
        self.xval  += 5
        Done = [self.xval, 3, 5, 5,7 ]
        self.drawGraphMain(Done = Done)

    
    def on_enter(self):
        app = App.get_running_app()
        try:
            lblusername = self.ids['lblusername'] #Label(text="showing the log here")
            
            lblusername.text = app.api.username

            self.graphContainerMain =  self.ids['graphContainerMain']
            self.graphContainerSecondary =  self.ids['graphContainerSecondary']
            
            self.drawGraphMain()
            self.drawGraphSecondary()

            # Clock.schedule_interval(self.animate, 1)
            bar = self.ids['pbar']
            
            if (platform.system() == "Darwin"):
                bar.widget_size = 120
            bar.value = 10

            label = self.ids['logLabel'] #Label(text="showing the log here")
            self.hide_widget(label)
           
            self.lblTotalTime =  self.ids['lblTotalTime']
            self.tbar =  self.ids['tbar']
            self.pnlNotStarted =  self.ids['pnlNotStarted']
            self.pnlStarted =  self.ids['pnlStarted']
            self.lblAutoStartLabel =  self.ids['lblAutoStartLabel']
            self.lblStartTime =  self.ids['lblStartTime']
            self.pbar = self.ids['pbar']
            self.graphContainer = self.ids['graphContainer']
            
            

            if app.gVars.SequenceRunning == True:
                self.hide_widget(self.pnlNotStarted)
                self.hide_widget(self.pnlStarted,False)
                self.hide_widget(self.pbar,False)
                self.hide_widgetGraph(self.graphContainer,False)
                
            else:
                self.hide_widget(self.pnlNotStarted, False)
                self.hide_widget(self.pnlStarted)
                self.hide_widget(self.pbar)
                self.hide_widgetGraph(self.graphContainer)
                

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
            self.log.info("Manifest Refreshed.")
        else:
            self.ShowErrorMessage("Growth Session is already running, cannot refresh!.")


    def startBot(self):
        app = App.get_running_app()

        if app.gVars.manifestObj.PaymentPlanId is None or app.gVars.manifestObj.PaymentPlanId == 1:
            self.ShowErrorMessage("Please upgrade your subscription to start the sequence")
            return

        self.ElapsedTime = app.gVars.ElapsedTime

        if app.gVars.LastSuccessfulSequenceRunDate is None or app.gVars.LastSuccessfulSequenceRunDate != datetime.datetime.today() :
           
                oBot = Bot(Client,self.log,self,self.botStop_event,self.ids['logLabel'])
                self.botThread = Thread(target=oBot.RunBot)
                self.botThread.start()

                
                self.hide_widget(self.pnlNotStarted)
                self.hide_widget(self.pnlStarted,False)
                self.hide_widget(self.pbar,False)
                self.hide_widgetGraph(self.graphContainer,False)
                    
              
                
                Clock.schedule_interval(self.updateTime, 1)
                Clock.schedule_interval(self.updateGraph, 30)

               
                
               
        else:
            self.log.info("Sequence has been completed successfully for today. Next run is possible tomorrow.")
        
        
        # t = threading.Thread(target=self.my_thread, args=(log,))
        #thread.start_new(self.my_thread, (log,))
        # t.start()

    def updateGraph(self,dt):
        app = App.get_running_app()
        #updating graph
        if app.gVars.TotalActionsLoaded != 0 or app.gVars.RequiredActionPerformed  != 0:
            Req = [app.gVars.ReqFollow, app.gVars.ReqUnFollow, app.gVars.ReqLikes, app.gVars.ReqStoryViews, app.gVars.ReqComments]
            Loaded = [app.gVars.TotFollow, app.gVars.TotUnFollow , app.gVars.TotLikes, app.gVars.TotStoryViews,app.gVars.TotComments ]
            Done = [app.gVars.CurrentFollowDone, app.gVars.CurrentUnFollowDone, app.gVars.CurrentLikeDone, app.gVars.CurrentStoryViewDone,app.gVars.CurrentCommentsDone ]
            self.drawGraphMain(Req,Loaded,Done)
            # LX FX CX
            Req = [app.gVars.ReqExLikes, app.gVars.ReqExFollow, app.gVars.ReqExComments]
            Loaded = [app.gVars.TotExLikes, app.gVars.TotExFollow , app.gVars.TotExComments ]
            Done = [app.gVars.CurrentExLikeDone, app.gVars.CurrentExFollowDone, app.gVars.CurrentExCommentsDone ]
            self.drawGraphSecondary(Req,Loaded,Done)
        


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
        Clock.unschedule(self.updateGraph)
        
        self.botStop_event.set()

        app.gVars.SequenceRunning = False

        if app.gVars.SequenceRunning == True:
            self.hide_widget(self.pnlNotStarted)
            self.hide_widget(self.pnlStarted,False)
            self.hide_widget(self.pbar,False)
            self.hide_widgetGraph(self.graphContainer,False)
            
        else:
            self.hide_widget(self.pnlNotStarted, False)
            self.hide_widget(self.pnlStarted)
            self.hide_widget(self.pbar)
            self.hide_widgetGraph(self.graphContainer)
        

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
        Clock.unschedule(self.updateGraph)
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
       
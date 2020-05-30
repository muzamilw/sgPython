import kivy
kivy.require('1.11.0')


from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.config import Config
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem
from kivy.app import App
import kivy.utils as util
import schedule
import time


class Home(Screen):
    
    app = None

    def on_enter(self):
        app = App.get_running_app()
        self.app = app

        # self.ids['bottom_toolbar'].remove_notch()

        if app.gVars.loginResult is not None:
            if app.gVars.IGusername == None:
                app.gVars.IGusername = 'nevillekmiec'
            if app.gVars.IGpassword == None:
                app.gVars.IGpassword = '!_LKvXc1'
            app.api = app.checkIGLogin(app.gVars.SGusername)
            if app.api is None:
                # manager.current = 'iglogin'
                pass
            else:
                # manager.current = 'ready'
                self.ids['btnIG'].text = 'Today\'s Status'
                self.ids['btnIG'].md_bg_color = util.get_color_from_hex("##16D39A")
        else:
            # manager.current = 'login'
            # self.ids['btnIG'].text = 'Today\'s Status'
            pass

    def btnIG_released(self):
        if self.app.gVars.loginResult is not None:
            
            self.app.api = self.app.checkIGLogin(self.app.gVars.SGusername)
            if self.app.api is None:
                self.manager.current = 'iglogin'
                
            else:
                self.manager.current = 'ready'
                
        else:
            self.manager.current = 'login'
            






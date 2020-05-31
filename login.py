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
import customFunctions as cf
from kivy.clock import Clock

class Login(Screen):
    
    alert_dialog = None
    Login_alert_dialog = None

    def build(self):
        app = App.get_running_app()

        self.ids['login'].text = app.gVars.SGusername
        self.ids['password'].text = app.gVars.SGPin

        
            
    def show_keyboard(self,args):
        self.ids['login'].focus = True

    def on_enter(self):
        Clock.schedule_once(self.show_keyboard)

    def do_login(self, loginText, passwordText):
        app = App.get_running_app()

        app.username = loginText
        app.password = passwordText

        if ( loginText == "" or  passwordText == ""):
            if not self.alert_dialog:
                self.alert_dialog = MDDialog(
                    title="Error!",
                    text="Either username or pin is missing.",
                    buttons=[
                        MDFlatButton(
                            text="Ok",
                            text_color=app.theme_cls.primary_color,
                        ),
                    ],
                )
            self.alert_dialog.open()
            return

         
        loginResult = cf.AppLogin(loginText,passwordText,'123',app.gVars)
        if loginResult[0] == False:
            
            self.Login_alert_dialog = MDDialog(
                title="Login Error!",
                text=loginResult[1],
                buttons=[
                    MDFlatButton(
                        text="Ok",
                        text_color=app.theme_cls.primary_color,
                    ),
                ],
            )
            self.Login_alert_dialog.open()
            
        else:
            app.gVars.loginResult = loginResult[1]
            app.gVars.SGusername = loginText
            app.gVars.SGPin = passwordText

            self.manager.transition = SlideTransition(direction="left")
            app.api = app.checkIGLogin(app.gVars.SGusername)
            if app.api is None:
                self.manager.current = 'iglogin'
            else:
                self.manager.current = 'ready'


            app.config.read(app.get_application_config())
            app.config.write()

    def resetForm(self):
        self.ids['login'].text = ""
        self.ids['password'].text = ""

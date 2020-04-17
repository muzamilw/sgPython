
import kivy
kivy.require('1.0.7')

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
import os
from ready import Ready

class Instagram(Screen):
    pass
    # def do_IGlogin(self, loginText, passwordText):
    #     app = App.get_running_app()

    #     app.username = loginText
    #     app.password = passwordText

    #     #loginResult = cf.AppLogin(loginText,passwordText,'123',app.gVars)
    #     #app.gVars.loginResult = loginResult

    #     self.manager.transition = SlideTransition(direction="left")
    #     self.manager.current = 'ready'

    #     app.config.read(app.get_application_config())
    #     app.config.write()

    # def resetForm(self):
    #     self.ids['login'].text = ""
    #     self.ids['password'].text = ""
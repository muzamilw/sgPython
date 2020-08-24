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
from pathlib import Path
import logging
import threading
import requests
import json
import time
import datetime
import codecs
import hashlib
import string
import random
import time
import re
import requests
import json
import gzip
import platform

from io import BytesIO
from urllib.parse import urlparse
from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,ClientCheckpointRequiredError,ClientChallengeRequiredError,
        __version__ as client_version)
from instagram_private_api.client import compat_urllib_parse, compat_urllib_request, compat_urllib_error, ErrorHandler
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem
from kivy.app import App
# from instagram_web_api import Client as WebClient

class IgLoginValidationDlgContent(BoxLayout):
    pass

class IGLogin(Screen):

    headers = None
    alert_dialog = None
    Login_alert_dialog = None

    def to_json(self,python_object):
        if isinstance(python_object, bytes):
            return {'__class__': 'bytes',
                    '__value__': codecs.encode(python_object, 'base64').decode()}
        raise TypeError(repr(python_object) + ' is not JSON serializable')

    def from_json(self,json_object):
        if '__class__' in json_object and json_object['__class__'] == 'bytes':
            return codecs.decode(json_object['__value__'].encode(), 'base64')
        return json_object

    def onlogin_callback(self,api, new_settings_file):
        print('iglogin login call back received')
        cache_settings = api.settings
        with open(new_settings_file, 'w') as outfile:
            json.dump(cache_settings, outfile, default=self.to_json)
            print('SAVED: {0!s}'.format(new_settings_file))
        if api.IsChallengedResolved ==True: 
            app = App.get_running_app()
            app.api = api
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = 'ready'

    def onvalidation_required_callback(self,api):
        print('validation call back received')
        self.ShowValidationDialog()
    
    def show_keyboard(self,args):
        self.ids['password'].focus = True

    def ShowValidationDialog(self):
        app = App.get_running_app()
        self.dlgContent = IgLoginValidationDlgContent()
        self.Login_alert_dialog = MDDialog(
                # auto_dismiss=False,
                title="Instagram Login Validation!",
                type="custom",
                content_cls=self.dlgContent,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        text_color=app.theme_cls.primary_color,
                        on_release=self.dismiss_callback
                    ),
                    MDFlatButton(
                        text="ACCEPT",
                        text_color=app.theme_cls.primary_color,
                        on_release=self.continue_ig_validation
                    ),
                ],
            )
        # self.Login_alert_dialog.size_hint_y = 1
        self.Login_alert_dialog.set_normal_height()
        self.Login_alert_dialog.open()


    def continue_ig_validation(self, *args):
        app = App.get_running_app()
        code = self.dlgContent.ids['igvalidationcode'].text
        if code != "":
            app.api.continue_ig_validation(code)
            self.Login_alert_dialog.dismiss(force=True)
        

    def dismiss_callback(self, *args):
        self.Login_alert_dialog.dismiss(force=True)
        
        
    def on_enter(self):
        app = App.get_running_app()

        if app.gVars.IGusername != '':
            self.ids['login'].text = app.gVars.SGusername
        # else:
            # self.ids['login'].text = 'nevillekmiec'


        if app.gVars.IGpassword is not None and app.gVars.IGpassword != "":
            self.ids['password'].text = app.gVars.IGpassword
        # else:
        #     self.ids['password'].text = '!_LKvXc1'

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

        api = self.apilogin(loginText,passwordText)
        
        if api is None:

            self.Login_alert_dialog = MDDialog(
                title="Instagram Login Error!",
                text="There was error in performing login on Instagram, please enter the correct password and try again.",
                buttons=[
                    MDFlatButton(
                        text="Ok",
                        text_color=app.theme_cls.primary_color,
                    ),
                ],
            )
            self.Login_alert_dialog.open()
        else:

            if api.IsChallenged == False and api.cookie_jar.auth_expires is None:
                self.Login_alert_dialog = MDDialog(
                    title="Instagram Login Error!",
                    text="There was error in performing login on Instagram, please enter the correct password and try again.",
                    buttons=[
                        MDFlatButton(
                            text="Ok",
                            text_color=app.theme_cls.primary_color,
                        ),
                    ],
                )
                self.Login_alert_dialog.open()

            else:
                app.gVars.IGusername = loginText
                app.gVars.IGpassword = passwordText
                app.api = api
                if api.IsChallenged == False:
                    self.manager.transition = SlideTransition(direction="left")
                    self.manager.current = 'ready'
    

    def apilogin(self,loginText,passwordText):
        api = None
        device_id = None
        app = App.get_running_app()

        # useragentd = "'app_version': '10.26.0';
        # 'android_version': '18';
        # 'android_release': '4.3';
        # 'brand': 'Xiaomi';
        # 'device': 'armani';
        # 'model': 'HM 1SW';
        # 'dpi': '320dpi';
        # 'resolution': '720x1280';
        # 'chipset': 'qcom';
        # 'version_code': ''
        try:

            # settings_file = 'userdata\\'+ loginText +'_login.json'

            if (platform.system() == "Darwin"):
                Path(os.path.join(os.getenv("HOME"), "." + app.appName)).mkdir(parents=True, exist_ok=True)
                settings_file = os.path.join(os.getenv("HOME"), "." + app.appName, loginText+'_login.json')
            else:
                settings_file = Path("userdata") / str(loginText +'_login.json')

            
            if not os.path.isfile(settings_file):
                # settings file does not exist
                print('Unable to find login.json file: {0!s}'.format(settings_file))
               
                # login new
                api = Client(
                    loginText, passwordText,#auto_patch=True,
                    #app_version= '10.26.0',
                    # android_version= '18',
                    # android_release= '4.3',
                    # brand= 'Xiaomi',
                    # device= 'armani',
                    # model= 'HM 1SW',
                    # dpi= '320dpi',
                    # resolution= '720x1280',
                    # chipset= 'qcom',
                    # version_code= '',
                    on_login=lambda x: self.onlogin_callback(x, settings_file),
                    on_validation_required=lambda x: self.onvalidation_required_callback(x))
            else:
                with open(settings_file) as file_data:
                    cached_settings = json.load(file_data, object_hook=self.from_json)
                print('Reusing settings: {0!s}'.format(settings_file))

                device_id = cached_settings.get('device_id')
                # reuse auth settings
                api = Client(
                    loginText, passwordText,#auto_patch=True,
                    settings=cached_settings)

        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

            # Login expired
            # Do relogin but use default ua, keys and such
            api = Client(
                loginText, passwordText,#auto_patch=True,
                device_id=device_id,
                #user_agent = useragentd,
                on_login=lambda x: self.onlogin_callback(x, settings_file))
        
        except ClientCheckpointRequiredError as e:
            #(ClientError)
            print('Unexpected ClientCheckpointRequiredError: {0!s}'.format(e))
            print('Challenge url = ' + e.challenge_url)
            
            return None


        # except ClientChallengeRequiredError as e:
        #     print('Unexpected ClientChallengeRequiredError: {0!s}'.format(e))

        except ClientLoginError as e:
            print('ClientLoginError {0!s}'.format(e))
           
        except ClientError as e:
            print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
            
        except Exception as e:
            print('Unexpected Exception: {0!s}'.format(e))
            

        # Show when login expires
        if (api is not None):
            if api.cookie_jar.auth_expires is None:
                print('Cookie Expiry is null')
            else:
                cookie_expiry = api.cookie_jar.auth_expires
                print('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))

            if api.IsChallenged == True:
                print('Challenge Received')
         

        return api


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
from alert import Alert
import os
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

class MyAppClient(Client):
    
    def login(self):
        """Login."""

        print('overrided login()')

        prelogin_params = self._call_api(
            'si/fetch_headers/',
            params='',
            query={'challenge_type': 'signup', 'guid': self.generate_uuid(True)},
            return_response=True)

        login_params = {
            'device_id': self.device_id,
            'guid': self.uuid,
            'adid': self.ad_id,
            'phone_id': self.phone_id,
            '_csrftoken': self.csrftoken,
            'username': self.username,
            'password': self.password,
            'login_attempt_count': '0',
        }

        try:
            """
            login_response = self._call_api(
            'accounts/login/', params=login_params, return_response=True)
            """

            url = 'https://i.instagram.com/api/v1/accounts/login/'
            params = login_params

            headers = self.default_headers
            headers['Content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            
            json_params = json.dumps(params, separators=(',', ':'))
            hash_sig = self._generate_signature(json_params)
            post_params = {
                'ig_sig_key_version': self.key_version,
                'signed_body': hash_sig + '.' + json_params
            }

            data = compat_urllib_parse.urlencode(post_params).encode('ascii')
            req = compat_urllib_request.Request(url, data, headers=headers)

            try:
                response = self.opener.open(req, timeout=self.timeout)
            except compat_urllib_error.HTTPError as e:
                response_text = json.loads(e.read().decode('utf8'))
                checkpoint_url = response_text.get('challenge').get('url')
                self.login_challenge(checkpoint_url, headers)
                
        except Exception as e:
            print('unhandled exception', e)

    def login_challenge(self, checkpoint_url, headers):

        try:
            print('redirecting to ..', checkpoint_url)
            headers['X-CSRFToken'] = self.csrftoken
            headers['Referer'] = checkpoint_url
            
            mode = int(input('Choose a challenge mode (0 - SMS, 1 - Email): '))
            challenge_data = {'choice': mode}
            data = compat_urllib_parse.urlencode(challenge_data).encode('ascii')
            
            req = compat_urllib_request.Request(checkpoint_url, data, headers=headers)
            response = self.opener.open(req, timeout=self.timeout)

            code = input('Enter code received: ')
            code_data = {'security_code': code}
            data = compat_urllib_parse.urlencode(code_data).encode('ascii')

            req = compat_urllib_request.Request(checkpoint_url, data, headers=headers)
            response = self.opener.open(req, timeout=self.timeout)

            if response.info().get('Content-Encoding') == 'gzip':
                buf = BytesIO(response.read())
                res = gzip.GzipFile(fileobj=buf).read().decode('utf8')
            else:
                res = response.read().decode('utf8')
    
        except compat_urllib_error.HTTPError as e:
            print('unhandled exception', e)

  


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
        cache_settings = api.settings
        with open(new_settings_file, 'w') as outfile:
            json.dump(cache_settings, outfile, default=self.to_json)
            print('SAVED: {0!s}'.format(new_settings_file))

    def build(self):
        app = App.get_running_app()

        if app.gVars.IGusername != '':
            self.ids['login'].text = app.gVars.IGusername
        else:
            self.ids['login'].text = 'nevillekmiec'


        if app.gVars.IGpassword != '':
            self.ids['password'].text = app.gVars.IGpassword
        else:
            self.ids['password'].text = '!_LKvXc1'
    
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

        loginRes = self.apilogin(loginText,passwordText)
        api = loginRes[0]

        app.gVars.IGusername = loginText
        app.gVars.IGpassword = passwordText

        if api is None:
            self.Login_alert_dialog = MDDialog(
                title="Instagram Login Error!",
                text="There was error in performing login on Instagram, please try again",
                buttons=[
                    MDFlatButton(
                        text="Ok",
                        text_color=app.theme_cls.primary_color,
                    ),
                ],
            )
            self.Login_alert_dialog.open()
        else:
            app.api = api

            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = 'ready'
    

    def apilogin(self,loginText,passwordText):
        api = None
        device_id = None

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

            settings_file = 'userdata\\'+ loginText +'_login.json'
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
                    on_login=lambda x: self.onlogin_callback(x, settings_file))
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
            exit()
            return (None, e.challenge_url)


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
            cookie_expiry = api.cookie_jar.auth_expires
            print('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))

        return (api,None)

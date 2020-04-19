#from InstagramAPI import InstagramAPI


import requests 
import os.path
import datetime
#import numpy

#from collections import Counter
from time import sleep
from random import randint
import json
import logging
import time
import random
import codecs
from urllib.parse import urlparse
import datetime, pytz
import dateutil.tz
#import sys


import pickle
#from v import MIMETextnpm

import customFunctions as cf
import apiWrappers as apiW
import botLogic

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
from iglogin import IGLogin
from alert import Alert
from instagram_private_api import Client, ClientCompatPatch


class GlobalVars:
    pass




##login code

def login_challenge(self, checkpoint_url):
    BASE_URL = 'https://www.instagram.com/'
    self.s.headers.update({'Referer': BASE_URL})
    req = self.s.get(BASE_URL[:-1] + checkpoint_url)
    self.s.headers.update({'X-CSRFToken': req.cookies['csrftoken'], 'X-Instagram-AJAX': '1'})
    self.s.headers.update({'Referer': BASE_URL[:-1] + checkpoint_url})
    mode = int(input('Choose a challenge mode (0 - SMS, 1 - Email): '))
    challenge_data = {'choice': mode}
    challenge = self.s.post(BASE_URL[:-1] + checkpoint_url, data=challenge_data, allow_redirects=True)
    self.s.headers.update({'X-CSRFToken': challenge.cookies['csrftoken'], 'X-Instagram-AJAX': '1'})

    code = input('Enter code received: ').strip()
    code_data = {'security_code': code}
    code = self.s.post(BASE_URL[:-1] + checkpoint_url, data=code_data, allow_redirects=True)
    self.s.headers.update({'X-CSRFToken': code.cookies['csrftoken']})
    self.cookies = code.cookies
    code_text = json.loads(code.text)
    if code_text.get('status') == 'ok':
        self.authenticated = True
        self.logged_in = True
    elif 'errors' in code.text:
        for count, error in enumerate(code_text['challenge']['errors']):
            count += 1
            logging.error('Session error %(count)s: "%(error)s"' % locals())
    else:
        logging.error(json.dumps(code_text))

# def IGLogin():
#     InstagramAPI.ver = login_challenge
#     api = InstagramAPI("nevillekmiec", "!_LKvXc1")
#     api.login()
#     try:
#         link = api.LastJson['challenge']['api_path']
#         api.ver(link)
#         api.login()
#     except:
#         pass
#     return api

try:
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)





#reading api file if already exists.
# try:
#     with open('api.login', 'rb') as api_login_file:
#         print('api login found, loading')
#         api = pickle.load(api_login_file)
# except IOError:
#     print('api file does not exist, performing login')
#     api = IGLogin()
#     with open('api.login', 'wb') as api_login_file:
#         pickle.dump(api, api_login_file)







#botLogic.RunBot(gVars,api,Client)


########################################################

#cf.LoadStoryTodo(api,gVars.manifestObj,[1])
# rank_token = Client.generate_uuid()

#follfeed = apiW.GetUserFollowingFeed(api, 'muzamilw',10,Client)
#print(len(follfeed))
#print(follfeed)

# location_results = apiW.GetLocationFeed(api, 'london',300,Client)

# print(len(location_results))

# with open("loc.json", "w") as outfile: 
#     outfile.write(json.dumps(location_results))
# #results = apiW.GetTagFeed(api, 'musically',300,Client)
# tag_results = []
# results = api.feed_tag(
#             'musically', rank_token)


# print(len(tag_results))

# print(len(results['items']))

# print(tag_results)

#user_dtail_info = api.user_detail_info(api.authenticated_user_id)
#user_info = api.user_info(api.authenticated_user_id)
#username_info = api.username_info(api.authenticated_user_id)
#print(json.dumps(user, indent=2))
# print(json.dumps(results, indent=2))

#print(user_info['user']['media_count'])
########################################################





class Login(Screen):

    def build(self):
        app = App.get_running_app()

        self.ids['login'].text = app.gVars.SGusername
        self.ids['password'].text = app.gVars.SGPin

    def do_login(self, loginText, passwordText):
        app = App.get_running_app()

        app.username = loginText
        app.password = passwordText

        loginResult = cf.AppLogin(loginText,passwordText,'123',app.gVars)
        if loginResult[0] == False:
            Alert(title='Error', text=loginResult[1])
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



class LoginApp(App):
    gVars = None
    api = None
    username = StringProperty(None)
    password = StringProperty(None)

    def build(self):
        self.loadGlobalConfig()
        manager = ScreenManager()
        manager.add_widget(Login(name='login'))
        
        manager.add_widget(Ready(name='ready'))
        manager.add_widget(IGLogin(name='iglogin'))

        if self.gVars.loginResult is not None:
            self.api = self.checkIGLogin(self.gVars.SGusername)
            if self.api is None:
                manager.current = 'iglogin'
            else:
                manager.current = 'ready'
        else:
            manager.current = 'login'


        return manager

    def on_stop(self):
        with open('userdata\\glob.Vars', 'wb') as gVarFile:
            print('Updating gVars at Stop')
            pickle.dump(self.gVars, gVarFile)

    def on_pause(self):
        with open('userdata\\glob.Vars', 'wb') as gVarFile:
            print('Updating gVars at pause')
            pickle.dump(self.gVars, gVarFile)

    def get_application_config(self):
        if(not self.username):
            return super(LoginApp, self).get_application_config()

        conf_directory = self.user_data_dir + '/' + self.username

        if(not os.path.exists(conf_directory)):
            os.makedirs(conf_directory)

        return super(LoginApp, self).get_application_config(
            '%s/config.cfg' % (conf_directory)
        )

    def loadGlobalConfig(self):
        try:
            with open('userdata\\glob.Vars', 'rb') as gVarFile:
                print('Loading Existing Global Defaults')
                globvars = pickle.load(gVarFile)
                self.gVars = globvars
        except IOError:
            print('Vars file does not exist, InitBlank')
            gVars = GlobalVars()
            gVars.BotVer = 'py.1.6'
            gVars.RunStartTime = None
            gVars.RunEndTime = None
            gVars.TotalSessionTime = 0
            gVars.manifestJson = None
            gVars.manifestObj = None
            gVars.loginResult = None
            gVars.hashtagActions = None
            gVars.locationActions = None
            gVars.UnFollowActions = None
            gVars.DCActions = None
            gVars.SuggestFollowers = None
            gVars.StoryViewActions = None
            gVars.GlobalTodo = None
            gVars.Todo = None
            gVars.DailyStatsSent = False
            gVars.SGusername = None
            gVars.SGPin = None
            gVars.IGusername = None
            gVars.IGpassword = None

            gVars.CurrentFollowDone = 0
            gVars.CurrentUnFollowDone = 0
            gVars.CurrentLikeDone = 0
            gVars.CurrentStoryViewDone = 0
            gVars.CurrentCommentsDone = 0

            gVars.TotFollow = 0
            gVars.TotUnFollow = 0
            gVars.TotLikes = 0
            gVars.TotStoryViews = 0
            gVars.TotComments = 0

            gVars.ReqFollow = 0
            gVars.ReqUnFollow = 0
            gVars.ReqLikes = 0
            gVars.ReqStoryViews = 0
            gVars.ReqComments = 0

            gVars.API_BaseURL = "https://socialgrowthlabs.com/API"

            self.gVars = gVars
            print('Loading new Defaults')
            with open('userdata\\glob.Vars', 'wb') as gVarFile:
                pickle.dump(gVars, gVarFile)
        
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
            json.dump(cache_settings, outfile, default=to_json)
            print('SAVED: {0!s}'.format(new_settings_file))

    def checkIGLogin(self,username):
        device_id = None
        try:

            settings_file = 'userdata\\'+username+'_login.json'
            if not os.path.isfile(settings_file):
                # settings file does not exist
                print('Unable to find login.json: {0!s}'.format(settings_file))
                api = None

            elif self.gVars.IGusername is None or self.gVars.IGpassword is None:   
                 print('stored username or pwd are empty, relogin required')
                 api = None
            else:
                with open(settings_file) as file_data:
                    cached_settings = json.load(file_data, object_hook=self.from_json)
                    print('Reusing settings: {0!s}'.format(settings_file))

                device_id = cached_settings.get('device_id')
                # reuse auth settings
                api = Client(
                    self.gVars.IGusername, self.gVars.IGpassword,#auto_patch=True,
                    settings=cached_settings)

        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

            return None

        except ClientLoginError as e:
            print('ClientLoginError {0!s}'.format(e))
            return None
        except ClientError as e:
            print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
            return None
        except Exception as e:
            print('Unexpected Exception: {0!s}'.format(e))
            return None

        if api is not None:
        # Show when login expires
            cookie_expiry = api.cookie_jar.auth_expires
            print('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))

        return api

   
        

    def AppLogout(self):
        app = App.get_running_app()
        app.gVars.loginResult = None
        with open('userdata\\glob.Vars', 'wb') as gVarFile:
            print('Updating gVars at logout')
            pickle.dump(self.gVars, gVarFile)

    def show_popup(self):
        show = P()

        popupWindow = Popup(title="Popup Window", content=show, size_hint=(None,None),size=(400,400))

        popupWindow.open()

if __name__ == '__main__':
    LoginApp().run()

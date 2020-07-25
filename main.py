#from InstagramAPI import InstagramAPI


import requests 
import os.path
import datetime
import pandas

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
from pathlib import Path
import platform
#import sys


import pickle
#from v import MIMETextnpm

import customFunctions as cf
import apiWrappers as apiW
import botLogic

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
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
import os
os.environ['KIVY_IMAGE'] = 'sdl2,gif'
from ready import Ready
from iglogin import IGLogin
from login import Login
from alert import Alert
from instagram_private_api import Client
from instagram_private_api.client import compat_urllib_parse, compat_urllib_request, compat_urllib_error, ErrorHandler
import SPButton
from home import Home
from kivymd.app import MDApp


class GlobalVars:
    pass



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


class Client(Client):
    def mute_unmute(self, user_id, option = 'mute', media = 'both'):
        endpoint = 'friendships/{}_posts_or_story_from_follow/'.format(option.lower())
        data = {
                '_uuid': self.uuid,
                '_uid': self.authenticated_user_id,
                '_csrftoken': self.csrftoken,
                }
        if media.lower() == 'post':
            data['target_posts_author_id'] = str(user_id)
        elif media.lower() == 'story':
            data['target_reel_author_id'] = str(user_id)
        elif media.lower() == 'both':
            data['target_posts_author_id'] = str(user_id)
            data['target_reel_author_id'] = str(user_id)
        res = self._call_api(endpoint, data)
        return res

    def login_challenge(self, checkpoint_url):

        try:
            headers = self.default_headers
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








class LoginApp(MDApp):
    Config.set('graphics', 'resizable', '0')
    Config.set('graphics', 'width', '700')
    Config.set('graphics', 'height', '500')
    Window.size = (1000, 600)
    gVars = None
    api = None
    username = StringProperty(None)
    password = StringProperty(None)
    icon = 'data//ml.ico'
    ManifestRefreshed = False
    alert_dialog = None
    
    def __init__(self, **kwargs):
        self.title = "Machine Learning Growth API v1.9"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.primary_hue = "500"
        super().__init__(**kwargs)

    def build(self):
        self.loadGlobalConfig()
        manager = ScreenManager()
        
        manager.add_widget(Login(name='login'))
        manager.add_widget(Ready(name='ready'))
        manager.add_widget(IGLogin(name='iglogin'))
        manager.add_widget(Home(name='home'))

        manager.current = 'home'

        return manager

    def on_stop(self):
        if (platform.system() == "Darwin"):
                Path(os.path.join(os.getenv("HOME"), ".SocialPlannerPro")).mkdir(parents=True, exist_ok=True)
                file_to_open = os.path.join(os.getenv("HOME"), ".SocialPlannerPro", "glob.vars")
        else:
                file_to_open = Path("userdata") / "glob.vars"

        self.gVars.SequenceRunning = False
        with open(file_to_open, 'wb') as gVarFile:
            print('Updating gVars at Stop')
            pickle.dump(self.gVars, gVarFile)

    def on_pause(self):
        if (platform.system() == "Darwin"):
                Path(os.path.join(os.getenv("HOME"), ".SocialPlannerPro")).mkdir(parents=True, exist_ok=True)
                file_to_open = os.path.join(os.getenv("HOME"), ".SocialPlannerPro", "glob.vars")
        else:
                file_to_open = Path("userdata") / "glob.vars"

        self.gVars.SequenceRunning = False
        with open(file_to_open, 'wb') as gVarFile:
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
            if (platform.system() == "Darwin"):
                Path(os.path.join(os.getenv("HOME"), ".SocialPlannerPro")).mkdir(parents=True, exist_ok=True)
                file_to_open = os.path.join(os.getenv("HOME"), ".SocialPlannerPro", "glob.vars")
            else:
                file_to_open = Path("userdata") / "glob.vars"

            # try:
                with open(file_to_open, 'rb') as gVarFile:
                    print('Loading Existing Global Defaults')
                    globvars = pickle.load(gVarFile)
                    self.gVars = globvars
            # except Exception as e:
               
            #     app = App.get_running_app()
            #     if not self.alert_dialog:
            #         self.alert_dialog = MDDialog(
            #             title="Error!",
            #             text="Please re-launch the application with administrative rights.",
            #             buttons=[
            #                 MDFlatButton(
            #                     text="Ok",
            #                     text_color=app.theme_cls.primary_color,
            #                 ),
            #             ],
            #         )
            #         self.alert_dialog.open()
                    
        except IOError:
            print('Vars file does not exist, InitBlank')
            gVars = GlobalVars()
            gVars.BotVer = 'py.1.6'
            gVars.RunStartTime = None
            gVars.RunEndTime = None
            gVars.TotalSessionTime = 0
            gVars.ElapsedTime = 0
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
            gVars.DailyStatsSentDate = ''
            gVars.SGusername = None
            gVars.SGPin = None
            gVars.IGusername = None
            gVars.IGpassword = None

            gVars.CurrentFollowDone = 0
            gVars.CurrentUnFollowDone = 0
            gVars.CurrentLikeDone = 0
            gVars.CurrentStoryViewDone = 0
            gVars.CurrentCommentsDone = 0

            gVars.CurrentExFollowDone = 0
            gVars.CurrentExCommentsDone = 0
            gVars.CurrentExLikeDone = 0

            gVars.TotFollow = 0
            gVars.TotUnFollow = 0
            gVars.TotLikes = 0
            gVars.TotStoryViews = 0
            gVars.TotComments = 0

            gVars.TotExComments = 0
            gVars.TotExLikes = 0
            gVars.TotExFollow = 0

            gVars.ReqFollow = 0
            gVars.ReqUnFollow = 0
            gVars.ReqLikes = 0
            gVars.ReqStoryViews = 0
            gVars.ReqComments = 0

            gVars.ReqExFollow = 0
            gVars.ReqExLikes = 0
            gVars.ReqExComments = 0

            gVars.SequenceRunning = False

            gVars.TotalActionsLoaded = 0
            gVars.ActionLoaded = 0
            
            gVars.RequiredActionPerformed = 0
            gVars.ActionPerformed = 0
            gVars.LastSuccessfulSequenceRunDate = None


            gVars.API_BaseURL = "https://socialplannerpro.com/API"

            self.gVars = gVars
            print('Loading New Defaults')
            if (platform.system() == "Darwin"):
                Path(os.path.join(os.getenv("HOME"), ".SocialPlannerPro")).mkdir(parents=True, exist_ok=True)
                file_to_open = os.path.join(os.getenv("HOME"), ".SocialPlannerPro", "glob.vars")
            else:
                file_to_open = Path("userdata") / "glob.vars"

            try:
                with open(file_to_open, 'wb') as gVarFile:
                    pickle.dump(gVars, gVarFile)
            except Exception as e:
                #show error that admin access is required
                if not self.alert_dialog:
                    self.alert_dialog = MDDialog(
                        title="Error!",
                        text="Please re-launch the application with administrative rights.",
                        buttons=[
                            MDFlatButton(
                                text="Ok",
                                text_color=app.theme_cls.primary_color,
                            ),
                        ],
                    )
                    self.alert_dialog.open()
        
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

            if (platform.system() == "Darwin"):
                Path(os.path.join(os.getenv("HOME"), ".SocialPlannerPro")).mkdir(parents=True, exist_ok=True)
                settings_file = os.path.join(os.getenv("HOME"), ".SocialPlannerPro", username + '_login.json')
            else:
                settings_file = Path("userdata") / str(username + '_login.json')

            
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


    def ResetGlobalVars(self):
        app = App.get_running_app()
        api = app.api
        
        gVars = app.gVars

        gVars.RunStartTime = None
        gVars.RunEndTime = None
        gVars.TotalSessionTime = 0
        gVars.manifestJson = None
        gVars.manifestObj = None
        gVars.ElapsedTime = 0 
        
        gVars.hashtagActions = None
        gVars.locationActions = None
        gVars.UnFollowActions = None
        gVars.DCActions = None
        gVars.SuggestFollowers = None
        gVars.StoryViewActions = None
        gVars.GlobalTodo = None
        gVars.Todo = None
        gVars.DailyStatsSent = False
        gVars.DailyStatsSentDate = ''
    

        gVars.CurrentFollowDone = 0
        gVars.CurrentUnFollowDone = 0
        gVars.CurrentLikeDone = 0
        gVars.CurrentStoryViewDone = 0
        gVars.CurrentCommentsDone = 0

        gVars.CurrentExFollowDone = 0
        gVars.CurrentExCommentsDone = 0
        gVars.CurrentExLikeDone = 0

        gVars.TotFollow = 0
        gVars.TotUnFollow = 0
        gVars.TotLikes = 0
        gVars.TotStoryViews = 0
        gVars.TotComments = 0

        gVars.TotExComments = 0
        gVars.TotExLikes = 0
        gVars.TotExFollow = 0

        gVars.ReqFollow = 0
        gVars.ReqUnFollow = 0
        gVars.ReqLikes = 0
        gVars.ReqStoryViews = 0
        gVars.ReqComments = 0

        gVars.ReqExFollow = 0
        gVars.ReqExLikes = 0
        gVars.ReqExComments = 0
        gVars.SequenceRunning = False

        gVars.TotalActionsLoaded = 0
        gVars.ActionLoaded = 0
        
        gVars.RequiredActionPerformed = 0
        gVars.ActionPerformed = 0

        


        

    def AppLogout(self):
        app = App.get_running_app()
        igusername = app.gVars.IGusername
        self.ResetGlobalVars()    
        app.gVars.loginResult = None
        app.api = None

        if (platform.system() == "Darwin"):
            Path(os.path.join(os.getenv("HOME"), ".SocialPlannerPro")).mkdir(parents=True, exist_ok=True)
            settings_file = os.path.join(os.getenv("HOME"), ".SocialPlannerPro", igusername+'_login.json')
        else:
            settings_file = Path("userdata") / str(igusername + '_login.json')

        try:
            os.remove(settings_file)
        except:
            print("Error while deleting file ", settings_file)


        if (platform.system() == "Darwin"):
            Path(os.path.join(os.getenv("HOME"), ".SocialPlannerPro")).mkdir(parents=True, exist_ok=True)
            file_to_open = os.path.join(os.getenv("HOME"), ".SocialPlannerPro", "glob.vars")
        else:
            file_to_open = Path("userdata") / "glob.vars"

        with open(file_to_open, 'wb') as gVarFile:
            print('Updating gVars at logout')
            pickle.dump(self.gVars, gVarFile)

    

if __name__ == '__main__':
    
    LoginApp().run()

#from InstagramAPI import InstagramAPI
from instagram_private_api import Client, ClientCompatPatch

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
import os
from connected import Connected


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


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('SAVED: {0!s}'.format(new_settings_file))

def IGLogin(username,password):
    device_id = None
    try:

        settings_file = 'login.json'
        if not os.path.isfile(settings_file):
            # settings file does not exist
            print('Unable to find file: {0!s}'.format(settings_file))

            # login new
            api = Client(
                username, password,#auto_patch=True,
                on_login=lambda x: onlogin_callback(x, settings_file))
        else:
            with open(settings_file) as file_data:
                cached_settings = json.load(file_data, object_hook=from_json)
            print('Reusing settings: {0!s}'.format(settings_file))

            device_id = cached_settings.get('device_id')
            # reuse auth settings
            api = Client(
                username, password,#auto_patch=True,
                settings=cached_settings)

    except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
        print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

        # Login expired
        # Do relogin but use default ua, keys and such
        api = Client(
            username, password,#auto_patch=True,
            device_id=device_id,
            on_login=lambda x: onlogin_callback(x, settings_file))

    except ClientLoginError as e:
        print('ClientLoginError {0!s}'.format(e))
        exit(9)
    except ClientError as e:
        print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
        exit(9)
    except Exception as e:
        print('Unexpected Exception: {0!s}'.format(e))
        exit(99)

    # Show when login expires
    cookie_expiry = api.cookie_jar.auth_expires
    print('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))

    return api




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


try:
    with open('glob.Vars', 'rb') as gVarFile:
        print('Vars file found, loading')
        gVars = pickle.load(gVarFile)
except IOError:
    print('Vars file does not exist, InitBlank')
    gVars = GlobalVars()
    gVars.BotVer = 'py.1.6'
    gVars.RunStartTime = None
    gVars.RunEndTime = None
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
    gVars.API_BaseURL = "https://socialgrowthlabs.com/API"

    with open('glob.Vars', 'wb') as gVarFile:
        pickle.dump(gVars, gVarFile)


if gVars.loginResult is None:
        print('performing app login')
        gVars.loginResult = cf.AppLogin('nevillekmiec','103381','123',gVars)

api = IGLogin('nevillekmiec','!_LKvXc1')

print(api.authenticated_user_id)

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

with open('glob.Vars', 'wb') as gVarFile:
    print('Updating gVars at end')
    pickle.dump(gVars, gVarFile)




class Login(Screen):
    def do_login(self, loginText, passwordText):
        app = App.get_running_app()

        app.username = loginText
        app.password = passwordText

        gVars.loginResult = cf.AppLogin(loginText,passwordText,'123',gVars)

        print(gVars.loginResult)

        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'connected'

        app.config.read(app.get_application_config())
        app.config.write()

    def resetForm(self):
        self.ids['login'].text = ""
        self.ids['password'].text = ""

class LoginApp(App):
    username = StringProperty(None)
    password = StringProperty(None)

    def build(self):
        manager = ScreenManager()

        manager.add_widget(Login(name='login'))
        manager.add_widget(Connected(name='connected'))

        return manager

    def get_application_config(self):
        if(not self.username):
            return super(LoginApp, self).get_application_config()

        conf_directory = self.user_data_dir + '/' + self.username

        if(not os.path.exists(conf_directory)):
            os.makedirs(conf_directory)

        return super(LoginApp, self).get_application_config(
            '%s/config.cfg' % (conf_directory)
        )

if __name__ == '__main__':
    LoginApp().run()
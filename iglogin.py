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
import logging
import threading
import requests
import json
import time
import datetime
import codecs
from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,ClientCheckpointRequiredError,ClientChallengeRequiredError,
        __version__ as client_version)


class IGLogin(Screen):

    headers = None


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

    
    def do_login(self, loginText, passwordText):
        app = App.get_running_app()

        app.username = loginText
        app.password = passwordText
        api = None
        device_id = None
        try:

            settings_file = 'login.json'
            if not os.path.isfile(settings_file):
                # settings file does not exist
                print('Unable to find file: {0!s}'.format(settings_file))
               
                # login new
                api = Client(
                    loginText, passwordText,#auto_patch=True,
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
                on_login=lambda x: self.onlogin_callback(x, settings_file))
        
        except ClientCheckpointRequiredError as e:
            #(ClientError)
            print('Unexpected ClientCheckpointRequiredError: {0!s}'.format(e))
            checkpoint_url = e.challenge_url

            headers = {}
            authenticated = False
            logged_in = False

            BASE_URL = ''#'https://www.instagram.com/'
            headers.update({'Referer': BASE_URL})
            req = requests.get(BASE_URL[:-1] + checkpoint_url)
            headers.update({'X-CSRFToken': req.cookies['csrftoken'], 'X-Instagram-AJAX': '1'})
            headers.update({'Referer': BASE_URL[:-1] + checkpoint_url})
            mode = int(input('Choose a challenge mode (0 - SMS, 1 - Email): '))
            challenge_data = {'choice': mode}
            challenge = requests.post(BASE_URL[:-1] + checkpoint_url, data=challenge_data, allow_redirects=True)
            headers.update({'X-CSRFToken': challenge.cookies['csrftoken'], 'X-Instagram-AJAX': '1'})

            code = input('Enter code received: ').strip()
            code_data = {'security_code': code}
            code = requests.post(BASE_URL[:-1] + checkpoint_url, data=code_data, allow_redirects=True)
            headers.update({'X-CSRFToken': code.cookies['csrftoken']})
            cookies = code.cookies
            code_text = json.loads(code.text)
            if code_text.get('status') == 'ok':
                authenticated = True
                logged_in = True
            elif 'errors' in code.text:
                for count, error in enumerate(code_text['challenge']['errors']):
                    count += 1
                    logging.error('Session error %(count)s: "%(error)s"' % locals())
            else:
                logging.error(json.dumps(code_text))


        # except ClientChallengeRequiredError as e:
        #     print('Unexpected ClientChallengeRequiredError: {0!s}'.format(e))

        except ClientLoginError as e:
            print('ClientLoginError {0!s}'.format(e))
           
        except ClientError as e:
            print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
            
        except Exception as e:
            print('Unexpected Exception: {0!s}'.format(e))
            

        # Show when login expires
        cookie_expiry = api.cookie_jar.auth_expires
        print('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))

       
        if api is None:
            Alert(title='Error', text='Login nai howa')
        else:
            app.api = api

            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = 'ready'
    
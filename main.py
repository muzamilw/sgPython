from InstagramAPI import InstagramAPI
from itertools import islice
import requests 
import pandas as pd
import datetime
#import numpy
from random import choices
#from collections import Counter
from time import sleep
from random import randint
import json
import logging
import time
import random
from random import randrange

import datetime, pytz
import dateutil.tz
#import sys
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
import pickle
#from v import MIMETextnpm

import customFunctions
import apiWrappers
import botLogic


#global vars

API_BaseURL = "https://socialgrowthlabs.com/API"




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

def IGLogin():
    InstagramAPI.ver = login_challenge
    api = InstagramAPI("nevillekmiec", "!_LKvXc1")
    api.login()
    try:
        link = api.LastJson['challenge']['api_path']
        api.ver(link)
        api.login()
    except:
        pass
    return api

#reading api file if already exists.
try:
    with open('api.login', 'rb') as api_login_file:
        print('api login found, loading')
        api = pickle.load(api_login_file)
except IOError:
    print('api file does not exist, performing login')
    api = IGLogin()
    with open('api.login', 'wb') as api_login_file:
        pickle.dump(api, api_login_file)


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
    gVars.GlobalTodo = None
    gVars.Todo = None
    gVars.DailyStatsSent = False

    with open('glob.Vars', 'wb') as gVarFile:
        pickle.dump(gVars, gVarFile)

print(api.username_id)
print(gVars.BotVer)

botLogic.RunBot(gVars,api)






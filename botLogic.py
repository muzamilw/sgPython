
import customFunctions as cf
import apiWrappers as apiW
import datetime
import time
from time import sleep
from enum import Enum
import datetime, pytz
import pandas as pd
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from itertools import islice
from random import randrange
from random import choices
import random
import sys
import pickle
import logging
from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)

from kivy.app import App

class Actions(Enum):
    Follow = 60
    UnFollow = 61
    Like = 62
    Comment = 63
    StoryView = 64
    FollowersCountUpdate = 65
    ActionBlock = 66
    HardBlock = 67
    PasswordBlock = 68
    ClearBlock = 69
    Block4 = 70
    Block5 = 71
    InitStatsReceived = 72
    FollowExchange=73
    LikeExchange = 74
    BotError = 80
    BadHashtag = 86

class Bot():
    def __init__(self,  Client, log, ui):
        self.ui = ui
        self.Client = Client
        self.log = log

    def dump(self,obj):
        for attr in dir(obj):
            self.log.info("obj.%s = %r" % (attr, getattr(obj, attr)))

    def RunBot(self):
        app = App.get_running_app()
        api = app.api
        log = self.log
        gVars = app.gVars
        gVars.RunStartTime = datetime.datetime.now()
        
        if gVars.loginResult is not None:
            gVars.SocialProfileId = gVars.loginResult["SocialProfileId"]
            gVars.manifest = cf.GetManifest(gVars.loginResult["SocialProfileId"],gVars)

            if api.authenticated_user_id is not None:

                try:
                    if (gVars.loginResult["InitialStatsReceived"] != True):

                        user_info = api.user_info(api.authenticated_user_id)

                        cf.UpdateInitialStatsToServer(gVars.SocialProfileId,user_info['user']['follower_count'],user_info['user']['following_count'],user_info['user']['media_count'],gVars)

                        log.info('int followers' + str(user_info['user']['follower_count']))
                        log.info('Init Following' +str(user_info['user']['following_count']))
                        log.info('InitPosts' + str(user_info['user']['media_count']))
                    else:
                        log.info('initial stats already sent')

                    
                    # counter = 0
                    # while  (counter < 100):
                    #     sleep(1) # blocking operation
                    #     log.info("count " + str(counter))
                    #     self.ui.lblFollowCount.text = str(counter)
                    #     counter = counter + 1

                    # return

                        
                    #sending daily stats
                    if gVars.DailyStatsSent == False:
                        # InitFollowers = len(apiW.getTotalFollowers(api,api.username_id))
                        # InitFollowing = len(apiW.getTotalFollowings(api,api.username_id))
                        # InitPosts = len(apiW.getTotalUserFeed(api,api.username_id))
                        user_info = api.user_info(api.authenticated_user_id)
                        log.info('Sending Daily Stats')
                        cf.SendAction(gVars,gVars.SocialProfileId,Actions.FollowersCountUpdate,'self','{\"InitialFollowings\":\"'+str(user_info['user']['following_count'])+'\",\"InitialFollowers\":\"'+ str(user_info['user']['follower_count']) +'\",\"InitialPosts\":\"'+str(user_info['user']['media_count'])+'\",\"SocialProfileId\":'+str(gVars.SocialProfileId)+'}')
                        gVars.DailyStatsSent = True
                    else:
                        log.info('Daily Stats already sent')
                    #"Message":"{\"InitialFollowings\":\"400\",\"InitialFollowers\":\"1200\",\"InitialPosts\":\"6\",\"SocialProfileId\":28}"
                        
                    

                    if gVars.manifestJson is None:
                        log.info('getting manifest from SGServer')
                        gVars.manifestJson = cf.GetManifest(gVars.SocialProfileId,gVars)

                    

                    if gVars.manifestObj is None:
                        log.info('loading manifest')
                        gVars.manifestObj = cf.LoadManifest(gVars.manifestJson)
                        gVars.ReqFollow = gVars.manifestObj.FollAccSearchTags
                        gVars.ReqUnFollow = gVars.manifestObj.UnFoll16DaysEngage
                        gVars.ReqLikes = gVars.manifestObj.LikeFollowingPosts
                        gVars.ReqStoryViews = gVars.manifestObj.VwStoriesFollowing
                        gVars.ReqComments = gVars.manifestObj.CommFollowingPosts
                    
                    

                    if gVars.Todo is None:
                        gVars.Todo = cf.SetupGlobalTodo([0.2, 0.3, 0.2, 0.2, 0.1], gVars.manifestObj.totalActions)
                        log.info('Creating Empty Global todo')
                    

                    if gVars.hashtagActions is None:
                        log.info('Getting Feeds of Hashtags and creating action list')
                        hashstart = datetime.datetime.now()
                        gVars.hashtagActions = cf.LoadHashtagsTodo(api,gVars.manifestObj,[0.33, 0.33, 0.33],Client)
                        LoadtimeHashtagsTodo = (datetime.datetime.now()-hashstart).total_seconds()
                        log.info('Hashtag Feed Done in seconds : ' + str(LoadtimeHashtagsTodo))
                        gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeHashtagsTodo
                    
                    
                        
                    if gVars.locationActions is None:
                        log.info('Getting Feeds of Location and creating action list')
                        locationtart = datetime.datetime.now()
                        gVars.locationActions = cf.LoadLocationsTodo(api,gVars.manifestObj,[0.33, 0.33, 0.33],gVars.hashtagActions.groupby(['Action'])['Seq'].count(),Client)
                        LoadtimeLocTodo = (datetime.datetime.now()-locationtart).total_seconds()
                        log.info('Location Feed Done in seconds : ' + str(LoadtimeLocTodo))
                        gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeLocTodo

                    
                        
                    if gVars.DCActions is None:
                        log.info('Getting Feeds of Competitors and creating action list')
                        DCstart = datetime.datetime.now()
                        gVars.DCActions = cf.LoadCompetitorTodo(api,gVars.manifestObj,[0.33, 0.33, 0.33],gVars.locationActions.groupby(['Action'])['Seq'].count(),Client)
                        LoadtimeDCTodo = (datetime.datetime.now()-DCstart).total_seconds()
                        log.info('Competitors Feed Done in seconds : ' + str(LoadtimeDCTodo))
                        gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeDCTodo

                    if gVars.SuggestFollowers is None:
                        log.info('Getting Feeds of Suggested Users and creating action list')
                        Suggestedstart = datetime.datetime.now()
                        gVars.SuggestFollowers = cf.LoadSuggestedUsersForFollow(api,gVars.manifestObj,[0.33, 0.33, 0.33],gVars.DCActions.groupby(['Action'])['Seq'].count(),Client)
                        LoadtimeSuggestedTodo = (datetime.datetime.now()-Suggestedstart).total_seconds()
                        log.info('Suggested Users Feed Done in seconds : ' + str(LoadtimeSuggestedTodo))
                        gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeSuggestedTodo

                        
                    if gVars.UnFollowActions is None:
                        log.info('Getting Feeds of UnFollow and creating action list')
                        UnFollstart = datetime.datetime.now()
                        gVars.UnFollowActions = cf.LoadUnFollowTodo(api,gVars.manifestObj,[1])
                        LoadtimeUnFollTodo = (datetime.datetime.now()-UnFollstart).total_seconds()
                        log.info('UnFollow Feed Done in seconds : ' + str(LoadtimeUnFollTodo))
                        gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeUnFollTodo

                    if gVars.StoryViewActions is None:
                        log.info('Getting Feeds of StoryViews and creating action list')
                        Storystart = datetime.datetime.now()
                        gVars.StoryViewActions = cf.LoadStoryTodo(api,gVars.manifestObj,[1])
                        LoadtimeStoryTodo = (datetime.datetime.now()-Storystart).total_seconds()
                        log.info('StoryViews Feed Done in seconds : ' + str(LoadtimeStoryTodo))
                        gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeStoryTodo

                    #media_seen(reels)

                    frames = [gVars.hashtagActions, gVars.locationActions, gVars.DCActions, gVars.UnFollowActions,gVars.SuggestFollowers,gVars.StoryViewActions]
                    actions = pd.concat(frames)

                    if gVars.GlobalTodo is None:
                        gVars.GlobalTodo = gVars.Todo.merge(actions,how='left', left_on=['Seq','Action'], right_on=['Seq','Action'])
                        gVars.GlobalTodo.to_csv('GlobData.csv')
                        log.info('GlobalTodo merged')
                        gVars.TotFollow = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'Follow') & (gVars.GlobalTodo['UserId'] != '')])
                        gVars.TotUnFollow = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'UnFollow') & (gVars.GlobalTodo['UserId'] != '')])
                        gVars.TotLikes = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'Like') & (gVars.GlobalTodo['UserId'] != '')])
                        gVars.TotStoryViews = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'StoryView') & (gVars.GlobalTodo['UserId'] != '')])
                        gVars.TotComments = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'Comment') & (gVars.GlobalTodo['UserId'] != '')])
                        

                    #GlobalTodo[GlobalTodo['Action'] == 'Like']

                    
                    
                    LoadtimeTodo = (datetime.datetime.now()-gVars.RunStartTime).total_seconds()
                    log.info("Total Seconds to Build Action Todo " + str(LoadtimeTodo))
                    # #dump(gVars.manifestObj)
                except Exception as e: ## try catch block for the 
                    log.info('Unexpected Exception in initial feed loads : {0!s}'.format(e))
                
                    
                return

                # #iterList = (GlobalTodo[GlobalTodo['Status'] == '1']).iterrows()
                # #log.info(iterList) 
                # #for i, row in islice(GlobalTodo.iterrows(),0,10):
                # #    if row['Status'] == 1:
                # #        log.info(row)
                
                
                
                Comments = ['😀','👍','💓','🤩','🥰']
                curRow = None

                try:
                    for i, row in islice(gVars.GlobalTodo.iterrows(),0,10000):
                        if row['Status'] == 1 and not pd.isnull(str(row['MediaId'])):
                            
                            waitTime = randrange(20,30)
                            
                            
                            if row['Action'] == 'Like':
                                try:
                                    log.info('like action : ' + row['MediaId'])
                                    apiW.LikeMedia(api,row['MediaId'])
                                    cf.SendAction(gVars,gVars.SocialProfileId,Actions.Like,row['Username'],row['MediaId'])
                                
                                except ClientError as e:
                                    log.info('Like IG Error MediaId deleted {3!s}  {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response, row['MediaId']))
                                    cf.SendAction(gVars,gVars.SocialProfileId,Actions.BotError,row['Username'],'Deleted MediaId while liking : ' + str(row['MediaId']))
                                    gVars.GlobalTodo.loc[i,'Data'] = 'Deleted MediaId while liking'

                                gVars.GlobalTodo.loc[i,'Status'] = 2
                                gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                log.info('sleeping for : ' + str(waitTime))
                                gVars.CurrentLikeDone = gVars.CurrentLikeDone + 1
                                time.sleep(waitTime) 
                                

                            if row['Action'] == 'Follow':
                                apiW.FollowUser(api,row['UserId'])
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.Follow,row['Username'],'')
                                log.info('Follow action : ' + row['Username'])
                                gVars.GlobalTodo.loc[i,'Status'] = 2
                                gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                log.info('sleeping for : ' + str(waitTime))
                                gVars.CurrentFollowDone = gVars.CurrentFollowDone + 1
                                time.sleep(waitTime) 

                            if row['Action'] == 'Comment':
                                comm = random.choice(Comments)
                                try:
                                    log.info('Comment action : ' + row['MediaId'])
                                    apiW.CommentOnMedia(api,row['MediaId'],comm)
                                    cf.SendAction(gVars,gVars.SocialProfileId,Actions.Comment,row['Username'],row['Username'] + 'Comment added : ' + comm)
                                    gVars.GlobalTodo.loc[i,'Data'] = 'Comment added : ' + comm
                                except ClientError as e:
                                    log.info('Comment IG Error MediaId deleted {3!s}  {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response, row['MediaId']))
                                    cf.SendAction(gVars,gVars.SocialProfileId,Actions.BotError,row['Username'],'Deleted MediaId while Commenting : ' + str(row['MediaId']))
                                    gVars.GlobalTodo.loc[i,'Data'] = 'Deleted MediaId while Commenting'

                                gVars.GlobalTodo.loc[i,'Status'] = 2
                                gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                
                                log.info('sleeping for : ' + str(waitTime))
                                gVars.CurrentCommentsDone = gVars.CurrentCommentsDone + 1
                                time.sleep(waitTime) 
                                        
                            if row['Action'] == 'UnFollow':
                                if row['Tag'] == 'delete_not_found':  ##ignore the IG action and send it anyways
                                    cf.SendAction(gVars,gVars.SocialProfileId,Actions.UnFollow,row['Username'],'delete_not_found')
                                else:
                                    apiW.UnFollowUser(api,row['UserId'])
                                    cf.SendAction(gVars,gVars.SocialProfileId,Actions.UnFollow,row['Username'],'')
                                log.info('UnFollow action : ' + row['Username'])
                                gVars.GlobalTodo.loc[i,'Status'] = 2
                                gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                log.info('sleeping for : ' + str(waitTime))
                                gVars.CurrentUnFollowDone = gVars.CurrentUnFollowDone + 1
                                time.sleep(waitTime) 

                            if row['Action'] == 'StoryView':
                                log.info('StoryView action : ' + row['Username'])
                                apiW.ViewStory(api,row['MediaId'],row['FriendShipStatus'])
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.StoryView,row['Username'],'story pages : ' + str(len(row['MediaId'])))
                                
                                gVars.GlobalTodo.loc[i,'Status'] = 2
                                gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                gVars.GlobalTodo.loc[i,'Data'] = 'story pages : ' + str(len(row['MediaId']))
                                log.info('sleeping for : ' + str(waitTime))
                                gVars.CurrentStoryViewDone = gVars.CurrentStoryViewDone + 1
                                time.sleep(waitTime) 

                            with open('glob.Vars', 'wb') as gVarFile:
                                pickle.dump(gVars, gVarFile)

                    #Run Ending
                    gVars.RunEndTime = datetime.datetime.now()
                    
                    #writing log to file
                    
                    with open("dataframe_GlobalTodo.html", "w", encoding="utf-8") as file:
                        file.writelines('<meta charset="UTF-8">\n')
                        file.write(gVars.GlobalTodo.to_html())
                    
                    
                    
                    #cf.SendEmail('muzamilw@gmail.com','muzamilw@gmail.com','Sh@rp2020','dataframe_GlobalTodo.html','','')
                    
                except:# ClientError:
                    #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                    log.info("exception occurred in main bot action loop")
                    log.info(sys.exc_info())

                #gVars.GlobalTodo.to_csv('GlobData.csv')

                return gVars
            else:
                #perform login
                log.info('IG user is not logged in.')
        else:
            log.info('Error logging onto SG Server')

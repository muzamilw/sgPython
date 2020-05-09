
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
import ctypes 
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
    def __init__(self,  Client, log, ui,botStop):
        self.ui = ui
        self.Client = Client
        self.log = log
        self.botStop = botStop

    def raise_exception(self): 
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
              ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            print('Exception raise failure') 
        

    def dump(self,obj):
        for attr in dir(obj):
            self.log.info("obj.%s = %r" % (attr, getattr(obj, attr)))

    def CleanupAfterSuccessfulRun(self):
        app = App.get_running_app()
        api = app.api
        log = self.log


        gVars = app.gVars

        gVars.RunStartTime = None
        gVars.RunEndTime = None
        gVars.TotalSessionTime = 0
        gVars.manifestJson = None
        gVars.manifestObj = None
        
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


    def RunBot(self):
        app = App.get_running_app()
        api = app.api
        log = self.log


        gVars = app.gVars

        
        # i = True
        # while i  < 100:
        #     log.info('Looopi ' + str(i))
        #     waitTime = randrange(1,2)
        #     time.sleep(waitTime) 
        #     i = i + 1
        #     if (self.ui.botStop == True):
        #         print('exiting thread')
        #         return


        # return
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
                    if gVars.DailyStatsSent == False and gVars.DailyStatsSentDate != datetime.datetime.today:
                        # InitFollowers = len(apiW.getTotalFollowers(api,api.username_id))
                        # InitFollowing = len(apiW.getTotalFollowings(api,api.username_id))
                        # InitPosts = len(apiW.getTotalUserFeed(api,api.username_id))
                        user_info = api.user_info(api.authenticated_user_id)
                        log.info('Sending Daily Stats')
                        cf.SendAction(gVars,gVars.SocialProfileId,Actions.FollowersCountUpdate,'self','{\"InitialFollowings\":\"'+str(user_info['user']['following_count'])+'\",\"InitialFollowers\":\"'+ str(user_info['user']['follower_count']) +'\",\"InitialPosts\":\"'+str(user_info['user']['media_count'])+'\",\"SocialProfileId\":'+str(gVars.SocialProfileId)+'}')
                        gVars.DailyStatsSent = True
                        gVars.DailyStatsSentDate = datetime.datetime.today
                    else:
                        log.info('Daily Stats already sent for today')
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

                        gVars.ReqExComments = len(gVars.manifestObj.FollowersToComment)
                        gVars.ReqExFollow = len(gVars.manifestObj.FollowList)
                        gVars.ReqExLikes  = len(gVars.manifestObj.LikeList)
                    
                    self.ui.lblFollow.text = str(gVars.CurrentFollowDone) +'/'+ str(gVars.TotFollow) +'/'+ str(gVars.ReqFollow)
                    self.ui.lblUnFollow.text = str(gVars.CurrentUnFollowDone) +'/'+str(gVars.TotUnFollow ) +'/'+ str( gVars.ReqUnFollow)
                    self.ui.lblLike.text = str(gVars.CurrentLikeDone) +'/'+str(gVars.TotLikes ) +'/'+ str( gVars.ReqLikes)
                    self.ui.lblStoryView.text = str(gVars.CurrentStoryViewDone) +'/'+str(gVars.TotStoryViews ) +'/'+ str( gVars.ReqStoryViews)
                    self.ui.lblComments.text = str(gVars.CurrentCommentsDone) +'/'+str(gVars.TotComments ) +'/'+ str( gVars.ReqComments)
                    self.ui.lblLikeExchange.text = str(gVars.CurrentExLikeDone) +'/'+str(gVars.TotExLikes ) +'/'+ str( gVars.ReqExLikes)
                    self.ui.lblFollowExchange.text = str(gVars.CurrentExFollowDone) +'/'+ str(gVars.TotExFollow ) +'/'+ str( gVars.ReqExFollow)
                    self.ui.lblCommentExchange.text = str(gVars.CurrentExCommentsDone) +'/'+str(gVars.TotExComments ) +'/'+ str( gVars.ReqExComments)
                    
                    

                    if gVars.Todo is not  None:
                        gVars.Todo = cf.SetupGlobalTodo([0.2, 0.3, 0.2, 0.2, 0.1], gVars.manifestObj.totalActions)
                        log.info('Creating Empty Global todo')
                    

                    if gVars.hashtagActions is None:
                        log.info('Getting Feeds of Hashtags and creating action list')
                        hashstart = datetime.datetime.now()
                        gVars.hashtagActions = cf.LoadHashtagsTodo(api,gVars.manifestObj,Client,log)
                        LoadtimeHashtagsTodo = (datetime.datetime.now()-hashstart).total_seconds()
                        log.info('Hashtag Feed Done in seconds : ' + str(LoadtimeHashtagsTodo))
                        gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeHashtagsTodo
                    
                        
                    if gVars.locationActions is None:
                        log.info('Getting Feeds of Location and creating action list')
                        locationtart = datetime.datetime.now()
                        gVars.locationActions = cf.LoadLocationsTodo(api,gVars.manifestObj,gVars.hashtagActions.groupby(['Action'])['Seq'].count(),Client,log)
                        LoadtimeLocTodo = (datetime.datetime.now()-locationtart).total_seconds()
                        log.info('Location Feed Done in seconds : ' + str(LoadtimeLocTodo))
                        gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeLocTodo

                    
                        
                    if gVars.DCActions is None:
                        log.info('Getting Feeds of Competitors and creating action list')
                        DCstart = datetime.datetime.now()
                        gVars.DCActions = cf.LoadCompetitorTodo(api,gVars.manifestObj,gVars.locationActions.groupby(['Action'])['Seq'].count(),Client,log)
                        LoadtimeDCTodo = (datetime.datetime.now()-DCstart).total_seconds()
                        log.info('Competitors Feed Done in seconds : ' + str(LoadtimeDCTodo))
                        gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeDCTodo

                    if gVars.SuggestFollowers is None:
                        log.info('Getting Feeds of Suggested Users and creating action list')
                        Suggestedstart = datetime.datetime.now()
                        gVars.SuggestFollowers = cf.LoadSuggestedUsersForFollow(api,gVars.manifestObj,gVars.DCActions.groupby(['Action'])['Seq'].count(),Client,log)
                        LoadtimeSuggestedTodo = (datetime.datetime.now()-Suggestedstart).total_seconds()
                        log.info('Suggested Users Feed Done in seconds : ' + str(LoadtimeSuggestedTodo))
                        gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeSuggestedTodo

                        
                    if gVars.UnFollowActions is None:
                        log.info('Getting Feeds of UnFollow and creating action list')
                        UnFollstart = datetime.datetime.now()
                        gVars.UnFollowActions = cf.LoadUnFollowTodo(api,gVars.manifestObj,[1],log)
                        LoadtimeUnFollTodo = (datetime.datetime.now()-UnFollstart).total_seconds()
                        log.info('UnFollow Feed Done in seconds : ' + str(LoadtimeUnFollTodo))
                        gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeUnFollTodo

                    if gVars.StoryViewActions is None:
                        log.info('Getting Feeds of StoryViews and creating action list')
                        Storystart = datetime.datetime.now()
                        gVars.StoryViewActions = cf.LoadStoryTodo(api,gVars.manifestObj,[1],log)
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

                    gVars.TotExComments = len(gVars.GlobalTodo[(gVars.GlobalTodo['FriendShipStatus'] == 'MustComment') & (gVars.GlobalTodo['UserId'] != '')])
                    gVars.TotExLikes = len(gVars.GlobalTodo[(gVars.GlobalTodo['FriendShipStatus'] == 'MustLike') & (gVars.GlobalTodo['UserId'] != '')])
                    gVars.TotExFollow = len(gVars.GlobalTodo[(gVars.GlobalTodo['FriendShipStatus'] == 'MustFollow') & (gVars.GlobalTodo['UserId'] != '')])
                    #row["FriendShipStatus"]
                    

                    #GlobalTodo[GlobalTodo['Action'] == 'Like']
                    self.ui.lblFollow.text = str(gVars.CurrentFollowDone) +'/'+ str(gVars.TotFollow) +'/'+ str(gVars.ReqFollow)
                    self.ui.lblUnFollow.text = str(gVars.CurrentUnFollowDone) +'/'+str(gVars.TotUnFollow ) +'/'+ str( gVars.ReqUnFollow)
                    self.ui.lblLike.text = str(gVars.CurrentLikeDone) +'/'+str(gVars.TotLikes ) +'/'+ str( gVars.ReqLikes)
                    self.ui.lblStoryView.text = str(gVars.CurrentStoryViewDone) +'/'+str(gVars.TotStoryViews ) +'/'+ str( gVars.ReqStoryViews)
                    self.ui.lblComments.text = str(gVars.CurrentCommentsDone) +'/'+str(gVars.TotComments ) +'/'+ str( gVars.ReqComments)
                    self.ui.lblLikeExchange.text = str(gVars.CurrentExLikeDone) +'/'+str(gVars.TotExLikes ) +'/'+ str( gVars.ReqExLikes)
                    self.ui.lblFollowExchange.text = str(gVars.CurrentExFollowDone) +'/'+ str(gVars.TotExFollow ) +'/'+ str( gVars.ReqExFollow)
                    self.ui.lblCommentExchange.text = str(gVars.CurrentExCommentsDone) +'/'+str(gVars.TotExComments ) +'/'+ str( gVars.ReqExComments)
                    

                    
                    LoadtimeTodo = (datetime.datetime.now()-gVars.RunStartTime).total_seconds()
                    log.info("Total Seconds to Build Action Todo " + str(LoadtimeTodo))
                    # #dump(gVars.manifestObj)
                except Exception as e: ## try catch block for the 
                    log.info('Unexpected Exception in initial feed loads : {0!s}'.format(e))
                
                    
                
                # #iterList = (GlobalTodo[GlobalTodo['Status'] == '1']).iterrows()
                # #log.info(iterList) 
                # #for i, row in islice(GlobalTodo.iterrows(),0,10):
                # #    if row['Status'] == 1:
                # #        log.info(row)

                # with open("dataframe_GlobalTodo.html", "w", encoding="utf-8") as file:
                #         file.writelines('<meta charset="UTF-8">\n')
                #         file.write(gVars.GlobalTodo.to_html())
                #         log.info('Todo writen to file')
                # gVars.GlobalTodo.to_csv('GlobData.csv')
                
                
                Comments = ['😀','👍','💓','🤩','🥰']
                curRow = None

                try:
                    for i, row in islice(gVars.GlobalTodo.iterrows(),0,10000):

                        if (self.ui.botStop == True):
                            print('Stopping Sequence')
                            return

                        if row['Status'] == 1 and not pd.isnull(str(row['MediaId'])) and str(row['MediaId']) != 'nan':
                            
                            waitTime = randrange(20,30)
                            
                            
                            if row['Action'] == 'Like' and gVars.manifestObj.AfterFollLikeuserPosts == 1 and ( gVars.CurrentLikeDone < gVars.manifestObj.LikeFollowingPosts or gVars.CurrentExLikeDone < gVars.ReqExLikes):
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

                                if row['FriendShipStatus'] == 'MustLike':
                                    gVars.CurrentExLikeDone = gVars.CurrentExLikeDone + 1
                                else:
                                    gVars.CurrentLikeDone = gVars.CurrentLikeDone + 1
                                
                                time.sleep(waitTime) 
                                

                            if row['Action'] == 'Follow' and gVars.manifestObj.FollowOn == 1 and (gVars.CurrentFollowDone < gVars.manifestObj.FollAccSearchTags or gVars.CurrentExFollowDone < gVars.ReqExFollow) :
                                apiW.FollowUser(api,row['UserId'])
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.Follow,row['Username'],'')
                                log.info('Follow action : ' + row['Username'])
                                gVars.GlobalTodo.loc[i,'Status'] = 2
                                gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                log.info('sleeping for : ' + str(waitTime))
                                if row['FriendShipStatus'] == 'MustFollow':
                                    gVars.CurrentExFollowDone = gVars.CurrentExFollowDone + 1
                                else:
                                    gVars.CurrentFollowDone = gVars.CurrentFollowDone + 1
                                
                                time.sleep(waitTime) 

                            if row['Action'] == 'Comment' and gVars.manifestObj.AfterFollCommentUserPosts == 1 and (gVars.CurrentCommentsDone < gVars.manifestObj.CommFollowingPosts or  gVars.CurrentExCommentsDone < gVars.ReqExComments):
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
                                if row['FriendShipStatus'] == 'MustComment':
                                    gVars.CurrentExCommentsDone = gVars.CurrentExCommentsDone + 1
                                else:
                                    gVars.CurrentCommentsDone = gVars.CurrentCommentsDone + 1
                                
                                time.sleep(waitTime) 
                                        
                            if row['Action'] == 'UnFollow' and gVars.manifestObj.UnFollFollowersAfterMinDays == 1:
                                log.info('UnFollow action : ' + row['Username'])
                                if row['Tag'] == 'delete_not_found':  ##ignore the IG action and send it anyways
                                    cf.SendAction(gVars,gVars.SocialProfileId,Actions.UnFollow,row['Username'],'delete_not_found')
                                else:
                                    try:
                                        apiW.UnFollowUser(api,row['UserId'])
                                        cf.SendAction(gVars,gVars.SocialProfileId,Actions.UnFollow,row['Username'],'')
                                    except ClientError as e:
                                        log.info('UnFollow api action error {3!s}  {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response, row['Username']))
                                        cf.SendAction(gVars,gVars.SocialProfileId,Actions.UnFollow,row['Username'],'delete_not_found')
                                    
                                gVars.GlobalTodo.loc[i,'Status'] = 2
                                gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                log.info('sleeping for : ' + str(waitTime))
                                gVars.CurrentUnFollowDone = gVars.CurrentUnFollowDone + 1
                                time.sleep(waitTime) 

                            if row['Action'] == 'StoryView' and gVars.manifestObj.AfterFollViewUserStory == 1 and gVars.CurrentStoryViewDone < gVars.manifestObj.VwStoriesFollowing :
                                log.info('StoryView action : ' + row['Username'])
                                apiW.ViewStory(api,row['MediaId'],row['FriendShipStatus'])
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.StoryView,row['Username'],'story pages : ' + str(len(row['MediaId'])))
                                
                                gVars.GlobalTodo.loc[i,'Status'] = 2
                                gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                gVars.GlobalTodo.loc[i,'Data'] = 'story pages : ' + str(len(row['MediaId']))
                                log.info('sleeping for : ' + str(waitTime))
                                gVars.CurrentStoryViewDone = gVars.CurrentStoryViewDone + 1
                                time.sleep(waitTime)

                            self.ui.lblFollow.text = str(gVars.CurrentFollowDone) +'/'+ str(gVars.TotFollow) +'/'+ str(gVars.ReqFollow)
                            self.ui.lblUnFollow.text = str(gVars.CurrentUnFollowDone) +'/'+str(gVars.TotUnFollow ) +'/'+ str( gVars.ReqUnFollow)
                            self.ui.lblLike.text = str(gVars.CurrentLikeDone) +'/'+str(gVars.TotLikes ) +'/'+ str( gVars.ReqLikes)
                            self.ui.lblStoryView.text = str(gVars.CurrentStoryViewDone) +'/'+str(gVars.TotStoryViews ) +'/'+ str( gVars.ReqStoryViews)
                            self.ui.lblComments.text = str(gVars.CurrentCommentsDone) +'/'+str(gVars.TotComments ) +'/'+ str( gVars.ReqComments)
                            self.ui.lblLikeExchange.text = str(gVars.CurrentExLikeDone) +'/'+str(gVars.TotExLikes ) +'/'+ str( gVars.ReqExLikes)
                            self.ui.lblFollowExchange.text = str(gVars.CurrentExFollowDone) +'/'+ str(gVars.TotExFollow ) +'/'+ str( gVars.ReqExFollow)
                            self.ui.lblCommentExchange.text = str(gVars.CurrentExCommentsDone) +'/'+str(gVars.TotExComments ) +'/'+ str( gVars.ReqExComments)
                    

                            with open('glob.Vars', 'wb') as gVarFile:
                                pickle.dump(gVars, gVarFile)

                    #Run Ending
                    gVars.RunEndTime = datetime.datetime.now()
                    log.info('Sequence has completed at : ' + str(gVars.RunEndTime) )
                    #writing log to file
                    
                    with open("dataframe_GlobalTodo.html", "w", encoding="utf-8") as file:
                        file.writelines('<meta charset="UTF-8">\n')
                        file.write(gVars.GlobalTodo.to_html())

                    log.info('Action List saved for Email' )
                    
                    
                    cf.SendEmail('muzamilw@gmail.com','muzamilw@gmail.com','Sh@rp2020','dataframe_GlobalTodo.html','','')
                    log.info('Email sent' )

                    self.CleanupAfterSuccessfulRun()
                    log.info('Cleanup performed exiting main thread')

                except ClientError as e:
                    #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                    log.info("api Client occurred in main bot action loop")
                    log.info(str(e))

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

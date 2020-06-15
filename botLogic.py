
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
import traceback
import sys
import os
import platform
from pathlib import Path
from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        ClientSentryBlockError, ClientChallengeRequiredError, ClientCheckpointRequiredError,ClientConnectionError,
        __version__ as client_version)

from kivy.app import App
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem

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
    ping = 99

    dialog = None




class Bot():
    def __init__(self,  Client, log, ui,botStop, logControl):
        self.ui = ui
        self.Client = Client
        self.log = log
        self.botStop = botStop
        self.logControl = logControl
        self.dialog = None

    def ShowErrorMessage(self, ErrorMsg):
        app = App.get_running_app()
        self.dialog = MDDialog(
                title="Critical Error!",
                text=ErrorMsg,
                
                buttons=[
                        MDFlatButton(
                            text="Ok",
                            text_color=app.theme_cls.primary_color,
                        ),
                    ],
            )

        # self.Logout_alert_dialog.buttons.append ("Close me!",action=lambda *x: self.dismiss_callback())
        # self.dialog.set_normal_height()
        self.dialog.open()

    def dismiss_callback(self, *args):
        self.dialog.dismiss()

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

    


    def RunBot(self):
        app = App.get_running_app()
        api = app.api
        log = self.log
        MaxRetryCount = 10
        RetryCount = 0
        RetryTimeSeconds = 30
        IsApiClientError = False

        gVars = app.gVars

        while True and self.botStop.is_set() == False and RetryCount <= MaxRetryCount and IsApiClientError == False:
            try:
                RetryCount = RetryCount + 1
                log.info("Starting Sequence")
                # return
                gVars.RunStartTime = datetime.datetime.now()
                gVars.SequenceRunning = True
                
                
                if gVars.loginResult is not None:
                    gVars.SocialProfileId = gVars.loginResult["SocialProfileId"]
                    gVars.manifest = cf.GetManifest(gVars.loginResult["SocialProfileId"],gVars)

                    if api.authenticated_user_id is not None:

                        try:

                            
                            if (gVars.loginResult["InitialStatsReceived"] != True):

                                user_info = api.user_info(api.authenticated_user_id)
                                cf.UpdateInitialStatsToServer(gVars.SocialProfileId,user_info['user']['follower_count'],user_info['user']['following_count'],user_info['user']['media_count'],gVars)
                                log.info('Int followers : ' + str(user_info['user']['follower_count']))
                                log.info('Init Following : ' +str(user_info['user']['following_count']))
                                log.info('InitPosts : ' + str(user_info['user']['media_count']))
                            else:
                                log.info('Initial stats already sent')

                            #sending daily stats
                            if gVars.DailyStatsSent == False and gVars.DailyStatsSentDate != datetime.datetime.today:
                                user_info = api.user_info(api.authenticated_user_id)
                                log.info('Sending Daily Stats')
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.FollowersCountUpdate,'self','{\"InitialFollowings\":\"'+str(user_info['user']['following_count'])+'\",\"InitialFollowers\":\"'+ str(user_info['user']['follower_count']) +'\",\"InitialPosts\":\"'+str(user_info['user']['media_count'])+'\",\"SocialProfileId\":'+str(gVars.SocialProfileId)+'}')
                                gVars.DailyStatsSent = True
                                gVars.DailyStatsSentDate = datetime.datetime.today
                            else:
                                log.info('Daily Stats already sent for today')
                            

                            if gVars.manifestJson is None:
                                log.info('getting manifest')
                                gVars.manifestJson = cf.GetManifest(gVars.SocialProfileId,gVars)

                            

                            if gVars.manifestObj is None:
                                log.info('loading manifest')
                                gVars.manifestObj = cf.LoadManifest(gVars.manifestJson)

                            gVars.ReqFollow = gVars.manifestObj.FollAccSearchTags
                            
                            gVars.ReqUnFollow = len(gVars.manifestObj.FollowersToUnFollow) #gVars.manifestObj.UnFoll16DaysEngage
                            gVars.TotUnFollow = len(gVars.manifestObj.FollowersToUnFollow)

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
                            
                            runTimeComputation = (gVars.ReqFollow + gVars.ReqUnFollow + gVars.ReqLikes + gVars.ReqStoryViews + gVars.ReqComments + gVars.ReqExComments + gVars.ReqExFollow + gVars.ReqExLikes) * 30 
                            gVars.TotalActionsLoaded = gVars.ReqFollow + gVars.ReqUnFollow + gVars.ReqLikes + gVars.ReqStoryViews + gVars.ReqComments + gVars.ReqExComments + gVars.ReqExFollow + gVars.ReqExLikes
                            runTimeComputation += gVars.manifestObj.totalActions  * 10
                            gVars.RequiredActionPerformed = gVars.manifestObj.totalActions

                            self.ui.TotalTime = int(runTimeComputation)


                            if gVars.Todo is None:
                                gVars.Todo = cf.SetupGlobalTodo(gVars.manifestObj)
                                log.info('Creating Empty Global todo')
                            

                            if gVars.hashtagActions is None:
                                log.info('Getting Feeds of Hashtags and creating action list')
                                hashstart = datetime.datetime.now()
                                gVars.hashtagActions = cf.LoadHashtagsTodo(api,gVars.manifestObj,Client,log,gVars)
                                LoadtimeHashtagsTodo = (datetime.datetime.now()-hashstart).total_seconds()
                                log.info('Hashtag Feed Done in seconds : ' + str(LoadtimeHashtagsTodo))
                                gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeHashtagsTodo
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.ping,'','ping')
                            
                                
                            if gVars.locationActions is None:
                                log.info('Getting Feeds of Location and creating action list')
                                locationtart = datetime.datetime.now()
                                gVars.locationActions = cf.LoadLocationsTodo(api,gVars.manifestObj,gVars.hashtagActions.groupby(['Action'])['Seq'].count(),Client,log,gVars)
                                LoadtimeLocTodo = (datetime.datetime.now()-locationtart).total_seconds()
                                log.info('Location Feed Done in seconds : ' + str(LoadtimeLocTodo))
                                gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeLocTodo
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.ping,'','ping')

                            
                                
                            if gVars.DCActions is None:
                                log.info('Getting Feeds of Competitors and creating action list')
                                DCstart = datetime.datetime.now()
                                SeqNos = gVars.locationActions.groupby(['Action'])['Seq'].count() + gVars.hashtagActions.groupby(['Action'])['Seq'].count()
                                gVars.DCActions = cf.LoadCompetitorTodo(api,gVars.manifestObj,SeqNos,Client,log,gVars)
                                LoadtimeDCTodo = (datetime.datetime.now()-DCstart).total_seconds()
                                log.info('Competitors Feed Done in seconds : ' + str(LoadtimeDCTodo))
                                gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeDCTodo
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.ping,'','ping')

                            if gVars.SuggestFollowers is None:
                                log.info('Getting Feeds of Suggested Users and creating action list')
                                Suggestedstart = datetime.datetime.now()
                                SeqNos = gVars.locationActions.groupby(['Action'])['Seq'].count() + gVars.hashtagActions.groupby(['Action'])['Seq'].count()
                                if (len(gVars.DCActions.groupby(['Action'])['Seq'].count()) > 0 ):
                                    SeqNos = SeqNos + gVars.DCActions.groupby(['Action'])['Seq'].count()
                                

                                gVars.SuggestFollowers = cf.LoadSuggestedUsersForFollow(api,gVars.manifestObj,SeqNos,Client,log,gVars)
                                LoadtimeSuggestedTodo = (datetime.datetime.now()-Suggestedstart).total_seconds()
                                log.info('Suggested Users Feed Done in seconds : ' + str(LoadtimeSuggestedTodo))
                                gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeSuggestedTodo
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.ping,'','ping')

                                
                            if gVars.UnFollowActions is not None and gVars.manifestObj.UnFollFollowersAfterMinDays == 1:
                                log.info('Getting Feeds of UnFollow and creating action list')
                                UnFollstart = datetime.datetime.now()
                                gVars.UnFollowActions = cf.LoadUnFollowTodo(api,gVars.manifestObj,[1],log,gVars)
                                LoadtimeUnFollTodo = (datetime.datetime.now()-UnFollstart).total_seconds()
                                log.info('UnFollow Feed Done in seconds : ' + str(LoadtimeUnFollTodo))
                                gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeUnFollTodo
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.ping,'','ping')

                            if gVars.StoryViewActions is None and gVars.manifestObj.AfterFollViewUserStory == 1:
                                log.info('Getting Feeds of StoryViews and creating action list')
                                Storystart = datetime.datetime.now()
                                gVars.StoryViewActions = cf.LoadStoryTodo(api,gVars.manifestObj,[1],log,gVars)
                                LoadtimeStoryTodo = (datetime.datetime.now()-Storystart).total_seconds()
                                log.info('StoryViews Feed Done in seconds : ' + str(LoadtimeStoryTodo))
                                gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeStoryTodo
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.ping,'','ping')

                            frames = [gVars.hashtagActions, gVars.locationActions, gVars.DCActions, gVars.UnFollowActions,gVars.SuggestFollowers,gVars.StoryViewActions]
                            actions = pd.concat(frames)

                            if gVars.GlobalTodo is None:
                                gVars.GlobalTodo = gVars.Todo.merge(actions,how='left', left_on=['Seq','Action'], right_on=['Seq','Action'])
                                #gVars.GlobalTodo.to_csv('GlobData.csv')
                                log.info('GlobalTodo merged')

                            gVars.TotFollow = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'Follow') & (gVars.GlobalTodo['UserId'] != '')])
                            gVars.TotUnFollow = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'UnFollow') & (gVars.GlobalTodo['UserId'].isnull() == False)])
                            gVars.TotLikes = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'Like') & (gVars.GlobalTodo['UserId'] != '')])
                            gVars.TotStoryViews = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'StoryView') & (gVars.GlobalTodo['UserId'] != '')])
                            gVars.TotComments = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'Comment') & (gVars.GlobalTodo['UserId'] != '')])

                            gVars.TotExComments = len(gVars.GlobalTodo[(gVars.GlobalTodo['FriendShipStatus'] == 'MustComment') & (gVars.GlobalTodo['UserId'] != '')])
                            gVars.TotExLikes = len(gVars.GlobalTodo[(gVars.GlobalTodo['FriendShipStatus'] == 'MustLike') & (gVars.GlobalTodo['UserId'] != '')])
                            gVars.TotExFollow = len(gVars.GlobalTodo[(gVars.GlobalTodo['FriendShipStatus'] == 'MustFollow') & (gVars.GlobalTodo['UserId'] != '')])
                            
                            
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

                            #debugging file
                            file_to_open = ""
                            if (platform.system() == "Darwin"):
                                Path(os.path.join(os.getenv("HOME"), ".SocialPlannerPro")).mkdir(parents=True, exist_ok=True)
                                file_to_open = os.path.join(os.getenv("HOME"), ".SocialPlannerPro", "GlobData.csv")
                            else:
                                file_to_open = Path("userdata") / "GlobData.csv"
                            gVars.GlobalTodo.to_csv(file_to_open)

                        except (ClientLoginError, ClientLoginRequiredError, ClientCookieExpiredError) as e:
                            #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                            log.info("Initial feed : Instagram Login occurred, Please sign off and relogin to continue")
                            log.info(str(traceback.format_exc()))
                            cf.SendError('muzamilw@gmail.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                            self.ShowErrorMessage("Initial feed : Instagram Login occurred,Stopping Sequence. Please sign off and relogin to continue")
                            IsApiClientError = True
                            return

                        except (ClientSentryBlockError, ClientChallengeRequiredError, ClientCheckpointRequiredError) as e:
                            #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                            log.info("Initial feed : Instagram Error occurred, Please open Instagram in the browser and manually clear any location Challenges or checkpoints")
                            log.info(str(traceback.format_exc()))
                            cf.SendError('muzamilw@gmail.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                            self.ShowErrorMessage("Initial feed : Critical Instagram Error occurred, Stopping Sequence. Please open Instagram in the browser and manually clear any location Challenges or checkpoints")
                            IsApiClientError = True
                            return

                        except (ClientError,ClientConnectionError) as e:
                            #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                            log.info("Initial feed : Api Client or Network Error occurred, Restarting")
                            log.info(str(traceback.format_exc()))
                            cf.SendError('muzamilw@gmail.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                           
                            raise e
                            
                        except Exception as e: ## try catch block for the 
                            log.info('Unexpected Exception in initial feed loads, restarting : {0!s}'.format(traceback.format_exc()))
                            cf.SendError('muzamilw@gmail.com',traceback.format_exc() + self.logControl.text ,gVars.SGusername)
                            raise e
                            
                        Comments = ['😀','👍','💓','🤩','🥰']
                        curRow = None

                        try:
                            for i, row in islice(gVars.GlobalTodo.iterrows(),0,10000):
                            
                                if (self.botStop.is_set() == True):
                                    print('Stopping Sequence')
                                    break

                                if row['Status'] == 1 and not pd.isnull(str(row['MediaId'])) and str(row['MediaId']) != 'nan':
                                    
                                    waitTime = randrange(20,30)
                                    
                                    
                                    if row['Action'] == 'Like' and gVars.manifestObj.AfterFollLikeuserPosts == 1 and ( gVars.CurrentLikeDone < gVars.manifestObj.LikeFollowingPosts or gVars.CurrentExLikeDone < gVars.ReqExLikes):
                                        try:
                                            log.info('like action : ' + row['MediaId'] + ', Sleeping for : ' + str(waitTime))
                                            apiW.LikeMedia(api,row['MediaId'])
                                            cf.SendAction(gVars,gVars.SocialProfileId,Actions.Like,row['Username'],row['MediaId'])
                                        except ClientError as e:
                                            log.info('Like IG Error MediaId deleted {3!s}  {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response, row['MediaId']))
                                            cf.SendAction(gVars,gVars.SocialProfileId,Actions.BotError,row['Username'],'Deleted MediaId while liking : ' + str(row['MediaId']))
                                            gVars.GlobalTodo.loc[i,'Data'] = 'Deleted MediaId while liking'

                                        gVars.GlobalTodo.loc[i,'Status'] = 2
                                        gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                        

                                        if row['FriendShipStatus'] == 'MustLike':
                                            gVars.CurrentExLikeDone = gVars.CurrentExLikeDone + 1
                                        else:
                                            gVars.CurrentLikeDone = gVars.CurrentLikeDone + 1
                                        
                                        time.sleep(waitTime) 
                                        

                                    if row['Action'] == 'Follow' and gVars.manifestObj.FollowOn == 1 and (gVars.CurrentFollowDone < gVars.manifestObj.FollAccSearchTags or gVars.CurrentExFollowDone < gVars.ReqExFollow) :
                                        apiW.FollowUser(api,row['UserId'])
                                        api.mute_unmute(row['UserId'])
                                        cf.SendAction(gVars,gVars.SocialProfileId,Actions.Follow,row['Username'],'')
                                        log.info('Follow action : ' + row['Username'] + ', Sleeping for : ' + str(waitTime))
                                        gVars.GlobalTodo.loc[i,'Status'] = 2
                                        gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                        
                                        if row['FriendShipStatus'] == 'MustFollow':
                                            gVars.CurrentExFollowDone = gVars.CurrentExFollowDone + 1
                                        else:
                                            gVars.CurrentFollowDone = gVars.CurrentFollowDone + 1
                                        
                                        time.sleep(waitTime) 

                                    if row['Action'] == 'Comment' and gVars.manifestObj.AfterFollCommentUserPosts == 1 and (gVars.CurrentCommentsDone < gVars.manifestObj.CommFollowingPosts or  gVars.CurrentExCommentsDone < gVars.ReqExComments):
                                        comm = random.choice(Comments)
                                        try:
                                            log.info('Comment action : ' + row['MediaId'] + ', Sleeping for : ' + str(waitTime))
                                            apiW.CommentOnMedia(api,row['MediaId'],comm)
                                            cf.SendAction(gVars,gVars.SocialProfileId,Actions.Comment,row['Username'],row['Username'] + 'Comment added : ' + comm)
                                            gVars.GlobalTodo.loc[i,'Data'] = 'Comment added : ' + comm
                                        except ClientError as e:
                                            log.info('Comment IG Error MediaId deleted {3!s}  {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response, row['MediaId']))
                                            cf.SendAction(gVars,gVars.SocialProfileId,Actions.BotError,row['Username'],'Deleted MediaId while Commenting : ' + str(row['MediaId']))
                                            gVars.GlobalTodo.loc[i,'Data'] = 'Deleted MediaId while Commenting'

                                        gVars.GlobalTodo.loc[i,'Status'] = 2
                                        gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                        
                                        
                                        if row['FriendShipStatus'] == 'MustComment':
                                            gVars.CurrentExCommentsDone = gVars.CurrentExCommentsDone + 1
                                        else:
                                            gVars.CurrentCommentsDone = gVars.CurrentCommentsDone + 1
                                        
                                        time.sleep(waitTime) 
                                                
                                    if row['Action'] == 'UnFollow' and gVars.manifestObj.UnFollFollowersAfterMinDays == 1:
                                        log.info('UnFollow action : ' + row['Username'] +  ', Sleeping for : ' + str(waitTime))
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
                                        
                                        gVars.CurrentUnFollowDone = gVars.CurrentUnFollowDone + 1
                                        time.sleep(waitTime) 

                                    if row['Action'] == 'StoryView' and gVars.manifestObj.AfterFollViewUserStory == 1 and gVars.CurrentStoryViewDone < gVars.manifestObj.VwStoriesFollowing :
                                        log.info('StoryView action : ' + row['Username'] +  ', Sleeping for : ' + str(waitTime))
                                        apiW.ViewStory(api,row['MediaId'],row['FriendShipStatus'])
                                        cf.SendAction(gVars,gVars.SocialProfileId,Actions.StoryView,row['Username'],'story pages : ' + str(len(row['MediaId'])))
                                        
                                        gVars.GlobalTodo.loc[i,'Status'] = 2
                                        gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                        gVars.GlobalTodo.loc[i,'Data'] = 'story pages : ' + str(len(row['MediaId']))
                                        
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
                            
                                    gVars.ActionPerformed += 1 

                                    if (platform.system() == "Darwin"):
                                        Path(os.path.join(os.getenv("HOME"), ".SocialPlannerPro")).mkdir(parents=True, exist_ok=True)
                                        file_to_open = os.path.join(os.getenv("HOME"), ".SocialPlannerPro", "glob.vars")
                                    else:
                                        file_to_open = Path("userdata") / "glob.vars"

                                    with open(file_to_open, 'wb') as gVarFile:
                                        pickle.dump(gVars, gVarFile)

                            if self.botStop.is_set() != True :  #do not perform cleanup and send email if stop signal is sent.. 
                                #Run Ending
                                gVars.RunEndTime = datetime.datetime.now()
                                gVars.LastSuccessfulSequenceRunDate = datetime.datetime.today() 
                                log.info('Sequence has completed at : ' + str(gVars.RunEndTime) )
                                #writing log to file

                                if (platform.system() == "Darwin"):
                                    Path(os.path.join(os.getenv("HOME"), ".SocialPlannerPro")).mkdir(parents=True, exist_ok=True)
                                    file_to_open = os.path.join(os.getenv("HOME"), ".SocialPlannerPro", "GlobalTodo.html")
                                else:
                                    file_to_open = Path("userdata") / "GlobalTodo.html"
                                
                                with open(file_to_open, "w", encoding="utf-8") as file:
                                    file.writelines('<meta charset="UTF-8">\n')
                                    file.write(gVars.GlobalTodo.to_html())

                                log.info('Action List saved for Email' )
                                
                                cf.SendEmail('muzamilw@gmail.com',file_to_open,gVars.SGusername,'')
                                log.info('Email sent' )
                                

                                app.ResetGlobalVars()
                                log.info('Cleanup performed exiting main thread')

                            # log.info("Action sequence running")

                            # i = True
                            # while i  < 100 and self.botStop == False:
                            #     log.info('Looopi ' + str(i))
                            #     waitTime = randrange(1,2)
                            #     time.sleep(waitTime) 
                            #     i = i + 1
                            #     if (self.ui.botStop == True):
                            #         print('exiting thread')
                            #         return

                        except (ClientLoginError, ClientLoginRequiredError, ClientCookieExpiredError) as e:
                            #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                            log.info("Instagram Login occurred, Please sign off and relogin to continue")
                            log.info(str(traceback.format_exc()))
                            cf.SendError('muzamilw@gmail.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                            self.ShowErrorMessage("Instagram Login occurred,Stopping Sequence. Please sign off and relogin to continue")
                            IsApiClientError = True
                            return

                        except (ClientSentryBlockError, ClientChallengeRequiredError, ClientCheckpointRequiredError) as e:
                            #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                            log.info("Instagram Error occurred, Please open Instagram in the browser and manually clear any location Challenges or checkpoints")
                            log.info(str(traceback.format_exc()))
                            cf.SendError('muzamilw@gmail.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                            self.ShowErrorMessage("Critical Instagram Error occurred, Stopping Sequence. Please open Instagram in the browser and manually clear any location Challenges or checkpoints")
                            IsApiClientError = True
                            return

                        except (ClientError,ClientConnectionError) as e:
                            #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                            log.info("Api Client or Network Error occurred, Restarting")
                            log.info(str(traceback.format_exc()))
                            cf.SendError('muzamilw@gmail.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                           
                            raise e

                        except Exception as e:# ClientError:
                            #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                            log.info("Exception occurred in main sequence action loop, restarting")
                            log.info(traceback.format_exc())
                            cf.SendError('muzamilw@gmail.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                            raise e

                        #gVars.GlobalTodo.to_csv('GlobData.csv')
                        log.info('Sequence Completed Successfully')
                        return

                        #return gVars
                    else:
                        #perform login
                        log.info('IG user is not logged in.')
                else:
                    log.info('Error logging onto SG Server')
            except:
                # restart main loop
                # self.logControl.text = ""
                log.info('An Exception happened, Restarting Session in ' + str(RetryTimeSeconds * RetryCount) +  ' seconds')
                log.info(str(traceback.format_exc()))
                log.info('###################################################################')
                log.info('Retry #'+str(RetryCount)+' \n')
                
                time.sleep(RetryTimeSeconds * RetryCount) 
                pass
            finally:
                # restart main loop
                pass

        gVars.SequenceRunning = False
        log.info('Ending')
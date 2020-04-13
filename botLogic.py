
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
from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)

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

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

def RunBot(gVars,api,Client):
        
    gVars.RunStartTime = datetime.datetime.now()
    
    if gVars.loginResult is not None:
        gVars.SocialProfileId = gVars.loginResult["SocialProfileId"]
        gVars.manifest = cf.GetManifest(gVars.loginResult["SocialProfileId"],gVars)

        if api.authenticated_user_id is not None:

            try:
                if (gVars.loginResult["InitialStatsReceived"] != True):

                    user_info = api.user_info(api.authenticated_user_id)

                    cf.UpdateInitialStatsToServer(gVars.SocialProfileId,user_info['user']['follower_count'],user_info['user']['following_count'],user_info['user']['media_count'],gVars)

                    print('int followers' + str(user_info['user']['follower_count']))
                    print('Init Following' +str(user_info['user']['following_count']))
                    print('InitPosts' + str(user_info['user']['media_count']))
                else:
                    print('initial stats already sent')

                    
                #sending daily stats
                if gVars.DailyStatsSent == False:
                    # InitFollowers = len(apiW.getTotalFollowers(api,api.username_id))
                    # InitFollowing = len(apiW.getTotalFollowings(api,api.username_id))
                    # InitPosts = len(apiW.getTotalUserFeed(api,api.username_id))
                    user_info = api.user_info(api.authenticated_user_id)
                    print('Sending Daily Stats')
                    cf.SendAction(gVars,gVars.SocialProfileId,Actions.FollowersCountUpdate,'self','{\"InitialFollowings\":\"'+str(user_info['user']['following_count'])+'\",\"InitialFollowers\":\"'+ str(user_info['user']['follower_count']) +'\",\"InitialPosts\":\"'+str(user_info['user']['media_count'])+'\",\"SocialProfileId\":'+str(gVars.SocialProfileId)+'}')
                    gVars.DailyStatsSent = True
                else:
                    print('Daily Stats already sent')
                #"Message":"{\"InitialFollowings\":\"400\",\"InitialFollowers\":\"1200\",\"InitialPosts\":\"6\",\"SocialProfileId\":28}"
                    
                

                if gVars.manifestJson is None:
                    print('getting manifest')
                    gVars.manifestJson = cf.GetManifest(gVars.SocialProfileId,gVars)

                if gVars.manifestObj is None:
                    print('loading manifest')
                    gVars.manifestObj = cf.LoadManifest(gVars.manifestJson)
                

                if gVars.Todo is None:
                    gVars.Todo = cf.SetupGlobalTodo([0.2, 0.3, 0.2, 0.2, 0.1], gVars.manifestObj.totalActions)
                    print('Creating Empty Global todo')
                

                if gVars.hashtagActions is None:
                    print('Getting Feeds of Hashtags and creating action list')
                    hashstart = datetime.datetime.now()
                    gVars.hashtagActions = cf.LoadHashtagsTodo(api,gVars.manifestObj,[0.33, 0.33, 0.33],Client)
                    LoadtimeHashtagsTodo = (datetime.datetime.now()-hashstart).total_seconds()
                    print('Hashtag Feed Done in seconds : ' + str(LoadtimeHashtagsTodo))
                
                
                    
                if gVars.locationActions is None:
                    print('Getting Feeds of Location and creating action list')
                    locationtart = datetime.datetime.now()
                    gVars.locationActions = cf.LoadLocationsTodo(api,gVars.manifestObj,[0.33, 0.33, 0.33],gVars.hashtagActions.groupby(['Action'])['Seq'].count(),Client)
                    LoadtimeLocTodo = (datetime.datetime.now()-locationtart).total_seconds()
                    print('Location Feed Done in seconds : ' + str(LoadtimeLocTodo))

                
                    
                if gVars.DCActions is None:
                    print('Getting Feeds of Competitors and creating action list')
                    DCstart = datetime.datetime.now()
                    gVars.DCActions = cf.LoadCompetitorTodo(api,gVars.manifestObj,[0.33, 0.33, 0.33],gVars.locationActions.groupby(['Action'])['Seq'].count(),Client)
                    LoadtimeDCTodo = (datetime.datetime.now()-DCstart).total_seconds()
                    print('Competitors Feed Done in seconds : ' + str(LoadtimeDCTodo))

                if gVars.SuggestFollowers is None:
                    print('Getting Feeds of Suggested Users and creating action list')
                    Suggestedstart = datetime.datetime.now()
                    gVars.SuggestFollowers = cf.LoadSuggestedUsersForFollow(api,gVars.manifestObj,[0.33, 0.33, 0.33],gVars.DCActions.groupby(['Action'])['Seq'].count(),Client)
                    LoadtimeSuggestedTodo = (datetime.datetime.now()-Suggestedstart).total_seconds()
                    print('Suggested Users Feed Done in seconds : ' + str(LoadtimeSuggestedTodo))

                    
                if gVars.UnFollowActions is None:
                    print('Getting Feeds of UnFollow and creating action list')
                    UnFollstart = datetime.datetime.now()
                    gVars.UnFollowActions = cf.LoadUnFollowTodo(api,gVars.manifestObj,[1])
                    LoadtimeUnFollTodo = (datetime.datetime.now()-UnFollstart).total_seconds()
                    print('UnFollow Feed Done in seconds : ' + str(LoadtimeUnFollTodo))

                if gVars.StoryViewActions is None:
                    print('Getting Feeds of StoryViews and creating action list')
                    Storystart = datetime.datetime.now()
                    gVars.StoryViewActions = cf.LoadStoryTodo(api,gVars.manifestObj,[1])
                    LoadtimeStoryTodo = (datetime.datetime.now()-Storystart).total_seconds()
                    print('StoryViews Feed Done in seconds : ' + str(LoadtimeStoryTodo))

                #media_seen(reels)

                frames = [gVars.hashtagActions, gVars.locationActions, gVars.DCActions, gVars.UnFollowActions,gVars.SuggestFollowers,gVars.StoryViewActions]
                actions = pd.concat(frames)

                if gVars.GlobalTodo is None:
                    gVars.GlobalTodo = gVars.Todo.merge(actions,how='left', left_on=['Seq','Action'], right_on=['Seq','Action'])
                    gVars.GlobalTodo.to_csv('GlobData.csv')
                    print('GlobalTodo merged')
                #GlobalTodo[GlobalTodo['Action'] == 'Like']

                
                
                LoadtimeTodo = (datetime.datetime.now()-gVars.RunStartTime).total_seconds()
                print("Total Seconds to Build Action Todo " + str(LoadtimeTodo))
                # #dump(gVars.manifestObj)
            except Exception as e: ## try catch block for the 
                print('Unexpected Exception in initial feed loads : {0!s}'.format(e))
            
            

            # #iterList = (GlobalTodo[GlobalTodo['Status'] == '1']).iterrows()
            # #print(iterList) 
            # #for i, row in islice(GlobalTodo.iterrows(),0,10):
            # #    if row['Status'] == 1:
            # #        print(row)
            
            
            
            Comments = ['😀','👍','💓','🤩','🥰']
            curRow = None

            try:
                for i, row in islice(gVars.GlobalTodo.iterrows(),0,10000):
                    if row['Status'] == 1 and not pd.isnull(str(row['MediaId'])):
                        
                        waitTime = randrange(20,30)
                        
                        
                        if row['Action'] == 'Like':
                            try:
                                print('like action : ' + row['MediaId'])
                                apiW.LikeMedia(api,row['MediaId'])
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.Like,row['Username'],row['MediaId'])
                               
                            except ClientError as e:
                                print('Like IG Error MediaId deleted {3!s}  {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response, row['MediaId']))
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.BotError,row['Username'],'Deleted MediaId while liking : ' + str(row['MediaId']))
                                gVars.GlobalTodo.loc[i,'Data'] = 'Deleted MediaId while liking'

                            gVars.GlobalTodo.loc[i,'Status'] = 2
                            gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                            print('sleeping for : ' + str(waitTime))
                            time.sleep(waitTime) 
                            

                        if row['Action'] == 'Follow':
                            apiW.FollowUser(api,row['UserId'])
                            cf.SendAction(gVars,gVars.SocialProfileId,Actions.Follow,row['Username'],'')
                            print('Follow action : ' + row['Username'])
                            gVars.GlobalTodo.loc[i,'Status'] = 2
                            gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                            print('sleeping for : ' + str(waitTime))
                            time.sleep(waitTime) 

                        if row['Action'] == 'Comment':
                            comm = random.choice(Comments)
                            try:
                                print('Comment action : ' + row['MediaId'])
                                apiW.CommentOnMedia(api,row['MediaId'],comm)
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.Comment,row['Username'],row['Username'] + 'Comment added : ' + comm)
                                gVars.GlobalTodo.loc[i,'Data'] = 'Comment added : ' + comm
                            except ClientError as e:
                                print('Comment IG Error MediaId deleted {3!s}  {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response, row['MediaId']))
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.BotError,row['Username'],'Deleted MediaId while Commenting : ' + str(row['MediaId']))
                                gVars.GlobalTodo.loc[i,'Data'] = 'Deleted MediaId while Commenting'

                            gVars.GlobalTodo.loc[i,'Status'] = 2
                            gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                            
                            print('sleeping for : ' + str(waitTime))
                            time.sleep(waitTime) 
                                    
                        if row['Action'] == 'UnFollow':
                            if row['Tag'] == 'delete_not_found':  ##ignore the IG action and send it anyways
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.UnFollow,row['Username'],'delete_not_found')
                            else:
                                apiW.UnFollowUser(api,row['UserId'])
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.UnFollow,row['Username'],'')
                            print('UnFollow action : ' + row['Username'])
                            gVars.GlobalTodo.loc[i,'Status'] = 2
                            gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                            print('sleeping for : ' + str(waitTime))
                            time.sleep(waitTime) 

                        if row['Action'] == 'StoryView':
                            print('StoryView action : ' + row['Username'])
                            apiW.ViewStory(api,row['MediaId'],row['FriendShipStatus'])
                            cf.SendAction(gVars,gVars.SocialProfileId,Actions.StoryView,row['Username'],'story pages : ' + str(len(row['MediaId'])))
                            
                            gVars.GlobalTodo.loc[i,'Status'] = 2
                            gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                            gVars.GlobalTodo.loc[i,'Data'] = 'story pages : ' + str(len(row['MediaId']))
                            print('sleeping for : ' + str(waitTime))
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
                print("exception occurred in main bot action loop")
                print(sys.exc_info())

            gVars.GlobalTodo.to_csv('GlobData.csv')

            return gVars
        else:
            #perform login
            print('IG user is not logged in.')
    else:
        print('Error logging onto SG Server')

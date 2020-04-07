
import customFunctions as cf
import apiWrappers as apiW
import datetime
from enum import Enum
import datetime, pytz
import pandas as pd
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
import sys

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

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

def RunBot(gVars,api):
        
    gVars.RunStartTime = datetime.datetime.now()
    
    if gVars.loginResult is not None:
        gVars.SocialProfileId = gVars.loginResult["SocialProfileId"]
        gVars.manifest = cf.GetManifest(gVars.loginResult["SocialProfileId"],gVars)

        if api.username_id is not None:
            if (gVars.loginResult["InitialStatsReceived"] != True):
                InitFollowers = len(apiW.getTotalFollowers(api,api.username_id))
                InitFollowing = len(apiW.getTotalFollowings(api,api.username_id))
                InitPosts = len(apiW.getTotalUserFeed(api,api.username_id))

                cf.UpdateInitialStatsToServer(gVars.SocialProfileId,InitFollowers,InitFollowing,InitPosts,gVars)

                print('int followers' + str(InitFollowers))
                print('InitFollowing' +str(InitFollowers))
                print('InitPosts' + str(InitPosts))
            else:
                print('initial stats already sent')

                
            #sending daily stats
            if gVars.DailyStatsSent == False:
                InitFollowers = len(apiW.getTotalFollowers(api,api.username_id))
                InitFollowing = len(apiW.getTotalFollowings(api,api.username_id))
                InitPosts = len(apiW.getTotalUserFeed(api,api.username_id))
                print('Sending Daily Stats')
                cf.SendAction(gVars,gVars.SocialProfileId,Actions.FollowersCountUpdate,'self','{\"InitialFollowings\":\"'+str(InitFollowing)+'\",\"InitialFollowers\":\"'+ str(InitFollowers) +'\",\"InitialPosts\":\"'+str(InitPosts)+'\",\"SocialProfileId\":'+str(gVars.SocialProfileId)+'}')
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
                gVars.hashtagActions = cf.LoadHashtagsTodo(api,gVars.manifestObj,[0.33, 0.33, 0.33])
                print('Hashtag Feed Done')
            
            
                
            if gVars.locationActions is None:
                print('Getting Feeds of Location and creating action list')
                gVars.locationActions = cf.LoadLocationsTodo(api,gVars.manifestObj,[0.33, 0.33, 0.33],gVars.hashtagActions.groupby(['Action'])['Seq'].count())
                print('Location Feed Done')

            
                
            if gVars.DCActions is None:
                print('Getting Feeds of Competitors and creating action list')
                gVars.DCActions = cf.LoadCompetitorTodo(api,gVars.manifestObj,[0.33, 0.33, 0.33],gVars.locationActions.groupby(['Action'])['Seq'].count())
                print('Competitors Feed Done')

              
                
            if gVars.UnFollowActions is None:
                print('Getting Feeds of UnFollow and creating action list')
                gVars.UnFollowActions = cf.LoadUnFollowTodo(api,gVars.manifestObj,[1])
                print('UnFollow Feed Done')


            frames = [gVars.hashtagActions, gVars.locationActions, gVars.DCActions,gVars.UnFollowActions]
            actions = pd.concat(frames)

            if gVars.GlobalTodo is not None:
                gVars.GlobalTodo = gVars.Todo.merge(actions,how='left', left_on=['Seq','Action'], right_on=['Seq','Action'])
                print('GlobalTodo merged')
            #GlobalTodo[GlobalTodo['Action'] == 'Like']
            
            LoadtimeTodo = (datetime.datetime.now()-gVars.RunStartTime).total_seconds()

            print("Total Seconds to Build Action Todo " + str(LoadtimeTodo))
            #dump(gVars.manifestObj)
            
            
           

            # #iterList = (GlobalTodo[GlobalTodo['Status'] == '1']).iterrows()
            # #print(iterList) 
            # #for i, row in islice(GlobalTodo.iterrows(),0,10):
            # #    if row['Status'] == 1:
            # #        print(row)
            
            
            
            Comments = ['😀','👍','💓','🤩','🥰']
            curRow = None

            try:
                # for i, row in islice(gVars.GlobalTodo.iterrows(),0,10000):
                #     if row['Status'] == 1 and not pd.isnull(row['MediaId']):
                        
                #         waitTime = randrange(20,30)
                        
                        
                #         if row['Action'] == 'Like' :
                #             apiW.LikeMedia(api,row['MediaId'])
                #             cf.SendAction(gVars.SocialProfileId,Actions.Like,row['Username'],row['MediaId'])
                #             print('like action : ' + row['MediaId'])
                #             gVars.GlobalTodo.loc[i,'Status'] = 2
                #             gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                #             print('sleeping for : ' + str(waitTime))
                #             time.sleep(waitTime) 

                        # if row['Action'] == 'Follow':
                        #     apiW.FollowUser(api,row['UserId'])
                        #     cf.SendAction(SocialProfileId,Actions.Follow,row['Username'],'')
                        #     print('Follow action : ' + row['Username'])
                        #     gVars.GlobalTodo.loc[i,'Status'] = 2
                        #     gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                        #     print('sleeping for : ' + str(waitTime))
                        #     time.sleep(waitTime) 

                #         if row['Action'] == 'Comment':
                #             comm = random.choice(Comments)
                #             apiW.CommentOnMedia(api,row['MediaId'],comm)
                #             cf.SendAction(SocialProfileId,Actions.Comment,row['Username'],row['Username'] + 'Comment added : ' + comm)
                #             print('Comment action : ' + row['MediaId'])
                #             gVars.GlobalTodo.loc[i,'Status'] = 2
                #             gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                #             gVars.GlobalTodo.loc[i,'Data'] = 'Comment added : ' + comm
                #             print('sleeping for : ' + str(waitTime))
                #             time.sleep(waitTime) 
                            
                # if row['Action'] == 'UnFollow':
                #     if row['Tag'] != 'delete_not_found':  ##ignore the IG action and send it anyways
                #         apiW.UnFollowUser(api,row['UserId'])
                # cf.SendAction(SocialProfileId,Actions.UnFollow,row['Username'],'delete_not_found')
                # print('UnFollow action : ' + row['Username'])
                # gVars.GlobalTodo.loc[i,'Status'] = 2
                # gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                # print('sleeping for : ' + str(waitTime))
                # time.sleep(waitTime) 

                #Run Ending
                gVars.RunEndTime = datetime.datetime.now()
                
                #writing log to file
                
                with open("dataframe_GlobalTodo.html", "w", encoding="utf-8") as file:
                    file.writelines('<meta charset="UTF-8">\n')
                    file.write(gVars.GlobalTodo.to_html())
                
                gVars.GlobalTodo.to_csv('GlobData.csv')
                
                #cf.SendEmail('muzamilw@gmail.com','muzamilw@gmail.com','Sh@rp2020','dataframe_GlobalTodo.html','','')
                
            except:# ClientError:
                #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                print("exception occurred")
                print(sys.exc_info())

            return gVars
        else:
            #perform login
            print('IG user is not logged in.')
    else:
        print('Error logging onto SG Server')

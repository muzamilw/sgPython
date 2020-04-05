
import customFunctions as cf
import apiWrappers as apiW

from enum import Enum
import datetime, pytz

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

def RunBot(gVars,api):
        
    RunStartTime = datetime.datetime.now()
    
    if gVars.loginResult is None:
        print('performing app login')
        gVars.loginResult = cf.AppLogin('nevillekmiec','103381','123',gVars)

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

            return gVars

            # if Todo is None:
            #     Todo = SetupGlobalTodo([0.2, 0.3, 0.2, 0.2, 0.1], gVars.manifestObj.totalActions)
            #     print('Creating Empty Global todo')

            # if hashtagActions is None:
            #     print('Getting Feeds of Hashtags and creating action list')
            #     hashtagActions = LoadHashtagsTodo(api,manifestObj,[0.33, 0.33, 0.33])
            #     print('Hashtag Feed Done')
                
                
            # if locationActions is None:
            #     print('Getting Feeds of Location and creating action list')
            #     locationActions = LoadLocationsTodo(api,manifestObj,[0.33, 0.33, 0.33],hashtagActions.groupby(['Action'])['Seq'].count())
            #     print('Location Feed Done')
                
            # if DCActions is None:
            #     print('Getting Feeds of Competitors and creating action list')
            #     DCActions = LoadCompetitorTodo(api,manifestObj,[0.33, 0.33, 0.33],locationActions.groupby(['Action'])['Seq'].count())
            #     print('Competitors Feed Done')
                
            # if UnFollowActions is None:
            #     print('Getting Feeds of UnFollow and creating action list')
            #     UnFollowActions = LoadUnFollowTodo(api,manifestObj,[1])
            #     print('UnFollow Feed Done')
            
            
            # frames = [hashtagActions, locationActions, DCActions,UnFollowActions]
            # actions = pd.concat(frames)

            # if GlobalTodo is None:
            #     GlobalTodo = Todo.merge(actions,how='left', left_on=['Seq','Action'], right_on=['Seq','Action'])
            #     print('GlobalTodo merged')
            # #GlobalTodo[GlobalTodo['Action'] == 'Like']
            
            # print(manifestObj.totalActions)
           

            # #iterList = (GlobalTodo[GlobalTodo['Status'] == '1']).iterrows()
            # #print(iterList) 
            # #for i, row in islice(GlobalTodo.iterrows(),0,10):
            # #    if row['Status'] == 1:
            # #        print(row)
            
            
            
            # Comments = ['😀','👍','💓','🤩','🥰']

            # try:
            #     for i, row in islice(GlobalTodo.iterrows(),0,1000):
            #         if row['Status'] == 1 and not pd.isnull(row['MediaId']):
                        
            #             waitTime = randrange(20,30)
                        
                        
            #             if row['Action'] == 'Like' :
            #                 LikeMedia(api,row['MediaId'])
            #                 SendAction(SocialProfileId,Actions.Like,row['Username'],row['MediaId'])
            #                 print('like action : ' + row['MediaId'])
            #                 GlobalTodo.loc[i,'Status'] = 2
            #                 GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
            #                 print('sleeping for : ' + str(waitTime))
            #                 time.sleep(waitTime) 

            #             if row['Action'] == 'Follow':
            #                 FollowUser(api,row['UserId'])
            #                 SendAction(SocialProfileId,Actions.Follow,row['Username'],'')
            #                 print('Follow action : ' + row['Username'])
            #                 GlobalTodo.loc[i,'Status'] = 2
            #                 GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
            #                 print('sleeping for : ' + str(waitTime))
            #                 time.sleep(waitTime) 

            #             if row['Action'] == 'Comment':
            #                 comm = random.choice(Comments)
            #                 CommentOnMedia(api,row['MediaId'],comm)
            #                 SendAction(SocialProfileId,Actions.Comment,row['Username'],row['Username'] + 'Comment added : ' + comm)
            #                 print('Comment action : ' + row['MediaId'])
            #                 GlobalTodo.loc[i,'Status'] = 2
            #                 GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
            #                 GlobalTodo.loc[i,'Data'] = 'Comment added : ' + comm
            #                 print('sleeping for : ' + str(waitTime))
            #                 time.sleep(waitTime) 
                            
            #             if row['Action'] == 'UnFollow':
            #                 UnFollowUser(api,row['UserId'])
            #                 SendAction(SocialProfileId,Actions.UnFollow,row['Username'],'')
            #                 print('UnFollow action : ' + row['Username'])
            #                 GlobalTodo.loc[i,'Status'] = 2
            #                 GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
            #                 print('sleeping for : ' + str(waitTime))
            #                 time.sleep(waitTime) 

            #     #Run Ending
            #     RunEndTime = datetime.datetime.now()
                
            #     #writing log to file
                
            #     with open("dataframe_GlobalTodo.html", "w", encoding="utf-8") as file:
            #         file.writelines('<meta charset="UTF-8">\n')
            #         file.write(GlobalTodo.to_html())
                
            #     SendEmail('muzamilw@gmail.com','muzamilw@gmail.com','Sh@rp2020','dataframe_GlobalTodo.html','','')
                
            # except:# ClientError:
            #     SendAction(SocialProfileId,Actions.ActionBlock,row['Username'],row)
            #     print(sys.exc_info())


        else:
            #perform login
            print('IG user is not logged in.')
    else:
        print('Error logging onto SG Server')

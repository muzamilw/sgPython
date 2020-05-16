import datetime, pytz
import dateutil.tz
import json
import requests 
from random import choices
from random import randrange
import pandas as pd
from itertools import islice
import datetime
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import time
import calendar
import sys
from random import randrange
import math
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)

import apiWrappers as apiW

def SendEmail(you,me,pwd,filename,SocialProfileName, Header):
    msg= ''
    
    with open(filename,mode="r", encoding="utf-8") as fp:
    # Create a text/plain message
        #msg = EmailMessage()
        msg = fp.read()

    message = MIMEMultipart()
    message = MIMEText(msg, 'html')
    sender_address = me
    sender_pass = pwd
    receiver_address = you
    #Setup the MIME
    
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Bot Run Report'   #The subject line
    #The body and the attachments for the mail
    #message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    #text = message.as_string()
    
    session.sendmail(sender_address, receiver_address, message.as_string().encode("utf8"))
    session.quit()
    print('Mail Sent')

def AppLogin(socialUsername,pin,IMEI,gVars):
    API_Login = gVars.API_BaseURL + "/Mobile/Login"
    
    localtz = dateutil.tz.tzlocal()
    localoffset = localtz.utcoffset(datetime.datetime.now(localtz))
    
    data = {'Email':socialUsername,    #1101
            'Pin':pin,
            'IMEI':IMEI,
            'ForceSwitchDevice':'true',
            'AppVersion':'py 1.0',
            'AppTimeZoneOffSet':localoffset.total_seconds() / 3600
           } 
    r = json.loads(requests.post(url = API_Login, data = data).text) 
    if r["MobileLoginJsonRootObject"]["StatusCode"] == 1:
        return (True, r["MobileLoginJsonRootObject"])
    else:
        return (False, r["MobileLoginJsonRootObject"]["StatusMessage"])

def SendAction(gVars,SocialProfileId, Action, TargetSocialUserName,Message):
    
    API_Login = gVars.API_BaseURL + "/Mobile/AppActionBulk"
    data = [{'SocialProfileId':SocialProfileId,    #1101
            'ActionId':Action.value,
            'TargetSocialUserName':TargetSocialUserName,
            'Message':Message
           }]
    r = json.loads(requests.post(url = API_Login, json=data).text) 
    if r is not None:
        return True
    else:
        return False
    
def UpdateInitialStatsToServer(SocialProfileId, InitFollowers, InitFollowing,InitPosts,gVars):
    API_Login = gVars.API_BaseURL + "/Mobile/InitialStats"
    data = {'SocialProfileId':SocialProfileId,    #1101
            'InitialFollowings':InitFollowing,
            'InitialFollowers':InitFollowers,
            'InitialPosts':InitPosts
           } 
    r = json.loads(requests.post(url = API_Login, data = data).text) 
    if r is not None:
        return True
    else:
        return False


def GetManifest(SocialProfileId,gVars):
    API_Manifest = gVars.API_BaseURL + "/Mobile/GetManifest"
    data = {'SocialProfileId':SocialProfileId,    #1101
            'SocialPassword':'1'} 

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    r = session.post(url = API_Manifest, data = data)
    #r = requests.post(url = API_Manifest, data = data) 
    return json.loads(r.text)

class Manifest:
    pass
    

def LoadManifest(manifest):
    hashtags = []
    locations = []
    DirectCompetitors = []
    
    manifestObj = Manifest()

    manifestObj.FollowOn = manifest["MobileJsonRootObject"]["TargetInformation"]["FollowOn"]
    manifestObj.AfterFollLikeuserPosts = manifest["MobileJsonRootObject"]["TargetInformation"]["AfterFollLikeuserPosts"]
    manifestObj.AfterFollCommentUserPosts = manifest["MobileJsonRootObject"]["TargetInformation"]["AfterFollCommentUserPosts"]
    manifestObj.AfterFollViewUserStory = manifest["MobileJsonRootObject"]["TargetInformation"]["AfterFollViewUserStory"]
    manifestObj.AfterFollCommentUserStory = manifest["MobileJsonRootObject"]["TargetInformation"]["AfterFollCommentUserStory"]
    manifestObj.UnFollFollowersAfterMinDays = manifest["MobileJsonRootObject"]["TargetInformation"]["UnFollFollowersAfterMinDays"]

    manifestObj.FollUserProfileImage = manifest["MobileJsonRootObject"]["TargetInformation"]["FollUserProfileImage"]

    manifestObj.FollDoNotFollowUsernamewithdigits = manifest["MobileJsonRootObject"]["TargetInformation"]["FollDoNotFollowUsernamewithdigits"]
    manifestObj.FollDoNotFollowUsernamewithdigitsVal = manifest["MobileJsonRootObject"]["TargetInformation"]["FollDoNotFollowUsernamewithdigitsVal"]

    if manifest["MobileJsonRootObject"]["TargetInformation"]["FollUserLangsList"] is not None:
        manifestObj.FollUserLangsList = manifest["MobileJsonRootObject"]["TargetInformation"]["FollUserLangsList"].strip().split(",")

    manifestObj.GenderEngagmentPref = manifest["MobileJsonRootObject"]["TargetInformation"]["GenderEngagmentPref"]
    manifestObj.IncludeBusinessAccounts = manifest["MobileJsonRootObject"]["TargetInformation"]["IncludeBusinessAccounts"]

    manifestObj.hashtags = [x.strip() for x in manifest["MobileJsonRootObject"]["TargetInformation"]["HashTagsToEngage"].strip().split(",")]

    if manifest["MobileJsonRootObject"]["TargetInformation"]["LocationsToEngage"] is not None:
        manifestObj.locations = manifest["MobileJsonRootObject"]["TargetInformation"]["LocationsToEngage"].strip().split(",")

    if manifest["MobileJsonRootObject"]["TargetInformation"]["DirectCompetitors"] is not None:
        manifestObj.DirectCompetitors = manifest["MobileJsonRootObject"]["TargetInformation"]["DirectCompetitors"].strip().split(",")

    intervals = json.loads(manifest["MobileJsonRootObject"]["TargetInformation"]["ExecutionIntervals"])
    
    manifestObj.FollowersToUnFollow = manifest["MobileJsonRootObject"]["FollowersToUnFollow"]
    manifestObj.FollowersToComment = manifest["MobileJsonRootObject"]["FollowersToComment"]
    
    manifestObj.FollowList = manifest["MobileJsonRootObject"]["FollowList"]
    manifestObj.LikeList = manifest["MobileJsonRootObject"]["LikeList"]
    
    
    
    manifestObj.FollAccSearchTags = int(intervals[0]["FollAccSearchTags"])
    manifestObj.UnFoll16DaysEngage = int(intervals[0]["UnFoll16DaysEngage"])
    manifestObj.LikeFollowingPosts = int(intervals[0]["LikeFollowingPosts"])
    manifestObj.VwStoriesFollowing = int(intervals[0]["VwStoriesFollowing"])
    manifestObj.CommFollowingPosts = int(intervals[0]["CommFollowingPosts"])

    manifestObj.totalActions = 0

    if manifestObj.FollowOn == 1:
        manifestObj.totalActions += manifestObj.FollAccSearchTags 

    if manifestObj.UnFollFollowersAfterMinDays == 1:
        manifestObj.totalActions += manifestObj.UnFoll16DaysEngage 

    if manifestObj.AfterFollLikeuserPosts == 1:
        manifestObj.totalActions += manifestObj.LikeFollowingPosts

    if manifestObj.AfterFollViewUserStory == 1:  
        manifestObj.totalActions += manifestObj.VwStoriesFollowing 

    if manifestObj.AfterFollCommentUserPosts == 1:
        manifestObj.totalActions += manifestObj.CommFollowingPosts

    
    
    manifestObj.totalActionsHashTag = math.ceil(manifestObj.totalActions / 4)
    manifestObj.totalActionsLocation = math.ceil(manifestObj.totalActions / 4 )
    manifestObj.totalActionsDirectCompetitor = math.ceil(manifestObj.totalActions / 4)
    manifestObj.totalActionsIGUsers = math.ceil(manifestObj.totalActions / 4)

    manifestObj.totalActionsPerHahTag = math.ceil(manifestObj.totalActionsHashTag / len(manifestObj.hashtags))
    manifestObj.totalActionsPerLocation = math.ceil(manifestObj.totalActionsLocation / len(manifestObj.locations))
    
    return manifestObj

    
def LoadHashtagsTodo(api, manifestObj ,Client,log):
    
    tagMediaUsers = []

    for tag in islice(manifestObj.hashtags,0,20):
        lItems = apiW.GetTagFeed(api,tag,manifestObj.totalActionsHashTag,Client,log) #api.getHashtagFeed(tag)

        for photo in  islice(lItems, 0, int(math.ceil(manifestObj.totalActionsPerHahTag))): #islice(filter(lambda x: (x["media_type"] == 1),  items), 0, int(totalActionsPerHahTag)): #items::
            if (photo["has_liked"] == False):
                if photo["user"]["is_private"] == False and photo["user"]["friendship_status"]["following"] == False:                
                    tagMediaUsers.append([tag,str(photo["pk"]),str(photo["user"]["pk"]),str(photo["user"]["username"]),str(photo["user"]["full_name"]), str(photo["user"]["friendship_status"]["following"]) ])

         
    hcols = ["Tag", "MediaId","UserId","Username","FullName","FriendShipStatus"]
   
    usersdf = pd.DataFrame(tagMediaUsers,columns = hcols)
    usersdf.insert(0, 'Seq',0)
    SubActionWeights = []
    weightedObjects = 0
    actions = []
    if manifestObj.FollowOn == 1:
        actions.extend (['Follow'])
        weightedObjects = weightedObjects + 1
    if manifestObj.AfterFollLikeuserPosts == 1 :
        actions.extend (['Like'])
        weightedObjects = weightedObjects + 1
    if manifestObj.AfterFollCommentUserPosts == 1:
        actions.extend (['Comment'])
        weightedObjects = weightedObjects + 1

    if ( weightedObjects == 1):
        SubActionWeights = [1]
    if ( weightedObjects == 2):
        SubActionWeights = [0.5, 0.5]
    if ( weightedObjects == 3):
        SubActionWeights = [0.33, 0.33, 0.33]


    
    Samples = choices(actions, SubActionWeights, k=len(usersdf))

    usersdf['Action'] = Samples

    fc = 1
    lc = 1
    cc = 1

    for i, row in usersdf.iterrows():
        if row["Action"] == 'Follow':
            usersdf.loc[i,'Seq']  = fc
            fc = fc + 1

        if row["Action"] == 'Like':
            usersdf.loc[i,'Seq']  = lc
            lc = lc + 1

        if row["Action"] == 'Comment':
            usersdf.loc[i,'Seq']  = cc
            cc = cc + 1
            
    return usersdf

def LoadLocationsTodo(api, manifestObj,SeqNos,Client,log):
    
    locMediaUsers = []

    for loc in islice(manifestObj.locations,0,20):
        lItems = apiW.GetLocationFeed(api,loc,manifestObj.totalActionsPerLocation,Client,log)

        for photo in  islice(lItems, 0, int(math.ceil(manifestObj.totalActionsPerLocation))): #islice(filter(lambda x: (x["media_type"] == 1),  items), 0, int(totalActionsPerHahTag)): #items::
            if (photo["has_liked"] == False):
                locMediaUsers.append([loc,str(photo["pk"]),str(photo["user"]["pk"]),str(photo["user"]["username"]),str(photo["user"]["full_name"]), str(photo["user"]["friendship_status"]["following"]) ])
  
    hcols = ["Tag", "MediaId","UserId","Username","FullName","FriendShipStatus"]
   
    usersdf = pd.DataFrame(locMediaUsers,columns = hcols)
    usersdf.insert(0, 'Seq',0)
    SubActionWeights = []
    weightedObjects = 0
    actions = []
    if manifestObj.FollowOn == 1:
        actions.extend (['Follow'])
        weightedObjects = weightedObjects + 1
    if manifestObj.AfterFollLikeuserPosts == 1 :
        actions.extend (['Like'])
        weightedObjects = weightedObjects + 1
    if manifestObj.AfterFollCommentUserPosts == 1:
        actions.extend (['Comment'])
        weightedObjects = weightedObjects + 1

    if ( weightedObjects == 1):
        SubActionWeights = [1]
    if ( weightedObjects == 2):
        SubActionWeights = [0.5, 0.5]
    if ( weightedObjects == 3):
        SubActionWeights = [0.33, 0.33, 0.33]
    
    Samples = choices(actions, SubActionWeights, k=len(usersdf))

    usersdf['Action'] = Samples
    fc = 0
    lc = 0
    cc = 0

    # len(SeqNos.keys())
    # SeqNos.keys()[0]

    if len(SeqNos.keys()) > 0:
        for key in SeqNos.keys():
            if key == 'Follow':
                fc = SeqNos['Follow'] + 1
            if key == 'Like':
                lc = SeqNos['Like'] + 1
            if key == 'Comment':
                cc = SeqNos['Comment'] + 1

    for i, row in usersdf.iterrows():
        if row["Action"] == 'Follow':
            usersdf.loc[i,'Seq']  = fc
            fc = fc + 1

        if row["Action"] == 'Like':
            usersdf.loc[i,'Seq']  = lc
            lc = lc + 1

        if row["Action"] == 'Comment':
            usersdf.loc[i,'Seq']  = cc
            cc = cc + 1
            
    return usersdf

def LoadCompetitorTodo(api, manifestObj,SeqNos,Client,log):
    
    locMediaUsers = []

    for compe in islice(manifestObj.DirectCompetitors,0,20): #20
        lItems = apiW.GetUserFollowingFeed(api,compe,manifestObj.totalActionsDirectCompetitor,Client,log) 

        if lItems is not None and len(lItems) > 0:
            for photo in  islice(lItems, 0, int(math.ceil(manifestObj.totalActionsDirectCompetitor))): #islice(filter(lambda x: (x["media_type"] == 1),  items), 0, int(totalActionsPerHahTag)): #items::
                if (photo["has_liked"] == False):
                    locMediaUsers.append([compe,str(photo["pk"]),str(photo["user"]["pk"]),str(photo["user"]["username"]),str(photo["user"]["full_name"]), '' ])
  
    hcols = ["Tag", "MediaId","UserId","Username","FullName","FriendShipStatus"]
   
    usersdf = pd.DataFrame(locMediaUsers,columns = hcols)
    usersdf.insert(0, 'Seq',0)
    SubActionWeights = []
    weightedObjects = 0
    actions = []
    if manifestObj.FollowOn == 1:
        actions.extend (['Follow'])
        weightedObjects = weightedObjects + 1
    if manifestObj.AfterFollLikeuserPosts == 1 :
        actions.extend (['Like'])
        weightedObjects = weightedObjects + 1
    if manifestObj.AfterFollCommentUserPosts == 1:
        actions.extend (['Comment'])
        weightedObjects = weightedObjects + 1

    if ( weightedObjects == 1):
        SubActionWeights = [1]
    if ( weightedObjects == 2):
        SubActionWeights = [0.5, 0.5]
    if ( weightedObjects == 3):
        SubActionWeights = [0.33, 0.33, 0.33]
    
    Samples = choices(actions, SubActionWeights, k=len(usersdf))

    usersdf['Action'] = Samples

    # fc = SeqNos[1]+1
    # lc = SeqNos[2]+1
    # cc = SeqNos[0]+1
    fc = 0
    lc = 0
    cc = 0

    if len(SeqNos.keys()) > 0:
        for key in SeqNos.keys():
            if key == 'Follow':
                fc = SeqNos['Follow'] + 1
            if key == 'Like':
                lc = SeqNos['Like'] + 1
            if key == 'Comment':
                cc = SeqNos['Comment'] + 1

    for i, row in usersdf.iterrows():
        if row["Action"] == 'Follow':
            usersdf.loc[i,'Seq']  = fc
            fc = fc + 1

        if row["Action"] == 'Like':
            usersdf.loc[i,'Seq']  = lc
            lc = lc + 1

        if row["Action"] == 'Comment':
            usersdf.loc[i,'Seq']  = cc
            cc = cc + 1
            
    return usersdf

def LoadSuggestedUsersForFollow(api, manifestObj,SeqNos,Client,log):
    try:
        locMediaUsers = []

        iguserCount = 0

        try:
            if manifestObj.FollowOn == 1:
                suggUsers = api.discover_chaining(api.authenticated_user_id)['users']
                if suggUsers is not None and len(suggUsers) > 0:
                            for user in suggUsers:
                                if user["is_private"] == False and iguserCount <= manifestObj.totalActionsIGUsers :
                                    ufeed = api.user_feed(user['pk'])
                                    if ufeed is not None and len(ufeed['items']) > 0 :
                                        if ufeed['items'][0]['has_liked'] == False:
                                            # follFeed_results.extend([ufeed['items'][0]])
                                            locMediaUsers.append(['suggested ' + user['username'],str(ufeed['items'][0]["pk"]),str(user["pk"]),str(user["username"]),str(user["full_name"]), 'MustFollow' ])
                                    sleepTime = randrange(5,10)
                                    log.info('pulling suggested user feed for ' + user['username'] + ' sleep for ' +  str(sleepTime)  )
                                    time.sleep(sleepTime)
                                    iguserCount = iguserCount + 1
                            
                            
        except:
            print('exception in chaining i.e suggested users')
            raise

        folluser = ''
        try:
            if manifestObj.FollowOn == 1:
                #server follow list
                for foll in manifestObj.FollowList:
                    folluser = foll['FollowedSocialUsername'].strip()
                    try:
                        user = api.username_info(foll['FollowedSocialUsername'].strip())   #check_username(username)
                    except ClientError as e:
                        print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
                        user = None

                    if user is not None:
                        user = user['user']
                        if user["is_private"] == False:
                            ufeed = api.user_feed(user['pk'])
                            if ufeed is not None and len(ufeed['items']) > 0 :
                                if ufeed['items'][0]['has_liked'] == False:
                                    # follFeed_results.extend([ufeed['items'][0]])
                                    locMediaUsers.append(['suggested ' + user['username'],str(ufeed['items'][0]["pk"]),str(user["pk"]),str(user["username"]),str(user["full_name"]), 'MustFollow' ])
                            sleepTime = randrange(5,10)
                            log.info('pulling Follow exchange feed for ' + user['username'] + ' sleep for ' +  str(sleepTime)  )
                            time.sleep(sleepTime)
        except Exception as e:
            print('exception in FollowList for user' + folluser)
            raise

        #server Like list
        try:
            if manifestObj.AfterFollLikeuserPosts == 1:
                for foll in manifestObj.LikeList:
                    try:
                        user = api.username_info(foll['FollowedSocialUsername'].strip())   #check_username(username)
                    except ClientError as e:
                        print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
                        user = None

                    if user is not None:
                        user = user['user']
                        if user["is_private"] == False:
                            ufeed = api.user_feed(user['pk'])
                            if ufeed is not None and len(ufeed['items']) > 0 :
                                if ufeed['items'][0]['has_liked'] == False:
                                    # follFeed_results.extend([ufeed['items'][0]])
                                    locMediaUsers.append(['suggested ' + user['username'],str(ufeed['items'][0]["pk"]),str(user["pk"]),str(user["username"]),str(user["full_name"]), 'MustLike' ])
                            sleepTime = randrange(5,10)
                            log.info('pulling like exchange feed for ' + user['username'] + ' sleep for ' +  str(sleepTime)  )
                            time.sleep(sleepTime)
        except:
            print('exception in LikeList')
            raise

        #server Comment list
        try:
            if manifestObj.AfterFollCommentUserPosts == 1:
                for foll in manifestObj.FollowersToComment:
                    try:
                        user = api.username_info(foll['FollowedSocialUsername'].strip())   #check_username(username)
                    except ClientError as e:
                        print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
                        user = None

                    if user is not None:
                        user = user['user']
                        if user["is_private"] == False:
                            ufeed = api.user_feed(user['pk'])
                            if ufeed is not None and len(ufeed['items']) > 0 :
                                if ufeed['items'][0]['has_liked'] == False:
                                    # follFeed_results.extend([ufeed['items'][0]])
                                    locMediaUsers.append(['suggested ' + user['username'],str(ufeed['items'][0]["pk"]),str(user["pk"]),str(user["username"]),str(user["full_name"]), 'MustComment' ])
                            sleepTime = randrange(5,10)
                            log.info('pulling comment exchange feed for ' + user['username'] + ' sleep for ' +  str(sleepTime)  )
                            time.sleep(sleepTime)
        except:
            print('exception in FollowersToComment')
            raise

        hcols = ["Tag", "MediaId","UserId","Username","FullName","FriendShipStatus"]
    
        usersdf = pd.DataFrame(locMediaUsers,columns = hcols)
        usersdf.insert(0, 'Seq',0)
        SubActionWeights = []
        weightedObjects = 0
        actions = []
        if manifestObj.FollowOn == 1:
            actions.extend (['Follow'])
            weightedObjects = weightedObjects + 1
        if manifestObj.AfterFollLikeuserPosts == 1 :
            actions.extend (['Like'])
            weightedObjects = weightedObjects + 1
        if manifestObj.AfterFollCommentUserPosts == 1:
            actions.extend (['Comment'])
            weightedObjects = weightedObjects + 1

        if ( weightedObjects == 1):
            SubActionWeights = [1]
        if ( weightedObjects == 2):
            SubActionWeights = [0.5, 0.5]
        if ( weightedObjects == 3):
            SubActionWeights = [0.33, 0.33, 0.33]
        
        Samples = choices(actions, SubActionWeights, k=len(usersdf))

        usersdf['Action'] = Samples
        fc = 0
        lc = 0
        cc = 0

        if len(SeqNos.keys()) > 0:
            for key in SeqNos.keys():
                if key == 'Follow':
                    fc = SeqNos['Follow'] + 1
                if key == 'Like':
                    lc = SeqNos['Like'] + 1
                if key == 'Comment':
                    cc = SeqNos['Comment'] + 1

        for i, row in usersdf.iterrows():
            if row["FriendShipStatus"] == 'MustFollow':
                usersdf.loc[i,'Action']  = 'Follow'

            if row["FriendShipStatus"] == 'MustLike':
                usersdf.loc[i,'Action']  = 'Like'

            if row["FriendShipStatus"] == 'MustComment':
                usersdf.loc[i,'Action']  = 'Comment'


        for i, row in usersdf.iterrows():
            if row["Action"] == 'Follow':
                usersdf.loc[i,'Seq']  = fc
                fc = fc + 1

            if row["Action"] == 'Like':
                usersdf.loc[i,'Seq']  = lc
                lc = lc + 1

            if row["Action"] == 'Comment':
                usersdf.loc[i,'Seq']  = cc
                cc = cc + 1
            
            
        
                
        return usersdf
    except Exception as e:
        print('Unexpected Exception LoadSuggestedUsersForFollow: {0!s} '.format(e))
        print(print(sys.exc_info()))
        return None

def LoadUnFollowTodo(api, manifestObj, SubActionWeights,log):
    
    locMediaUsers = []

    for foll in manifestObj.FollowersToUnFollow:
        
        # resUser = api.searchUsername(foll['FollowedSocialUsername'])

        try:
            follUserRes = api.username_info(foll['FollowedSocialUsername'].strip())   #check_username(username)
            sleepTime = randrange(2,7)
            log.info('pulling user details for unfollow for ' + foll['FollowedSocialUsername'].strip() + ' sleep for ' +  str(sleepTime)  )
            time.sleep(sleepTime)
            
        except ClientError as e:
            print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
            follUserRes = None

        if follUserRes is not None:
            locMediaUsers.append([str(follUserRes['user']['username']),'',str(follUserRes['user']['pk']),str(follUserRes['user']['username']),str(follUserRes["user"]["full_name"]), '' ])
        else:
            locMediaUsers.append(['delete_not_found','','',foll['FollowedSocialUsername'],'', '' ])
  
    hcols = ["Tag", "MediaId","UserId","Username","FullName","FriendShipStatus"]
   
    usersdf = pd.DataFrame(locMediaUsers,columns = hcols)
    usersdf.insert(0, 'Seq',0)
    actions = ['UnFollow' ]
    
    Samples = choices(actions, SubActionWeights, k=len(usersdf))

    usersdf['Action'] = Samples

    uf = 1

    for i, row in usersdf.iterrows():
        
            usersdf.loc[i,'Seq']  = uf
            uf = uf + 1
        
            
    return usersdf

def LoadStoryTodo(api, manifestObj, SubActionWeights,log):
    
    reelMediaUsers = []
    storyviewsCount = 0

    reel_tray = api.reels_tray()
    if reel_tray is not None and len(reel_tray['tray']) > 0:
        for reel_user in reel_tray['tray']:
            #reel_tray_users = [(x['user']['pk'],x['user']['username'],x['seen'],x['media_count']) for x in reel_tray()['tray']]
            if reel_user['seen'] == 0  and storyviewsCount <= manifestObj.VwStoriesFollowing :
                user_reel_media = api.user_reel_media(reel_user['user']['pk']) #getting the reel media for the user
                if user_reel_media is not None and len(user_reel_media['items']) > 0:
                    reelMediaUsers.append(['StoryView ' + str(reel_user['user']['username']),[x['id']+'_'+str(reel_user['user']['pk']) for x in user_reel_media['items']],str(reel_user['user']['pk']),str(reel_user['user']['username']),str(reel_user["user"]["full_name"]), [str(x['taken_at'])+'_'+str(calendar.timegm(time.gmtime())) for x in user_reel_media['items']] ])
                    storyviewsCount = storyviewsCount + 1
                sleepTime = randrange(5,10)
                log.info('pulling story feed for view ' + str(reel_user['user']['username']) + ' sleep for ' +  str(sleepTime)  )
                time.sleep(sleepTime)
        
  
    hcols = ["Tag", "MediaId","UserId","Username","FullName","FriendShipStatus"]
   
    usersdf = pd.DataFrame(reelMediaUsers,columns = hcols)
    usersdf.insert(0, 'Seq',0)
    actions = ['StoryView' ]
    
    Samples = choices(actions, SubActionWeights, k=len(usersdf))

    usersdf['Action'] = Samples

    uf = 1

    for i, row in usersdf.iterrows():
        
            usersdf.loc[i,'Seq']  = uf
            uf = uf + 1
        
            
    return usersdf


def SetupGlobalTodo(manifestObj):
    
    # GlobalActionWeights = [0.2, 0.3, 0.2, 0.2, 0.1]
    totalActions = manifestObj.totalActions
    # actions = ['Follow', 'UnFollow', 'Like', 'Comment', 'StoryView' ]
    GlobalActionWeights = []
    actions = []
    if manifestObj.FollowOn == 1:
        actions.extend (['Follow'])
        GlobalActionWeights.extend([0.2])

    if manifestObj.AfterFollLikeuserPosts == 1 :
        actions.extend (['Like'])
        GlobalActionWeights.extend([0.2])

    if manifestObj.AfterFollCommentUserPosts == 1:
        actions.extend (['Comment'])
        GlobalActionWeights.extend([0.2])

    if manifestObj.UnFollFollowersAfterMinDays == 1:
        actions.extend (['UnFollow' ])
        GlobalActionWeights.extend([0.3])

    if manifestObj.AfterFollViewUserStory == 1:  
        actions.extend (['StoryView' ])
        GlobalActionWeights.extend([0.1])

    Samples = choices(actions, GlobalActionWeights, k=totalActions)

    list_dict = []

    for item in Samples:
        list_dict.append({'Action' : item , 'UserId' : '', 'Status' : 1, 'ActionDateTime':'', 'Data':''} )

    column_names = ["Action","Status","ActionDateTime","Data"]
    Todo = pd.DataFrame(list_dict, columns = column_names)

    Todo.insert(0, 'Seq',0)
    
    fc = 1
    sc = 1
    lc = 1
    uc = 1
    cc = 1


    for i, row in Todo.iterrows():
        if row["Action"] == 'Follow':
            Todo.loc[i,'Seq']  = fc
            fc = fc + 1

        if row["Action"] == 'StoryView':
            Todo.loc[i,'Seq']  = sc
            sc = sc + 1

        if row["Action"] == 'Like':
            Todo.loc[i,'Seq']  = lc
            lc = lc + 1

        if row["Action"] == 'UnFollow':
            Todo.loc[i,'Seq']  = uc
            uc = uc + 1

        if row["Action"] == 'Comment':
            Todo.loc[i,'Seq']  = cc
            cc = cc + 1
    return Todo


    
    
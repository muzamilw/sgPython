from itertools import islice
from time import sleep
import datetime
import time
import json
from random import randrange
from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)

#user_info(user_id)




#api Wrappers
def getSelfTimeline(api): #feed_timeline(**kwargs)
    return api.getTimeline()

#username_feed(user_name, **kwargs)

def getFollowers(api, user_id, Client, maxlen):   #user_followers(user_id, rank_token, **kwargs)
    #return api.getTotalFollowers(user_id)
    
    rank_token = Client.generate_uuid()
    has_more = True
    user_results = []
    while has_more and rank_token and len(user_results) < maxlen:
        results = api.user_followers(
            user_id, rank_token)
        user_results.extend(results.get('users', []))
        has_more = results.get('has_more')
        rank_token = results.get('rank_token')
    return user_results
    #print(json.dumps([t['name'] for t in tag_results], indent=2))

def getFollowings(api, user_id,Client, maxlen):   #user_following(user_id, rank_token, **kwargs)
    #return api.getTotalFollowings(user_id)
    rank_token = Client.generate_uuid()
    has_more = True
    user_results = []
    while has_more and rank_token and len(user_results) < maxlen:
        results = api.user_following(
            user_id, rank_token)
        user_results.extend(results.get('users', []))
        has_more = results.get('has_more')
        rank_token = results.get('rank_token')
    return user_results

def getSelfFeedAll(api, Client, maxlen):   #user_following(user_id, rank_token, **kwargs)
    #return api.getTotalFollowings(user_id)
    rank_token = Client.generate_uuid()
    has_more = True
    user_results = []
    next_max_id = True

    while has_more and rank_token and next_max_id and len(user_results) < maxlen:
        if next_max_id is True:
            next_max_id = ''

        results = api.self_feed(
            max_id=next_max_id)
        user_results.extend(results.get('items', []))
        has_more = results.get('more_available')
        next_max_id = results.get('next_max_id')
    return user_results

def getTotalUserFeed(api, user_id):   #user_feed(user_id, **kwargs)
    return api.getTotalUserFeed(user_id)


def GetSelfFeed(api, userId):
    api.getSelfUserFeed()
    return api.LastJson["items"]

def FollowUser(api, userId):  #friendships_create(user_id)
    api.friendships_create(userId)
    #api.follow(userId)
    
def UnFollowUser(api, userId):  #friendships_destroy(user_id, **kwargs)
    api.friendships_destroy(userId)
    #api.unfollow(userId)
    
def CommentOnMedia(api, mediaId,commentText):  #post_comment(media_id, comment_text)
    api.post_comment(mediaId, commentText)
    #api.comment(mediaId, commentText)

def LikeMedia(api, mediaId):  #post_like(media_id, module_name='feed_timeline')
    api.post_like(mediaId, module_name='feed_timeline')
    #return api.like(mediaId) #


def ViewStory(api, itemids, timestamps):  #post_like(media_id, module_name='feed_timeline')
    iIndex = 0
    for i in itemids:
        api.media_seen({str(i): [str(timestamps[iIndex])]})
        #api.media_seen({"2284544142979976553_145316263_145316263": ['1586558904_'+str(calendar.timegm(time.gmtime()))]})
    
def checkUsernameinFollowedList(json_object, name):
    result = [obj for obj in json_object if obj['FollowedSocialUsername']==name]
    if len(result) == 0:
        return True
    else:
        return False

def checkInList(json_object,blacklist, name):
    result = [obj for obj in json_object if name == str(obj)]

    result2 = [obj for obj in blacklist if name == str(obj)]

    if len(result) == 0 and len(result2) == 0:
        return True
    else:
        return False


def checkFriendshipStatus(user):
    if 'friendship_status' in user:
        if user["friendship_status"]["following"] == False:
            return True
        else:
            return False
    else:
        return True

def checkGender(user, genderDetector,manifestObj):
    
    if manifestObj.GenderEngagmentPref == 1: #male
        up = genderDetector.get_gender(user['username'])
        fp = genderDetector.get_gender(user['full_name'])

        if fp.gender is None and up.gender == None:
            return True
        else:

            if fp.gender is None and up.gender == "m":
                return True
            
            if up.gender is None and fp.gender == "m":
                return True

            if up.gender == "m" and fp.gender == "m":
                return True

            return False

    if manifestObj.GenderEngagmentPref == 2: #female
        up = genderDetector.get_gender(user['username'])
        fp = genderDetector.get_gender(user['full_name'])

        if fp.gender is None and up.gender == None:
            return True
        else:

            if fp.gender is None and up.gender == "f":
                return True
            
            if up.gender is None and fp.gender == "f":
                return True

            if up.gender == "f" and fp.gender == "f":
                return True

            return False

    return True ## when no gender pref always load
                

    

    





def GetTagFeed(api, hashTag,maxCountToGet,Client,log,manifestObj,gVars,blacklist,genderDetector):   #feed_tag(tag, rank_token, **kwargs)
    
    rank_token = Client.generate_uuid()
    has_more = True
    tag_results = []
    next_max_id = True
    # results = api.feed_tag(
    #         hashTag, rank_token)
    # tag_results.extend(results.get('ranked_items', []))
    # tag_results.extend(results.get('items', []))

          

    
    while has_more and rank_token and next_max_id and len(tag_results) < maxCountToGet:
        if next_max_id is True:
            next_max_id = ''

        results = api.feed_tag(
            hashTag, rank_token, max_id=next_max_id)

        prev = len(tag_results) 
        #tag_results.extend(results.get('ranked_items', []))
        #tag_results.extend(results.get('items', []))
        tag_results.extend([x for x in results.get('ranked_items', []) if x["user"]["is_private"] == False if checkFriendshipStatus(x["user"]) if checkGender(x["user"],genderDetector,manifestObj) if checkUsernameinFollowedList(manifestObj.AllFollowedAccounts, str(x["user"]["username"])) if checkInList(manifestObj.BlackListUsers,blacklist, str(x["user"]["username"])) ]   )
        tag_results.extend([x for x in results.get('items', []) if x["user"]["is_private"] == False if checkFriendshipStatus(x["user"]) if checkGender(x["user"],genderDetector,manifestObj) if checkUsernameinFollowedList(manifestObj.AllFollowedAccounts, str(x["user"]["username"])) if checkInList(manifestObj.BlackListUsers,blacklist, str(x["user"]["username"])) ] )

        has_more = results.get('more_available')
        next_max_id = results.get('next_max_id')
        sleepTime = randrange(int(manifestObj.HashLoadDelayRange[0]),int(manifestObj.HashLoadDelayRange[1]))
        # if maxCountToGet > len(tag_results):
        #     gVars.ActionLoaded +=  (len(tag_results) - prev)
        # else:
        #     gVars.ActionLoaded +=  maxCountToGet

        log.info('Fetching hashtag feed : ' + hashTag + ' - Wait :  ' +  str(sleepTime) + ' - Count : ' + str(len(tag_results)) + ' of ' + str(maxCountToGet) )
        time.sleep(sleepTime)

    gVars.ActionLoaded +=  maxCountToGet
    return tag_results
        

def GetLocationFeed(api, locationTag,maxCountToGet,Client,log,manifestObj,gVars,blacklist,genderDetector):
    rank_token = Client.generate_uuid()
    has_more = True
    location_results = []
    next_max_id = True

    
    locastionSearchResult =  api.location_fb_search(locationTag, rank_token)

    if len(locastionSearchResult) > 0:

        
        
        while has_more and rank_token and next_max_id and len(location_results) < maxCountToGet:
            if next_max_id is True:
                next_max_id = ''

            results = api.location_section(locastionSearchResult['items'][0]['location']['pk'], rank_token,tab='ranked', max_id=next_max_id)
            prev = len(location_results)
            res = [val['media'] for sublist in [x['layout_content']['medias'] for x in results.get('sections', [])]  for val in sublist] 
            location_results.extend( [x for x in res if x["user"]["is_private"] == False if checkFriendshipStatus(x["user"]) if checkGender(x["user"],genderDetector,manifestObj) if checkUsernameinFollowedList(manifestObj.AllFollowedAccounts, str(x["user"]["username"]) ) if checkInList(manifestObj.BlackListUsers,blacklist, str(x["user"]["username"]))  ])
            
            # if maxCountToGet > len(location_results):
            #     gVars.ActionLoaded +=  (len(location_results) - prev)
            # else:
            #     gVars.ActionLoaded +=  maxCountToGet

            has_more = results.get('more_available')
            next_max_id = results.get('next_max_id')
            
            sleepTime = randrange(int(manifestObj.LocationLoadDelayRange[0]),int(manifestObj.LocationLoadDelayRange[1]))
            log.info('Fetching location : ' + locationTag + ' - Wait :  ' +  str(sleepTime) + ' - Count : ' + str(len(location_results)) + ' of ' + str(maxCountToGet) )
            time.sleep(sleepTime)

        #loading recents if target not met
        next_max_id = True
        has_more = True
        while has_more and rank_token and next_max_id and len(location_results) < maxCountToGet:
            if next_max_id is True:
                next_max_id = ''

            results = api.location_section(locastionSearchResult['items'][0]['location']['pk'], rank_token,tab='ranked', max_id=next_max_id)
            prev = len(location_results)
            res = [val['media'] for sublist in [x['layout_content']['medias'] for x in results.get('sections', [])]  for val in sublist] 
            location_results.extend( [x for x in res if x["user"]["is_private"] == False if checkFriendshipStatus(x["user"]) if checkGender(x["user"],genderDetector,manifestObj) if checkUsernameinFollowedList(manifestObj.AllFollowedAccounts, str(x["user"]["username"]))  if checkInList(manifestObj.BlackListUsers,blacklist, str(x["user"]["username"])) ])
            

            # if maxCountToGet > len(location_results):
            #     gVars.ActionLoaded +=  len(location_results) - prev
            # else:
            #     gVars.ActionLoaded +=  maxCountToGet

            has_more = results.get('more_available')
            next_max_id = results.get('next_max_id')
            sleepTime = randrange(int(manifestObj.LocationLoadDelayRange[0]),int(manifestObj.LocationLoadDelayRange[1]))
            log.info('Fetching location : ' + locationTag + ' - Wait :  ' +  str(sleepTime) + ' - Count : ' + str(len(location_results)) + ' of ' + str(maxCountToGet) )
            time.sleep(sleepTime)

        gVars.ActionLoaded +=  maxCountToGet
        return location_results
        #res = api.getLocationFeed(locastionSearchResult[0]["location"]["pk"])
        #return api.LastJson["items"],api.LastJson["ranked_items"]
    else:
        return None
    
def GetUserFollowingFeed(api, userName,maxCountToGet,Client,log,manifestObj, gVars,blacklist,genderDetector):
    try:
    
        follUserRes = None
        try:
            follUserRes = api.username_info(userName.strip())   #check_username(username)
        except ClientError as e:
            print('General exception for username {3!s}  {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response, userName.strip()))
            return None
        except Exception as e:
            print('Unexpected Exception api.username_info: {0!s} username {1!s}'.format(e,userName.strip()))
            return None

        if follUserRes is not None and follUserRes['user']['is_private'] == False:
            
            rank_token = Client.generate_uuid()
            has_more = True
            follFeed_results = []
            next_max_id = True

            while has_more and rank_token and next_max_id and len(follFeed_results) < maxCountToGet:
                    if next_max_id is True:
                        next_max_id = ''

                    results = api.user_followers(follUserRes['user']['pk'], rank_token, max_id=next_max_id)

                    if results is not None and len(results) > 0:
                        for user in results['users']:
                            if user["is_private"] == False and len(follFeed_results) <= maxCountToGet:
                                ufeed = api.user_feed(user['pk'])
                                if ufeed is not None and len(ufeed['items']) > 0 :
                                    if ufeed['items'][0]['has_liked'] == False and checkGender(x["user"],genderDetector,manifestObj) and checkUsernameinFollowedList(manifestObj.AllFollowedAccounts, str(ufeed['items'][0]['user']["username"])) and  checkInList(manifestObj.BlackListUsers,blacklist, str(ufeed['items'][0]['user']["username"])):
                                        prev = len(follFeed_results) 
                                        follFeed_results.extend([ufeed['items'][0]])
                                        # if maxCountToGet > len(follFeed_results):
                                        #     gVars.ActionLoaded +=  len(follFeed_results) - prev
                                        # else:
                                        #     gVars.ActionLoaded +=  maxCountToGet

                    #tag_results.extend(results.get('ranked_items', []))
                    #tag_results.extend(results.get('items', []))
                    #tag_results.extend([x for x in results.get('ranked_items', []) if x["user"]["is_private"] == False if x["user"]["friendship_status"]["following"] == False])
                    #tag_results.extend([x for x in results.get('items', []) if x["user"]["is_private"] == False if x["user"]["friendship_status"]["following"] == False])

                    has_more = results.get('more_available')
                    next_max_id = results.get('next_max_id')
                    sleepTime = randrange(int(manifestObj.UserFollowLoadDelayRange[0]),int(manifestObj.UserFollowLoadDelayRange[1]))
                    log.info('Fetching user : ' + userName + ' - Wait :  ' +  str(sleepTime) + ' - Count :  ' + str(len(follFeed_results)) + ' of ' + str(maxCountToGet) )
                    time.sleep(sleepTime)


            # api.getUserFollowers(follUserRes['user']['pk'])   #user_followers(user_id, rank_token, **kwargs)

            # if len(api.LastJson["users"]) > 0:
            
            #     userFollowers = api.LastJson["users"]
                
            #     for user in islice(userFollowers, 0, int(maxCountToGet)): 
            #         if (user["is_private"] == False):
            #             time.sleep(3)
            #             feedres = api.getUserFeed(user['pk'])   #user_feed(user_id, **kwargs)
            #             if feedres == True and api.LastJson['items'] is not None:
            #                 if len(api.LastJson['items']) > 0:
            #                     #items.extend([{**api.LastJson['items'][0],**user} ])
            #                     items.extend([api.LastJson['items'][0]])
            
            gVars.ActionLoaded +=  maxCountToGet
            return follFeed_results
                
        else:  # followers list is empty
            return None
    
    except Exception as e:
        print('Unexpected Exception GetUserFollowingFeed: {0!s} username {1!s}'.format(e,userName.strip()))
        return None

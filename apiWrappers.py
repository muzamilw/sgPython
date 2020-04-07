from itertools import islice
from time import sleep
import datetime
import time

#user_info(user_id)

#api Wrappers
def getSelfTimeline(api): #feed_timeline(**kwargs)
    return api.getTimeline()

#username_feed(user_name, **kwargs)

def getTotalFollowers(api, user_id):   #user_followers(user_id, rank_token, **kwargs)
    return api.getTotalFollowers(user_id)

def getTotalFollowings(api, user_id):   #user_following(user_id, rank_token, **kwargs)
    return api.getTotalFollowings(user_id)

def getTotalUserFeed(api, user_id):   #user_feed(user_id, **kwargs)
    return api.getTotalUserFeed(user_id)


def GetSelfFeed(api, userId):
    api.getSelfUserFeed()
    return api.LastJson["items"]

def FollowUser(api, userId):  #friendships_create(user_id)
    api.follow(userId)
    
def UnFollowUser(api, userId):  #friendships_destroy(user_id, **kwargs)
    api.unfollow(userId)
    
def CommentOnMedia(api, mediaId,commentText):  #post_comment(media_id, comment_text)
    api.comment(mediaId, commentText)

def LikeMedia(api, mediaId):  #post_like(media_id, module_name='feed_timeline')
    return api.like(mediaId)   #

def GetTagFeed(api, hashTag,maxCountToGet):   #feed_tag(tag, rank_token, **kwargs)
    
    res = api.getHashtagFeed(hashTag)    #usertag_feed(user_id, **kwargs)


    items = []

    items.extend(api.LastJson.get('ranked_items', []))

    itemCount = len(items)
    next_max_id = True
    while next_max_id:
        # first iteration hack
        if next_max_id is True:
            next_max_id = ''

        _ = api.getHashtagFeed(hashTag,maxid=next_max_id) #api.getUserFollowers(user_id, maxid=next_max_id)
        itemCount = itemCount + len(api.LastJson["items"])
        items.extend(api.LastJson.get('items', []))
        next_max_id = api.LastJson.get('next_max_id', '')

        if itemCount >= maxCountToGet:
            next_max_id = False

        time.sleep(2)

    return items
        

def GetLocationFeed(api, locationTag,maxCountToGet):
    res = api.searchLocation(locationTag)
    locastionSearchResult = api.LastJson["items"]

    if len(locastionSearchResult) > 0:
        
        items = []
        
        items.extend(api.LastJson.get('ranked_items', []))
        
        itemCount = len(items)
        next_max_id = True
        while next_max_id:
            # first iteration hack
            if next_max_id is True:
                next_max_id = ''

            _ = api.getLocationFeed(locastionSearchResult[0]["location"]["pk"],maxid=next_max_id) #api.getUserFollowers(user_id, maxid=next_max_id)
            itemCount = itemCount + len(api.LastJson["items"])
            items.extend(api.LastJson.get('items', []))
            next_max_id = api.LastJson.get('next_max_id', '')
            
            if itemCount >= maxCountToGet:
                next_max_id = False

            time.sleep(3)
                
        return items
        #res = api.getLocationFeed(locastionSearchResult[0]["location"]["pk"])
        #return api.LastJson["items"],api.LastJson["ranked_items"]
    else:
        return None
    
def GetUserFollowingFeed(api, userName,maxCountToGet):
    
    items = []
    
    follUserRes = api.searchUsername(userName)   #check_username(username)

    if follUserRes == True and api.LastJson['user'] is not None:
        
        api.getUserFollowers(api.LastJson['user']['pk'])   #user_followers(user_id, rank_token, **kwargs)

        if len(api.LastJson["users"]) > 0:
        
            userFollowers = api.LastJson["users"]
            
            for user in islice(userFollowers, 0, int(maxCountToGet)): 
                if (user["is_private"] == False):
                    time.sleep(3)
                    feedres = api.getUserFeed(user['pk'])   #user_feed(user_id, **kwargs)
                    if feedres == True and api.LastJson['items'] is not None:
                        if len(api.LastJson['items']) > 0:
                            #items.extend([{**api.LastJson['items'][0],**user} ])
                            items.extend([api.LastJson['items'][0]])
        
            return items
            
        else:  # followers list is empty
            return None
    else: # user is not found
        return None

#api Wrappers
def getSelfTimeline(api):
    return api.getTimeline()


def getTotalFollowers(api, user_id):
    return api.getTotalFollowers(user_id);

def getTotalFollowings(api, user_id):
    return api.getTotalFollowings(user_id);

def getTotalUserFeed(api, user_id):
    return api.getTotalUserFeed(user_id);


def GetSelfFeed(api, userId):
    api.getSelfUserFeed()
    return api.LastJson["items"]

def FollowUser(api, userId):
    api.follow(userId)
    
def UnFollowUser(api, userId):
    api.unfollow(userId)
    
def CommentOnMedia(api, mediaId,commentText):
    api.comment(mediaId, commentText)

def LikeMedia(api, mediaId):
    return api.like(mediaId)

def GetTagFeed(api, hashTag,maxCountToGet):
    
    res = api.getHashtagFeed(hashTag)

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
                
        return items
        #res = api.getLocationFeed(locastionSearchResult[0]["location"]["pk"])
        #return api.LastJson["items"],api.LastJson["ranked_items"]
    else:
        return None
    
def GetUserFollowingFeed(api, userName,maxCountToGet):
    
    items = []
    
    follUserRes = api.searchUsername(userName)

    if follUserRes == True and api.LastJson['user'] is not None:
        
        api.getUserFollowers(api.LastJson['user']['pk'])

        if len(api.LastJson["users"]) > 0:
        
            userFollowers = api.LastJson["users"]
            
            for user in islice(userFollowers, 0, int(maxCountToGet)): 
                if (user["is_private"] == False):
                    time.sleep(3)
                    feedres = api.getUserFeed(user['pk'])
                    if feedres == True and api.LastJson['items'] is not None:
                        if len(api.LastJson['items']) > 0:
                            #items.extend([{**api.LastJson['items'][0],**user} ])
                            items.extend([api.LastJson['items'][0]])
        
            return items
            
        else:  # followers list is empty
            return None
    else: # user is not found
        return None

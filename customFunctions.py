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

def AppLogin(socialUsername,pin,IMEI):
    API_Login = API_BaseURL + "/Mobile/Login"
    
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
        return r["MobileLoginJsonRootObject"]
    else:
        None

def SendAction(SocialProfileId, Action, TargetSocialUserName,Message):
    
    API_Login = API_BaseURL + "/Mobile/AppActionBulk"
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
    
def UpdateInitialStatsToServer(SocialProfileId, InitFollowers, InitFollowing,InitPosts):
    API_Login = API_BaseURL + "/Mobile/InitialStats"
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


def GetManifest(SocialProfileId):
    API_Manifest = API_BaseURL + "/Mobile/GetManifest"
    data = {'SocialProfileId':SocialProfileId,    #1101
            'SocialPassword':'1'} 
    r = requests.post(url = API_Manifest, data = data) 
    return json.loads(r.text)

class Manifest:
    pass
    

def LoadManifest(manifest):
    hashtags = []
    locations = []
    DirectCompetitors = []
    
    manifestObj = Manifest()

    manifestObj.AfterFollLikeuserPosts = manifest["MobileJsonRootObject"]["TargetInformation"]["AfterFollLikeuserPosts"]
    manifestObj.AfterFollCommentUserPosts = manifest["MobileJsonRootObject"]["TargetInformation"]["AfterFollCommentUserPosts"]
    manifestObj.AfterFollViewUserStory = manifest["MobileJsonRootObject"]["TargetInformation"]["AfterFollViewUserStory"]
    manifestObj.AfterFollCommentUserStory = manifest["MobileJsonRootObject"]["TargetInformation"]["AfterFollCommentUserStory"]
    manifestObj.UnFollFollowersAfterMinDays = manifest["MobileJsonRootObject"]["TargetInformation"]["UnFollFollowersAfterMinDays"]

    manifestObj.FollUserProfileImage = manifest["MobileJsonRootObject"]["TargetInformation"]["FollUserProfileImage"]

    manifestObj.FollDoNotFollowUsernamewithdigits = manifest["MobileJsonRootObject"]["TargetInformation"]["FollDoNotFollowUsernamewithdigits"]
    manifestObj.FollDoNotFollowUsernamewithdigitsVal = manifest["MobileJsonRootObject"]["TargetInformation"]["FollDoNotFollowUsernamewithdigitsVal"]

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
    manifestObj.FollowList = manifest["MobileJsonRootObject"]["FollowList"]
    manifestObj.LikeList = manifest["MobileJsonRootObject"]["LikeList"]
    
    
    
    manifestObj.FollAccSearchTags = int(intervals[0]["FollAccSearchTags"])
    manifestObj.UnFoll16DaysEngage = int(intervals[0]["UnFoll16DaysEngage"])
    manifestObj.LikeFollowingPosts = int(intervals[0]["LikeFollowingPosts"])
    manifestObj.VwStoriesFollowing = int(intervals[0]["VwStoriesFollowing"])
    manifestObj.CommFollowingPosts = int(intervals[0]["CommFollowingPosts"])

    manifestObj.totalActions = manifestObj.FollAccSearchTags + manifestObj.UnFoll16DaysEngage + manifestObj.LikeFollowingPosts  + manifestObj.VwStoriesFollowing + manifestObj.CommFollowingPosts

    
    
    manifestObj.totalActionsHashTag = (manifestObj.totalActions / 4) + 5
    manifestObj.totalActionsLocation = (manifestObj.totalActions / 4 ) + 5
    manifestObj.totalActionsDirectCompetitor = (manifestObj.totalActions / 4) + 5
    manifestObj.totalActionsIGUsers = (manifestObj.totalActions / 4) + 5

    manifestObj.totalActionsPerHahTag = manifestObj.totalActionsHashTag / len(manifestObj.hashtags)
    manifestObj.totalActionsPerLocation = manifestObj.totalActionsLocation / len(manifestObj.locations)
    
    return manifestObj

    
def LoadHashtagsTodo(api, manifestObj, SubActionWeights):
    
    tagMediaUsers = []

    for tag in islice(manifestObj.hashtags,0,20):
        lItems = GetTagFeed(api,tag,manifestObj.totalActionsHashTag) #api.getHashtagFeed(tag)

        for photo in  islice(lItems, 0, int(manifestObj.totalActionsPerHahTag)): #islice(filter(lambda x: (x["media_type"] == 1),  items), 0, int(totalActionsPerHahTag)): #items::
            if (photo["has_liked"] == False):
                tagMediaUsers.append([tag,str(photo["pk"]),str(photo["user"]["pk"]),str(photo["user"]["username"]),str(photo["user"]["full_name"]), str(photo["user"]["friendship_status"]["following"]) ])

#         for photo in  islice(api.LastJson["items"], 0, int(manifestObj.totalActionsPerHahTag)): #islice(filter(lambda x: (x["media_type"] == 1),  items), 0, int(totalActionsPerHahTag)): #items::
#             if (photo["has_liked"] == False):
#                 tagMediaUsers.append([tag,str(photo["pk"]),str(photo["user"]["pk"]),str(photo["user"]["username"]),str(photo["user"]["full_name"]), str(photo["user"]["friendship_status"]["following"]) ])
  
    hcols = ["Tag", "MediaId","UserId","Username","FullName","FriendShipStatus"]
   
    usersdf = pd.DataFrame(tagMediaUsers,columns = hcols)
    usersdf.insert(0, 'Seq',0)
    actions = ['Follow', 'Like', 'Comment' ]
    
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

def LoadLocationsTodo(api, manifestObj, SubActionWeights,SeqNos):
    
    locMediaUsers = []

    for loc in islice(manifestObj.locations,0,20):
        lItems = GetLocationFeed(api,loc,manifestObj.totalActionsPerLocation)

        for photo in  islice(lItems, 0, int(manifestObj.totalActionsPerLocation)): #islice(filter(lambda x: (x["media_type"] == 1),  items), 0, int(totalActionsPerHahTag)): #items::
            if (photo["has_liked"] == False):
                locMediaUsers.append([loc,str(photo["pk"]),str(photo["user"]["pk"]),str(photo["user"]["username"]),str(photo["user"]["full_name"]), str(photo["user"]["friendship_status"]["following"]) ])
  
    hcols = ["Tag", "MediaId","UserId","Username","FullName","FriendShipStatus"]
   
    usersdf = pd.DataFrame(locMediaUsers,columns = hcols)
    usersdf.insert(0, 'Seq',0)
    actions = ['Follow', 'Like', 'Comment' ]
    
    Samples = choices(actions, SubActionWeights, k=len(usersdf))

    usersdf['Action'] = Samples

    fc = SeqNos[1]+1
    lc = SeqNos[2]+1
    cc = SeqNos[0]+1

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

def LoadCompetitorTodo(api, manifestObj, SubActionWeights,SeqNos):
    
    locMediaUsers = []

    for compe in islice(manifestObj.DirectCompetitors,0,1): #20
        lItems = GetUserFollowingFeed(api,compe,manifestObj.totalActionsDirectCompetitor) 

        if lItems is not None and len(lItems) > 0:
            for photo in  islice(lItems, 0, int(manifestObj.totalActionsDirectCompetitor)): #islice(filter(lambda x: (x["media_type"] == 1),  items), 0, int(totalActionsPerHahTag)): #items::
                if (photo["has_liked"] == False):
                    locMediaUsers.append([compe,str(photo["pk"]),str(photo["user"]["pk"]),str(photo["user"]["username"]),str(photo["user"]["full_name"]), '' ])
  
    hcols = ["Tag", "MediaId","UserId","Username","FullName","FriendShipStatus"]
   
    usersdf = pd.DataFrame(locMediaUsers,columns = hcols)
    usersdf.insert(0, 'Seq',0)
    actions = ['Follow', 'Like', 'Comment' ]
    
    Samples = choices(actions, SubActionWeights, k=len(usersdf))

    usersdf['Action'] = Samples

    fc = SeqNos[1]+1
    lc = SeqNos[2]+1
    cc = SeqNos[0]+1

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

def LoadUnFollowTodo(api, manifestObj, SubActionWeights):
    
    locMediaUsers = []

    for foll in manifestObj.FollowersToUnFollow:
        
        resUser = api.searchUsername(foll['FollowedSocialUsername'])

        if resUser == True and api.LastJson['user'] is not None:
            locMediaUsers.append([str(api.LastJson['user']['username']),'',str(api.LastJson['user']['pk']),str(api.LastJson['user']['username']),str(api.LastJson["user"]["full_name"]), '' ])
  
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


def SetupGlobalTodo(GlobalActionWeights, totalActions):
            
    actions = ['Follow', 'UnFollow', 'Like', 'Comment', 'StoryView' ]
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


    
    
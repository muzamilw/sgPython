
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

    def resource_path(self,relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

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

        blacklist = ["porn","MAGA","Trump","redpill","incel","conservative","fakenews","gay","pill","weed","fake","spam","arse","ass","asshole","bastard","bitch","boong","cock","cocksucker","coon","coonnass","cunt","crap","dick","douche","fag","faggot","fuck","gook","motherfucker","piss","pussy","shit","slut","tits","xxx","a55","a55hole","aeolus","ahole","anal","analprobe","anilingus","anus","areola","areole","arian","aryan","ass","assbang","assbanged","assbangs","asses","assfuck","assfucker","assh0le","asshat","assho1e","ass hole","assholes","assmaster","assmunch","asswipe","asswipes","azazel","azz","b1tch","babe","babes","ballsack","bang","banger","barf","bastard","bastards","bawdy","beaner","beardedclam","beastiality","beatch","beater","beaver","beer","beeyotch","beotch","biatch","bigtits","big tits","bimbo","bitch","bitched","bitches","bitchy","blow job","blow","blowjob","blowjobs","bod","bodily","boink","bollock","bollocks","bollok","bone","boned","boner","boners","bong","boob","boobies","boobs","booby","booger","bookie","bootee","bootie","booty","booze","boozer","boozy","bosom","bosomy","bowel","bowels","bra","brassiere","breast","breasts","bugger","bukkake","bullshit","bull shit","bullshits","bullshitted","bullturds","bung","busty","butt","butt fuck","buttfuck","buttfucker","buttfucker","buttplug","c.0.c.k","c.o.c.k.","c.u.n.t","c0ck","c-0-c-k","caca","cahone","cameltoe","carpetmuncher","cawk","cervix","chinc","chincs","chink","chink","chode","chodes","cl1t","climax","clit","clitoris","clitorus","clits","clitty","cocain","cocaine","cock","c-o-c-k","cockblock","cockholster","cockknocker","cocks","cocksmoker","cocksucker","cock sucker","coital","commie","condom","coon","coons","corksucker","crabs","crack","cracker","crackwhore","crap","crappy","cum","cummin","cumming","cumshot","cumshots","cumslut","cumstain","cunilingus","cunnilingus","cunny","cunt","cunt","c-u-n-t","cuntface","cunthunter","cuntlick","cuntlicker","cunts","d0ng","d0uch3","d0uche","d1ck","d1ld0","d1ldo","dago","dagos","dammit","damn","damned","damnit","dawgie-style","dick","dickbag","dickdipper","dickface","dickflipper","dickhead","dickheads","dickish","dick-ish","dickripper","dicksipper","dickweed","dickwhipper","dickzipper","diddle","dike","dildo","dildos","diligaf","dillweed","dimwit","dingle","dipship","doggie-style","doggy-style","dong","doofus","doosh","dopey","douch3","douche","douchebag","douchebags","douchey","drunk","dumass","dumbass","dumbasses","dummy","dyke","dykes","ejaculate","enlargement","erect","erection","erotic","essohbee","extacy","extasy","f.u.c.k","fack","fag","fagg","fagged","faggit","faggot","fagot","fags","faig","faigt","fannybandit","fart","fartknocker","fat","felch","felcher","felching","fellate","fellatio","feltch","feltcher","fisted","fisting","fisty","floozy","foad","fondle","foobar","foreskin","freex","frigg","frigga","fubar","fuck","f-u-c-k","fuckass","fucked","fucked","fucker","fuckface","fuckin","fucking","fucknugget","fucknut","fuckoff","fucks","fucktard","fuck-tard","fuckup","fuckwad","fuckwit","fudgepacker","fuk","fvck","fxck","gae","gai","ganja","gay","gays","gey","gfy","ghay","ghey","gigolo","glans","goatse","godamn","godamnit","goddam","goddammit","goddamn","goldenshower","gonad","gonads","gook","gooks","gringo","gspot","g-spot","gtfo","guido","h0m0","h0mo","handjob","hardon","he11","hebe","heeb","hell","hemp","heroin","herp","herpes","herpy","hitler","hiv","hobag","hom0","homey","homo","homoey","honky","hooch","hookah","hooker","hoor","hootch","hooter","hooters","horny","hump","humped","humping","hussy","hymen","inbred","incest","injun","j3rk0ff","jackass","jackhole","jackoff","jap","japs","jerk","jerk0ff","jerked","jerkoff","jism","jiz","jizm","jizz","jizzed","junkie","junky","kike","kikes","kill","kinky","kkk","klan","knobend","kooch","kooches","kootch","kraut","kyke","labia","lech","leper","lesbians","lesbo","lesbos","lez","lezbian","lezbians","lezbo","lezbos","lezzie","lezzies","lezzy","lmao","lmfao","loin","loins","lube","lusty","mams","massa","masterbate","masterbating","masterbation","masturbate","masturbating","masturbation","maxi","menses","menstruate","menstruation","meth","m-fucking","mofo","molest","moolie","moron","motherfucka","motherfucker","motherfucking","mtherfucker","mthrfucker","mthrfucking","muff","muffdiver","murder","muthafuckaz","muthafucker","mutherfucker","mutherfucking","muthrfucking","nad","nads","naked","napalm","nappy","nazi","nazism","negro","nigga","niggah","niggas","niggaz","nigger","nigger","niggers","niggle","niglet","nimrod","ninny","nipple","nooky","nympho","opiate","opium","oral","orally","organ","orgasm","orgasmic","orgies","orgy","ovary","ovum","ovums","p.u.s.s.y.","paddy","paki","pantie","panties","panty","pastie","pasty","pcp","pecker","pedo","pedophile","pedophilia","pedophiliac","pee","peepee","penetrate","penetration","penial","penile","penis","perversion","peyote","phalli","phallic","phuck","pillowbiter","pimp","pinko","piss","pissed","pissoff","piss-off","pms","polack","pollock","poon","poontang","porn","porno","pornography","pot","potty","prick","prig","prostitute","prude","pube","pubic","pubis","punkass","punky","puss","pussies","pussy","pussypounder","puto","queaf","queef","queef","queer","queero","queers","quicky","quim","racy","rape","raped","raper","rapist","raunch","rectal","rectum","rectus","reefer","reetard","reich","retard","retarded","revue","rimjob","ritard","rtard","rtard","rum","rump","rumprammer","ruski","s.h.i.t.","s.o.b.","s0b","sadism","sadist","scag","scantily","schizo","schlong","screw","screwed","scrog","scrot","scrote","scrotum","scrud","scum","seaman","seamen","seduce","semen","sex","sexual","sh1t","s-h-1-t","shamedame","shit","s-h-i-t","shite","shiteater","shitface","shithead","shithole","shithouse","shits","shitt","shitted","shitter","shitty","shiz","sissy","skag","skank","slave","sleaze","sleazy","slut","slutdumper","slutkiss","sluts","smegma","smut","smutty","snatch","sniper","snuff","s-o-b","sodom","souse","soused","sperm","spic","spick","spik","spiks","spooge","spunk","steamy","stfu","stiffy","stoned","strip","stroke","stupid","suck","sucked","sucking","sumofabiatch","t1t","tampon","tard","tawdry","teabagging","teat","terd","teste","testee","testes","testicle","testis","thrust","thug","tinkle","tit","titfuck","titi","tits","tittiefucker","titties","titty","tittyfuck","tittyfucker","toke","toots","tramp","transsexual","trashy","tubgirl","turd","tush","twat","twats","ugly","undies","unwed","urinal","urine","uterus","uzi","vag","vagina","valium","viagra","virgin","vixen","vodka","vomit","voyeur","vulgar","vulva","wad","wang","wank","wanker","wazoo","wedgie","weed","weenie","weewee","weiner","weirdo","wench","wetback","wh0re","wh0reface","whitey","whiz","whoralicious","whore","whorealicious","whored","whoreface","whorehopper","whorehouse","whores","whoring","wigger","womb","woody","wop","wtf","x-rated","xxx","yeasty","yobbo","zoophile","xxx"]
        blacklist = pd.DataFrame(blacklist)

        gVars = app.gVars
        gVars.RunStartTime = datetime.datetime.now()

        while True and self.botStop.is_set() == False and RetryCount <= MaxRetryCount and IsApiClientError == False:
            try:
                RetryCount = RetryCount + 1
                log.info("Starting Sequence")
                # return
                
                gVars.SequenceRunning = True
                
                
                if gVars.loginResult is not None:
                    gVars.SocialProfileId = gVars.loginResult["SocialProfileId"]
                    gVars.manifest = cf.GetManifest(gVars.loginResult["SocialProfileId"],gVars)

                    if api.authenticated_user_id is not None:

                        try:

                            
                            if (gVars.loginResult["InitialStatsReceived"] != True):

                                user_info = api.user_info(api.authenticated_user_id)
                                cf.UpdateInitialStatsToServer(gVars.SocialProfileId,user_info['user']['follower_count'],user_info['user']['following_count'],user_info['user']['media_count'],gVars)
                                log.info('Init followers : ' + str(user_info['user']['follower_count']))
                                log.info('Init Following : ' +str(user_info['user']['following_count']))
                                log.info('Init Posts : ' + str(user_info['user']['media_count']))
                            else:
                                log.info('Initial info already sent')

                            #sending daily stats
                            if gVars.DailyStatsSent == False and gVars.DailyStatsSentDate != datetime.datetime.today:
                                user_info = api.user_info(api.authenticated_user_id)
                                log.info('Sending Today Stats')
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.FollowersCountUpdate,'self','{\"InitialFollowings\":\"'+str(user_info['user']['following_count'])+'\",\"InitialFollowers\":\"'+ str(user_info['user']['follower_count']) +'\",\"InitialPosts\":\"'+str(user_info['user']['media_count'])+'\",\"SocialProfileId\":'+str(gVars.SocialProfileId)+'}')
                                gVars.DailyStatsSent = True
                                gVars.DailyStatsSentDate = datetime.datetime.today
                            else:
                                log.info('Today Stats already sent')
                            

                            if gVars.manifestJson is None or app.ManifestRefreshed == True :
                                log.info('Getting manifest from server')
                                gVars.manifestJson = cf.GetManifest(gVars.SocialProfileId,gVars)

                            

                            if gVars.manifestObj is None or app.ManifestRefreshed == True:
                                log.info('Processing manifest')
                                gVars.manifestObj = cf.LoadManifest(gVars.manifestJson)

                            gVars.ReqFollow = gVars.manifestObj.FollAccSearchTags
                            
                            if gVars.manifestObj.UnFollFollowersAfterMinDays == 1:
                                gVars.ReqUnFollow = gVars.manifestObj.UnFoll16DaysEngage if gVars.manifestObj.UnFoll16DaysEngage <= len(gVars.manifestObj.FollowersToUnFollow) else len(gVars.manifestObj.FollowersToUnFollow) #len(gVars.manifestObj.FollowersToUnFollow) #gVars.manifestObj.UnFoll16DaysEngage
                                gVars.TotUnFollow = gVars.manifestObj.UnFoll16DaysEngage if gVars.manifestObj.UnFoll16DaysEngage <= len(gVars.manifestObj.FollowersToUnFollow) else len(gVars.manifestObj.FollowersToUnFollow)
                            else:
                                gVars.ReqUnFollow = 0
                                gVars.TotUnFollow = 0


                            gVars.ReqLikes = gVars.manifestObj.LikeFollowingPosts
                            if gVars.manifestObj.AfterFollViewUserStory == 1 :
                                gVars.ReqStoryViews = gVars.manifestObj.VwStoriesFollowing
                            else:
                                gVars.ReqStoryViews = 0

                            gVars.ReqComments = gVars.manifestObj.CommFollowingPosts

                            gVars.ReqExComments = len(gVars.manifestObj.FollowersToComment)
                            gVars.ReqExFollow = len(gVars.manifestObj.FollowList)
                            gVars.ReqExLikes  = len(gVars.manifestObj.LikeList)
                            
                            # #updating graph
                            # Req = [gVars.ReqFollow, gVars.ReqUnFollow, gVars.ReqLikes, gVars.ReqStoryViews, gVars.ReqComments]
                            # Loaded = [gVars.TotFollow, gVars.TotUnFollow , gVars.TotLikes, gVars.TotStoryViews,gVars.TotComments ]
                            # Done = [gVars.CurrentFollowDone, gVars.CurrentUnFollowDone, gVars.CurrentLikeDone, gVars.CurrentStoryViewDone,gVars.CurrentCommentsDone ]
                            # self.ui.drawGraphMain(Req,Loaded,Done)
                            # # LX FX CX
                            # Req = [gVars.ReqExLikes, gVars.ReqExFollow, gVars.ReqExComments]
                            # Loaded = [gVars.TotExLikes, gVars.TotExFollow , gVars.TotExComments ]
                            # Done = [gVars.CurrentExLikeDone, gVars.CurrentExFollowDone, gVars.CurrentExCommentsDone ]
                            # self.ui.drawGraphSecondary(Req,Loaded,Done)
                    
                            runTimeComputation = (gVars.ReqFollow + gVars.ReqUnFollow + gVars.ReqLikes + gVars.ReqStoryViews + gVars.ReqComments  + gVars.ReqExFollow + gVars.ReqExLikes) * 30 
                            gVars.TotalActionsLoaded = gVars.ReqFollow + gVars.ReqUnFollow + gVars.ReqLikes + gVars.ReqStoryViews + gVars.ReqComments + gVars.ReqExFollow + gVars.ReqExLikes
                            runTimeComputation += gVars.manifestObj.totalActions  * 10
                            gVars.RequiredActionPerformed = gVars.manifestObj.totalActions

                            self.ui.TotalTime = int(runTimeComputation)


                            if gVars.Todo is None or app.ManifestRefreshed == True:
                                gVars.Todo = cf.SetupGlobalTodo(gVars.manifestObj)
                                log.info('Creating list')
                            

                            if gVars.hashtagActions is None or app.ManifestRefreshed == True:
                                log.info('Fetching feed for Hashtags')
                                hashstart = datetime.datetime.now()
                                gVars.hashtagActions = cf.LoadHashtagsTodo(api,gVars.manifestObj,Client,log,gVars,blacklist)
                                LoadtimeHashtagsTodo = (datetime.datetime.now()-hashstart).total_seconds()
                                log.info('Hashtags feed done : ' + str(LoadtimeHashtagsTodo))
                                gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeHashtagsTodo
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.ping,'','ping')
                            
                                
                            if gVars.locationActions is None or app.ManifestRefreshed == True:
                                log.info('Fetching feed for Locations')
                                locationtart = datetime.datetime.now()
                                gVars.locationActions = cf.LoadLocationsTodo(api,gVars.manifestObj,gVars.hashtagActions.groupby(['Action'])['Seq'].count(),Client,log,gVars,blacklist)
                                LoadtimeLocTodo = (datetime.datetime.now()-locationtart).total_seconds()
                                log.info('Locations feed done : ' + str(LoadtimeLocTodo))
                                gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeLocTodo
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.ping,'','ping')

                            
                                
                            if gVars.DCActions is None or app.ManifestRefreshed == True:
                                log.info('Fetching feed for Competitors')
                                DCstart = datetime.datetime.now()
                                SeqNos = gVars.locationActions.groupby(['Action'])['Seq'].count().add(gVars.hashtagActions.groupby(['Action'])['Seq'].count(),fill_value=0)
                                gVars.DCActions = cf.LoadCompetitorTodo(api,gVars.manifestObj,SeqNos,Client,log,gVars,blacklist)
                                LoadtimeDCTodo = (datetime.datetime.now()-DCstart).total_seconds()
                                log.info('Competitors feed done : ' + str(LoadtimeDCTodo))
                                gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeDCTodo
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.ping,'','ping')

                            if gVars.SuggestFollowers is None or app.ManifestRefreshed == True:
                                log.info('Fetching Feed of Suggested Users')
                                Suggestedstart = datetime.datetime.now()
                                SeqNos = gVars.locationActions.groupby(['Action'])['Seq'].count().add(gVars.hashtagActions.groupby(['Action'])['Seq'].count(),fill_value=0)
                                if (len(gVars.DCActions.groupby(['Action'])['Seq'].count()) > 0 ):
                                    SeqNos = SeqNos.add(gVars.DCActions.groupby(['Action'])['Seq'].count(),fill_value=0)
                                

                                gVars.SuggestFollowers = cf.LoadSuggestedUsersForFollow(api,gVars.manifestObj,SeqNos,Client,log,gVars,blacklist)
                                LoadtimeSuggestedTodo = (datetime.datetime.now()-Suggestedstart).total_seconds()
                                log.info('Suggested Users feed done : ' + str(LoadtimeSuggestedTodo))
                                gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeSuggestedTodo
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.ping,'','ping')

                                
                            if (gVars.UnFollowActions is None or app.ManifestRefreshed == True) and gVars.manifestObj.UnFollFollowersAfterMinDays == 1 :
                                log.info('Fetching feed for UnFollow')
                                UnFollstart = datetime.datetime.now()
                                gVars.UnFollowActions = cf.LoadUnFollowTodo(api,gVars.manifestObj,[1],log,gVars)
                                LoadtimeUnFollTodo = (datetime.datetime.now()-UnFollstart).total_seconds()
                                log.info('UnFollow feed fone : ' + str(LoadtimeUnFollTodo))
                                gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeUnFollTodo
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.ping,'','ping')

                            if (gVars.StoryViewActions is None or app.ManifestRefreshed == True ) and gVars.manifestObj.AfterFollViewUserStory == 1 :
                                log.info('Fetching feeds for StoryViews')
                                Storystart = datetime.datetime.now()
                                gVars.StoryViewActions = cf.LoadStoryTodo(api,gVars.manifestObj,[1],log,gVars)
                                LoadtimeStoryTodo = (datetime.datetime.now()-Storystart).total_seconds()
                                log.info('StoryViews feed done : ' + str(LoadtimeStoryTodo))
                                gVars.TotalSessionTime = gVars.TotalSessionTime + LoadtimeStoryTodo
                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.ping,'','ping')

                            frames = [gVars.hashtagActions, gVars.locationActions, gVars.DCActions, gVars.UnFollowActions,gVars.SuggestFollowers,gVars.StoryViewActions]
                            actions = pd.concat(frames)

                            if gVars.GlobalTodo is None or app.ManifestRefreshed == True:
                                gVars.GlobalTodo = gVars.Todo.merge(actions,how='left', left_on=['Seq','Action'], right_on=['Seq','Action'])
                                #gVars.GlobalTodo.to_csv('GlobData.csv')
                                log.info('Actions Ready')

                            gVars.TotFollow = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'Follow') & (gVars.GlobalTodo['UserId'] != '')])
                            gVars.TotUnFollow = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'UnFollow') & (gVars.GlobalTodo['UserId'].isnull() == False)])
                            gVars.TotLikes = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'Like') & (gVars.GlobalTodo['UserId'] != '')])
                            gVars.TotStoryViews = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'StoryView') & (gVars.GlobalTodo['UserId'] != '')])
                            gVars.TotComments = len(gVars.GlobalTodo[(gVars.GlobalTodo['Action'] == 'Comment') & (gVars.GlobalTodo['UserId'] != '')])

                            gVars.TotExComments = len(gVars.GlobalTodo[(gVars.GlobalTodo['FriendShipStatus'] == 'MustComment') & (gVars.GlobalTodo['UserId'] != '')])
                            gVars.TotExLikes = len(gVars.GlobalTodo[(gVars.GlobalTodo['FriendShipStatus'] == 'MustLike') & (gVars.GlobalTodo['UserId'] != '')])
                            gVars.TotExFollow = len(gVars.GlobalTodo[(gVars.GlobalTodo['FriendShipStatus'] == 'MustFollow') & (gVars.GlobalTodo['UserId'] != '')])
                            
                            # Req = [gVars.ReqFollow, gVars.ReqUnFollow, gVars.ReqLikes, gVars.ReqStoryViews, gVars.ReqComments]
                            # Loaded = [gVars.TotFollow, gVars.TotUnFollow , gVars.TotLikes, gVars.TotStoryViews,gVars.TotComments ]
                            # Done = [gVars.CurrentFollowDone, gVars.CurrentUnFollowDone, gVars.CurrentLikeDone, gVars.CurrentStoryViewDone,gVars.CurrentCommentsDone ]
                            # self.ui.drawGraphMain(Req,Loaded,Done)
                            # # LX FX CX
                            # Req = [gVars.ReqExLikes, gVars.ReqExFollow, gVars.ReqExComments]
                            # Loaded = [gVars.TotExLikes, gVars.TotExFollow , gVars.TotExComments ]
                            # Done = [gVars.CurrentExLikeDone, gVars.CurrentExFollowDone, gVars.CurrentExCommentsDone ]
                            # self.ui.drawGraphSecondary(Req,Loaded,Done)
                    
                            

                            
                            LoadtimeTodo = (datetime.datetime.now()-gVars.RunStartTime).total_seconds()
                            log.info("Total time in fetching : " + str(LoadtimeTodo))
                            app.ManifestRefreshed == False

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
                            log.info("Initial feed : Instagram Login error occurred, Please sign off and relogin to continue")
                            log.info(str(traceback.format_exc()))
                            cf.SendError('info@socialplannerpro.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                            self.ShowErrorMessage("Initial feed : Instagram Login error occurred,Stopping Sequence. Please sign off and relogin to continue")
                            IsApiClientError = True
                            return

                        except (ClientSentryBlockError, ClientChallengeRequiredError, ClientCheckpointRequiredError) as e:
                            #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                            log.info("Initial feed : Instagram Error occurred, Please open Instagram in the browser and manually clear any location Challenges or checkpoints")
                            log.info(str(traceback.format_exc()))
                            cf.SendError('info@socialplannerpro.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                            self.ShowErrorMessage("Initial feed : Critical Instagram Error occurred, Stopping Sequence. Please open Instagram in the browser and manually clear any location Challenges or checkpoints")
                            IsApiClientError = True
                            return

                        except (ClientError,ClientConnectionError) as e:
                            #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                            log.info("Initial feed : Api Client or Network Error occurred, Restarting")
                            log.info(str(traceback.format_exc()))
                            cf.SendError('info@socialplannerpro.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                           
                            raise e
                            
                        except Exception as e: ## try catch block for the 
                            log.info('Unexpected Exception in initial feed loads, restarting : {0!s}'.format(traceback.format_exc()))
                            cf.SendError('info@socialplannerpro.com',traceback.format_exc() + self.logControl.text ,gVars.SGusername)
                            raise e
                            
                        Comments = ['😀','👍','💓','🤩','🥰']
                        curRow = None

                        try:
                            for i, row in islice(gVars.GlobalTodo.iterrows(),0,10000):
                            
                                if (self.botStop.is_set() == True):
                                    print('Stopping Session ')
                                    break

                                if row['Status'] == 1 and not pd.isnull(str(row['MediaId'])) and str(row['MediaId']) != 'nan':
                                    
                                    waitTime = randrange(40,60)
                                    
                                    
                                    if row['Action'] == 'Like' and gVars.manifestObj.AfterFollLikeuserPosts == 1 and ( gVars.CurrentLikeDone < gVars.manifestObj.LikeFollowingPosts or gVars.CurrentExLikeDone < gVars.ReqExLikes):
                                        try:
                                            log.info('Liking : ' + row['MediaId'] + ' - Wait : ' + str(waitTime))
                                            apiW.LikeMedia(api,row['MediaId'])
                                            cf.SendAction(gVars,gVars.SocialProfileId,Actions.Like,row['Username'],row['MediaId'])
                                        except ClientError as e:
                                            log.info('Error :  Media deleted {3!s}  {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response, row['MediaId']))
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

                                        try:
                                            api.mute_unmute(row['UserId'])
                                        except ClientError as e:
                                            log.info('Error : Mute  {3!s}  {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response, row['MediaId']))
                                            cf.SendAction(gVars,gVars.SocialProfileId,Actions.BotError,row['Username'],'You cant mute users you are not following  ' + str(row['Username']))
                                            gVars.GlobalTodo.loc[i,'Data'] = 'You cant mute users you are not following'
                                       
                                        cf.SendAction(gVars,gVars.SocialProfileId,Actions.Follow,row['Username'],'')
                                        log.info('Following : ' + row['Username'] + ' - Wait : ' + str(waitTime))
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
                                            log.info('Commenting : ' + row['MediaId'] + ' - Wait : ' + str(waitTime))
                                            apiW.CommentOnMedia(api,row['MediaId'],comm)
                                            cf.SendAction(gVars,gVars.SocialProfileId,Actions.Comment,row['Username'],row['Username'] + 'Comment added : ' + comm)
                                            gVars.GlobalTodo.loc[i,'Data'] = 'Comment added : ' + comm
                                        except ClientError as e:
                                            log.info('Error : Comment media deleted {3!s}  {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response, row['MediaId']))
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
                                        log.info('UnFollow : ' + row['Username'] +  ' - Wait : ' + str(waitTime))
                                        if row['Tag'] == 'delete_not_found':  ##ignore the IG action and send it anyways
                                            cf.SendAction(gVars,gVars.SocialProfileId,Actions.UnFollow,row['Username'],'delete_not_found')
                                        else:
                                            try:
                                                apiW.UnFollowUser(api,row['UserId'])
                                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.UnFollow,row['Username'],'')
                                            except ClientError as e:
                                                log.info('Error : UnFollow {3!s}  {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response, row['Username']))
                                                cf.SendAction(gVars,gVars.SocialProfileId,Actions.UnFollow,row['Username'],'delete_not_found')
                                            
                                        gVars.GlobalTodo.loc[i,'Status'] = 2
                                        gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                        
                                        gVars.CurrentUnFollowDone = gVars.CurrentUnFollowDone + 1
                                        time.sleep(waitTime) 

                                    if row['Action'] == 'StoryView' and gVars.manifestObj.AfterFollViewUserStory == 1 and gVars.CurrentStoryViewDone < gVars.manifestObj.VwStoriesFollowing :
                                        log.info('Story View : ' + row['Username'] +  ' - Wait : ' + str(waitTime))
                                        apiW.ViewStory(api,row['MediaId'],row['FriendShipStatus'])
                                        cf.SendAction(gVars,gVars.SocialProfileId,Actions.StoryView,row['Username'],'story pages : ' + str(len(row['MediaId'])))
                                        
                                        gVars.GlobalTodo.loc[i,'Status'] = 2
                                        gVars.GlobalTodo.loc[i,'ActionDateTime'] = datetime.datetime.now()
                                        gVars.GlobalTodo.loc[i,'Data'] = 'story pages : ' + str(len(row['MediaId']))
                                        
                                        gVars.CurrentStoryViewDone = gVars.CurrentStoryViewDone + 1
                                        time.sleep(waitTime)

                                    #  F U L S C
                                    # Req = [gVars.ReqFollow, gVars.ReqUnFollow, gVars.ReqLikes, gVars.ReqStoryViews, gVars.ReqComments]
                                    # Loaded = [gVars.TotFollow, gVars.TotUnFollow , gVars.TotLikes, gVars.TotStoryViews,gVars.TotComments ]
                                    # Done = [gVars.CurrentFollowDone, gVars.CurrentUnFollowDone, gVars.CurrentLikeDone, gVars.CurrentStoryViewDone,gVars.CurrentCommentsDone ]
                                    # self.ui.drawGraphMain(Req,Loaded,Done)
                                    # # LX FX CX
                                    # Req = [gVars.ReqExLikes, gVars.ReqExFollow, gVars.ReqExComments]
                                    # Loaded = [gVars.TotExLikes, gVars.TotExFollow , gVars.TotExComments ]
                                    # Done = [gVars.CurrentExLikeDone, gVars.CurrentExFollowDone, gVars.CurrentExCommentsDone ]
                                    # self.ui.drawGraphSecondary(Req,Loaded,Done)



                            
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
                                
                                log.info('Session completed at : ' + str(gVars.RunEndTime) )
                                #writing log to file

                                if (platform.system() == "Darwin"):
                                    Path(os.path.join(os.getenv("HOME"), ".SocialPlannerPro")).mkdir(parents=True, exist_ok=True)
                                    file_to_open = os.path.join(os.getenv("HOME"), ".SocialPlannerPro", "GlobalTodo.html")
                                else:
                                    file_to_open = Path("userdata") / "GlobalTodo.html"
                                
                                with open(file_to_open, "w", encoding="utf-8") as file:
                                    file.writelines('<meta charset="UTF-8">\n')
                                    file.write(gVars.GlobalTodo.to_html())

                                
                                cf.SendEmail('info@socialplannerpro.com',file_to_open,gVars.SGusername,'')

                                app.ResetGlobalVars()
                                log.info('Cleanup done for Session')
                                self.ui.stop()

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
                            log.info("Fatal Error : Instagram Login occurred, Please sign off and relogin to continue")
                            log.info(str(traceback.format_exc()))
                            cf.SendError('info@socialplannerpro.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                            self.ShowErrorMessage("Instagram Login occurred,Stopping Sequence. Please sign off and relogin to continue")
                            IsApiClientError = True
                            return

                        except (ClientSentryBlockError, ClientChallengeRequiredError, ClientCheckpointRequiredError) as e:
                            #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                            log.info("Fatal Error : Instagram Error occurred, Please open Instagram in the browser and manually clear any location Challenges or checkpoints")
                            log.info(str(traceback.format_exc()))
                            cf.SendError('info@socialplannerpro.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                            self.ShowErrorMessage("Critical Instagram Error occurred, Stopping Sequence. Please open Instagram in the browser and manually clear any location Challenges or checkpoints")
                            IsApiClientError = True
                            return

                        except (ClientError,ClientConnectionError) as e:
                            #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                            log.info("Error : Api Client or Network Error occurred, Restarting")
                            log.info(str(traceback.format_exc()))
                            cf.SendError('info@socialplannerpro.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                           
                            raise e

                        except Exception as e:# ClientError:
                            #cf.SendAction(gVars.SocialProfileId,Actions.ActionBlock,curRow['Username'],curRow)
                            log.info("Error : Exception occurred in actions, restarting")
                            log.info(traceback.format_exc())
                            cf.SendError('info@socialplannerpro.com',traceback.format_exc() + self.logControl.text,gVars.SGusername)
                            raise e

                        #gVars.GlobalTodo.to_csv('GlobData.csv')
                        log.info('Sequence Completed Successfully')
                        return

                        #return gVars
                    else:
                        #perform login
                        log.info('Fatal Error : IG user is not logged in.')
                else:
                    log.info('Fatal Error : Error logging onto SPPro Server')
            except:
                # restart main loop
                # self.logControl.text = ""
                log.info('###################################################################')
                log.info(str(traceback.format_exc()))
                log.info('Error : Retrying in ' + str(RetryTimeSeconds * RetryCount) +  ' seconds')
                log.info('Retry #'+str(RetryCount)+' \n')
                log.info('###################################################################')
                
                
                time.sleep(RetryTimeSeconds * RetryCount) 
                pass
            finally:
                # restart main loop
                pass

        gVars.SequenceRunning = False
        log.info('Ending Session')
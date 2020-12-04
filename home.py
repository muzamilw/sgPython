import kivy
kivy.require('1.11.0')


from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.config import Config
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu, MDMenuItem
from kivy.factory import Factory
from kivy.app import App
import kivy.utils as util
import schedule
import time
from functools import partial
import dbutil as db


class Home(Screen):
    
    profilename = ""
    profileid = 0
    profiles = None

    def set_item(self, instance):
        self.ids.dropdown_item.set_item(instance.text)   
        if  instance.text  != "New Profile":
            self.profilename = instance.text
            self.profileid = [obj for obj in self.profiles if obj[1]==instance.text][0][0]
        self.menu.dismiss()         
    
    def on_enter(self):
        app = App.get_running_app()
        self.app = app

        conn = db.create_connection(app.dbPath)
        with conn:
            db.create_table(conn, db.sql_create_profiles_table)
            # profile = ('muzamilw2', 'json here', 1);
            # profileid = db.create_profile(conn, profile)
            self.profiles = db.select_all_profiles(conn)
        
        menu_items = []
        if self.profiles is not None:
            menu_items = [{"icon": "git", "text": f"{i[1]}"
                       
                                                  } for i in self.profiles]
        menu_items.append ({"icon": "git", "text": f"New Profile"})    
                       
                                                  
        self.menu = MDDropdownMenu(
                caller=self.ids.dropdown_item,
                items=menu_items,
                position="center",
                callback=self.set_item,
                width_mult=4)


        # self.ids['bottom_toolbar'].remove_notch()

        

        
       

        # if app.gVars.loginResult is not None:
        #     if app.gVars.IGusername == None:
        #         app.gVars.IGusername = 'nevillekmiec'
        #     if app.gVars.IGpassword == None:
        #         app.gVars.IGpassword = '!_LKvXc1'
        #     app.api = app.checkIGLogin(app.gVars.SGusername)
        #     if app.api is None:
        #         # manager.current = 'iglogin'
        #         pass
        #     else:
        #         # manager.current = 'ready'
        #         self.ids['btnIG'].text = 'Running'
        #         self.ids['btnIG'].md_bg_color = util.get_color_from_hex("##16D39A")
                
        #         self.ids['lblstatusIG'].text = "View Todays Status"
        # else:
        #     # manager.current = 'login'
        #     # self.ids['btnIG'].text = 'Today\'s Status'
        #     self.ids['btnIG'].text = 'Connect'
        #     self.ids['btnIG'].md_bg_color = app.theme_cls.primary_color
                
        #     self.ids['lblstatusIG'].text = " "
        #     pass

    def btnIG_released(self):
        if self.profileid  != 0:
            
            self.app.api = self.app.checkIGLogin(self.profilename)
            if self.app.api is None:
                self.manager.current = 'iglogin'
                
            else:
                self.manager.current = 'ready'
                
        else:
            self.manager.current = 'login'


    

    def btnLIN_released(self):
        pass

        

        # if self.app.gVars.linloginResult is not None:
            
        #     self.app.linapi = self.app.checkLINLogin(self.app.gVars.SGusername)
        #     if self.app.linapi is None:
        #         self.manager.current = 'linlogin'
                
        #     else:
        #         self.manager.current = 'ready'
                
        # else:
        #     self.manager.current = 'login'
            






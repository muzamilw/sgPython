mport os
os.environ['KIVY_IMAGE'] = 'sdl2,gif'
import kivy
from kivy.app import runTouchApp
from kivy.lang import Builder



runTouchApp(Builder.load_string(
'''
Image:
    source:'processing.gif'
'''
))
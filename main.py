from cmu_graphics import *
from structures import *
from utils import *
import matplotlib as plt
import copy
import numpy as np
import os
from dotenv import load_dotenv
import ctypes
import math


def onAppStart(app):
    load_dotenv()
    app.api_key = os.getenv('GEMINI_API_KEY')
    app.isBackspacing = False
    app.backspaceCounter = 0

    #### coords stuff
    app.x,app.y = 0,0

    ##### MAKE MENUS AND TBS HERE ####
    fnInputMenu = Menu(app,'Manage Functions',cx=150,cy=100,
                       width=app.width*0.2,height=app.height*0.1)

    app.functions = []
    app.textboxes = []
    app.menus = [fnInputMenu]

def redrawAll(app):
    # draw title
    drawLabel('Matplotlib GUI',app.width//2,app.height*0.1,size=16,bold=True)
    drawLabel(f'x:{app.x}, y:{app.y}',app.width*0.945,app.height*0.96,size=12)
    drawLabel(f'relX:{pythonRound(app.x/app.width,2)}, relY:{pythonRound(app.y/app.height,2)}',
              app.width*0.94,app.height*0.98)
    ##### HANDLE TEXTBOXES #####
    for tb in app.textboxes:
        tb.drawClickable(app)
        tb.drawOpenedBox(app,tb.text)
    
    ##### HANDLE MENUS   #####
    for menu in app.menus:
         menu.drawClickable(app)
         menu.drawOpenedMenu(app)
    
    


def onKeyPress(app,key):
    ##### HANDLE TEXTBOXES #####
    for tb in app.textboxes:
        tb.handleKey(app,key)
    
    for menu in app.menus:
         menu.handleKey(app,key)
  

def onKeyHold(app,keys):
    #### textboxes ####
    ### HANDLES HOLDING BACKSPACE ####
    if 'backspace' in keys:
            app.isBackspacing = True
            if app.backspaceCounter >= 11:
                app.backspaceCounter = 8
                for tb in app.textboxes:
                        tb.handleKey(app,'backspace')

def onKeyRelease(app,key):
     ### HANDLES HOLDING BACKSPACE
     if key == 'backspace':
          app.isBackspacing = False
          app.backspaceCounter = 0
            

def onMouseMove(app,mouseX,mouseY):
    app.x,app.y=mouseX,mouseY
    ##### CHECK HOVERS #####
    for tb in app.textboxes:    ## textboxes
        tb.handleHover(app,mouseX,mouseY)
    
    for menu in app.menus:      ## menus
        menu.handleHover(app,mouseX,mouseY)

def onMousePress(app,mouseX,mouseY):
    ##### HANDLE TEXTBOXES ####
    for tb in app.textboxes:   ## textboxes
        if tb.checkOverlap(app,mouseX,mouseY):
            tb.opened = True

    for menu in app.menus:     ## menus
         if menu.checkOverlap(app,mouseX,mouseY):
              menu.opened = True

def onStep(app):
    if app.isBackspacing: app.backspaceCounter += 1


ctypes.windll.shcore.SetProcessDpiAwareness(2)
runApp(width=1920//2, height=1080//2)
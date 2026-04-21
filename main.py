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
import google.genai as genai


def onAppStart(app):
    load_dotenv()

    app.isBackspacing = False
    app.backspaceCounter = 0

    #### coords stuff
    app.x,app.y = 0,0

    ##### MAKE MENUS AND TBS HERE ####
    fnInputMenu = Menu(app,'Manage Functions',cx=150,cy=100,
                       width=app.width*0.2,height=app.height*0.1)

    cx,cy = app.width//2, app.height//2
    w,h = app.width*0.7, app.height*0.6
    padding = min(w,h) * 0.05
    gap = padding
    innerW, innerH = w-2*padding, h-2*padding
    titleH = padding * 1.25
    boxH = innerH - titleH - gap
    boxCY = cy + (titleH + gap) / 2
    halfW = (innerW - gap) / 2
    leftCX = cx - gap/2 - halfW/2
    leftTitleCY = boxCY - boxH*0.45
    fnInputBox = Textbox(app, 'Input New Function',
                         leftCX, leftTitleCY*1.2, halfW*0.8, boxH*0.15)
    fnInputMenu.internalBoxes['fnInputBox'] = fnInputBox

    app.functions = {}
    app.textboxes = {}
    app.menus = {'fnInputMenu':fnInputMenu}

def redrawAll(app):
    # draw title
    drawLabel('Matplotlib GUI',app.width//2,app.height*0.1,size=16,bold=True)
    drawLabel(f'x:{app.x}, y:{app.y}',app.width*0.945,app.height*0.96,size=12)
    drawLabel(f'relX:{pythonRound(app.x/app.width,3)}, relY:{pythonRound(app.y/app.height,3)}',
              app.width*0.93,app.height*0.98)

    ##### NEW MENU & TEXTBOX HANDLER #####
    for menuKey in app.menus:
        menu = app.menus[menuKey]
        if menuKey == 'fnInputMenu':
             drawFunctionInputMenu(app)
             continue
        elif menu.opened:
              menu.drawOpenedMenu(app)
              for boxKey in menu.internalBoxes:
                box = menu.internalBoxes[boxKey]
                if box.opened: box.drawOpenedBox(app)
                else: box.drawClickable(app)

                   


def onKeyPress(app,key):
    ##### HANDLE TEXTBOXES #####
    hasBeenHandled = False
    for boxKey in app.textboxes:
        tb = app.textboxes[boxKey]
        if tb.opened:
            tb.handleKey(app,key)
            hasBeenHandled = True
    
    if not hasBeenHandled:
        for menuKey in app.menus:
            menu = app.menus[menuKey]
            if menu.opened:
                for boxKey in menu.internalBoxes:
                    box = menu.internalBoxes[boxKey]
                    if box.opened and not hasBeenHandled:
                        box.handleKey(app,key)
                        hasBeenHandled = True
            if not hasBeenHandled: menu.handleKey(app,key)
  

def onKeyHold(app,keys):
    #### textboxes ####
    ### HANDLES HOLDING BACKSPACE ####
    if 'backspace' in keys:
            app.isBackspacing = True
            if app.backspaceCounter >= 11:
                app.backspaceCounter = 8
                for key in app.textboxes:
                        tb = app.textboxes[key]
                        tb.handleKey(app,'backspace')

def onKeyRelease(app,key):
     ### HANDLES HOLDING BACKSPACE
     if key == 'backspace':
          app.isBackspacing = False
          app.backspaceCounter = 0
            

def onMouseMove(app,mouseX,mouseY):
    app.x,app.y=mouseX,mouseY
    ##### CHECK HOVERS GENERAL #####
    for key in app.textboxes:    ## textboxes
        tb = app.textboxes[key]
        tb.handleHover(app,mouseX,mouseY)
    
    for key in app.menus:
        menu = app.menus[key]
        menu.handleHover(app,mouseX,mouseY)
        if menu.opened:
            for boxKey in menu.internalBoxes:
                menu.internalBoxes[boxKey].handleHover(app,mouseX,mouseY)
    


def onMousePress(app,mouseX,mouseY):
    ##### HANDLE TEXTBOXES ####
    for key in app.textboxes:   ## textboxes
        tb = app.textboxes[key]
        if tb.checkOverlap(app,mouseX,mouseY):
            tb.opened = True

    for key in app.menus:
        menu = app.menus[key]
        if menu.opened:
            for boxKey in menu.internalBoxes:
                box = menu.internalBoxes[boxKey]
                if box.checkOverlap(app,mouseX,mouseY):
                    box.opened = True
        elif menu.checkOverlap(app,mouseX,mouseY):
            menu.opened = True

def onStep(app):
    if app.isBackspacing: app.backspaceCounter += 1


ctypes.windll.shcore.SetProcessDpiAwareness(2)
runApp(width=1920//2, height=1080//2)
from cmu_graphics import *
from structures import *
from utils import *
import matplotlib as plt
import copy
import threading
import numpy as np
import os
from dotenv import load_dotenv
import ctypes
import math
import google.genai as genai


def onAppStart(app):
    load_dotenv()
    # client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    # for model in client.models.list():
    #     print(model.name)
    app.isBackspacing = False
    app.backspaceCounter = 0
    app.cursorStep = 0
    app.isParsing = False

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
                         leftCX, leftTitleCY*1.2, halfW*0.8, boxH*0.15,
                         openLabel='Enter your function in terms of the desired variables.')
    fnInputMenu.internalBoxes['fnInputBox'] = fnInputBox
    app.currMenu = 'main'
    app.functions = {}
    app.textboxes = {}
    app.menus = {'fnInputMenu':fnInputMenu}
    app.funcMenus = {}

def redrawAll(app):
    drawLabel(f'x:{app.x}, y:{app.y}',app.width*0.945,app.height*0.96,size=12)
    drawLabel(f'relX:{pythonRound(app.x/app.width,3)}, relY:{pythonRound(app.y/app.height,3)}',
              app.width*0.93,app.height*0.98)
    # draw title
    if app.currMenu == 'main':
        drawLabel('Matplotlib GUI',app.width//2,app.height*0.1,size=16,bold=True)
        app.menus['fnInputMenu'].drawClickable(app)

    if app.currMenu == 'fnInputMenu':
        drawFunctionInputMenu(app)
        drawClosedFuncMenus(app)  ### NOT WORKING?
        fnInputBox = app.menus['fnInputMenu'].internalBoxes['fnInputBox']
        if fnInputBox.opened:
            fnInputBox.drawOpenedBox(app,fnInputBox.text)
        else:
            app.menus['fnInputMenu'].internalBoxes['fnInputBox'].drawClickable(app)

    if app.currMenu == 'funcMenu':
        for key in app.funcMenus:
            funcMenu = app.funcMenus[key]
            if funcMenu.opened:
                funcMenu.drawOpenedMenu(app)

    if app.isParsing:
        drawRect(app.width//2, app.height//2, app.width*0.25, app.height*0.12,
                 align='center', fill='white', border='black', borderWidth=2)
        drawLabel('Parsing...', app.width//2, app.height//2, size=18, bold=True)

def onKeyPress(app,key):
    if app.currMenu == 'main':
        pass

    if app.currMenu == 'fnInputMenu':
        fnInputBox = app.menus['fnInputMenu'].internalBoxes['fnInputBox']
        if fnInputBox.opened:
            fnInputBox.handleKey(app,key)
            if key == 'enter':
                handleFnInputBox(app)
        elif key == 'escape':
            app.currMenu = 'main'
            app.menus['fnInputMenu'].opened = False

    if app.currMenu == 'funcMenu':
        handled = False
        for funcMenuKey in app.funcMenus:
            funcMenu = app.funcMenus[funcMenuKey]
            if funcMenu.opened:
                if funcMenu.relableBox.opened and not handled:
                    funcMenu.relableBox.handleKey(app,key)
                    handled = True 
                if funcMenu.colorMenu.opened and not handled:
                    funcMenu.colorMenu.handleKey(app,key)
                    handled = True
                else:
                    funcMenu.handleKey(app,key)
  

def onKeyHold(app,keys):
    ### HANDLES HOLDING BACKSPACE ####
    if 'backspace' in keys:
            app.isBackspacing = True
            if app.backspaceCounter >= 11:
                app.backspaceCounter = 8
                if app.menus['fnInputMenu'].internalBoxes.fnInputBox.opened:
                    app.menus['fnInputMenu'].internalBoxes.fnInputBox.handleKey(app,'backspace')
                for funcMenuKey in app.funcMenus:
                    funcMenu = app.funcMenus[funcMenuKey]
                    if funcMenu.opened and funcMenu.relableBox.opened:
                        funcMenu.relableBox.handleKey(app,'backspace')

def onKeyRelease(app,key):
     ### HANDLES HOLDING BACKSPACE
     if key == 'backspace':
          app.isBackspacing = False
          app.backspaceCounter = 0
            

def onMouseMove(app,mouseX,mouseY):
    app.x,app.y=mouseX,mouseY

    if app.currMenu == 'main':
        app.menus['fnInputMenu'].handleHover(app,mouseX,mouseY)

    if app.currMenu == 'fnInputMenu':
        fnInputBox = app.menus['fnInputMenu'].internalBoxes['fnInputBox']
        fnInputBox.handleHover(app,mouseX,mouseY)
        for menuKey in app.funcMenus:
            funcMenu = app.funcMenus[menuKey]
            funcMenu.handleHover(app,mouseX,mouseY)
    
    if app.currMenu == 'funcMenu':
        for key in app.funcMenus:
            funcMenu = app.funcMenus[key]
            if funcMenu.opened:
                funcMenu.handleHover(app,mouseX,mouseY)

    


def onMousePress(app,mouseX,mouseY):
    handled = False
    
    if app.currMenu == 'main':
        if app.menus['fnInputMenu'].checkOverlap(app,mouseX,mouseY):
            app.menus['fnInputMenu'].opened = True
            app.currMenu = 'fnInputMenu'
    
    elif app.currMenu == 'fnInputMenu':
        fnInputBox = app.menus['fnInputMenu'].internalBoxes['fnInputBox']
        if fnInputBox.checkOverlap(app,mouseX,mouseY): ## check the new function box
            fnInputBox.opened = True
        for funcMenuKey in app.funcMenus:              ## check all the function option menus
            funcMenu = app.funcMenus[funcMenuKey]
            if funcMenu.checkOverlap(app,mouseX,mouseY):
                funcMenu.opened = True
                app.currMenu = 'funcMenu'
                handled = True
    
    elif app.currMenu == 'funcMenu' and not handled:
        for key in app.funcMenus:
            funcMenu = app.funcMenus[key]
            if funcMenu.opened:
                    if funcMenu.relableBox.opened:
                        funcMenu.relableBox.handleClick(app,mouseX,mouseY)
                    elif funcMenu.colorMenu.opened:
                        funcMenu.colorMenu.handleClick(app,mouseX,mouseY)
                    else:
                        funcMenu.relableBox.handleClick(app,mouseX,mouseY)
                        funcMenu.colorMenu.handleClick(app,mouseX,mouseY)
                
    

def onStep(app):
    if app.isBackspacing: app.backspaceCounter += 1
    app.cursorStep = (app.cursorStep + 1) % 30


ctypes.windll.shcore.SetProcessDpiAwareness(2)
runApp(width=1920//2, height=1080//2)
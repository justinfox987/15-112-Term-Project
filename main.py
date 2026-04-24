import importlib, sys
for mod in ['utils', 'structures']:
    if mod in sys.modules:
        importlib.reload(sys.modules[mod])
from cmu_graphics import *
from structures import *
from utils import *
import copy
import threading
import numpy as np
import os
from dotenv import load_dotenv
import ctypes
import math
import google.genai as genai


#### vast majority of main is written by me, think 85/15 split

def onAppStart(app):
    load_dotenv()
    # client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    # for model in client.models.list():
    #     print(model.name)
    app.isBackspacing = False
    app.backspaceCounter = 0
    app.cursorStep = 0
    app.isParsing = False
    app.parseError = False
    app.isPlotting = False
    app.plotReady = False
    app.plotFile = None
    app.plotIsGif = False
    app.plotVersion = 0

    #### coords stuff
    app.x,app.y = 0,0

    ##### MAKE MENUS AND TBS HERE ####
    fnInputMenu = Menu(app,'Manage Functions',app.width*0.25,app.height*0.4,
                       app.width*0.4,app.height*0.35,fontSize=36)
    varEditMenu = Menu(app,'Manage Variables',app.width*0.25,app.height*0.8,
                       app.width*0.4,app.height*0.35,fontSize=36)
    graderMenu = Menu(app, 'Grader Menu',app.width*0.9,
                         app.height*0.9,app.width*0.15,app.height*0.05,fontSize=16)

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
                         leftCX, leftTitleCY+boxH*0.3, halfW*0.8, boxH*0.2,
                         openLabel='Enter your function in terms of the desired variables.')
    fnRemoveBox = Textbox(app,'Remove Function',leftCX,leftTitleCY+boxH*0.6,halfW*0.8,
                          boxH*0.2,openLabel='Enter the label of the function you wish to remove')
    fnInputMenu.internalBoxes['fnInputBox'] = fnInputBox
    fnInputMenu.internalBoxes['fnRemoveBox'] = fnRemoveBox

    autoAddFn2DBox = Textbox(app,'Auto-add 2D Functions',app.width*0.5,app.height*0.3,app.width*0.2,
                                  app.height*0.13)
    autoAddFn3DBox = Textbox(app,'Auto-add 3D Functions',app.width*0.5,app.height*0.45,app.width*0.2,
                            app.height*0.13)
    autoAddFnAnimated = Textbox(app,'Auto-add animated Functions',app.width*0.5,app.height*0.6,
                                app.width*0.2,app.height*0.13)
    autoSetVarsBox = Textbox(app,'Auto-set variables',app.width*0.5,app.height*0.75,app.width*0.2,
                             app.height*0.13)
    graderMenu.internalBoxes['autoAddFn2D'] = autoAddFn2DBox
    graderMenu.internalBoxes['autoaddFn3D'] = autoAddFn3DBox
    graderMenu.internalBoxes['autoAddFnAnimated'] = autoAddFnAnimated
    graderMenu.internalBoxes['autoSetVars'] = autoSetVarsBox


    app.refreshButton = Textbox(app, 'Refresh Plot', app.width*0.75, app.height*0.90,
                             app.width*0.2, app.height*0.05)
    app.outputMin = InlineTextbox(app, 'auto', 0, 0, 0, 0, fontSize=18)
    app.outputMax = InlineTextbox(app, 'auto', 0, 0, 0, 0, fontSize=18)
    app.currMenu = 'main'
    app.functions = {}
    app.vars = {}
    app.textboxes = {}
    app.menus = {'fnInputMenu':fnInputMenu,'varEditMenu':varEditMenu,'graderMenu':graderMenu}
    app.funcMenus = {}

def redrawAll(app):
    drawLabel(f'x:{app.x}, y:{app.y}',app.width*0.945,app.height*0.96,size=12)
    drawLabel(f'relX:{pythonRound(app.x/app.width,3)}, relY:{pythonRound(app.y/app.height,3)}',
              app.width*0.93,app.height*0.98)
    # draw title
    if app.currMenu == 'main':
        drawLabel('Matplotlib GUI',app.width//2,app.height*0.1,size=24,bold=True)
        app.menus['fnInputMenu'].drawClickable(app)
        app.menus['varEditMenu'].drawClickable(app)
        app.refreshButton.cx = app.width*0.75
        app.refreshButton.cy = app.height*0.9
        app.refreshButton.width = app.width*0.2
        app.refreshButton.height = app.height*0.05
        app.refreshButton.drawClickable(app)
        graderMenu = app.menus['graderMenu']
        graderMenu.cx = app.width*0.9
        graderMenu.cy = app.height*0.9
        graderMenu.width = app.width*0.09
        graderMenu.height = app.height*0.05
        graderMenu.drawClickable(app)
    if app.plotReady:
        drawImage(app.plotFile, app.width*0.75, app.height*0.5,
                align='center', width=app.width*0.45, height=app.height*0.7)

    if app.currMenu == 'fnInputMenu':
        drawFunctionInputMenu(app)
        drawClosedFuncMenus(app)
        fnInputBox = app.menus['fnInputMenu'].internalBoxes['fnInputBox']
        fnRemoveBox = app.menus['fnInputMenu'].internalBoxes['fnRemoveBox']
        if fnInputBox.opened:
            fnInputBox.drawOpenedBox(app,fnInputBox.text)
        elif fnRemoveBox.opened:
            fnRemoveBox.drawOpenedBox(app,fnRemoveBox.text)
        elif not fnInputBox.opened and not fnRemoveBox.opened:
            fnInputBox.drawClickable(app)
            fnRemoveBox.drawClickable(app)
        
    if app.currMenu == 'funcMenu':
        for key in app.funcMenus:
            funcMenu = app.funcMenus[key]
            if funcMenu.opened:
                funcMenu.drawOpenedMenu(app)
    
    if app.currMenu == 'varEditMenu':
        drawVarEditMenu(app)

    if app.currMenu == 'graderMenu':
        drawGraderMenu(app)

    if app.isParsing:
        drawRect(app.width//2, app.height//2, app.width*0.25, app.height*0.12,
                 align='center', fill='white', border='black', borderWidth=2)
        drawLabel('Parsing...', app.width//2, app.height//2, size=18, bold=True)
    if app.parseError:
        drawRect(app.width//2, app.height//2, app.width*0.5, app.height*0.15,
                 align='center', fill='white', border='red', borderWidth=2)
        drawLabel('Parse failed: input was not a valid function.', app.width//2, app.height//2, size=18, bold=True)
    if app.isPlotting:
        drawRect(app.width//2, app.height//2, app.width*0.25, app.height*0.12,
                 align='center', fill='white', border='black', borderWidth=2)
        drawLabel('Generating plot...', app.width//2, app.height//2, size=18, bold=True)

def onKeyPress(app,key):
    app.parseError = False
    if app.currMenu == 'main':
        pass

    if app.currMenu == 'fnInputMenu':
        fnInputBox = app.menus['fnInputMenu'].internalBoxes['fnInputBox']
        fnRemoveBox = app.menus['fnInputMenu'].internalBoxes['fnRemoveBox']
        if fnInputBox.opened:
            fnInputBox.handleKey(app,key)
            if key == 'enter':
                handleFnInputBox(app)
        elif fnRemoveBox.opened:
            fnRemoveBox.handleKey(app,key)
            if key == 'enter':
                handleFnRemoveBox(app)
        elif key == 'escape':
            app.currMenu = 'main'
            app.menus['fnInputMenu'].opened = False

    if app.currMenu == 'funcMenu':
        for funcMenuKey in app.funcMenus:
            funcMenu = app.funcMenus[funcMenuKey]
            if funcMenu.opened:
                funcMenu.handleKey(app,key)
    
    if app.currMenu == 'varEditMenu':
        openTextbox = None
        textboxIsOpen = False
        openDropdown = None
        dropdownIsOpen = False
        for box in [app.outputMin, app.outputMax]:
            if box.opened:
                openTextbox = box
                textboxIsOpen = True
        for data in app.vars.values():
            minBox, maxBox, dropdown, framesBox = data
            if minBox.opened:
                openTextbox = minBox
                textboxIsOpen = True
            if maxBox.opened:
                openTextbox = maxBox
                textboxIsOpen = True
            if framesBox.opened:
                openTextbox = framesBox
                textboxIsOpen = True
            if dropdown.opened:
                openDropdown = dropdown
                dropdownIsOpen = True
        if textboxIsOpen:
            openTextbox.handleKey(app, key)
        elif dropdownIsOpen and key == 'escape':
            openDropdown.opened = False
        elif key == 'escape':
            app.menus['varEditMenu'].opened = False
            app.currMenu = 'main'

    if app.currMenu == 'graderMenu':
        if key == 'escape':
            app.currMenu = 'main'
            app.menus['graderMenu'].opened = False

def onKeyHold(app,keys):
    ### HANDLES HOLDING BACKSPACE ####
    if 'backspace' in keys:
            app.isBackspacing = True
            if app.backspaceCounter >= 11:
                app.backspaceCounter = 8
                if app.menus['fnInputMenu'].internalBoxes['fnInputBox'].opened:
                    app.menus['fnInputMenu'].internalBoxes['fnInputBox'].handleKey(app,'backspace')
                if app.menus['fnInputMenu'].internalBoxes['fnRemoveBox'].opened:
                    app.menus['fnInputMenu'].internalBoxes['fnRemoveBox'].handleKey(app,'backspace')
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
        app.menus['varEditMenu'].handleHover(app,mouseX,mouseY)
        app.refreshButton.handleHover(app, mouseX, mouseY)
        app.menus['graderMenu'].handleHover(app,mouseX,mouseY)

    if app.currMenu == 'fnInputMenu':
        fnInputBox = app.menus['fnInputMenu'].internalBoxes['fnInputBox']
        fnRemoveBox = app.menus['fnInputMenu'].internalBoxes['fnRemoveBox']
        fnInputBox.handleHover(app,mouseX,mouseY)
        fnRemoveBox.handleHover(app,mouseX,mouseY)
        for menuKey in app.funcMenus:
            funcMenu = app.funcMenus[menuKey]
            funcMenu.handleHover(app,mouseX,mouseY)
    
    if app.currMenu == 'funcMenu':
        for key in app.funcMenus:
            funcMenu = app.funcMenus[key]
            if funcMenu.opened:
                funcMenu.handleHover(app,mouseX,mouseY)

    if app.currMenu == 'varEditMenu':
        app.outputMin.handleHover(app, mouseX, mouseY)
        app.outputMax.handleHover(app, mouseX, mouseY)
        for data in app.vars.values():
            minBox, maxBox, dropdown, framesBox = data
            minBox.handleHover(app, mouseX, mouseY)
            maxBox.handleHover(app, mouseX, mouseY)
            dropdown.handleHover(app, mouseX, mouseY)
            framesBox.handleHover(app, mouseX, mouseY)
    
    if app.currMenu == 'graderMenu':
        for key in app.menus['graderMenu'].internalBoxes:
            box = app.menus['graderMenu'].internalBoxes[key]
            box.handleHover(app,mouseX,mouseY)

def onMousePress(app,mouseX,mouseY):
    handled = False
    
    if app.currMenu == 'main':
        if app.menus['fnInputMenu'].checkOverlap(app,mouseX,mouseY):
            app.menus['fnInputMenu'].opened = True
            app.currMenu = 'fnInputMenu'
        if app.menus['varEditMenu'].checkOverlap(app,mouseX,mouseY):
            app.menus['varEditMenu'].opened = True
            refreshVars(app)
            app.currMenu = 'varEditMenu'
        if app.refreshButton.checkOverlap(app, mouseX, mouseY):
            triggerRefreshPlot(app)
        if app.menus['graderMenu'].checkOverlap(app,mouseX,mouseY):
            app.menus['graderMenu'].opened = True
            app.currMenu = 'graderMenu'

    
    elif app.currMenu == 'fnInputMenu':
        fnInputBox = app.menus['fnInputMenu'].internalBoxes['fnInputBox']
        fnRemoveBox = app.menus['fnInputMenu'].internalBoxes['fnRemoveBox']
        if fnInputBox.checkOverlap(app,mouseX,mouseY): ## check the new function box
            fnInputBox.opened = True
        elif fnRemoveBox.checkOverlap(app,mouseX,mouseY):
            fnRemoveBox.opened = True
        for funcMenuKey in app.funcMenus:              ## check all the function option menus
            funcMenu = app.funcMenus[funcMenuKey]
            if funcMenu.checkOverlap(app,mouseX,mouseY):
                funcMenu.opened = True
                app.currMenu = 'funcMenu'
                handled = True
    
    elif app.currMenu == 'varEditMenu':
        openDropdown = None
        dropdownIsOpen = False
        openTextbox = None
        textboxIsOpen = False
        for box in [app.outputMin, app.outputMax]:
            if box.opened:
                openTextbox = box
                textboxIsOpen = True
        for data in app.vars.values():
            minBox, maxBox, dropdown, framesBox = data
            if dropdown.opened:
                openDropdown = dropdown
                dropdownIsOpen = True
            if minBox.opened:
                openTextbox = minBox
                textboxIsOpen = True
            if maxBox.opened:
                openTextbox = maxBox
                textboxIsOpen = True
            if framesBox.opened:
                openTextbox = framesBox
                textboxIsOpen = True
        if dropdownIsOpen:
            openDropdown.handleClick(app, mouseX, mouseY)
        elif textboxIsOpen:
            openTextbox.handleClick(app, mouseX, mouseY)
        else:
            app.outputMin.handleClick(app, mouseX, mouseY)
            app.outputMax.handleClick(app, mouseX, mouseY)
            for data in app.vars.values():
                minBox, maxBox, dropdown, framesBox = data
                dropdown.handleClick(app, mouseX, mouseY)
                minBox.handleClick(app, mouseX, mouseY)
                maxBox.handleClick(app, mouseX, mouseY)
                framesBox.handleClick(app, mouseX, mouseY)

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

    elif app.currMenu == 'graderMenu':
        graderMenu = app.menus['graderMenu']
        if graderMenu.internalBoxes['autoAddFn2D'].checkOverlap(app,mouseX,mouseY):
            func1 = Function(app,'f(x)','2*x**2 + 4',{'x':'auto'},color='blue')
            func2 = Function(app,'g(x)','np.sin(x)/x',{'x':'auto'},color='green')
            app.functions = {'func1':func1,'func2':func2}
            refreshVars(app)
        if graderMenu.internalBoxes['autoaddFn3D'].checkOverlap(app,mouseX,mouseY):
            func1 = Function(app,'f(x,y)','2*x**2 + 4*y**2',{'x':'auto','y':'auto'},
                             color='blue')
            func2 = Function(app,'g(x,y)','10*np.sin((x**2 + y**2)/(2*np.pi))',
                             {'x':'auto','y':'auto'},color='green')
            app.functions = {'func1':func1,'func2':func2}
            refreshVars(app)
        if graderMenu.internalBoxes['autoAddFnAnimated'].checkOverlap(app,mouseX,mouseY):
            func = Function(app,'f(x,t)','np.sin(x*t)',{'x':'auto','t':'auto'},color='blue')
            app.functions = {'func1':func}
        if graderMenu.internalBoxes['autoSetVars'].checkOverlap(app,mouseX,mouseY):
            refreshVars(app)
            #### this part claude did
            roleMap = {'x': 'X-Axis', 'y': 'Y-Axis', 't': 'Animate', 'c': 'Constant'}
            rangeMap = {'x': ('-10', '10'), 'y': ('-10', '10'), 't': ('0', '10'), 'c': ('1', '1')}
            for var, data in app.vars.items():
                minBox, maxBox, dropdown, framesBox = data
                if var in roleMap:
                    dropdown.selected = roleMap[var]
                if var in rangeMap:
                    minBox.label = rangeMap[var][0]
                    maxBox.label = rangeMap[var][1]


                
def onStep(app):
    import utils
    if app.isBackspacing: app.backspaceCounter += 1
    app.cursorStep = (app.cursorStep + 1) % 30
    if app.isPlotting and app.plotReady:
        app.isPlotting = False
    result = utils._parseResult[0]
    if result is not None:
        utils._parseResult[0] = None
        app.isParsing = False
        if result == 'fail':
            app.parseError = True
        else:
            app.functions[f'function{len(app.functions)}'] = result

ctypes.windll.shcore.SetProcessDpiAwareness(2)
runApp(width=1920//2, height=1080//2)
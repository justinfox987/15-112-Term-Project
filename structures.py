from cmu_graphics import *

class Textbox:
    def __init__(self, app, label, cx, cy, width, height, openLabel=None):
        self.label = label
        self.openLabel = openLabel if openLabel is not None else label
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.opened = False
        self.clickableColor = 'lightgray'
        self.prevInputs = []
        self.totInputs = 0

        self.text = ''

    def drawClickable(self,app):
        from utils import drawText
        if not self.opened:
            drawRect(self.cx, self.cy, self.width, self.height,
                      fill=self.clickableColor,align='center', border='black',borderWidth=3)
            drawText(app,self.cx,self.cy,self.width*0.9,self.height*0.9,self.label,fontSize=16,bold=True)

    def checkOverlap(self,app, mouseX, mouseY):
        if ((self.cx - self.width*0.5 <= mouseX <= self.cx + self.width*0.5)
             and (self.cy - self.height*0.5 <= mouseY <= self.cy + self.height*0.5)):
            return True
        else: return False

    def handleHover(self,app,mouseX,mouseY):
        if self.checkOverlap(app,mouseX,mouseY) and not self.opened:
            self.clickableColor = 'lightblue'
        else:
            self.clickableColor = 'lightgray'
    
    def drawOpenedBox(self,app,userInput):
        from utils import drawText
        if self.opened:
            rectCX,rectCY = app.width*0.5,app.height*0.5  ## MIDDLE OF SCREEN
            rectW,rectH = app.width*0.25,app.height*0.25    ## width and height
            drawRect(rectCX,rectCY,rectW,rectH,
                    border='black',borderWidth=2,
                    align='center', fill='white')
            titleH = rectH * 0.35
            inputH = rectH * 0.55
            titleCY = rectCY - rectH/2 + titleH/2
            inputCY = rectCY + rectH/2 - inputH/2
            drawText(app,rectCX,titleCY,rectW*0.85,titleH,self.openLabel,fontSize=14,bold=True)
            cursor = '|' if app.cursorStep < 15 else ''
            drawText(app,rectCX,inputCY,rectW*0.85,inputH,userInput + cursor)
            
    def handleKey(self,app,key): ###### WRITTEN BY CLAUDE, FIXED BY ME
        if self.opened:
            if key == 'backspace':
                self.text = self.text[:-1]
            elif key == 'enter':    ######## HANDLE SENDING IT TO A FUNCTION
                self.prevInputs.append(self.text)
                self.totInputs += 1
                self.text = ''
                self.opened = False
            elif key == 'space':
                self.text += ' '
            elif key == 'escape':
                self.text = ''
                self.opened = False
            else:
                self.text += key
    
    def handleClick(self,app,mouseX,mouseY):
        if not self.opened and self.checkOverlap(app,mouseX,mouseY):
            self.opened = True


class Menu(Textbox):
    def __init__(self,app,label,cx,cy,width,height,internalBoxes=None):
        super().__init__(app,label,cx,cy,width,height)
        self.internalBoxes = internalBoxes if internalBoxes is not None else {}

    def handleKey(self,app,key):
        if self.opened:
            if key == 'escape':
                self.opened = False

    def drawOpenedMenu(self, app):
        if self.opened:
            cx,cy = app.width//2,app.height//2
            w,h = app.width*0.7, app.height*0.6
            drawRect(cx,cy,w,h,align='center',fill='lightgray' ### MAIN RECT
                ,border='black',borderWidth=2,opacity=75)


class Function:
    def __init__(self,app,label,pythonicInput,vars={},color='black'):
        self.label = label
        self.pythonicInput = pythonicInput
        self.vars = vars
        self.color = color

class FuncMenu(Menu):
    def __init__(self,app,cx,cy,width,height,function):
        super().__init__(app,function.label,cx,cy,width,height)
        self.label = function.label
        self.opened = False
        self.function = function
        self.internalOptions = {'color':False,'label':False}
        self.relableBox = Textbox(app,'Change Label',app.width*0.625,app.height*0.5,
                                  app.width*0.18,app.height*0.08,
                                  openLabel = 'Enter a new label for your function')
        self.colorMenu = ColorMenu(app.width*0.375,app.height*0.5,
                                   app.height*0.04,self.function.color)
    
    def drawOpenedMenu(self,app):
        cx,cy = app.width//2,app.height//2
        w,h = app.width*0.5,app.height*0.3
        drawRect(cx,cy,w,h,align='center',fill='lightgray',border='black',
                 borderWidth=2)
        drawLabel('Function Options',cx,cy - h*0.4,bold=True,size=16)
        ##### function details
        ## COLOR CIRCLE
        if self.colorMenu.opened:
            self.colorMenu.drawOpened(app)
            return
        else:
            self.colorMenu.drawClickable(app)
            self.function.color = self.colorMenu.currColor

        ## RE-LABLE
        if self.relableBox.opened:
            self.relableBox.drawOpenedBox(app,self.relableBox.text)
            return
        else:
            self.relableBox.drawClickable(app)

    def handleKey(self,app,key):
        if self.internalOptions['label']:
            self.relableBox.handleKey(app,key)
            if key == 'enter':
                newLabel = self.relableBox.prevInputs[-1]
                self.relableBox.prevInputs.pop()
                self.function.label = newLabel
        if key == 'escape':
            self.opened = False
            app.currMenu = 'fnInputMenu'
    
    def handleClick(self,app,mouseX,mouseY):
        if self.checkOverlap(app,mouseX,mouseY):
            self.opened = True
            app.currMenu = 'funcMenu'
    
    def handleHover(self,app,mouseX,mouseY):
        if self.opened:
            self.colorMenu.handleHover(app,mouseX,mouseY)
            self.relableBox.handleHover(app,mouseX,mouseY)
        else:
            if self.checkOverlap(app,mouseX,mouseY):
                self.clickableColor = 'lightblue'
            else:
                self.clickableColor = 'lightgray'
            
        
class ColorMenu:
    def __init__(self,cx,cy,radius,currColor):
        self.opened = False
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.currColor = currColor
        self.opacity = 75
        self.colorOptions = [['red',0,0],['orange',0,0],['yellow',0,0],
                             ['green',0,0],['blue',0,0],['purple',0,0],
                             ['black',0,0],['gray',0,0]]
                            
    
    def checkOverlap(self,app,mouseX,mouseY):
        distance = ((self.cx-mouseX)**2 + (self.cy-mouseY)**2)**0.5
        return distance <= self.radius

    def handleHover(self,app,mouseX,mouseY):
        if not self.opened:
            if self.checkOverlap(app,mouseX,mouseY):
                self.opacity = 100
            else:
                self.opacity = 75
    
    def drawClickable(self,app):
        drawCircle(self.cx,self.cy,self.radius,fill=self.currColor,
                   border='black',opacity=self.opacity)
    
    def drawOpened(self,app):
        cx,cy = app.width//2,app.height//2
        w,h = app.width*0.3,app.height*0.22
        titleH = h * 0.3
        padding = 0.025*app.width
        distBtwnDots = (w-2*padding)/len(self.colorOptions)
        rad = distBtwnDots*0.4
        drawRect(cx,cy,w,h,fill='white',border='black',align='center')
        drawLabel('Choose a new color',cx,cy - h/2 + titleH/2,size=14,bold=True)
        dotsY = cy - h/2 + titleH + (h - titleH)/2
        for i in range(len(self.colorOptions)):
            self.colorOptions[i][1] = cx - w/2 + padding + distBtwnDots*(i + 0.5)
            self.colorOptions[i][2] = dotsY
            drawCircle(self.colorOptions[i][1],self.colorOptions[i][2],
                       rad,fill=self.colorOptions[i][0],border='black')
    
    def handleKey(self,app,key):
        if key == 'escape' or key == 'enter':
            self.opened = False
    
    def handleClick(self,app,mouseX,mouseY):
        w = app.width*0.3
        padding = 0.025*app.width
        distBtwnDots = (w-2*padding)/len(self.colorOptions)
        rad = distBtwnDots*0.5
        if not self.opened and self.checkOverlap(app,mouseX,mouseY):
            self.opened = True
        elif self.opened:
            for i in range(len(self.colorOptions)):
                color = self.colorOptions[i][0]
                cx = self.colorOptions[i][1]
                cy = self.colorOptions[i][2]
                distance = ((cx-mouseX)**2 + (cy-mouseY)**2)**0.5
                if distance <= rad:
                    self.currColor = color
                    self.opened = False

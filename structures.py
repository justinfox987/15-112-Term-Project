from cmu_graphics import *

class Textbox:
    def __init__(self, app, label, cx, cy, width, height, openLabel=None,fontSize=16):
        self.label = label
        self.openLabel = openLabel if openLabel is not None else label
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.fontSize = fontSize
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
            drawText(app,self.cx,self.cy,self.width*0.9,self.height*0.9,
                     self.label,fontSize=self.fontSize,bold=True)

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
            rectW,rectH = app.width*0.5,app.height*0.5    ## width and height
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
    def __init__(self,app,label,cx,cy,width,height,fontSize=16,internalBoxes=None):
        super().__init__(app,label,cx,cy,width,height,fontSize=fontSize)
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
        self.colorMenu.cx = cx - w*0.25
        self.colorMenu.cy = cy
        self.colorMenu.radius = h*0.15
        self.relableBox.cx = cx + w*0.25
        self.relableBox.cy = cy
        self.relableBox.width = w*0.35
        self.relableBox.height = h*0.25
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
        if self.relableBox.opened:
            self.relableBox.handleKey(app,key)
            if key == 'enter':
                newLabel = self.relableBox.prevInputs[-1]
                self.relableBox.prevInputs.pop()
                self.function.label = newLabel
                self.label = newLabel
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

### some claude, used my format and class to write a subclass
class InlineTextbox(Textbox):
    """Textbox that edits in-place rather than opening a modal overlay.
    label acts as the committed value — defaults to 'auto' for matplotlib auto-sizing."""
    def __init__(self, app, label, cx, cy, width, height, fontSize=12):
        super().__init__(app, label, cx, cy, width, height, fontSize=fontSize)

    def drawClickable(self, app):
        from utils import drawText
        fill = 'lightyellow' if self.opened else self.clickableColor
        drawRect(self.cx, self.cy, self.width, self.height,
                 fill=fill, align='center', border='black', borderWidth=2)
        if self.opened:
            cursor = '|' if app.cursorStep < 15 else ''
            displayText = self.text + cursor
        else:
            displayText = self.label
        drawText(app, self.cx, self.cy, self.width * 0.9, self.height * 0.9,
                 displayText, fontSize=self.fontSize)

    def handleKey(self, app, key):
        if not self.opened:
            return
        if key == 'backspace':
            self.text = self.text[:-1]
        elif key == 'enter':
            isAuto = self.text == 'auto'
            isValidFloat = False
            try:
                float(self.text)
                isValidFloat = True
            except ValueError:
                pass
            if isAuto or isValidFloat:
                self.label = self.text
            self.text = ''
            self.opened = False
        elif key == 'escape':
            self.text = ''
            self.opened = False
        elif key == 'space':
            self.text += ' '
        else:
            self.text += key

    def handleClick(self, app, mouseX, mouseY):
        if self.opened and not self.checkOverlap(app, mouseX, mouseY):
            self.text = ''
            self.opened = False
        elif not self.opened and self.checkOverlap(app, mouseX, mouseY):
            self.opened = True

    def drawOpenedBox(self, app, userInput):
        pass  # inline only — no modal overlay

    @property
    def value(self):
        try:
            return float(self.label)
        except ValueError:
            return 'auto'

#### 50/50 claude and me
class Dropdown:
    def __init__(self, app, label, cx, cy, width, height, options, fontSize=16):
        self.label = label
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.options = options  # list of strings
        self.fontSize = fontSize
        self.opened = False
        self.selected = None
        self.clickableColor = 'lightgray'

    def checkOverlap(self, app, mouseX, mouseY):
        return ((self.cx - self.width*0.5 <= mouseX <= self.cx + self.width*0.5)
            and (self.cy - self.height*0.5 <= mouseY <= self.cy + self.height*0.5))

    def checkOptionOverlap(self, app, mouseX, mouseY, i):
        optCY = self.cy + self.height/2 + self.height * (i + 0.5)
        return ((self.cx - self.width*0.5 <= mouseX <= self.cx + self.width*0.5)
            and (optCY - self.height*0.5 <= mouseY <= optCY + self.height*0.5))

    def handleHover(self, app, mouseX, mouseY):
        if self.checkOverlap(app, mouseX, mouseY) and not self.opened:
            self.clickableColor = 'lightblue'
        else:
            self.clickableColor = 'lightgray'

    def drawClickable(self, app):
        from utils import drawText
        drawRect(self.cx, self.cy, self.width, self.height,
                 fill=self.clickableColor, align='center', border='black', borderWidth=3)
        label = self.selected if self.selected is not None else self.label
        drawText(app, self.cx, self.cy, self.width*0.9, self.height*0.9,
                 label, fontSize=self.fontSize, bold=True)

    def drawOpenedDropdown(self, app):
        from utils import drawText
        if self.opened:
            # Draw the main box
            drawRect(self.cx, self.cy, self.width, self.height,
                     fill='lightblue', align='center', border='black', borderWidth=3)
            label = self.selected if self.selected is not None else self.label
            drawText(app, self.cx, self.cy, self.width*0.9, self.height*0.9,
                     label, fontSize=self.fontSize, bold=True)
            # Draw options below
            for i, option in enumerate(self.options):
                optCY = self.cy + self.height/2 + self.height * (i + 0.5)
                drawRect(self.cx, optCY, self.width, self.height,
                         fill='white', align='center', border='black', borderWidth=2)
                drawText(app, self.cx, optCY, self.width*0.9, self.height*0.9,
                         option, fontSize=self.fontSize)

    def handleClick(self, app, mouseX, mouseY):
        if self.opened:
            for i, option in enumerate(self.options):
                if self.checkOptionOverlap(app, mouseX, mouseY, i):
                    self.selected = option
                    self.opened = False
                    return
            # Click outside options closes it
            self.opened = False
        elif self.checkOverlap(app, mouseX, mouseY):
            self.opened = True

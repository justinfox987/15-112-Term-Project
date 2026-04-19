from cmu_graphics import *

class Textbox:
    def __init__(self, app, label, cx, cy, width, height):
        self.label = label
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.opened = False
        self.clickableColor = 'lightgray'

        self.text = ''

    def drawClickable(self,app):
        from utils import drawText
        if not self.opened:
            drawRect(self.cx, self.cy, self.width, self.height, fill=self.clickableColor,align='center')
            drawLabel(self.label,self.cx,self.cy,size=16,bold=True)

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
            rectW,rectH = app.width*0.3,app.height*0.3    ## width and height
            drawRect(rectCX,rectCY,rectW,rectH,           ## draw rect for text to be in
                    border='black',borderWidth=2,
                    align='center', fill='white')
            drawText(app,rectCX,rectCY,rectW,rectH,userInput)
            
    def handleKey(self,app,key): ###### WRITTEN BY CLAUDE, FIXED BY ME
        if self.opened:
            if key == 'backspace':
                self.text = self.text[:-1]
            elif key == 'enter':    ######## HANDLE SENDING IT TO A FUNCTION
                self.opened = False
            elif key == 'space':
                self.text += ' '
            else:
                self.text += key


class Menu(Textbox):
    def __init__(self,app,label,cx,cy,width,height,internalBoxes = []):
        super().__init__(app,label,cx,cy,width,height)
        self.internalBoxes = internalBoxes

    def handleKey(self,app,key):
        if key == 'escape':
            self.opened = False

    def drawOpenedMenu(self, app):
        if self.opened:
            cx,cy = app.width//2,app.height//2
            w,h = app.width*0.7, app.height*0.6
            drawRect(cx,cy,w,h,align='center',fill='white' ### MAIN RECT
                ,border='black',borderWidth=2)
            
            for box in self.internalBoxes:  #### NEED TO HANDLE HOVER MECHANISM
                if box.opened: box.drawOpenedBox(app,box.text)
                else: box.drawClickable(app)
        

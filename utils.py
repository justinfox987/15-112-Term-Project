from cmu_graphics import *
from structures import *
import google.genai as genai
import os

##### CLI ELEMENTS #####


##### drawText() WRITTEN BY CLAUDE ####
def drawText(app, rectCX, rectCY, rectW, rectH, text, fontSize=16,bold=False):
    padding = 0.1
    maxW = rectW * (1 - 2*padding)
    maxH = rectH * (1 - 2*padding)
    textLX = rectCX - rectW*0.5 + rectW*padding
    textLY = rectCY - rectH*0.5 + rectH*padding

    def wrap(text, charsPerLine):
        words = text.split(' ')
        lines, current = [], ''
        for word in words:
            while len(word) > charsPerLine:
                room = charsPerLine - len(current) - (1 if current else 0)
                if room <= 0:
                    lines.append(current)
                    current = ''
                    room = charsPerLine
                lines.append((current + ' ' if current else '') + word[:room])
                word, current = word[room:], ''
            fits = len(current) + len(word) + (1 if current else 0) <= charsPerLine
            if fits:
                current += (' ' if current else '') + word
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    while fontSize > 6:
        charsPerLine = max(1, int(maxW / (fontSize * 0.52)))
        lineHeight = fontSize * 1.4
        lines = wrap(text, charsPerLine)
        if len(lines) * lineHeight <= maxH:
            break
        fontSize -= 1

    align = 'center' if bold else 'left-top'
    x = rectCX if bold else textLX
    y0 = rectCY - (len(lines) - 1) * lineHeight / 2 if bold else textLY
    for i, line in enumerate(lines):
        y = y0 + i * lineHeight
        drawLabel(line, x, y, size=fontSize, align=align, font='Arial', bold=bold)


def drawFunctionInputMenu(app):
     ##### HANDLE MENUS SPECIFIC ####
    fnInputMenu = app.menus['fnInputMenu']
        #### USED CLAUDE TO WRITE PADDING STUFF
    cx,cy = app.width//2, app.height//2
    w,h = app.width*0.7, app.height*0.6
    padding = min(w,h) * 0.05
    gap = padding
    innerW, innerH = w-2*padding, h-2*padding
    titleH = padding * 1.25
    boxH = innerH - titleH - gap
    boxCY = cy + (titleH + gap) / 2
    titleCY = cy - innerH/2 + titleH/2
    halfW = (innerW - gap) / 2
    leftCX  = cx - gap/2 - halfW/2
    rightCX = cx + gap/2 + halfW/2
    leftTitleCX,leftTitleCY = leftCX, (boxCY - boxH*0.45)
    rightTitleCX,rightTitleCY = rightCX, (boxCY - boxH*0.45)

    fnInputMenu.drawOpenedMenu(app)
    drawLabel(fnInputMenu.label, cx, titleCY, size=16, bold=True)
    #LEFT
    drawRect(leftCX,  boxCY, halfW, boxH,
                align='center', border='black', borderWidth=1.5, fill='white')
    drawLabel('Function Options',leftTitleCX,leftTitleCY,size=16,bold=True)
    #RIGHT
    drawRect(rightCX, boxCY, halfW, boxH,
                align='center', border='black', borderWidth=1.5, fill='white')
    drawLabel('Current Functions',rightTitleCX,rightTitleCY,size=16,bold=True)
    fnContentTop = rightTitleCY + gap
    fnContentBottom = boxCY + boxH/2 - gap
    fnContentCY = (fnContentTop + fnContentBottom) / 2
    fnContentH = fnContentBottom - fnContentTop
    makeAndSizeFnMenus(app, rightCX, fnContentCY, halfW*0.85, fnContentH)


def handleFnInputBox(app):
    import threading
    fnInputMenu = app.menus['fnInputMenu']
    fnInputBox = fnInputMenu.internalBoxes['fnInputBox']
    userInput = fnInputBox.prevInputs[-1]
    fnInputBox.prevInputs.pop()
    app.isParsing = True
    def parseAndAdd():
        function = parseFunction(userInput)
        app.functions[f"function{len(app.functions)}"] = function
        app.isParsing = False
    threading.Thread(target=parseAndAdd, daemon=True).start()
            

def parseFunction(userInput):
    print('parsing...')
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    prompt = f"""Convert this math expression into a single Pythonic expression
    using only numpy (as np) functions, in terms of the variables given. Return
    the pythonic function, then a tilde, then the function label, then a tilde,
    then a comma-separated list of variables. For example, a user input of
    'f(x,y) = 2x^2 * 3y^2' should return "'f(x,y)'~2*x**2 * 3*y**2~x,y".
    The user input is included below.
    Input: {userInput}
    """
    response = client.models.generate_content(model='gemma-4-26b-a4b-it', contents=prompt)
    print('done!')
    separatedResponse = response.text.strip().split('~')
    label,pythonFunction,vars = separatedResponse[0],separatedResponse[1],separatedResponse[2]
    varDict = dict()
    for var in vars.split(','):
        varDict[var] = 'auto'
    newFunc = Function(app,label,pythonFunction,varDict)
    return newFunc

def makeAndSizeFnMenus(app,boxCX,boxCY,w,h):
    totFuncs = len(app.functions)
    if totFuncs > 0:
        contentTop = boxCY - h/2
        distBtwnBoxes = h / totFuncs
        fnBoxH, fnBoxW = distBtwnBoxes * 0.9, w
        i = 0
        for functionKey in app.functions:
            function = app.functions[functionKey]
            matchKey = None
            for funcMenuKey in app.funcMenus:
                if app.funcMenus[funcMenuKey].function == function:
                    matchKey = funcMenuKey
            cy = contentTop + distBtwnBoxes/2 + distBtwnBoxes*i
            cx = boxCX
            if matchKey:
                app.funcMenus[matchKey].cx = cx
                app.funcMenus[matchKey].cy = cy
                app.funcMenus[matchKey].height = fnBoxH
                app.funcMenus[matchKey].width = fnBoxW
            else:
                app.funcMenus[function.label] = FuncMenu(app,cx,cy,fnBoxW,fnBoxH,function)
            i += 1

def drawClosedFuncMenus(app):
    for menuKey in app.funcMenus:
        funcMenu = app.funcMenus[menuKey]
        funcMenu.drawClickable(app)
            
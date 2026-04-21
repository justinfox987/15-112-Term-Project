from cmu_graphics import *
from structures import *
import google.genai as genai

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

        ####### HANDLE FUNCTION INPUT MENU
    if fnInputMenu.opened:
        fnInputMenu.drawOpenedMenu(app)
        drawLabel(fnInputMenu.label, cx, titleCY, size=16, bold=True)
        #LEFT
        drawRect(leftCX,  boxCY, halfW, boxH,
                 align='center', border='black', borderWidth=1.5, fill='white')
        drawLabel('Function Options',leftTitleCX,leftTitleCY,size=16,bold=True)
        #RIGHT
        drawRect(rightCX, boxCY, halfW, boxH,
                 align='center', border='black', borderWidth=1.5, fill='white')
        #OPTIONS
        for boxKey in fnInputMenu.internalBoxes:
            box = fnInputMenu.internalBoxes[boxKey]
            box.drawClickable(app)
            box.drawOpenedBox(app,box.text)
    else:
         fnInputMenu.drawClickable(app)

def handleFnInputBox(app):
    fnInputMenu = app.menus['fnInputMenu']
    fnInputBox = fnInputMenu.internalBoxes['fnInputBox']
    for inputKey in fnInputBox.prevInputs:
        if inputKey not in app.functions:
            #### GEMINI API INTERPRETER
            pythonicFunction = parseFunction(fnInputBox.prevInputs[inputKey])
            app.functions[f'function{fnInputBox.totInputs}']


def parseFunction(userInput):
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    prompt = f"""Convert this math expression into a single Pythonic expression 
using only numpy (as np) functions, in terms of the variables given. 
Return only the expression, nothing else.
Input: {userInput}"""
    response = model.generate_content(prompt)
    return response.text.strip()
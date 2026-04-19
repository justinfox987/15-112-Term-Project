from cmu_graphics import *
from structures import *

##### CLI ELEMENTS #####


##### drawText() WRITTEN BY CLAUDE ####
def drawText(app, rectCX, rectCY, rectW, rectH, text, fontSize=16):
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

    for i, line in enumerate(lines):
        y = textLY + i * lineHeight
        drawLabel(line, textLX, y, size=fontSize, align='left-top', font='Arial')




##### MAKE TEXTBOXES #####
def makeTextboxes(app):
    functionInput = Textbox(app,label='test', cx=app.width*0.2,cy=app.height*0.2,
                            width = app.width*0.2, height = app.height*0.1)
    boxes = [functionInput]
    for box in boxes:
        app.textboxes.append(box)
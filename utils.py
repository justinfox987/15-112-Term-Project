import matplotlib
matplotlib.use('Agg')
from cmu_graphics import *
from structures import *
import google.genai as genai
import os
import numpy as np

_parseResult = [None]  # written by background thread, consumed by onStep

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
    fnInputBox = fnInputMenu.internalBoxes['fnInputBox']
    fnRemoveBox = fnInputMenu.internalBoxes['fnRemoveBox']
    fnInputBox.cx, fnInputBox.cy = leftCX, leftTitleCY + boxH*0.3
    fnInputBox.width, fnInputBox.height = halfW*0.8, boxH*0.2
    fnRemoveBox.cx, fnRemoveBox.cy = leftCX, leftTitleCY + boxH*0.6
    fnRemoveBox.width, fnRemoveBox.height = halfW*0.8, boxH*0.2


def handleFnInputBox(app):
    import threading
    fnInputMenu = app.menus['fnInputMenu']
    fnInputBox = fnInputMenu.internalBoxes['fnInputBox']
    userInput = fnInputBox.prevInputs[-1]
    fnInputBox.prevInputs.pop()
    app.isParsing = True
    app.parseError = False
    def parseAndAdd():
        function = parseFunction(userInput)
        if function is None:
            _parseResult[0] = 'fail'
        else:
            _parseResult[0] = function
    threading.Thread(target=parseAndAdd, daemon=True).start()

def handleFnRemoveBox(app):
    fnRemoveBox = app.menus['fnInputMenu'].internalBoxes['fnRemoveBox']
    userInput = fnRemoveBox.prevInputs.pop()
    keyToRemove = None
    for funcKey in app.functions:
        if app.functions[funcKey].label == userInput:
            keyToRemove = funcKey
            break
    if keyToRemove is not None:
        funcToRemove = app.functions[keyToRemove]
        menuKeyToRemove = None
        for menuKey in app.funcMenus:
            if app.funcMenus[menuKey].function is funcToRemove:
                menuKeyToRemove = menuKey
                break
        if menuKeyToRemove is not None:
            del app.funcMenus[menuKeyToRemove]
        del app.functions[keyToRemove]
        refreshVars(app)
            
### 50/50 claude me
def parseFunction(userInput):
    print('parsing...')
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    prompt = f"""Convert this math expression into a single Pythonic expression
    using only numpy (as np) functions, in terms of the variables given. Return
    the pythonic function, then a tilde, then the function label, then a tilde,
    then a comma-separated list of variables. For example, a user input of
    'f(x,y) = 2x^2 * 3y^2' should return "'f(x,y)'~2*x**2 * 3*y**2~x,y".
    If the input is not a valid mathematical function, return only the word FAIL.
    Input: {userInput}
    """
    response = client.models.generate_content(model='gemma-4-26b-a4b-it', contents=prompt)
    print('done!')
    if response.text.strip() == 'FAIL':
        return None
    separatedResponse = response.text.strip().split('~')
    label,pythonFunction,vars = separatedResponse[0].strip().strip("'\""),separatedResponse[1],separatedResponse[2]
    varDict = dict()
    for var in vars.split(','):
        varDict[var] = 'auto'
    newFunc = Function(app,label,pythonFunction,varDict)
    print(f'Function: {newFunc.pythonicInput}')
    return newFunc

### 50/50 me and Claude
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

## 70/30 me and claude 
def drawVarEditMenu(app):
    varEditMenu = app.menus['varEditMenu']
    cx, cy = app.width//2, app.height//2
    w, h = app.width*0.7, app.height*0.6
    padding = min(w,h) * 0.05
    gap = padding
    innerW, innerH = w-2*padding, h-2*padding
    titleH = padding * 1.25
    boxH = innerH - titleH - gap
    boxCY = cy + (titleH + gap) / 2
    titleCY = cy - innerH/2 + titleH/2
    varEditMenu.drawOpenedMenu(app)
    drawLabel(varEditMenu.label, cx, titleCY, size=24, bold=True)

    # White inner rectangle (with padding inside the box area)
    outputRowH = padding * 2
    tableW = innerW - 2*padding
    tableH = boxH - 3*padding - outputRowH
    tableLeft = cx - tableW/2
    tableTop = boxCY - (tableH + padding + outputRowH) / 2
    drawRect(tableLeft, tableTop, tableW, tableH,
              fill='white', border='black', borderWidth=2)
    drawLine(tableLeft, tableTop, tableLeft + tableW,
              tableTop, fill='black', lineWidth=2)

    # Column layout
    colWidths = [0.1, 0.2, 0.2, 0.3, 0.2]
    colNames = ['Var', 'Min', 'Max', 'Role', 'Frames/Val']
    headerH = padding * 1.2

    # Header row background
    drawRect(tableLeft, tableTop, tableW, headerH, fill='white')

    x = tableLeft
    for name, frac in zip(colNames, colWidths):
        colW = tableW * frac
        drawLabel(name, x + colW/2, tableTop + headerH/2, size=14, bold=True)
        drawLine(x, tableTop, x, tableTop + tableH, fill='black', lineWidth=2)
        x += colW
    drawLine(x, tableTop, x, tableTop + tableH, fill='black', lineWidth=2)

    drawLine(tableLeft, tableTop + headerH, tableLeft + tableW,
              tableTop + headerH, fill='black', lineWidth=2)
    makeAndSizeVarMenus(app, tableLeft, tableTop, tableW, headerH)

    # Output range row
    rowY = tableTop + tableH + padding
    rowCY = rowY + outputRowH / 2
    boxW = tableW * 0.22
    drawLabel('Output Range:', tableLeft + tableW * 0.18, rowCY, size=14, bold=True)
    app.outputMin.cx = tableLeft + tableW * 0.45
    app.outputMin.cy = rowCY
    app.outputMin.width = boxW
    app.outputMin.height = outputRowH * 0.75
    app.outputMin.drawClickable(app)
    drawLabel('to', tableLeft + tableW * 0.6, rowCY, size=14)
    app.outputMax.cx = tableLeft + tableW * 0.75
    app.outputMax.cy = rowCY
    app.outputMax.width = boxW
    app.outputMax.height = outputRowH * 0.75
    app.outputMax.drawClickable(app)

## 70/30 me and claude
def refreshVars(app):
    allVars = set()
    for funcKey in app.functions:
        for var in app.functions[funcKey].vars:
            allVars.add(var)

    for var in allVars:
        if var not in app.vars:
            minBox = InlineTextbox(app, 'auto', 0, 0, 0, 0, fontSize=24)
            maxBox = InlineTextbox(app, 'auto', 0, 0, 0, 0, fontSize=24)
            dropdown = Dropdown(app, 'Role', 0, 0, 0, 0,
                                ['X-Axis', 'Y-Axis', 'Animate', 'Constant'])
            framesBox = InlineTextbox(app, '120', 0, 0, 0, 0, fontSize=24)
            app.vars[var] = [minBox, maxBox, dropdown, framesBox]

    for var in list(app.vars.keys()):
        if var not in allVars:
            del app.vars[var]

### 50/50 claude and me
def makeAndSizeVarMenus(app, tableLeft, tableTop, tableW, headerH):
    colWidths = [0.1, 0.2, 0.2, 0.3, 0.2]
    rowH = headerH * 2.5
    openedDropdown = None

    for i, (var, data) in enumerate(app.vars.items()):
        rowY = tableTop + headerH + i * rowH
        rowCY = rowY + rowH / 2
        minBox, maxBox, dropdown, framesBox = data

        x = tableLeft
        colW = tableW * colWidths[0]
        drawLabel(var, x + colW/2, rowCY, size=18, bold=True)
        x += colW

        for box, frac in [(minBox, colWidths[1]), (maxBox, colWidths[2])]:
            colW = tableW * frac
            box.cx = x + colW/2
            box.cy = rowCY
            box.width = colW * 0.85
            box.height = rowH * 0.7
            box.drawClickable(app)
            x += colW

        colW = tableW * colWidths[3]
        dropdown.cx = x + colW/2
        dropdown.cy = rowCY
        dropdown.width = colW * 0.85
        dropdown.height = rowH * 0.7
        dropdown.drawClickable(app)
        if dropdown.opened:
            openedDropdown = dropdown
        x += colW

        colW = tableW * colWidths[4]
        framesBox.cx = x + colW/2
        framesBox.cy = rowCY
        framesBox.width = colW * 0.85
        framesBox.height = rowH * 0.7
        framesBox.drawClickable(app)

        drawLine(tableLeft, rowY + rowH, tableLeft + tableW, rowY + rowH,
                 fill='black', lineWidth=2)

    if openedDropdown:
        openedDropdown.drawOpenedDropdown(app)

## 30/70  me claude
def refreshPlot(app):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.colors import LinearSegmentedColormap
    from mpl_toolkits.mplot3d import Axes3D
    

    # --- Step 1: Determine plot type ---
    xVar = None
    yVar = None
    animateVar = None

    for var in app.vars:
        role = app.vars[var][2].selected
        if role == 'X-Axis':
            xVar = var
        elif role == 'Y-Axis':
            yVar = var
        elif role == 'Animate':
            animateVar = var

    if xVar is None:
        return  # nothing to plot

    is3D = (yVar is not None)
    isAnimated = (animateVar is not None)

    # --- Step 2: Build linspaces for each var ---
    def getLinspace(var, nPoints):
        minLabel = app.vars[var][0].label
        maxLabel = app.vars[var][1].label
        lo = -10.0 if minLabel == 'auto' else float(minLabel)
        hi = 10.0 if maxLabel == 'auto' else float(maxLabel)
        return np.linspace(lo, hi, nPoints)

    def getConstant(var):
        valLabel = app.vars[var][3].label
        if valLabel == 'auto':
            return 1.0
        return float(valLabel)

    def getFrameCount(var):
        framesLabel = app.vars[var][3].label
        if framesLabel == 'auto':
            return 120
        return int(framesLabel)

    xArr = getLinspace(xVar, 5000)
    if is3D:
        from scipy.interpolate import RectBivariateSpline
        xCoarse = getLinspace(xVar, 50)
        yCoarse = getLinspace(yVar, 50)
        Xc, Yc = np.meshgrid(xCoarse, yCoarse)
        xFine = getLinspace(xVar, 300)
        yFine = getLinspace(yVar, 300)
        Xfine, Yfine = np.meshgrid(xFine, yFine)

    # --- Step 3: Build eval dict ---
    def buildEvalDict(frameVal=None):
        evalDict = {'np': np}
        for var in app.vars:
            role = app.vars[var][2].selected
            if role == 'X-Axis':
                evalDict[var] = Xc if is3D else xArr
            elif role == 'Y-Axis':
                evalDict[var] = Yc
            elif role == 'Constant':
                evalDict[var] = getConstant(var)
            elif role == 'Animate':
                evalDict[var] = frameVal
        return evalDict

    def interpolate3D(Zcoarse):
        spline = RectBivariateSpline(yCoarse, xCoarse, Zcoarse)
        return spline(yFine, xFine)

    def shadedSurface(ax, Zfine, color):
        from matplotlib.colors import to_rgb, LightSource
        r, g, b = to_rgb(color)
        cmap = LinearSegmentedColormap.from_list('', [(r*0.85, g*0.85, b*0.85), color])
        rgb = LightSource(270, 45).shade(Zfine, cmap=cmap, blend_mode='soft', vert_exag=0.05)
        n = Zfine.shape[0]
        ax.plot_surface(Xfine, Yfine, Zfine, facecolors=rgb,
                        edgecolor='none', antialiased=True,
                        rcount=n, ccount=n)

    # --- Step 4: Plot ---
    if isAnimated:
        import tempfile, shutil, PIL.Image as Image
        numFrames = getFrameCount(animateVar)
        animArr = getLinspace(animateVar, numFrames) if app.vars[animateVar][0].label != 'auto' else np.linspace(-10, 10, numFrames)
        frameVals = np.linspace(animArr[0], animArr[-1], numFrames)
        tmpDir = tempfile.mkdtemp()
        framePaths = []

        for i, frameVal in enumerate(frameVals):
            fig = Figure()
            FigureCanvasAgg(fig)
            if is3D:
                ax = fig.add_subplot(111, projection='3d')
            else:
                ax = fig.add_subplot(111)

            for funcKey in app.functions:
                func = app.functions[funcKey]
                evalDict = buildEvalDict(frameVal=frameVal)
                Z = eval(func.pythonicInput, evalDict)
                if is3D:
                    shadedSurface(ax, interpolate3D(Z), func.color)
                else:
                    ax.plot(xArr, Z, color=func.color, label=func.label)

            if not is3D:
                ax.legend()
            ax.set_title(f'{animateVar} = {frameVal:.2f}')
            framePath = os.path.join(tmpDir, f'frame_{i:03d}.png')
            fig.savefig(framePath, bbox_inches='tight')
            framePaths.append(framePath)

        app.plotVersion += 1
        gifFile = f'plot_{app.plotVersion}.gif'
        imgs = [Image.open(f) for f in framePaths]
        imgs[0].save(gifFile, save_all=True, append_images=imgs[1:],
                     duration=1000//30, loop=0)
        stillFile = f'plot_{app.plotVersion}.png'
        shutil.copy(framePaths[len(framePaths) // 2], stillFile)
        shutil.rmtree(tmpDir)
        app.plotFile = stillFile
        app.plotReady = True

    else:
        fig = Figure()
        FigureCanvasAgg(fig)
        if is3D:
            ax = fig.add_subplot(111, projection='3d')
        else:
            ax = fig.add_subplot(111)

        for funcKey in app.functions:
            func = app.functions[funcKey]
            evalDict = buildEvalDict()
            Z = eval(func.pythonicInput, evalDict)
            if is3D:
                shadedSurface(ax, interpolate3D(Z), func.color)
            else:
                ax.plot(xArr, Z, color=func.color, label=func.label)

        if not is3D:
            ax.legend()
        outMin = app.outputMin.value
        outMax = app.outputMax.value
        if outMin != 'auto' and outMax != 'auto':
            if is3D:
                ax.set_zlim(outMin, outMax)
            else:
                ax.set_ylim(outMin, outMax)
        app.plotVersion += 1
        filename = f'plot_{app.plotVersion}.png'
        fig.savefig(filename, bbox_inches='tight')
        app.plotFile = filename
        app.plotReady = True

def triggerRefreshPlot(app):
    import threading
    app.plotReady = False
    app.isPlotting = True
    def run():
        refreshPlot(app)
    threading.Thread(target=run, daemon=True).start()

def drawGraderMenu(app):
    graderMenu = app.menus['graderMenu']
    keys = ['autoAddFn2D', 'autoaddFn3D', 'autoAddFnAnimated', 'autoSetVars']
    boxW = app.width * 0.2
    boxH = app.height * 0.1
    gap = app.height * 0.03
    totalH = len(keys) * boxH + (len(keys) - 1) * gap
    startY = app.height * 0.5 - totalH / 2 + boxH / 2
    for i, key in enumerate(keys):
        box = graderMenu.internalBoxes[key]
        box.cx = app.width * 0.5
        box.cy = startY + i * (boxH + gap)
        box.width = boxW
        box.height = boxH
        box.drawClickable(app)
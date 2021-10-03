"""
This is a simple 3D interactive graphics and animation library for Python.
Author: Andrew Merrill, Catlin Gabel School
Version: 1.1  (last updated March, 2020)

This code is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike license
see http://creativecommons.org/licenses/by-nc-sa/3.0/ for details

Note: You must have the PyGame and PyOpenGL libraries installed for this to work.
        You can install PyGame by running:
             pip3 install pygame
        You can install PyOpenGL by running:
             pip3 install pyopengl

This has been tested with Python 3.7.6, PyGame 1.9.6, and PyOpenGL 3.1.5.
"""

import sys, math, re, os, os.path, random, struct
import zipfile, xml.etree.ElementTree
import pygame

import OpenGL
OpenGL.ERROR_CHECKING = True

from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.arrays.lists

class World:
    pass

class Point3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
class Angles3D:
    def __init__(self, heading, pitch, roll):
        self.heading = heading
        self.pitch = pitch
        self.roll = roll

class Viewport:
    def __init__(self, label, x, y, width, height, offscreen=False):
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.offscreen = offscreen
        self.cameraPosition = (0,0,0)
        self.cameraRotation = (0,0,0)
        
class GameLibInfo:
    def __init__(self):
        self.initialize()
        
    def initialize(self):
        self.version = "1.1"
        self.world = None
        self.fonts = dict()
        self.macFonts = None      
        self.defaultFont = None
        self.defaultFontSize = 30        
        self.eventListeners = dict()
        self.frameRate = 60
        self.windowWidth = 0
        self.windowHeight = 0
        self.viewportWidth = 0
        self.viewportHeight = 0
        self.viewports = dict()
        self.currentViewport = None
        self.background = (0,0,0)
        self.foreground = (1,1,1)
        self.nextEventType = pygame.USEREVENT
        self.arrayHandler = OpenGL.arrays.lists.ListHandler()
        self.textureIDs = dict()
        self.FPStime = 0
        self.FPSinterval = 0
        self.FPScount = 0
        self.cameraPosition = Point3D(0,0,0)
        self.cameraAngles = Angles3D(0,0,0)
        self.keysPressedNow = dict()
        self.polygonCount = 0
        self.fieldOfView=45
        self.nearClip=0.1
        self.farClip=1000.0
        self.textureMapsEnabled = False
        self.lightingEnabled = False
        self.numLights = 0
        self.lights = []
        self.fogMode = 0
        self.numPushedMatrices = 0
        self.useNewCamera = True
        self.enableSelection = False
        self.selectColorDict = {} # key = color, value = ID
        self.selectColorIDDict = {} # key = ID, value = color
        self.selectionDrawingOn = False
        self.useInterleavedArrays = True
        self.START_MODE = 1
        self.EVENT_MODE = 2
        self.UPDATE_MODE = 3
        self.DRAW_MODE = 4
        self.currentMode = self.START_MODE
        self.joysticks = []
        self.joystickLabels = []  # list of dictionaries
        self.numJoysticks = 0
        self.joystickDeadZone = 0.05
        self.joystickLabelDefault = [["X", "Y"]]
        self.joystickLabelDefaults = {
            "Logitech Dual Action" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech RumblePad 2 USB" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Cordless RumblePad 2" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Attack 3" : [["X", "Y", "Throttle"]],

            "Logitech Logitech Dual Action" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Logitech RumblePad 2 USB" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Logitech Cordless RumblePad 2" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Logitech Attack 3" : [["X", "Y", "Throttle"]],

            "Controller (Gamepad F310)" : [["X","Y"], ["LeftX","LeftY","Trigger","RightY","RightX"]],
            "Controller (Wireless Gamepad F710)" : [["X","Y"], ["LeftX","LeftY","Trigger","RightY","RightX"]],

            "Saitek Aviator Stick" : [["X", "Y", "LeftThrottle", "Twist", "RightThrottle"]],
            "Saitek Pro Flight Throttle Quadrant" : [["LeftThrottle", "CenterThrottle", "RightThrottle"]],

            "XBOX 360 For Windows (Controller)" : [["X","Y"], ["LeftX", "LeftY", "Trigger", "RightY", "RightX"]]

            }

        
    def initializeListeners(self):
        onAnyKeyPress(lambda world,key: 0)
        onAnyKeyRelease(lambda world,key: 0)
        onMousePress(lambda world,x,y,button: 0)
        onMouseRelease(lambda world,x,y,button: 0)
        onWheelForward(lambda world,x,y: 0)
        onWheelBackward(lambda world,x,y: 0)
        onMouseMotion(lambda world,x,y,dx,dy,b1,b2,b3: 0)
        onGameControllerStick(lambda world,device,axis,value: 0)
        onGameControllerDPad(lambda world,device,pad,xvalue,yvalue: 0)
        onGameControllerButtonPress(lambda world,device,button: 0)
        onGameControllerButtonRelease(lambda world,device,button: 0)

    def initializeJoysticks(self):
        self.numJoysticks = pygame.joystick.get_count()
        for id in range(self.numJoysticks):
            self.joysticks.append(pygame.joystick.Joystick(id))
            self.joystickLabels.append(dict())
            self.joysticks[id].init()
            stickname = self.joysticks[id].get_name()
            if stickname in self.joystickLabelDefaults:
                print("recognized a " + stickname)
                labelList = self.joystickLabelDefaults[stickname]
            else:
                print("unknown game controller: " + stickname)
                labelList = self.joystickLabelDefault
            for labels in labelList:
                gameControllerSetStickAxesNames(labels, id)
            print("    with axes:", gameControllerGetStickAxesNames())

    def loadColors(self, colorsList):
        self.colorsList = colorsList
        self.colorTable3D = dict()
        for (name, red, green, blue, hexcolor) in colorsList:
            self.colorTable3D[name] = (red/255.0, green/255.0, blue/255.0)
        self.colorTable3D['clear'] = (0,0,0,0)

    def loadKeys(self, keyList):
        self.keyList = keyList
        self.key2nameDict = dict()
        self.name2keyDict = dict()
        for (code, nameList) in keyList:
            self.key2nameDict[code] = nameList[0]
            for name in nameList:
                self.name2keyDict[name] = code

    def loadPolyhedra(self, polyhedraDict):
        self.polyhedraDict = dict()
        for name in polyhedraDict:
            poly = polyhedraDict[name]
            self.polyhedraDict[name] = poly
            self.polyhedraDict[name.lower()] = poly
            self.polyhedraDict[name.replace('_', ' ')] = poly
            self.polyhedraDict[name.lower().replace('_', ' ')] = poly
                            
    

    def startAnimation(self):
        self.clock = pygame.time.Clock()
        self.startTime = pygame.time.get_ticks()
        self.keepRunning = True
        self.FPScount = 0
        if self.FPSinterval > 0:
            self.FPStime = pygame.time.get_ticks() + self.FPSinterval

    def maybePrintFPS(self):
        self.FPScount += 1
        if self.FPSinterval > 0:
            time = pygame.time.get_ticks()
            if time > self.FPStime + self.FPSinterval:
                print(getActualFrameRate(), " (" + str(_GLI.polygonCount) + " polygons)")
                sys.stdout.flush()
                self.FPStime = time
                self.FPScount = 0

    # Returns the textureID given the name of a texture
    # Three cases:
    #   If given None, it always returns 0 (no texture)
    #   If given a name already in the textureIDs dict, then lookup the ID in the dict
    #   Otherwise, load the texture using loadTexture
    def getTextureID(self, textureName):
        if textureName is None:
            return 0
        elif textureName in self.textureIDs:
            return self.textureIDs[textureName]
        elif isinstance(textureName, tuple):
            (data, filename) = textureName
            if filename in self.textureIDs:
                return self.textureIDs[filename]
        return loadTexture(textureName)

    def enableTextureMaps(self):
        if self.textureMapsEnabled:
            return
        self.textureMapsEnabled = True
        glEnable(GL_TEXTURE_2D)
        #glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

    def handleNumPy(self):
        global numpy
        try:
            import numpy
            self.hasNumPy = True
            print("using numpy")
        except ImportError:
            self.hasNumPy = False

    def handleOldOpenGLVersions(self):
        openglVersion = str(glGetString(GL_VERSION))
        if openglVersion < "1.5":
            import OpenGL.GL.ARB.vertex_buffer_object as ARBVBO
            global glGenBuffers, glBindBuffer, glBufferData
            glGenBuffers = ARBVBO.glGenBuffersARB
            glBindBuffer = ARBVBO.glBindBufferARB
            glBufferData = ARBVBO.glBufferDataARB
        if openglVersion < "1.4":
            self.hasWindowPos = False
        else:
            self.hasWindowPos = True
        if openglVersion < "1.3":
            import OpenGL.GL.ARB.transpose_matrix as ARBTransposeMatrix
            global glMultTransposeMatrixf
            glMultTransposeMatrixf = ARBTransposeMatrix.glMultTransposeMatrixfARB
        if openglVersion < "1.2":
            print("Your Open GL Version ("+openglVersion+") is too old")

        
_GLI = GameLibInfo()

def makeGraphicsWindow(width, height, fullscreen=False, position=None):
    initGraphics()
    
    if position is None:
        os.environ['SDL_VIDEO_CENTERED'] = 'center'
    else:
        (x,y) = position
        os.environ['SDL_VIDEO_WINDOW_POS'] = str(x)+','+str(y)
    
    setGraphicsMode(width, height, fullscreen)
    print(getOpenGLVersion())
    _GLI.handleOldOpenGLVersions()
    _GLI.handleNumPy()
    enable_vsync()

def initGraphics():
    pygame.init()
    _GLI.initialize()
    _GLI.initializeListeners()
    _GLI.initializeJoysticks()
    _GLI.graphicsInited = True

def endGraphics():
    _GLI.keepRunning = False

def setGraphicsMode(width, height, fullscreen=False):
    _GLI.windowWidth = width
    _GLI.windowHeight = height
    _GLI.viewportWidth = width
    _GLI.viewportHeight = height
    flags = 0
    if fullscreen == True:
        flags = flags | pygame.FULLSCREEN
    flags = flags | pygame.OPENGL | pygame.HWSURFACE | pygame.DOUBLEBUF
    _GLI.screen = pygame.display.set_mode((width, height), flags)
    glViewport(0, 0, width, height)
    createViewport("mainwindow", 0, 0, width, height)
    setProjection()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glShadeModel(GL_SMOOTH)
    glEnableClientState(GL_VERTEX_ARRAY)
    _GLI.textureIDs = dict()


def getScreenSize():
    initGraphics()
    info = pygame.display.Info()
    return (info.current_w, info.current_h)

def getAllScreenSizes():
    initGraphics()
    return pygame.display.list_modes()

def setProjection(fieldOfView=None, nearClip=None, farClip=None):
    if fieldOfView is not None:
        _GLI.fieldOfView = fieldOfView
    if nearClip is not None:
        _GLI.nearClip = nearClip
    if farClip is not None:
        _GLI.farClip = farClip
    _applyProjection()

def setFieldOfView(fieldOfView):
    _GLI.fieldOfView = fieldOfView
    _applyProjection()

def setClipRange(nearClip=None, farClip=None):
    if nearClip is not None:
        _GLI.nearClip = nearClip
    if farClip is not None:
        _GLI.farClip = farClip
    _applyProjection()

def _applyProjection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = float(_GLI.viewportWidth) / float(_GLI.viewportHeight)
    gluPerspective(_GLI.fieldOfView, aspect, _GLI.nearClip, _GLI.farClip)
    glMatrixMode(GL_MODELVIEW)

def enableInterleavedArrays(isEnabled):
    _GLI.useInterleavedArrays = isEnabled

def setBackground(background):
    if isinstance(background, str):
        _GLI.background = lookupColor3D(background)
    else:
        _GLI.background = background
    glClearColor(_GLI.background[0], _GLI.background[1], _GLI.background[2], 1.0)



# enables vsync (to avoid tearing) on macs that disable it by default!
# original code from http://beta.macgamedev.com/forums/printthread.php?tid=2974
# revised version from http://stackoverflow.com/questions/17084928/how-to-enable-vsync-in-pyopengl
# parameter 222 is kCGLCPSwapInterval
def enable_vsync():
    if sys.platform != 'darwin':
        return
    try:
        import ctypes
        import ctypes.util
        ogl = ctypes.cdll.LoadLibrary(ctypes.util.find_library("OpenGL"))
        v = ctypes.c_int(1)

        ogl.CGLGetCurrentContext.argtypes = []
        ogl.CGLGetCurrentContext.restype = ctypes.c_void_p

        ogl.CGLSetParameter.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
        ogl.CGLSetParameter.restype = ctypes.c_int

        context = ogl.CGLGetCurrentContext()

        ogl.CGLSetParameter(context, 222, ctypes.pointer(v))

    except Exception as e:
        print("Unable to set vsync mode, using driver defaults: {}".format(e))    
    
    
def getActualFrameRate():
    return _GLI.clock.get_fps()

def displayFPS(interval):
    _GLI.FPSinterval = interval*1000
    _GLI.FPStime = pygame.time.get_ticks()
    _GLI.FPScount = 0

def getWindowWidth():
    return _GLI.windowWidth

def getWindowHeight():
    return _GLI.windowHeight

def getViewportWidth():
    return _GLI.viewportWidth

def getViewportHeight():
    return _GLI.viewportHeight


def setWindowTitle(title):
    pygame.display.set_caption(str(title))

def lookupColor3D(color):
    if color in _GLI.colorTable3D:
        return _GLI.colorTable3D[color]
    elif isinstance(color, str):
        raise ValueError("Not a known color: " + color)
    else:
        return color
    
def getColorsList():
    return [color[0] for color in _GLI.colorsList]

def getOpenGLVersion():
    return "OpenGL " + str(glGetString(GL_VERSION)) + " " + str(glGetString(GL_VENDOR)) + " " + str(glGetString(GL_RENDERER)) + " PyOpenGL " + str(OpenGL.version.__version__) + " graphics3d " + str(_GLI.version)

##############################################################

def createViewport(label, x, y, width, height):
    viewport = Viewport(label, x, y, width, height)
    _GLI.viewports[label] = viewport
    _GLI.currentViewport = viewport
    
def getCurrentViewport():
    if _GLI.currentViewport is None:
        return None
    else:
        return _GLI.currentViewport.label

def createViewportOffscreen(label, width, height):
    viewport = Viewport(label, 0, 0, width, height, True)
    _GLI.viewports[label] = viewport

def useViewportCamera(label):
    if _GLI.currentViewport != None:
        _GLI.currentViewport.cameraPosition = getCameraPosition()
        _GLI.currentViewport.cameraRotation = getCameraRotation()
    _GLI.currentViewport = _GLI.viewports[label]
    _GLI.viewportWidth = _GLI.currentViewport.width
    _GLI.viewportHeight = _GLI.currentViewport.height
    (x,y,z) = _GLI.currentViewport.cameraPosition
    (h,p,r) = _GLI.currentViewport.cameraRotation
    setCameraPosition(x,y,z)
    setCameraRotation(h,p,r)

def useViewport(label):
    useViewportCamera(label)
    x = _GLI.currentViewport.x
    y = _GLI.currentViewport.y
    width = _GLI.currentViewport.width
    height = _GLI.currentViewport.height
    setViewport(x, y, width, height)
    if _GLI.currentViewport.offscreen:
        glDrawBuffer(GL_AUX2)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

def stopOffscreenViewport():
    if _GLI.currentViewport == None: return
    if _GLI.currentViewport.offscreen == False: return
    glDrawBuffer(GL_BACK)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    useViewport("mainwindow")

def updateTextureFromOffscreenViewport(model, viewportlabel):
    glReadBuffer(GL_AUX2)
    textureID = model.textureID
    glBindTexture(GL_TEXTURE_2D, textureID)
    width = _GLI.viewports[viewportlabel].width
    height = _GLI.viewports[viewportlabel].height
    glTexParameter(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
    glCopyTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 0, 0, width, height)    
    #glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 0, 0, width, height, 0)    
    glReadBuffer(GL_BACK)


# this should normally not be called from outside the library
#  provided for backwards compatibility
def setViewport(x, y, width, height):
    _GLI.viewportWidth = width
    _GLI.viewportHeight = height
    if not _GLI.currentViewport.offscreen:
        glViewport(x,  _GLI.windowHeight - (y+height), width, height)
    _applyProjection()
    glLoadIdentity()
    setupCamera()
    _drawLights()


###############################################################################



# This should only be called when texture is NOT in the _GLI.textureIDs dict
# Normally, from inside the library, you need to call _GLI.getTextureID instead
def loadTexture(texture, alias=None, scale=None, tiles=None):
    if isinstance(texture,str):
        textureImage = pygame.image.load(texture)
        if scale is not None:
            textureImage = pygame.transform.scale(textureImage, scale)
        if tiles is not None:
            (horizontalTiles, verticalTiles) = tiles
            tile_width = textureImage.get_width()
            tile_height = textureImage.get_height()
            new_width = tile_width * horizontalTiles
            new_height = tile_height * verticalTiles
            new_image = pygame.Surface((new_width,new_height))
            for h in range(horizontalTiles):
                for v in range(verticalTiles):
                    new_image.blit(textureImage, (h*tile_width, v*tile_height))
            textureImage = new_image
        textureFileName = texture
        textureData = pygame.image.tostring(textureImage, "RGBA", True)
        width = textureImage.get_width()
        height = textureImage.get_height()
    else:   
        (width, height, textureFileName, textureData) = _getTextureData(texture)
    _GLI.enableTextureMaps()
    textureID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    #glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameter(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
    #gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, width, height, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
    if textureFileName is not None:
        _GLI.textureIDs[textureFileName] = textureID
    if alias is not None:
        _GLI.textureIDs[alias] = textureID
    return textureID


def setTexture(model, textureName):
    model.textureID = _GLI.getTextureID(textureName)

def updateTexture(model, texture):
    (width, height, textureFileName, textureData) = _getTextureData(texture)
    textureID = model.textureID
    glBindTexture(GL_TEXTURE_2D, textureID)
    #glTexParameter(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
    #gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, width, height, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

def _getTextureData(texture):
    if isinstance(texture, str) or isinstance(texture, unicode):
        # texture is an image file
        textureImage = pygame.image.load(texture)
        textureFileName = texture
        textureData = pygame.image.tostring(textureImage, "RGBA", True)
    elif isinstance(texture, Canvas2D):
        # texture is a Canvas2D object
        textureImage = texture.image
        textureData = texture.getImageData()
        textureFileName = None
    elif isinstance(texture, pygame.Surface):
        textureImage = texture
        textureData = pygame.image.tostring(textureImage, "RGBA", True)
        textureFileName = None
    else:
        # texture is a FileObject, probably from inside a zip archive
        # in this case we are passed a tuple: (FileObject, FileName)
        (textureFileObject, textureFileName) = texture
        if textureFileName in _GLI.textureIDs:
            return _GLI.textureIDs[textureFileName]
        textureImage = pygame.image.load(textureFileObject, textureFileName)
        textureData = pygame.image.tostring(textureImage, "RGBA", True)
    width = textureImage.get_width()
    height = textureImage.get_height()
    return (width, height, textureFileName, textureData)


#########################################################################

def makeFog(density=0.05, color=(1,1,1), mode=1):
    glEnable(GL_FOG)
    if mode == 1:
        glFogi(GL_FOG_MODE, GL_EXP)
    if mode == 2:
        glFogi(GL_FOG_MODE, GL_EXP2)

    glFogf(GL_FOG_DENSITY, density)
    glFogfv(GL_FOG_COLOR, lookupColor3D(color))
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    _GLI.fogDensity = density
    _GLI.fogMode = mode
    _GLI.fogColor = color

def removeFog():
    glDisable(GL_FOG)
    _GLI.fogMode = 0


# returns the distance at which the fraction of visible color has dropped to the given value
def getFogRange(visibility=0.005):
    if _GLI.fogMode == 0:
        return 1e100
    elif _GLI.fogMode == 1:
        return (-math.log(visibility)) / _GLI.fogDensity
    elif _GLI.fogMode == 2:
        return math.sqrt(-math.log(visibility)) / _GLI.fogDensity

def setWireFrame(wireframe, width=1):
    if wireframe:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(width)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
 
#########################################################

def loadSound(filename, volume=1):
    sound = pygame.mixer.Sound(filename)
    if volume != 1:
        sound.set_volume(volume)
    return sound

def playSound(sound, repeat=False):
    if repeat:
        sound.play(-1)
    else:
        sound.play()

def stopSound(sound):
    sound.stop()

def loadMusic(filename, volume=1):
    pygame.mixer.music.load(filename)
    if volume != 1:
        pygame.mixer.music.set_volume(volume)

def playMusic(repeat=False):
    if repeat:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.play()

def stopMusic():
    pygame.mixer.music.stop()
    
    
#########################################################


def onKeyPress(listenerFunction, key):
    key = getKeyCode(key)
    if key is None:
        raise Exception("that is not a valid key")
    _GLI.eventListeners[("keydown",key)] = listenerFunction

def onAnyKeyPress(listenerFunction):
    _GLI.eventListeners["keydown"] = listenerFunction

def onKeyRelease(listenerFunction, key):
    key = getKeyCode(key)
    if key == None:
        raise Exception("that is not a valid key")
    _GLI.eventListeners[("keyup",key)] = listenerFunction

def onAnyKeyRelease(listenerFunction):
    _GLI.eventListeners["keyup"] = listenerFunction


    
def onMousePress(listenerFunction):
    _GLI.eventListeners["mousedown"] = listenerFunction
    
def onMouseRelease(listenerFunction):
    _GLI.eventListeners["mouseup"] = listenerFunction

def onWheelForward(listenerFunction):
    _GLI.eventListeners["wheelforward"] = listenerFunction

def onWheelBackward(listenerFunction):
    _GLI.eventListeners["wheelbackward"] = listenerFunction

def onMouseMotion(listenerFunction):
    _GLI.eventListeners["mousemotion"] = listenerFunction

def onGameControllerStick(listenerFunction):
    _GLI.eventListeners["stickmotion"] = listenerFunction
    
def onGameControllerDPad(listenerFunction):
    _GLI.eventListeners["dpadmotion"] = listenerFunction
    
def onGameControllerButtonPress(listenerFunction):
    _GLI.eventListeners["joybuttondown"] = listenerFunction
    
def onGameControllerButtonRelease(listenerFunction):
    _GLI.eventListeners["joybuttonup"] = listenerFunction

def onTimer(listenerFunction, interval):
    if _GLI.nextEventType > pygame.NUMEVENTS:
        raise ValueError("too many timer listeners")
    _GLI.eventListeners["timer" + str(_GLI.nextEventType)] = listenerFunction
    pygame.time.set_timer(_GLI.nextEventType, interval)
    _GLI.nextEventType += 1



def removeTimerListener(listenerFunction):
    for key in _GLI.eventListeners:
        if key.startswith("timer"):
            oldListener = _GLI.eventListeners[key]
            if oldListener == listenerFunction:
                eventid = int(key[5:])
                del _GLI.eventListeners[key]
                pygame.time.set_timer(eventid, 0)

            
def removeAllTimerListeners():
    badListeners = []
    for key in _GLI.eventListeners:
        if key.startswith("timer"):
            badListener.append(key)
    for key in badListeners:
        del _GLI.eventListeners[key]
        eventid = int(key[5:])
        pygame.time.set_timer(eventid, 0)
    _GLI.nextEventType = pygame.USEREVENT
            


#########################################################

def getMousePosition():
    return pygame.mouse.get_pos()

def getMouseButton(button):
    return pygame.mouse.get_pressed()[button-1]

def hideMouse():
    pygame.mouse.set_visible(False)

def showMouse():
    pygame.mouse.set_visible(True)

def moveMouse(x, y):
    pygame.mouse.set_pos((int(x), int(y)))

def isKeyPressed(key):
    key = getKeyCode(key)
    return _GLI.keysPressedNow.get(key, False)

def getKeyName(key):
    if key in _GLI.key2nameDict:
        return _GLI.key2nameDict[key]
    else:
        return None

def getKeyCode(key):
    if key is None:
        return None
    if key in _GLI.key2nameDict:
        return key
    key = key.lower()
    if key in _GLI.name2keyDict:
        return _GLI.name2keyDict[key]
    else:
        return None

def sameKeys(key1, key2):
    code1 = getKeyCode(key1)
    code2 = getKeyCode(key2)
    if code1 is None:
        raise Exception("unknown key name: " + key1)
    if code2 is None:
        raise Exception("unknown key name: " + key2)
    return code1 == code2

#########################################################

def numGameControllers():
    return _GLI.numJoysticks

def gameControllerNumStickAxes(device=0):
    if device < _GLI.numJoysticks:
        return _GLI.joysticks[device].get_numaxes()
    else:
        return 0

def gameControllerNumDPads(device=0):
    if device < _GLI.numJoysticks:
        return _GLI.joysticks[device].get_numhats()
    else:
        return 0

def gameControllerNumButtons(device=0):
    if device < _GLI.numJoysticks:
        return _GLI.joysticks[device].get_numbuttons()
    else:
        return 0

def gameControllerSetDeadZone(deadzone):
    _GLI.joystickDeadZone = deadzone

def gameControllerGetStickAxesNames(device=0):
    if device < _GLI.numJoysticks:
        labelDict = _GLI.joystickLabels[device]
        axes = list(labelDict.keys())
        axes.sort(key=lambda axis: labelDict[axis])
        return axes
    return []

def gameControllerStickAxis(axis, device=0):
    if device < _GLI.numJoysticks:
        joystick = _GLI.joysticks[device]
        labelDict = _GLI.joystickLabels[device]
        if axis in labelDict:
            axis = labelDict[axis]
        if axis < joystick.get_numaxes():
            value = joystick.get_axis(axis)
            if abs(value) > _GLI.joystickDeadZone:
                return value
    return 0            

def gameControllerSetStickAxesNames(axesList, device=0):
    if device < _GLI.numJoysticks:
        labelDict = _GLI.joystickLabels[device]
        for i in range(len(axesList)):
            labelDict[axesList[i]] = i
        
def gameControllerButton(button, device=0):
    if device < _GLI.numJoysticks:
        joystick = _GLI.joysticks[device]
        button -= 1
        if button >= 0 and button < joystick.get_numbuttons():
            value = joystick.get_button(button)
            return (value == 1)
    return False            

def gameControllerDPadX(dpad=0, device=0):
    if device < _GLI.numJoysticks:
        joystick = _GLI.joysticks[device]
        if dpad < joystick.get_numhats():
            (dx,dy) = joystick.get_hat(dpad)
            return dx
    return 0            

def gameControllerDPadY(dpad=0, device=0):
    if device < _GLI.numJoysticks:
        joystick = _GLI.joysticks[device]
        if dpad < joystick.get_numhats():
            (dx,dy) = joystick.get_hat(dpad)
            return dy
    return 0

            
#########################################################
# use animate for non-interactive animations
##def animate(drawFunction, timeLimit, frameRate=_GLI.frameRate):
##    def startWorld():
##        pass
##    def timeExpired(world):
##        if getElapsedTime() > timeLimit:
##            _GLI.keepRunning = False
##        return world
##    def drawAnimationFrame(world):
##        drawFunction(getElapsedTime())
##    runGraphics(startWorld, timeExpired, drawAnimationFrame, frameRate)

# use run for interactive programs like games
def runGraphics(startFunction, updateFunction, drawFunction, quit=True):
    try:
        _GLI.startAnimation()
        _GLI.world = World()
        _GLI.startFunction = startFunction
        _GLI.updateFunction = updateFunction
        _GLI.drawFunction = drawFunction
        startFunction(_GLI.world)
        while _GLI.keepRunning:
            _GLI.currentMode = _GLI.EVENT_MODE
            eventlist = pygame.event.get()
            _GLI.world.guiEventList = eventlist
            for event in eventlist:
                if event.type == pygame.QUIT:
                    _GLI.keepRunning = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        _GLI.keepRunning = False
                        break
                    else:
                        _GLI.keysPressedNow[event.key] = True
                        if ("keydown",event.key) in _GLI.eventListeners:
                            _GLI.eventListeners[("keydown",event.key)](_GLI.world)
                        else:
                            _GLI.eventListeners["keydown"](_GLI.world, event.key)

                elif event.type == pygame.KEYUP:
                    _GLI.keysPressedNow[event.key] = False
                    if ("keyup",event.key) in _GLI.eventListeners:
                        _GLI.eventListeners[("keyup",event.key)](_GLI.world)
                    else:
                        _GLI.eventListeners["keyup"](_GLI.world, event.key)

                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button <= 3:
                        _GLI.eventListeners["mousedown"](_GLI.world, event.pos[0], event.pos[1], event.button)
                    elif event.button == 4:
                        _GLI.eventListeners["wheelforward"](_GLI.world, event.pos[0], event.pos[1])
                    elif event.button == 5:
                        _GLI.eventListeners["wheelbackward"](_GLI.world, event.pos[0], event.pos[1])
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button <= 3:
                        _GLI.eventListeners["mouseup"](_GLI.world, event.pos[0], event.pos[1], event.button)
                elif event.type == pygame.MOUSEMOTION:
                    if event.rel[0] != 0 or event.rel[1] != 0:
                        button1 = (event.buttons[0] == 1)
                        button2 = (event.buttons[1] == 1)
                        button3 = (event.buttons[2] == 1)
                        _GLI.eventListeners["mousemotion"](_GLI.world, event.pos[0],event.pos[1],event.rel[0],event.rel[1],button1,button2,button3)

                elif event.type == pygame.JOYAXISMOTION:
                    if abs(event.value) < _GLI.joystickDeadZone:
                        joystickValue = 0
                    else:
                        joystickValue = event.value
                    _GLI.eventListeners["stickmotion"](_GLI.world, event.joy, event.axis, joystickValue)
                elif event.type == pygame.JOYHATMOTION:
                    _GLI.eventListeners["dpadmotion"](_GLI.world, event.joy, event.hat, event.value[0], event.value[1])
                elif event.type == pygame.JOYBUTTONUP:
                    _GLI.eventListeners["joybuttonup"](_GLI.world, event.joy, event.button+1)
                elif event.type == pygame.JOYBUTTONDOWN:
                    _GLI.eventListeners["joybuttondown"](_GLI.world, event.joy, event.button+1)

                elif event.type >= pygame.USEREVENT:   # timer event
                    _GLI.eventListeners["timer"+str(event.type)](_GLI.world)
            _GLI.currentMode = _GLI.UPDATE_MODE
            updateFunction(_GLI.world)
            _render()
            pygame.display.flip()
            _GLI.maybePrintFPS()
            _GLI.clock.tick(_GLI.frameRate)
    finally:
        if quit:
            pygame.quit()

def closeGraphicsWindow():
    pygame.display.quit()

def quit():
    pygame.quit()

def _render():
    _GLI.currentMode = _GLI.DRAW_MODE
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setupCamera()
    _drawLights()
    _GLI.polygonCount = 0
    _GLI.numPushedMatrices = 0
    _GLI.drawFunction(_GLI.world)
    while _GLI.numPushedMatrices > 0:
        glPopMatrix()
        _GLI.numPushedMatrices -= 1
    


def getWorld():
    return _GLI.world

def getElapsedTime():
    return pygame.time.get_ticks() - _GLI.startTime

def resetTime():
    _GLI.startTime = pygame.time.get_ticks()

def setFrameRate(frameRate):
    _GLI.frameRate = frameRate


#########################################################

def getPixelColor(x,y):
    data = glReadPixels(x, _GLI.windowHeight - y, 1, 1, GL_RGB, GL_UNSIGNED_BYTE)
    (r, g, b) = struct.unpack("BBB", data)
    return (r, g, b)

def getPixelDistance(x,y):
    [[depth]] = glReadPixels(x, _GLI.windowHeight - y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)
    depth = (depth - 0.5) * 2.0
    far = _GLI.farClip
    near = _GLI.nearClip
    z = (-2.0 * far * near) / (depth * (far-near) - (far+near))
    return z

#########################################################

def useNewCamera(newCamera):
    _GLI.useNewCamera = newCamera

def setupCamera():
    if _GLI.useNewCamera:
        glRotate(-_GLI.cameraAngles.roll, 0, 0, 1)
        glRotate(-_GLI.cameraAngles.pitch, 1, 0, 0)
        glRotate(-_GLI.cameraAngles.heading, 0, 1, 0)
        glTranslate(-_GLI.cameraPosition.x, -_GLI.cameraPosition.y, -_GLI.cameraPosition.z)
    else:
        glRotate(-_GLI.cameraAngles.heading, 1, 0, 0)
        glRotate(-_GLI.cameraAngles.pitch, 0, 1, 0)
        glRotate(-_GLI.cameraAngles.roll, 0, 0, 1)
        glTranslate(-_GLI.cameraPosition.x, -_GLI.cameraPosition.y, -_GLI.cameraPosition.z)

def getCameraPosition():
    return (_GLI.cameraPosition.x, _GLI.cameraPosition.y, _GLI.cameraPosition.z)

def setCameraPosition(x, y, z):
    _GLI.cameraPosition.x = x
    _GLI.cameraPosition.y = y
    _GLI.cameraPosition.z = z

def adjustCameraPosition(x, y, z):
    _GLI.cameraPosition.x += x
    _GLI.cameraPosition.y += y
    _GLI.cameraPosition.z += z

def moveCameraForward(distance, flat=False):
    moveCamera(distance, 0, 0, flat)
def moveCameraBackward(distance, flat=False):
    moveCamera(-distance, 0, 0, flat)
def strafeCameraLeft(distance, flat=False):
    moveCamera(distance, 90, 0, flat)
def strafeCameraRight(distance, flat=False):
    moveCamera(distance, -90, 0, flat)


def moveCamera(distance, headingOffset=0, pitchOffset=0, flat=False):
    heading = _GLI.cameraAngles.heading + headingOffset
    pitch = _GLI.cameraAngles.pitch + pitchOffset
    if flat:
        (dx, dz) = polarToCartesian(heading, distance)
        dy = 0
    else:
        (dx, dy, dz) = sphericalToCartesian(heading, pitch, distance)
    adjustCameraPosition(dx, dy, dz)


# converts spherical coordinates to cartesian vector components
# inputs:
#   heading: the angle, in degrees, of ccw rotation around the Y axis (in the XZ plane)
#   pitch: the angle, in degrees, of ccw rotation around the X axis (in the YZ plane)
#   length: the desired length of the resulting vector
# result: a tuple (x,y,z) with the three cartesian components of the resulting vector

def sphericalToCartesian(heading, pitch, length):
    pitch = pitch / 180.0 * 3.1415926535897931
    heading = heading / 180.0 * 3.1415926535897931
    cos_pitch = math.cos(pitch)
    sin_pitch = math.sin(pitch)
    cos_heading = math.cos(heading)
    sin_heading = math.sin(heading)
    dx = length * cos_pitch * -sin_heading
    dy = length * sin_pitch
    dz = length * cos_pitch * -cos_heading
    return (dx,dy,dz)

def cartesianToSphericalAngles(x, y, z):
    heading = math.degrees(math.atan2(-x, -z))
    base = math.sqrt(x**2 + z**2)
    pitch = math.degrees(math.atan2(y, base))
    return (heading, pitch)

def polarToCartesian(heading, length):
    heading = heading / 180.0 * 3.1415926535897931
    dx = length * -math.sin(heading)
    dz = length * -math.cos(heading)
    return (dx,dz)

def cartesianToPolarAngle(x, z):
    return math.degrees(math.atan2(-x, -z))

###########

def setCameraRotation(heading, pitch, roll):
    _GLI.cameraAngles.heading = heading
    _GLI.cameraAngles.pitch = pitch
    _GLI.cameraAngles.roll = roll

def adjustCameraRotation(heading, pitch, roll):
    _GLI.cameraAngles.heading += heading
    _GLI.cameraAngles.pitch += pitch
    _GLI.cameraAngles.roll += roll

def getCameraRotation():
    return (_GLI.cameraAngles.heading, _GLI.cameraAngles.pitch, _GLI.cameraAngles.roll)

#########################################################
#########################################################
#########################################################

class Canvas2D:

    def __init__(self, width, height, opacity=0.8, frameRate=0):
        self.width = width
        self.height = height
        self.transparent = True # opacity < 1
        self.opacity = int(255*opacity)
        surfaceflags = 0
        if self.transparent:
            surfaceflags |= pygame.SRCALPHA
        self.image = pygame.Surface((width,height), surfaceflags)
        self.dirty = True
        self.frameRate = frameRate
        if self.frameRate > 0:
            self.framesToWait = _GLI.frameRate / float(self.frameRate)
        else:
            self.framesToWait = 0
        self.frameCount = self.framesToWait

    def getImageData(self):
        self.frameCount += 1
        if self.dirty and self.frameCount >= self.framesToWait:
            self.imageData = pygame.image.tostring(self.image, "RGBA", True)
            self.dirty = False
            self.frameCount = 0
        return self.imageData

    def lookupColor(self, color):
        if self.transparent:
            a = self.opacity
        else:
            a = 255
        if color is None:
            color = _GLI.foreground
        if isinstance(color, str):
            color = lookupColor3D(color)
        if len(color) == 3:
            (r,g,b) = color
        elif len(color) == 4:
            (r,g,b,a) = color
            a = int(a*255)
        r = int(r*255)
        g = int(g*255)
        b = int(b*255)
        return (r,g,b,a)

def clearCanvas2D(canvas, color='clear'):
    canvas.image.fill(canvas.lookupColor(color))
    canvas.dirty = True

def drawPoint2D(canvas, x, y, color=None):
    canvas.image.set_at((int(x),int(y)), canvas.lookupColor(color))
    canvas.dirty = True

def drawLine2D(canvas, x1, y1, x2, y2, color=None, thickness=1):
    pygame.draw.line(canvas.image, canvas.lookupColor(color), (int(x1),int(y1)), (int(x2),int(y2)), int(thickness))
    canvas.dirty = True

def drawCircle2D(canvas, x, y, radius, color=None, thickness=1):
    pygame.draw.circle(canvas.image, canvas.lookupColor(color), (int(x),int(y)), int(radius), int(thickness))
    canvas.dirty = True

def fillCircle2D(canvas, x, y, radius, color=None):
    drawCircle2D(canvas, x, y, radius, color, 0)

def drawEllipse2D(canvas, x, y, width, height, color=None, thickness=1):
    pygame.draw.ellipse(canvas.image, canvas.lookupColor(color), pygame.Rect(int(x-width/2), int(y-height/2), int(width), int(height)), int(thickness))
    canvas.dirty = True

def fillEllipse2D(canvas, x, y, width, height, color=None):
    drawEllipse2D(canvas, x, y, width, height, color, 0)

def drawRectangle2D(canvas, x, y, width, height, color=None, thickness=1):
    pygame.draw.rect(canvas.image, canvas.lookupColor(color), pygame.Rect(int(x),int(y),int(width),int(height)), int(thickness))
    canvas.dirty = True

def fillRectangle2D(canvas, x, y, width, height, color=None):
    drawRectangle2D(canvas, x, y, width, height, color, 0)

def drawPolygon2D(canvas, pointlist, color=None, thickness=1):
    pygame.draw.polygon(canvas.image, canvas.lookupColor(color), pointlist, int(thickness))
    canvas.dirty = True
    
def fillPolygon2D(canvas, pointlist, color=None):
    drawPolygon2D(canvas, pointlist, color, 0)


def drawString2D(canvas, text, x, y, size=None, color=None, bold=False, italic=False, font=None):
    font = _getFont(font, size, bold, italic)
    color = canvas.lookupColor(color)
    textimage = font.render(str(text), False, color)
    if canvas.transparent:
        textimage.set_alpha(canvas.opacity)
    canvas.image.blit(textimage, (int(x), int(y)))
    canvas.dirty = True
    return (textimage.get_width(), textimage.get_height())

def sizeString(text, size=None, bold=False, italic=False, font=None):
    font = _getFont(font, size, bold, italic)
    textimage = font.render(str(text), False, (1,1,1))
    return (textimage.get_width(), textimage.get_height())
 
def getFontList():
    if sys.platform != 'darwin':
        return pygame.font.get_fonts()
    else:
        _initMacFonts()
        return sorted(_GLI.macFonts.keys())

def setDefaultFont(font, size=None):
    _GLI.defaultFont = font
    if size is not None:
        _GLI.defaultFontSize = size

def _getFont(font, size, bold, italic):
    if font is None and _GLI.defaultFont is not None:
        font = _GLI.defaultFont
    if size is None:
        size = _GLI.defaultFontSize
    fontSignature = (font,size,bold,italic)
    if fontSignature in _GLI.fonts:
        font = _GLI.fonts[fontSignature]
    else:
        extensions = ('.ttf', '.ttc', '.otf', '.dfont')
        if font is not None and font.endswith(extensions):
            font = _loadFontFile(font, size)
        else:
            if sys.platform != 'darwin':
                font = pygame.font.SysFont(font, size, bold, italic)
            else:
                _initMacFonts()
                if font in _GLI.macFonts:
                    font = _GLI.macFonts[font]
                font = _loadFontFile(font, size)
        _GLI.fonts[fontSignature] = font
    return font


def _loadFontFile(font, size):
    try:
        font = pygame.font.Font(font, size)
    except IOError:
        print("Failed to load font: " + font)
        font = pygame.font.Font(None, size)
    return font


# used on Macs as long as pygame's font handling is broken
def _initMacFonts():
    if _GLI.macFonts is not None: return
    _GLI.macFonts = dict()
    folders = ['/System/Library/Fonts', '/Library/Fonts']
    if 'HOME' in os.environ:
        folders.append(os.environ['HOME'] + '/Library/Fonts')
    extensions = ('.ttf', '.ttc', '.otf', '.dfont')
    for folder in folders:
        if not os.path.isdir(folder): continue
        files = os.listdir(folder)
        for filename in files:
            if filename.endswith(extensions):
                dot = filename.rfind('.')
                fontname = filename[:dot]
                _GLI.macFonts[fontname] = os.path.join(folder, filename)
                

#########################################################

def loadImage(filename, rotate=0, scale=1, flipHorizontal=False, flipVertical=False):
    image = pygame.image.load(filename)
    if flipHorizontal or flipVertical:
        image = pygame.transform.flip(image, flipHorizontal, flipVertical)
    if rotate != 0 or scale != 1:
        image = pygame.transform.rotozoom(image, rotate, scale)
    return image

def loadImagePIL(pilImage):
    pilImage = pilImage.convert("RGBA")
    return pygame.image.frombuffer(pilImage.tobytes(), pilImage.size, pilImage.mode)


def drawImage2D(canvas, image, x, y, rotate=0, scale=1, flipHorizontal=False, flipVertical=False):
    if flipHorizontal or flipVertical:
        image = pygame.transform.flip(image, flipHorizontal, flipVertical)
    if rotate != 0 or scale != 1:
        image = pygame.transform.rotozoom(image, rotate, scale)
    if canvas.transparent:
        image.set_alpha(canvas.opacity)
    canvas.image.blit(image, (int(x-image.get_width()/2),int(y-image.get_height()/2)))
    canvas.dirty = True

def getImageWidth(image):
    return image.get_width()

def getImageHeight(image):
    return image.get_height()

def getImagePixel(image, x, y):
    return image.get_at((int(x),int(y)))

def resizeImage(image, width, height):
    return pygame.transform.scale(image, (int(width), int(height)))

def tileImage(image, horizontalRepeat, verticalRepeat):
    if isinstance(image, str):
        image = loadImage(image)
    tile_width = image.get_width()
    tile_height = image.get_height()
    new_width = tile_width * horizontalRepeat
    new_height = tile_height * verticalRepeat
    new_image = pygame.Surface((new_width,new_height))
    for h in range(horizontalRepeat):
        for v in range(verticalRepeat):
            new_image.blit(image, (h*tile_width, v*tile_height))
    return new_image
            

def saveImage(image, filename):
    pygame.image.save(image, filename)

def saveScreenShot(filename):
    pygame.image.save(_GLI.screen, filename)

#########################################################
#########################################################

def draw3D(model, x=0, y=0, z=0, anglex=0, angley=0, anglez=0, scale=1):
    glPushMatrix()
    if x != 0 or y != 0 or z != 0:
        glTranslate(x, y, z)
    if angley != 0:
        glRotate(angley, 0, 1, 0)
    if anglex != 0:
        glRotate(anglex, 1, 0, 0)
    if anglez != 0:
        glRotate(anglez, 0, 0, 1)
    if scale != 1:
        glEnable(GL_RESCALE_NORMAL)
        glScale(scale, scale, scale)
    model.draw()
    if scale != 1:
        glDisable(GL_RESCALE_NORMAL)
    glPopMatrix()

def draw2D(canvas, x, y):
    if _GLI.selectionDrawingOn:
        return
    # _GLI.hasWindowPos = False # TESTING!
    if _GLI.textureMapsEnabled:
        glDisable(GL_TEXTURE_2D)
    if _GLI.lightingEnabled:
        glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    if _GLI.hasWindowPos:
        if _GLI.currentViewport != None:
            cv = _GLI.currentViewport
            x += cv.x
            y += cv.y
        y = _GLI.windowHeight - (y + canvas.height)
        glWindowPos2d(x,y)
    else:
        y = _GLI.viewportHeight - (y + canvas.height)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, _GLI.viewportWidth, 0, _GLI.viewportHeight)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glRasterPos2d(x,y)
    glDrawPixels(canvas.width, canvas.height, GL_RGBA, GL_UNSIGNED_BYTE, canvas.getImageData())
    if not _GLI.hasWindowPos:
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    if _GLI.textureMapsEnabled:
        glEnable(GL_TEXTURE_2D)
    if _GLI.lightingEnabled:
        glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)

#################################################################    

def rotateXAxis(angle):
    glPushMatrix()
    glRotate(angle, 1, 0, 0)
    _GLI.numPushedMatrices += 1
    
def rotateYAxis(angle):
    glPushMatrix()
    glRotate(angle, 0, 1, 0)
    _GLI.numPushedMatrices += 1
    
def rotateZAxis(angle):
    glPushMatrix()
    glRotate(angle, 0, 0, 1)
    _GLI.numPushedMatrices += 1

def rotateAroundVector(angle, x, y, z):
    glPushMatrix()
    glRotate(angle, x, y, z)
    _GLI.numPushedMatrices += 1

    
def translateAxes(x=0, y=0, z=0):
    glPushMatrix()
    glTranslate(x,y,z)
    _GLI.numPushedMatrices += 1

def endTransformation():
    glPopMatrix()
    _GLI.numPushedMatrices -= 1



##########################################################################

def addLight(x=0, y=0, z=0, intensity=1.0):
    if not _GLI.lightingEnabled:
        _GLI.lightingEnabled = True
        glEnable(GL_LIGHTING)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.3, 0.3, 0.3));
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
    lightNum = GL_LIGHT0 + _GLI.numLights
    _GLI.numLights += 1
    glLightfv(lightNum, GL_DIFFUSE, (intensity, intensity, intensity, 1.0))
    glLightfv(lightNum, GL_POSITION, (x,y,z,1) )
    _GLI.lights.append( (x,y,z,1) )
    glEnable(lightNum)
    
def enableLighting():
    _GLI.lightingEnabled = True
    glEnable(GL_LIGHTING)

def disableLighting():
    _GLI.lightingEnabled = False
    glDisable(GL_LIGHTING)

def removeAllLights():
    _GLI.numLights = 0
    _GLI.lights = []

def _drawLights():
    if _GLI.lightingEnabled and not _GLI.selectionDrawingOn:
        for lightNum in range(len(_GLI.lights)):
            glLightfv(GL_LIGHT0 + lightNum, GL_POSITION, _GLI.lights[lightNum])


def setAmbientLight(intensity=0.3):
    if not _GLI.lightingEnabled:
        _GLI.lightingEnabled = True
        glEnable(GL_LIGHTING)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (intensity,intensity,intensity));
    

############################################################################
    
def makeColorsWebPage():
    web = file("colors.html", "w")
    web.write("""<html><head><title>Colors</title></head>
                 <body><center>
                 <h1>Color Names and Values</h1>
                 <table>
              """)
    count = 0
    for (name, red, green, blue, hexcode) in _GLI.colorsList:
        if count % 4 == 0:
            if count > 0:
                web.write('</tr>')
            web.write('<tr>\n')   
        fontcolor = '#000000'
        r = int(red)
        g = int(green)
        b = int(blue)
        if (r+g+b) < 250:
            fontcolor = '#FFFFFF'
        web.write("""<td bgcolor="%s" align=center width=200 height=75>
                  <font color="%s"><b>%s<br>(%d,%d,%d)</b></font></td>""" % (hexcode, fontcolor, name, r, g, b))
        count = count+1
    web.write('</tr></table></center></body></html>')
    web.close()


_GLI.loadColors([
("aliceblue",240,248,255,"#f0f8ff"),
("antiquewhite",250,235,215,"#faebd7"),
("aqua",0,255,255,"#00ffff"),
("aquamarine",127,255,212,"#7fffd4"),
("azure",240,255,255,"#f0ffff"),
("beige",245,245,220,"#f5f5dc"),
("bisque",255,228,196,"#ffe4c4"),
("black",0,0,0,"#000000"),
("blanchedalmond",255,235,205,"#ffebcd"),
("blue",0,0,255,"#0000ff"),
("blueviolet",138,43,226,"#8a2be2"),
("brown",165,42,42,"#a52a2a"),
("burlywood",222,184,135,"#deb887"),
("cadetblue",95,158,160,"#5f9ea0"),
("chartreuse",127,255,0,"#7fff00"),
("chocolate",210,105,30,"#d2691e"),
("coral",255,127,80,"#ff7f50"),
("cornflowerblue",100,149,237,"#6495ed"),
("cornsilk",255,248,220,"#fff8dc"),
("crimson",220,20,60,"#dc143c"),
("cyan",0,255,255,"#00ffff"),
("darkblue",0,0,139,"#00008b"),
("darkcyan",0,139,139,"#008b8b"),
("darkgoldenrod",184,134,11,"#b8860b"),
("darkgray",169,169,169,"#a9a9a9"),
("darkgreen",0,100,0,"#006400"),
("darkgrey",169,169,169,"#a9a9a9"),
("darkkhaki",189,183,107,"#bdb76b"),
("darkmagenta",139,0,139,"#8b008b"),
("darkolivegreen",85,107,47,"#556b2f"),
("darkorange",255,140,0,"#ff8c00"),
("darkorchid",153,50,204,"#9932cc"),
("darkred",139,0,0,"#8b0000"),
("darksalmon",233,150,122,"#e9967a"),
("darkseagreen",143,188,143,"#8fbc8f"),
("darkslateblue",72,61,139,"#483d8b"),
("darkslategray",47,79,79,"#2f4f4f"),
("darkslategrey",47,79,79,"#2f4f4f"),
("darkturquoise",0,206,209,"#00ced1"),
("darkviolet",148,0,211,"#9400d3"),
("deeppink",255,20,147,"#ff1493"),
("deepskyblue",0,191,255,"#00bfff"),
("dimgray",105,105,105,"#696969"),
("dimgrey",105,105,105,"#696969"),
("dodgerblue",30,144,255,"#1e90ff"),
("firebrick",178,34,34,"#b22222"),
("floralwhite",255,250,240,"#fffaf0"),
("forestgreen",34,139,34,"#228b22"),
("fuchsia",255,0,255,"#ff00ff"),
("gainsboro",220,220,220,"#dcdcdc"),
("ghostwhite",248,248,255,"#f8f8ff"),
("gold",255,215,0,"#ffd700"),
("goldenrod",218,165,32,"#daa520"),
("gray",128,128,128,"#808080"),
("green",0,128,0,"#008000"),
("greenyellow",173,255,47,"#adff2f"),
("grey",128,128,128,"#808080"),
("honeydew",240,255,240,"#f0fff0"),
("hotpink",255,105,180,"#ff69b4"),
("indianred",205,92,92,"#cd5c5c"),
("indigo",75,0,130,"#4b0082"),
("ivory",255,255,240,"#fffff0"),
("khaki",240,230,140,"#f0e68c"),
("lavender",230,230,250,"#e6e6fa"),
("lavenderblush",255,240,245,"#fff0f5"),
("lawngreen",124,252,0,"#7cfc00"),
("lemonchiffon",255,250,205,"#fffacd"),
("lightblue",173,216,230,"#add8e6"),
("lightcoral",240,128,128,"#f08080"),
("lightcyan",224,255,255,"#e0ffff"),
("lightgoldenrodyellow",250,250,210,"#fafad2"),
("lightgray",211,211,211,"#d3d3d3"),
("lightgreen",144,238,144,"#90ee90"),
("lightgrey",211,211,211,"#d3d3d3"),
("lightpink",255,182,193,"#ffb6c1"),
("lightsalmon",255,160,122,"#ffa07a"),
("lightseagreen",32,178,170,"#20b2aa"),
("lightskyblue",135,206,250,"#87cefa"),
("lightslategray",119,136,153,"#778899"),
("lightslategrey",119,136,153,"#778899"),
("lightsteelblue",176,196,222,"#b0c4de"),
("lightyellow",255,255,224,"#ffffe0"),
("lime",0,255,0,"#00ff00"),
("limegreen",50,205,50,"#32cd32"),
("linen",250,240,230,"#faf0e6"),
("magenta",255,0,255,"#ff00ff"),
("maroon",128,0,0,"#800000"),
("mediumaquamarine",102,205,170,"#66cdaa"),
("mediumblue",0,0,205,"#0000cd"),
("mediumorchid",186,85,211,"#ba55d3"),
("mediumpurple",147,112,219,"#9370db"),
("mediumseagreen",60,179,113,"#3cb371"),
("mediumslateblue",123,104,238,"#7b68ee"),
("mediumspringgreen",0,250,154,"#00fa9a"),
("mediumturquoise",72,209,204,"#48d1cc"),
("mediumvioletred",199,21,133,"#c71585"),
("midnightblue",25,25,112,"#191970"),
("mintcream",245,255,250,"#f5fffa"),
("mistyrose",255,228,225,"#ffe4e1"),
("moccasin",255,228,181,"#ffe4b5"),
("navajowhite",255,222,173,"#ffdead"),
("navy",0,0,128,"#000080"),
("oldlace",253,245,230,"#fdf5e6"),
("olive",128,128,0,"#808000"),
("olivedrab",107,142,35,"#6b8e23"),
("orange",255,165,0,"#ffa500"),
("orangered",255,69,0,"#ff4500"),
("orchid",218,112,214,"#da70d6"),
("palegoldenrod",238,232,170,"#eee8aa"),
("palegreen",152,251,152,"#98fb98"),
("paleturquoise",175,238,238,"#afeeee"),
("palevioletred",219,112,147,"#db7093"),
("papayawhip",255,239,213,"#ffefd5"),
("peachpuff",255,218,185,"#ffdab9"),
("peru",205,133,63,"#cd853f"),
("pink",255,192,203,"#ffc0cb"),
("plum",221,160,221,"#dda0dd"),
("powderblue",176,224,230,"#b0e0e6"),
("purple",128,0,128,"#800080"),
("red",255,0,0,"#ff0000"),
("rosybrown",188,143,143,"#bc8f8f"),
("royalblue",65,105,225,"#4169e1"),
("saddlebrown",139,69,19,"#8b4513"),
("salmon",250,128,114,"#fa8072"),
("sandybrown",244,164,96,"#f4a460"),
("seagreen",46,139,87,"#2e8b57"),
("seashell",255,245,238,"#fff5ee"),
("sienna",160,82,45,"#a0522d"),
("silver",192,192,192,"#c0c0c0"),
("skyblue",135,206,235,"#87ceeb"),
("slateblue",106,90,205,"#6a5acd"),
("slategray",112,128,144,"#708090"),
("slategrey",112,128,144,"#708090"),
("snow",255,250,250,"#fffafa"),
("springgreen",0,255,127,"#00ff7f"),
("steelblue",70,130,180,"#4682b4"),
("tan",210,180,140,"#d2b48c"),
("teal",0,128,128,"#008080"),
("thistle",216,191,216,"#d8bfd8"),
("tomato",255,99,71,"#ff6347"),
("turquoise",64,224,208,"#40e0d0"),
("violet",238,130,238,"#ee82ee"),
("wheat",245,222,179,"#f5deb3"),
("white",255,255,255,"#ffffff"),
("whitesmoke",245,245,245,"#f5f5f5"),
("yellow",255,255,0,"#ffff00"),
("yellowgreen",154,205,50,"#9acd32")])

_GLI.loadKeys([
    (pygame.K_UP, ['up','up arrow']),
    (pygame.K_DOWN, ['down','down arrow']),
    (pygame.K_RIGHT, ['right','right arrow']),
    (pygame.K_LEFT, ['left','left arrow']),
    (pygame.K_BACKSPACE, ['backspace']),
    (pygame.K_SPACE, ['space', ' ']),
    (pygame.K_RETURN, ['enter', 'return']),
    (pygame.K_TAB, ['tab']),
    
    (pygame.K_a, ['a']),
    (pygame.K_b, ['b']),
    (pygame.K_c, ['c']),
    (pygame.K_d, ['d']),
    (pygame.K_e, ['e']),
    (pygame.K_f, ['f']),
    (pygame.K_g, ['g']),
    (pygame.K_h, ['h']),
    (pygame.K_i, ['i']),
    (pygame.K_j, ['j']),
    (pygame.K_k, ['k']),
    (pygame.K_l, ['l']),
    (pygame.K_m, ['m']),
    (pygame.K_n, ['n']),
    (pygame.K_o, ['o']),
    (pygame.K_p, ['p']),
    (pygame.K_q, ['q']),
    (pygame.K_r, ['r']),
    (pygame.K_s, ['s']),
    (pygame.K_t, ['t']),
    (pygame.K_u, ['u']),
    (pygame.K_v, ['v']),
    (pygame.K_w, ['w']),
    (pygame.K_x, ['x']),
    (pygame.K_y, ['y']),
    (pygame.K_z, ['z']),
    (pygame.K_0, ['0']),
    (pygame.K_1, ['1']),
    (pygame.K_2, ['2']),
    (pygame.K_3, ['3']),
    (pygame.K_4, ['4']),
    (pygame.K_5, ['5']),
    (pygame.K_6, ['6']),
    (pygame.K_7, ['7']),
    (pygame.K_8, ['8']),
    (pygame.K_9, ['9']),

    (pygame.K_BACKQUOTE, ['`' ,'backquote', 'grave', 'grave accent']),
    (pygame.K_MINUS, ['-','minus','dash','hyphen']),
    (pygame.K_EQUALS, ['=','equals']),
    (pygame.K_LEFTBRACKET, ['[','left bracket']),
    (pygame.K_RIGHTBRACKET, [']','right bracket']),
    (pygame.K_BACKSLASH, ['backslash', '\\']),
    (pygame.K_SEMICOLON, [';','semicolon']),
    (pygame.K_QUOTE, ['quote', '\'']),
    (pygame.K_COMMA, [',','comma']),
    (pygame.K_PERIOD, ['.','period']),
    (pygame.K_SLASH, ['/','slash','divide']),

    (pygame.K_DELETE, ['delete']),
    (pygame.K_INSERT, ['insert']),
    (pygame.K_HOME, ['home']),
    (pygame.K_END, ['end']),
    (pygame.K_PAGEUP, ['page up']),
    (pygame.K_PAGEDOWN, ['page down']),
    (pygame.K_CLEAR, ['clear']),
    (pygame.K_PAUSE, ['pause']),

    (pygame.K_F1, ['F1']),
    (pygame.K_F2, ['F2']),
    (pygame.K_F3, ['F3']),
    (pygame.K_F4, ['F4']),
    (pygame.K_F5, ['F5']),
    (pygame.K_F6, ['F6']),
    (pygame.K_F7, ['F7']),
    (pygame.K_F8, ['F8']),
    (pygame.K_F9, ['F9']),
    (pygame.K_F10, ['F10']),
    (pygame.K_F11, ['F11']),
    (pygame.K_F12, ['F12']),
    (pygame.K_F13, ['F13']),
    (pygame.K_F14, ['F14']),
    (pygame.K_F15, ['F15']),

    (pygame.K_RSHIFT, ['right shift']),
    (pygame.K_LSHIFT, ['left shift']),
    (pygame.K_RCTRL, ['right ctrl']),
    (pygame.K_LCTRL, ['left ctrl']),
    (pygame.K_RALT, ['right alt', 'right option']),
    (pygame.K_LALT, ['left alt', 'left option']),
    (pygame.K_RMETA, ['right command']),
    (pygame.K_LMETA, ['left command']),
    (pygame.K_LSUPER, ['left windows']),
    (pygame.K_RSUPER, ['right windows']),

    (pygame.K_NUMLOCK, ['numlock']),
    (pygame.K_CAPSLOCK, ['capslock']),
    (pygame.K_SCROLLOCK, ['scrollock']),
    (pygame.K_MODE, ['mode']),
    (pygame.K_HELP, ['help']),
    (pygame.K_PRINT, ['print','print screen','prtsc']),
    (pygame.K_SYSREQ, ['sysrq']),
    (pygame.K_BREAK, ['break']),
    (pygame.K_MENU, ['menu']),
    (pygame.K_POWER, ['power']),
    (pygame.K_EURO, ['euro']),
    
    (pygame.K_KP0, ['keypad 0']),
    (pygame.K_KP1, ['keypad 1']),
    (pygame.K_KP2, ['keypad 2']),
    (pygame.K_KP3, ['keypad 3']),
    (pygame.K_KP4, ['keypad 4']),
    (pygame.K_KP5, ['keypad 5']),
    (pygame.K_KP6, ['keypad 6']),
    (pygame.K_KP7, ['keypad 7']),
    (pygame.K_KP8, ['keypad 8']),
    (pygame.K_KP9, ['keypad 9']),
    (pygame.K_KP_PERIOD, ['keypad period']),
    (pygame.K_KP_DIVIDE, ['keypad divide']),
    (pygame.K_KP_MULTIPLY, ['keypad multiply']),
    (pygame.K_KP_MINUS, ['keypad minus']),
    (pygame.K_KP_PLUS, ['keypad plus']),
    (pygame.K_KP_EQUALS, ['keypad equals']),
    (pygame.K_KP_ENTER, ['keypad enter'])
])

##    (pygame.K_EXCLAIM, ['!','exclaimation','exclaimation point']),
##    (pygame.K_QUOTEDBL, ['"','double quote']),
##    (pygame.K_HASH, ['#','hash','pound','pound sign']),
##    (pygame.K_DOLLAR, ['$','dollar','dollar sign']),
##    (pygame.K_AMPERSAND, ['&','ampersand','and']),
##    (pygame.K_LEFTPAREN, ['(','left parenthesis']),
##    (pygame.K_RIGHTPAREN, [')','right parenthesis']),
##    (pygame.K_ASTERISK, ['*','asterisk','star','multiply']),
##    (pygame.K_PLUS, ['+','plus','add']),
##    (pygame.K_COLON, [':','colon']),
##    (pygame.K_LESS, ['<','less-than']),
##    (pygame.K_GREATER, ['>','greater-than']),
##    (pygame.K_QUESTION, ['?','question','question mark']),
##    (pygame.K_AT, ['@','at','at sign']),
##    (pygame.K_CARET, ['^','caret']),
##    (pygame.K_UNDERSCORE, ['_','underscore']),

#############################################################################
#############################################################################

# Polyhedra data is from Kaleido by Zvi Har'El (http://www.math.technion.ac.il/S/rl/kaleido/)
_GLI.loadPolyhedra({
    'Pentagonal prism' : (
        [(0.000000,0.000000,1.000000),(0.873711,0.000000,0.486446),(-0.301860,0.819909,0.486446),(-0.665131,-0.566543,0.486446),(0.571851,0.819909,-0.027109),(0.748563,-0.566543,-0.344503),(-0.966991,0.253366,-0.027109),(-0.202494,-0.916687,-0.344503),(0.446703,0.253366,-0.858057),(-0.504353,-0.096777,-0.858057)],
        [(0,1,4,2),(0,2,6,3),(0,3,7,5,1),(1,5,8,4),(2,4,8,9,6),(3,6,9,7),(5,7,9,8)]),
    'Pentagonal_antiprism' : (
        [(0.000000,0.000000,1.000000),(0.894427,0.000000,0.447214),(0.276393,0.850651,0.447214),(-0.723607,0.525731,0.447214),(-0.723607,-0.525731,0.447214),(0.723607,-0.525731,-0.447214),(0.723607,0.525731,-0.447214),(-0.894427,-0.000000,-0.447214),(-0.276393,-0.850651,-0.447214),(0.000000,-0.000000,-1.000000)],
        [(0,1,2),(0,2,3),(0,3,4),(0,4,8,5,1),(1,5,6),(1,6,2),(2,6,9,7,3),(3,7,4),(4,7,8),(5,8,9),(5,9,6),(7,9,8)]),
    'Pentagrammic_prism' : (
        [(0.000000,0.000000,1.000000),(0.998742,0.000000,0.050140),(-0.903371,0.425919,0.050140),(0.635471,-0.770495,0.050140),(0.095371,0.425919,-0.899721),(0.018214,-0.770495,0.637186),(-0.267900,-0.344576,-0.899721),(0.606000,0.476192,0.637186),(-0.885157,-0.344576,-0.312675),(-0.297371,0.902111,-0.312675)],
        [(0,1,4,2),(0,2,6,3),(0,3,7,5,1),(1,5,8,4),(2,4,8,9,6),(3,6,9,7),(5,7,9,8)]),
    'Pentagrammic_antiprism' : (
        [(0.000000,0.000000,1.000000),(0.987059,0.000000,-0.160357),(-0.188511,0.968891,-0.160357),(-0.915054,-0.370083,-0.160357),(0.538031,-0.827531,-0.160357),(-0.072005,-0.827531,0.556783),(-0.305018,-0.370083,-0.877498),(0.144010,0.457448,-0.877498),(0.654538,0.511442,0.556783),(-0.843049,0.457448,0.282860)],
        [(0,1,2),(0,2,3),(0,3,4),(0,4,8,5,1),(1,5,6),(1,6,2),(2,6,9,7,3),(3,7,4),(4,7,8),(5,8,9),(5,9,6),(7,9,8)]),
    'Pentagrammic_crossed_antiprism' : (
        [(0.000000,0.000000,1.000000),(0.894427,0.000000,-0.447214),(-0.723607,0.525731,-0.447214),(0.276393,-0.850651,-0.447214),(0.276393,0.850651,-0.447214),(-0.276393,0.850651,0.447214),(-0.276393,-0.850651,0.447214),(-0.894427,0.000000,0.447214),(0.723607,-0.525731,0.447214),(0.000000,0.000000,-1.000000)],
        [(0,1,2),(0,2,3),(0,3,4),(0,4,8,5,1),(1,5,6),(1,6,2),(2,6,9,7,3),(3,7,4),(4,7,8),(5,8,9),(5,9,6),(7,9,8)]),
    'Tetrahedron' : (
        [(0.000000,0.000000,1.000000),(0.942809,0.000000,-0.333333),(-0.471405,0.816497,-0.333333),(-0.471405,-0.816497,-0.333333)],
        [(0,1,2),(0,2,3),(0,3,1),(1,3,2)]),
    'Truncated_tetrahedron' : (
        [(0.000000,0.000000,1.000000),(0.771389,0.000000,0.636364),(-0.642824,0.426401,0.636364),(0.299985,-0.710669,0.636364),(0.899954,0.426401,-0.090909),(-0.985664,0.142134,-0.090909),(-0.514259,0.852803,-0.090909),(-0.042855,-0.994937,-0.090909),(0.557114,0.142134,-0.818182),(0.257130,0.852803,-0.454545),(-0.685679,-0.568535,-0.454545),(0.085710,-0.568535,-0.818182)],
        [(0,1,4,9,6,2),(0,2,5,10,7,3),(0,3,1),(1,3,7,11,8,4),(2,6,5),(4,8,9),(5,6,9,8,11,10),(7,10,11)]),
    'Octahemioctahedron' : (
        [(0.000000,0.000000,1.000000),(0.866025,0.000000,0.500000),(-0.866025,0.000000,0.500000),(-0.288675,0.816497,0.500000),(0.288675,-0.816497,0.500000),(0.866025,0.000000,-0.500000),(0.577350,0.816497,-0.000000),(-0.577350,-0.816497,0.000000),(-0.866025,0.000000,-0.500000),(-0.288675,0.816497,-0.500000),(0.288675,-0.816497,-0.500000),(-0.000000,0.000000,-1.000000)],
        [(0,1,5,11,8,2),(0,2,3),(0,3,9,11,10,4),(0,4,1),(1,4,7,8,9,6),(1,6,5),(2,8,7),(2,7,10,5,6,3),(3,6,9),(4,10,7),(5,10,11),(8,11,9)]),
    'Octahedron' : (
        [(0.000000,0.000000,1.000000),(1.000000,0.000000,0.000000),(0.000000,1.000000,0.000000),(-1.000000,0.000000,0.000000),(-0.000000,-1.000000,0.000000),(0.000000,0.000000,-1.000000)],
        [(0,1,2),(0,2,3),(0,3,4),(0,4,1),(1,4,5),(1,5,2),(2,5,3),(3,5,4)]),
    'Cube' : (
        [(0.000000,0.000000,1.000000),(0.942809,0.000000,0.333333),(-0.471405,0.816497,0.333333),(-0.471405,-0.816497,0.333333),(0.471405,0.816497,-0.333333),(0.471405,-0.816497,-0.333333),(-0.942809,0.000000,-0.333333),(0.000000,0.000000,-1.000000)],
        [(0,1,4,2),(0,2,6,3),(0,3,5,1),(1,5,7,4),(2,4,7,6),(3,6,7,5)]),
    'Cuboctahedron' : (
        [(0.000000,0.000000,1.000000),(0.866025,0.000000,0.500000),(0.288675,0.816497,0.500000),(-0.866025,-0.000000,0.500000),(-0.288675,-0.816497,0.500000),(0.866025,0.000000,-0.500000),(0.577350,-0.816497,-0.000000),(-0.577350,0.816497,0.000000),(0.288675,0.816497,-0.500000),(-0.866025,-0.000000,-0.500000),(-0.288675,-0.816497,-0.500000),(-0.000000,0.000000,-1.000000)],
        [(0,1,2),(0,2,7,3),(0,3,4),(0,4,6,1),(1,6,5),(1,5,8,2),(2,8,7),(3,7,9),(3,9,10,4),(4,10,6),(5,6,10,11),(5,11,8),(7,8,11,9),(9,11,10)]),
    'Truncated_octahedron' : (
        [(0.000000,0.000000,1.000000),(0.600000,0.000000,0.800000),(-0.400000,0.447214,0.800000),(-0.066667,-0.596285,0.800000),(0.800000,0.447214,0.400000),(0.533333,-0.596285,0.600000),(-0.866667,0.298142,0.400000),(-0.200000,0.894427,0.400000),(-0.533333,-0.745356,0.400000),(0.933333,0.298142,-0.200000),(0.400000,0.894427,0.200000),(0.666667,-0.745356,-0.000000),(-0.666667,0.745356,0.000000),(-0.933333,-0.298142,0.200000),(-0.400000,-0.894427,-0.200000),(0.533333,0.745356,-0.400000),(0.866667,-0.298142,-0.400000),(0.200000,-0.894427,-0.400000),(-0.533333,0.596285,-0.600000),(-0.800000,-0.447214,-0.400000),(0.066667,0.596285,-0.800000),(0.400000,-0.447214,-0.800000),(-0.600000,-0.000000,-0.800000),(0.000000,-0.000000,-1.000000)],
        [(0,1,4,10,7,2),(0,2,6,13,8,3),(0,3,5,1),(1,5,11,16,9,4),(2,7,12,6),(3,8,14,17,11,5),(4,9,15,10),(6,12,18,22,19,13),(7,10,15,20,18,12),(8,13,19,14),(9,16,21,23,20,15),(11,17,21,16),(14,19,22,23,21,17),(18,20,23,22)]),
    'Truncated_cube' : (
        [(0.000000,0.000000,1.000000),(0.539504,0.000000,0.841983),(-0.460496,0.281085,0.841983),(0.246611,-0.479841,0.841983),(0.841983,0.281085,0.460496),(-0.865124,0.198757,0.460496),(-0.572231,0.678598,0.460496),(0.134876,-0.877355,0.460496),(0.976859,0.198757,-0.079009),(0.730248,0.678598,0.079009),(-0.976859,-0.198757,0.079009),(-0.269752,0.959683,0.079009),(-0.269752,-0.959683,0.079009),(0.269752,-0.959683,-0.079009),(0.865124,-0.198757,-0.460496),(0.269752,0.959683,-0.079009),(-0.730248,-0.678598,-0.079009),(-0.841983,-0.281085,-0.460496),(-0.134876,0.877355,-0.460496),(0.572231,-0.678598,-0.460496),(0.460496,-0.281085,-0.841983),(-0.539504,-0.000000,-0.841983),(-0.246611,0.479841,-0.841983),(0.000000,0.000000,-1.000000)],
        [(0,1,4,9,15,11,6,2),(0,2,5,10,16,12,7,3),(0,3,1),(1,3,7,13,19,14,8,4),(2,6,5),(4,8,9),(5,6,11,18,22,21,17,10),(7,12,13),(8,14,20,23,22,18,15,9),(10,17,16),(11,15,18),(12,16,17,21,23,20,19,13),(14,19,20),(21,22,23)]),
    'Rhombicuboctahedron' : (
        [(0.000000,0.000000,1.000000),(0.667599,0.000000,0.744521),(-0.097768,0.660402,0.744521),(-0.638964,0.193427,0.744521),(-0.097768,-0.660402,0.744521),(0.569832,0.660402,0.489042),(0.972763,0.193427,0.127740),(0.569832,-0.660402,0.489042),(-0.333800,0.933949,0.127740),(-0.736731,-0.466974,0.489042),(-0.874996,0.466974,0.127740),(-0.333800,-0.933949,0.127740),(0.333800,0.933949,-0.127740),(0.874996,-0.466974,-0.127740),(0.736731,0.466974,-0.489042),(0.333800,-0.933949,-0.127740),(-0.569832,0.660402,-0.489042),(-0.972763,-0.193427,-0.127740),(-0.569832,-0.660402,-0.489042),(0.097768,0.660402,-0.744521),(0.638964,-0.193427,-0.744521),(0.097768,-0.660402,-0.744521),(-0.667599,-0.000000,-0.744521),(0.000000,-0.000000,-1.000000)],
        [(0,1,5,2),(0,2,3),(0,3,9,4),(0,4,7,1),(1,7,13,6),(1,6,5),(2,5,12,8),(2,8,10,3),(3,10,17,9),(4,9,11),(4,11,15,7),(5,6,14,12),(6,13,20,14),(7,15,13),(8,12,19,16),(8,16,10),(9,17,18,11),(10,16,22,17),(11,18,21,15),(12,14,19),(13,15,21,20),(14,20,23,19),(16,19,23,22),(17,22,18),(18,22,23,21),(20,21,23)]),
    'Truncated_cuboctahedron' : (
        [(0.000000,0.000000,1.000000),(0.421318,0.000000,0.906913),(-0.020567,0.420816,0.906913),(-0.333027,-0.258074,0.906913),(0.400751,0.420816,0.813826),(0.684125,-0.258074,0.682181),(-0.374160,0.583557,0.720739),(-0.382679,-0.623045,0.682181),(-0.686620,-0.095332,0.720739),(0.642991,0.583557,0.496007),(0.634472,-0.623045,0.457449),(0.926365,-0.095332,0.364362),(-0.452899,0.813709,0.364362),(-0.707187,0.325484,0.627652),(-0.736273,-0.460303,0.496007),(-0.119872,-0.881119,0.457449),(0.564252,0.813709,0.139630),(0.905798,0.325484,0.271275),(0.876712,-0.460303,0.139630),(0.301445,-0.881119,0.364362),(-0.785926,0.555635,0.271275),(-0.210659,0.976451,0.046543),(-0.827059,-0.555635,0.085101),(-0.210659,-0.976451,0.046543),(0.827059,0.555635,-0.085101),(0.210659,0.976451,-0.046543),(0.785926,-0.555635,-0.271275),(0.210659,-0.976451,-0.046543),(-0.876712,0.460303,-0.139630),(-0.301445,0.881119,-0.364362),(-0.905798,-0.325484,-0.271275),(-0.564252,-0.813709,-0.139630),(0.736273,0.460303,-0.496007),(0.119872,0.881119,-0.457449),(0.707187,-0.325484,-0.627652),(0.452899,-0.813709,-0.364362),(-0.926365,0.095332,-0.364362),(-0.634472,0.623045,-0.457449),(-0.642991,-0.583557,-0.496007),(0.686620,0.095332,-0.720739),(0.382679,0.623045,-0.682181),(0.374160,-0.583557,-0.720739),(-0.684125,0.258074,-0.682181),(-0.400751,-0.420816,-0.813826),(0.333027,0.258074,-0.906913),(0.020567,-0.420816,-0.906913),(-0.421318,0.000000,-0.906913),(0.000000,0.000000,-1.000000)],
        [(0,1,4,2),(0,2,6,13,8,3),(0,3,7,15,19,10,5,1),(1,5,11,17,9,4),(2,4,9,16,25,21,12,6),(3,8,14,7),(5,10,18,11),(6,12,20,13),(7,14,22,31,23,15),(8,13,20,28,36,30,22,14),(9,17,24,16),(10,19,27,35,26,18),(11,18,26,34,39,32,24,17),(12,21,29,37,28,20),(15,23,27,19),(16,24,32,40,33,25),(21,25,33,29),(22,30,38,31),(23,31,38,43,45,41,35,27),(26,35,41,34),(28,37,42,36),(29,33,40,44,47,46,42,37),(30,36,42,46,43,38),(32,39,44,40),(34,41,45,47,44,39),(43,46,47,45)]),
    'Snub_cube' : (
        [(0.000000,0.000000,1.000000),(0.690766,0.000000,0.723078),(0.289875,0.627001,0.723078),(-0.447477,0.526233,0.723078),(-0.665437,-0.185340,0.723078),(-0.111015,-0.681787,0.723078),(0.579751,-0.681787,0.446157),(0.980641,-0.185340,0.063181),(0.823039,0.526233,0.213740),(0.243289,0.967894,0.063181),(-0.494064,0.867127,0.063181),(-0.934054,0.286107,0.213740),(-0.651666,-0.727768,0.213740),(0.025329,-0.997681,0.063181),(0.618850,-0.727768,-0.295598),(0.762681,-0.084573,-0.641221),(0.605079,0.627001,-0.490662),(-0.111015,0.812341,-0.572519),(-0.751124,0.441661,-0.490662),(-0.920283,-0.256321,-0.295598),(-0.414662,-0.766359,-0.490662),(0.178860,-0.496447,-0.849441),(0.171373,0.240126,-0.955495),(-0.468735,-0.130554,-0.873638)],
        [(0,1,2),(0,2,3),(0,3,4),(0,4,5),(0,5,6,1),(1,6,7),(1,7,8),(1,8,2),(2,8,9),(2,9,10,3),(3,10,11),(3,11,4),(4,11,19,12),(4,12,5),(5,12,13),(5,13,6),(6,13,14),(6,14,7),(7,14,15),(7,15,16,8),(8,16,9),(9,16,17),(9,17,10),(10,17,18),(10,18,11),(11,18,19),(12,19,20),(12,20,13),(13,20,21,14),(14,21,15),(15,21,22),(15,22,16),(16,22,17),(17,22,23,18),(18,23,19),(19,23,20),(20,23,21),(21,23,22)]),
    'Small_cubicuboctahedron' : (
        [(0.000000,0.000000,1.000000),(0.667599,0.000000,0.744521),(-0.638964,0.193427,0.744521),(-0.097768,0.660402,0.744521),(-0.097768,-0.660402,0.744521),(0.972763,0.193427,0.127740),(0.569832,0.660402,0.489042),(0.569832,-0.660402,0.489042),(-0.736731,-0.466974,0.489042),(-0.874996,0.466974,0.127740),(-0.333800,0.933949,0.127740),(-0.333800,-0.933949,0.127740),(0.874996,-0.466974,-0.127740),(0.736731,0.466974,-0.489042),(0.333800,0.933949,-0.127740),(0.333800,-0.933949,-0.127740),(-0.972763,-0.193427,-0.127740),(-0.569832,0.660402,-0.489042),(-0.569832,-0.660402,-0.489042),(0.638964,-0.193427,-0.744521),(0.097768,0.660402,-0.744521),(0.097768,-0.660402,-0.744521),(-0.667599,-0.000000,-0.744521),(0.000000,-0.000000,-1.000000)],
        [(0,1,5,13,20,17,9,2),(0,2,3),(0,3,10,17,22,18,11,4),(0,4,7,1),(1,7,15,21,23,20,14,6),(1,6,5),(2,9,16,8),(2,8,11,15,12,5,6,3),(3,6,14,10),(4,11,8),(4,8,16,22,23,19,12,7),(5,12,19,13),(7,12,15),(9,17,10),(9,10,14,13,19,21,18,16),(11,18,21,15),(13,14,20),(16,18,22),(17,20,23,22),(19,23,21)]),
    'Great_cubicuboctahedron' : (
        [(0.000000,0.000000,1.000000),(0.996874,0.000000,0.079009),(0.455678,0.886631,0.079009),(-0.850885,0.519377,0.079009),(-0.850885,-0.519377,0.079009),(0.042759,0.886631,0.460496),(0.145989,0.519377,-0.841983),(0.145989,-0.519377,-0.841983),(-0.395207,0.367255,-0.841983),(0.808126,-0.367255,0.460496),(-0.498437,-0.734510,0.460496),(-0.498437,0.734510,0.460496),(-0.808126,0.367255,-0.460496),(0.395207,-0.367255,0.841983),(0.498437,-0.734510,-0.460496),(0.498437,0.734510,-0.460496),(-0.042759,-0.886631,-0.460496),(-0.145989,0.519377,0.841983),(-0.145989,-0.519377,0.841983),(-0.455678,-0.886631,-0.079009),(0.850885,0.519377,-0.079009),(0.850885,-0.519377,-0.079009),(-0.996874,-0.000000,-0.079009),(0.000000,-0.000000,-1.000000)],
        [(0,1,5,13,20,17,9,2),(0,2,3),(0,3,10,17,22,18,11,4),(0,4,7,1),(1,7,15,21,23,20,14,6),(1,6,5),(2,9,16,8),(2,8,11,15,12,5,6,3),(3,6,14,10),(4,11,8),(4,8,16,22,23,19,12,7),(5,12,19,13),(7,12,15),(9,17,10),(9,10,14,13,19,21,18,16),(11,18,21,15),(13,14,20),(16,18,22),(17,20,23,22),(19,23,21)]),
    'Cubitruncated_cuboctahedron' : (
        [(0.000000,0.000000,1.000000),(0.699854,0.000000,0.714286),(0.460708,0.526825,0.714286),(-0.693993,-0.090389,0.714286),(0.170819,0.526825,0.832632),(0.995605,-0.090389,0.024510),(0.227423,0.963260,0.142857),(0.509023,-0.218218,0.832632),(-0.975592,-0.218218,0.024510),(-0.927277,0.346047,0.142857),(-0.062466,0.963260,0.261204),(0.219134,-0.218218,0.950979),(0.714005,-0.218218,-0.665265),(0.762320,0.346047,-0.546918),(-0.054176,0.835431,-0.546918),(-0.466569,0.872872,-0.142857),(-0.020013,0.308607,0.950979),(0.344066,-0.835431,0.428571),(-0.810635,0.398996,0.428571),(-0.679842,-0.308607,-0.665265),(-0.878963,-0.398996,0.261204),(-0.344066,0.835431,-0.428571),(0.233285,0.872872,-0.428571),(0.679842,0.308607,0.665265),(0.054176,-0.835431,0.546918),(0.878963,0.398996,-0.261204),(0.020013,-0.308607,-0.950979),(0.810635,-0.398996,-0.428571),(-0.349927,0.925820,0.142857),(-0.219134,0.218218,-0.950979),(-0.714005,0.218218,0.665265),(0.062466,-0.963260,-0.261204),(-0.349927,-0.925820,0.142857),(-0.762320,-0.346047,0.546918),(0.349927,0.925820,-0.142857),(-0.509023,0.218218,-0.832632),(0.975592,0.218218,-0.024510),(-0.227423,-0.963260,-0.142857),(0.349927,-0.925820,-0.142857),(0.927277,-0.346047,-0.142857),(-0.170819,-0.526825,-0.832632),(-0.995605,0.090389,-0.024510),(-0.233285,-0.872872,0.428571),(-0.460708,-0.526825,-0.714286),(0.693993,0.090389,-0.714286),(0.466569,-0.872872,0.142857),(-0.699854,-0.000000,-0.714286),(0.000000,-0.000000,-1.000000)],
        [(0,1,4,11,23,16,7,2),(0,2,6,15,9,3),(0,3,8,19,26,12,5,1),(1,5,13,22,10,4),(2,7,17,31,40,29,14,6),(3,9,20,30,41,33,18,8),(4,10,21,35,43,37,24,11),(5,12,25,39,44,36,27,13),(6,14,28,34,21,10,22,15),(7,16,30,20,32,17),(8,18,28,14,29,19),(9,15,22,13,27,38,32,20),(11,24,38,27,36,23),(12,26,35,21,34,25),(16,23,36,44,47,46,41,30),(17,32,38,24,37,45,42,31),(18,33,42,45,39,25,34,28),(19,29,40,46,47,43,35,26),(31,42,33,41,46,40),(37,43,47,44,39,45)]),
    'Great_rhombicuboctahedron' : (
        [(0.000000,0.000000,1.000000),(0.996874,0.000000,0.079009),(-0.850885,0.519377,0.079009),(0.455678,0.886631,0.079009),(-0.850885,-0.519377,0.079009),(0.145989,0.519377,-0.841983),(0.042759,0.886631,0.460496),(0.145989,-0.519377,-0.841983),(-0.498437,-0.734510,0.460496),(-0.395207,0.367255,-0.841983),(0.808126,-0.367255,0.460496),(-0.498437,0.734510,0.460496),(0.498437,-0.734510,-0.460496),(-0.808126,0.367255,-0.460496),(0.395207,-0.367255,0.841983),(0.498437,0.734510,-0.460496),(-0.145989,0.519377,0.841983),(-0.042759,-0.886631,-0.460496),(-0.145989,-0.519377,0.841983),(0.850885,0.519377,-0.079009),(-0.455678,-0.886631,-0.079009),(0.850885,-0.519377,-0.079009),(-0.996874,0.000000,-0.079009),(0.000000,0.000000,-1.000000)],
        [(0,1,5,2),(0,2,3),(0,3,9,4),(0,4,7,1),(1,7,13,6),(1,6,5),(2,5,12,8),(2,8,10,3),(3,10,17,9),(4,9,11),(4,11,15,7),(5,6,14,12),(6,13,20,14),(7,15,13),(8,12,19,16),(8,16,10),(9,17,18,11),(10,16,22,17),(11,18,21,15),(12,14,19),(13,15,21,20),(14,20,23,19),(16,19,23,22),(17,22,18),(18,22,23,21),(20,21,23)]),
    'Stellated_truncated_hexahedron' : (
        [(0.000000,0.000000,1.000000),(0.872260,0.000000,-0.489042),(-0.127740,0.862856,-0.489042),(-0.834846,-0.252725,-0.489042),(-0.489042,0.862856,0.127740),(-0.781935,-0.610131,0.127740),(0.925172,-0.357407,0.127740),(0.218065,0.967538,0.127740),(-0.270977,-0.610131,-0.744521),(0.563870,-0.357407,0.744521),(0.270977,0.610131,0.744521),(-0.436130,0.505449,0.744521),(-0.436130,-0.505449,0.744521),(0.436130,-0.505449,-0.744521),(0.781935,0.610131,-0.127740),(0.436130,0.505449,-0.744521),(-0.563870,0.357407,-0.744521),(0.489042,-0.862856,-0.127740),(-0.218065,-0.967538,-0.127740),(-0.925172,0.357407,-0.127740),(0.127740,-0.862856,0.489042),(-0.872260,0.000000,0.489042),(0.834846,0.252725,0.489042),(0.000000,0.000000,-1.000000)],
        [(0,1,4,9,15,11,6,2),(0,2,5,10,16,12,7,3),(0,3,1),(1,3,7,13,19,14,8,4),(2,6,5),(4,8,9),(5,6,11,18,22,21,17,10),(7,12,13),(8,14,20,23,22,18,15,9),(10,17,16),(11,15,18),(12,16,17,21,23,20,19,13),(14,19,20),(21,22,23)]),
    'Great_truncated_cuboctahedron' : (
        [(0.000000,0.000000,1.000000),(0.830509,0.000000,0.557005),(0.518050,0.649131,0.557005),(-0.769697,0.311950,0.557005),(0.174041,0.649131,0.740499),(0.891322,0.311950,-0.328986),(-0.251647,0.961080,0.114009),(0.615926,-0.268879,0.740499),(-0.708884,0.623900,-0.328986),(0.234854,0.961080,-0.145492),(0.271918,-0.268879,0.923994),(0.121625,0.623900,-0.771982),(-0.923467,0.355021,-0.145492),(-0.040542,0.380252,0.923994),(-0.055894,-0.874938,0.480998),(-0.276836,0.831867,0.480998),(0.393543,0.355021,-0.847988),(0.789968,0.380252,0.480998),(0.430607,-0.874938,0.221498),(0.553673,0.831867,0.038003),(-0.491420,0.562988,0.664493),(-0.825591,-0.562988,0.038003),(-0.712362,-0.225807,0.664493),(-0.948657,0.225807,0.221498),(0.825591,0.562988,-0.038003),(0.491420,-0.562988,-0.664493),(0.948657,-0.225807,-0.221498),(0.712362,0.225807,-0.664493),(-0.393543,-0.355021,0.847988),(-0.430607,0.874938,-0.221498),(-0.553673,-0.831867,-0.038003),(-0.789968,-0.380252,-0.480998),(0.923467,-0.355021,0.145492),(0.055894,0.874938,-0.480998),(0.276836,-0.831867,-0.480998),(0.040542,-0.380252,-0.923994),(-0.234854,-0.961080,0.145492),(-0.271918,0.268879,-0.923994),(-0.121625,-0.623900,0.771982),(0.251647,-0.961080,-0.114009),(-0.615926,0.268879,-0.740499),(0.708884,-0.623900,0.328986),(-0.891322,-0.311950,0.328986),(-0.174041,-0.649131,-0.740499),(0.769697,-0.311950,-0.557005),(-0.518050,-0.649131,-0.557005),(-0.830509,0.000000,-0.557005),(0.000000,-0.000000,-1.000000)],
        [(0,1,4,10,17,13,7,2),(0,2,6,3),(0,3,8,11,5,1),(1,5,9,4),(2,7,14,21,12,6),(3,6,12,20,29,23,15,8),(4,9,16,25,18,10),(5,11,19,27,33,24,16,9),(7,13,22,14),(8,15,19,11),(10,18,26,17),(12,21,28,20),(13,17,26,34,30,22),(14,22,30,38,42,36,28,21),(15,23,31,35,27,19),(16,24,32,25),(18,25,32,39,44,41,34,26),(20,28,36,43,37,29),(23,29,37,31),(24,33,40,45,39,32),(27,35,40,33),(30,34,41,38),(31,37,43,46,47,45,40,35),(36,42,46,43),(38,41,44,47,46,42),(39,45,47,44)]),
    'Icosahedron' : (
        [(0.000000,0.000000,1.000000),(0.894427,0.000000,0.447214),(0.276393,0.850651,0.447214),(-0.723607,0.525731,0.447214),(-0.723607,-0.525731,0.447214),(0.276393,-0.850651,0.447214),(0.723607,0.525731,-0.447214),(0.723607,-0.525731,-0.447214),(-0.276393,0.850651,-0.447214),(-0.894427,0.000000,-0.447214),(-0.276393,-0.850651,-0.447214),(0.000000,0.000000,-1.000000)],
        [(0,1,2),(0,2,3),(0,3,4),(0,4,5),(0,5,1),(1,5,7),(1,7,6),(1,6,2),(2,6,8),(2,8,3),(3,8,9),(3,9,4),(4,9,10),(4,10,5),(5,10,7),(6,7,11),(6,11,8),(7,10,11),(8,11,9),(9,11,10)]),
    'Dodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.666667,0.000000,0.745356),(-0.333333,0.577350,0.745356),(-0.333333,-0.577350,0.745356),(0.745356,0.577350,0.333333),(0.745356,-0.577350,0.333333),(-0.872678,0.356822,0.333333),(0.127322,0.934172,0.333333),(0.127322,-0.934172,0.333333),(-0.872678,-0.356822,0.333333),(0.872678,0.356822,-0.333333),(0.872678,-0.356822,-0.333333),(-0.745356,0.577350,-0.333333),(-0.127322,0.934172,-0.333333),(-0.127322,-0.934172,-0.333333),(-0.745356,-0.577350,-0.333333),(0.333333,0.577350,-0.745356),(0.333333,-0.577350,-0.745356),(-0.666667,0.000000,-0.745356),(0.000000,0.000000,-1.000000)],
        [(0,1,4,7,2),(0,2,6,9,3),(0,3,8,5,1),(1,5,11,10,4),(2,7,13,12,6),(3,9,15,14,8),(4,10,16,13,7),(5,8,14,17,11),(6,12,18,15,9),(10,11,17,19,16),(12,13,16,19,18),(14,15,18,19,17)]),
    'Icosidodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.587785,0.000000,0.809017),(0.262866,0.525731,0.809017),(-0.587785,-0.000000,0.809017),(-0.262866,-0.525731,0.809017),(0.951057,0.000000,0.309017),(0.688191,-0.525731,0.500000),(-0.162460,0.850651,0.500000),(0.425325,0.850651,0.309017),(-0.951057,-0.000000,0.309017),(-0.688191,0.525731,0.500000),(0.162460,-0.850651,0.500000),(-0.425325,-0.850651,0.309017),(0.951057,0.000000,-0.309017),(0.850651,0.525731,0.000000),(0.525731,-0.850651,0.000000),(-0.525731,0.850651,0.000000),(0.425325,0.850651,-0.309017),(-0.951057,-0.000000,-0.309017),(-0.850651,-0.525731,0.000000),(-0.425325,-0.850651,-0.309017),(0.587785,0.000000,-0.809017),(0.688191,-0.525731,-0.500000),(0.162460,-0.850651,-0.500000),(-0.688191,0.525731,-0.500000),(-0.162460,0.850651,-0.500000),(0.262866,0.525731,-0.809017),(-0.587785,-0.000000,-0.809017),(-0.262866,-0.525731,-0.809017),(-0.000000,0.000000,-1.000000)],
        [(0,1,2),(0,2,7,10,3),(0,3,4),(0,4,11,6,1),(1,6,5),(1,5,14,8,2),(2,8,7),(3,10,9),(3,9,19,12,4),(4,12,11),(5,6,15,22,13),(5,13,14),(6,11,15),(7,8,17,25,16),(7,16,10),(8,14,17),(9,10,16,24,18),(9,18,19),(11,12,20,23,15),(12,19,20),(13,22,21),(13,21,26,17,14),(15,23,22),(16,25,24),(17,26,25),(18,24,27),(18,27,28,20,19),(20,28,23),(21,22,23,28,29),(21,29,26),(24,25,26,29,27),(27,29,28)]),
    'Truncated_icosahedron' : (
        [(0.000000,0.000000,1.000000),(0.395248,0.000000,0.918574),(-0.222786,0.326477,0.918574),(-0.144097,-0.368045,0.918574),(0.567710,0.326477,0.755723),(0.495428,-0.368045,0.786825),(-0.589668,0.284910,0.755723),(-0.050324,0.652955,0.755723),(0.162095,-0.595510,0.786825),(-0.510979,-0.409613,0.755723),(0.840353,0.284910,0.461123),(0.344924,0.652955,0.674298),(0.768071,-0.409613,0.492225),(-0.643952,0.585697,0.492225),(-0.733765,-0.083136,0.674298),(-0.310619,0.813161,0.492225),(0.101404,-0.864542,0.492225),(-0.571670,-0.678645,0.461123),(0.786069,0.585697,0.197624),(0.940533,-0.083136,0.329373),(0.479877,0.813161,0.329373),(0.707379,-0.678645,0.197624),(-0.842332,0.518439,0.147300),(-0.932145,-0.150394,0.329373),(-0.175666,0.973367,0.147300),(0.374046,-0.906109,0.197624),(-0.265479,-0.906109,0.329373),(-0.831965,-0.518439,0.197624),(0.831965,0.518439,-0.197624),(0.986429,-0.150394,-0.065875),(0.219582,0.973367,0.065875),(0.842332,-0.518439,-0.147300),(-0.707379,0.678645,-0.197624),(-0.986429,0.150394,0.065875),(-0.374046,0.906109,-0.197624),(0.175666,-0.973367,-0.147300),(-0.219582,-0.973367,-0.065875),(-0.786069,-0.585697,-0.197624),(0.571670,0.678645,-0.461123),(0.932145,0.150394,-0.329373),(0.265479,0.906109,-0.329373),(0.643952,-0.585697,-0.492225),(-0.768071,0.409613,-0.492225),(-0.940533,0.083136,-0.329373),(-0.101404,0.864542,-0.492225),(0.310619,-0.813161,-0.492225),(-0.479877,-0.813161,-0.329373),(-0.840353,-0.284910,-0.461123),(0.510979,0.409613,-0.755723),(0.733765,0.083136,-0.674298),(0.589668,-0.284910,-0.755723),(-0.495428,0.368045,-0.786825),(-0.162095,0.595510,-0.786825),(0.050324,-0.652955,-0.755723),(-0.344924,-0.652955,-0.674298),(-0.567710,-0.326477,-0.755723),(0.144097,0.368045,-0.918574),(0.222786,-0.326477,-0.918574),(-0.395248,0.000000,-0.918574),(0.000000,0.000000,-1.000000)],
        [(0,1,4,11,7,2),(0,2,6,14,9,3),(0,3,8,5,1),(1,5,12,19,10,4),(2,7,15,13,6),(3,9,17,26,16,8),(4,10,18,20,11),(5,8,16,25,21,12),(6,13,22,33,23,14),(7,11,20,30,24,15),(9,14,23,27,17),(10,19,29,39,28,18),(12,21,31,29,19),(13,15,24,34,32,22),(16,26,36,35,25),(17,27,37,46,36,26),(18,28,38,40,30,20),(21,25,35,45,41,31),(22,32,42,43,33),(23,33,43,47,37,27),(24,30,40,44,34),(28,39,49,48,38),(29,31,41,50,49,39),(32,34,44,52,51,42),(35,36,46,54,53,45),(37,47,55,54,46),(38,48,56,52,44,40),(41,45,53,57,50),(42,51,58,55,47,43),(48,49,50,57,59,56),(51,52,56,59,58),(53,54,55,58,59,57)]),
    'Truncated_dodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.331954,0.000000,0.943295),(-0.286080,0.168381,0.943295),(0.161134,-0.290223,0.943295),(0.582989,0.168381,0.794841),(-0.587832,0.150605,0.794841),(-0.417011,0.440828,0.794841),(0.135775,-0.591433,0.794841),(0.818350,0.150605,0.554636),(0.657216,0.440828,0.611341),(-0.789998,-0.046539,0.611341),(-0.342784,0.713275,0.611341),(-0.066391,-0.788578,0.611341),(0.265564,-0.788578,0.554636),(0.948139,-0.046539,0.314432),(0.526284,0.713275,0.462886),(-0.815357,-0.347749,0.462886),(-0.946289,-0.075302,0.314432),(-0.393502,0.863880,0.314432),(-0.091750,0.881656,0.462886),(-0.368143,-0.806354,0.462886),(0.500925,-0.806354,0.314432),(0.922779,-0.347749,0.165977),(0.997007,-0.075302,-0.017523),(0.475566,0.863880,0.165977),(0.240205,0.881656,0.406182),(-0.654223,-0.637973,0.406182),(-0.997007,0.075302,0.017523),(-0.549793,0.835117,0.017523),(-0.524434,-0.835117,0.165977),(0.549793,-0.835117,-0.017523),(0.751959,-0.637973,0.165977),(0.946289,0.075302,-0.314432),(0.524434,0.835117,-0.165977),(-0.948139,0.046539,-0.314432),(-0.922779,0.347749,-0.165977),(-0.751959,0.637973,-0.165977),(-0.500925,0.806354,-0.314432),(-0.475566,-0.863880,-0.165977),(0.393502,-0.863880,-0.314432),(0.789998,0.046539,-0.611341),(0.815357,0.347749,-0.462886),(0.654223,0.637973,-0.406182),(0.368143,0.806354,-0.462886),(-0.818350,-0.150605,-0.554636),(-0.265564,0.788578,-0.554636),(-0.526284,-0.713275,-0.462886),(-0.240205,-0.881656,-0.406182),(0.091750,-0.881656,-0.462886),(0.342784,-0.713275,-0.611341),(0.587832,-0.150605,-0.794841),(0.066391,0.788578,-0.611341),(-0.657216,-0.440828,-0.611341),(-0.582989,-0.168381,-0.794841),(-0.135775,0.591433,-0.794841),(0.417011,-0.440828,-0.794841),(0.286080,-0.168381,-0.943295),(-0.331954,0.000000,-0.943295),(-0.161134,0.290223,-0.943295),(-0.000000,0.000000,-1.000000)],
        [(0,1,4,9,15,25,19,11,6,2),(0,2,5,10,16,26,20,12,7,3),(0,3,1),(1,3,7,13,21,31,22,14,8,4),(2,6,5),(4,8,9),(5,6,11,18,28,36,35,27,17,10),(7,12,13),(8,14,23,32,41,42,33,24,15,9),(10,17,16),(11,19,18),(12,20,29,38,47,48,39,30,21,13),(14,22,23),(15,24,25),(16,17,27,34,44,52,46,38,29,26),(18,19,25,24,33,43,51,45,37,28),(20,26,29),(21,30,31),(22,31,30,39,49,55,50,40,32,23),(27,35,34),(28,37,36),(32,40,41),(33,42,43),(34,35,36,37,45,54,58,57,53,44),(38,46,47),(39,48,49),(40,50,56,59,58,54,51,43,42,41),(44,53,52),(45,51,54),(46,52,53,57,59,56,55,49,48,47),(50,55,56),(57,58,59)]),
    'Rhombicosidodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.436466,0.000000,0.899721),(-0.023039,0.435858,0.899721),(-0.394788,0.186134,0.899721),(-0.165035,-0.404062,0.899721),(0.413427,0.435858,0.799441),(0.747896,0.186134,0.637186),(0.541183,-0.404062,0.737465),(-0.225353,0.737028,0.637186),(-0.559822,-0.217929,0.799441),(-0.597101,0.487304,0.637186),(0.169435,-0.653787,0.737465),(-0.455106,-0.621991,0.637186),(0.480865,0.737028,0.474930),(0.852613,-0.217929,0.474930),(0.815334,0.487304,0.312675),(0.687578,-0.621991,0.374651),(0.086077,0.923162,0.374651),(-0.529663,0.788474,0.312675),(-0.864132,-0.166483,0.474930),(-0.887172,0.269375,0.374651),(-0.120636,-0.871716,0.474930),(0.315830,-0.871716,0.374651),(-0.759416,-0.570545,0.312675),(0.613021,0.788474,0.050140),(0.984769,-0.166483,0.050140),(0.961729,0.269375,-0.050140),(0.819734,-0.570545,-0.050140),(-0.218233,0.974608,0.050140),(0.218233,0.974608,-0.050140),(-0.819734,0.570545,0.050140),(-0.961729,-0.269375,0.050140),(-0.984769,0.166483,-0.050140),(-0.218233,-0.974608,0.050140),(0.218233,-0.974608,-0.050140),(-0.613021,-0.788474,-0.050140),(0.759416,0.570545,-0.312675),(0.887172,-0.269375,-0.374651),(0.864132,0.166483,-0.474930),(0.529663,-0.788474,-0.312675),(-0.315830,0.871716,-0.374651),(0.120636,0.871716,-0.474930),(-0.687578,0.621991,-0.374651),(-0.815334,-0.487304,-0.312675),(-0.852613,0.217929,-0.474930),(-0.086077,-0.923162,-0.374651),(-0.480865,-0.737028,-0.474930),(0.455106,0.621991,-0.637186),(0.597101,-0.487304,-0.637186),(0.559822,0.217929,-0.799441),(0.225353,-0.737028,-0.637186),(-0.169435,0.653787,-0.737465),(-0.541183,0.404062,-0.737465),(-0.747896,-0.186134,-0.637186),(-0.413427,-0.435858,-0.799441),(0.165035,0.404062,-0.899721),(0.394788,-0.186134,-0.899721),(0.023039,-0.435858,-0.899721),(-0.436466,0.000000,-0.899721),(-0.000000,0.000000,-1.000000)],
        [(0,1,5,2),(0,2,3),(0,3,9,4),(0,4,11,7,1),(1,7,14,6),(1,6,5),(2,5,13,17,8),(2,8,10,3),(3,10,20,19,9),(4,9,12),(4,12,21,11),(5,6,15,13),(6,14,25,26,15),(7,11,22,16),(7,16,14),(8,17,28,18),(8,18,10),(9,19,23,12),(10,18,30,20),(11,21,22),(12,23,35,33,21),(13,15,24),(13,24,29,17),(14,16,27,25),(15,26,36,24),(16,22,34,39,27),(17,29,28),(18,28,40,42,30),(19,20,32,31),(19,31,23),(20,30,32),(21,33,34,22),(23,31,43,35),(24,36,47,41,29),(25,27,37),(25,37,38,26),(26,38,36),(27,39,48,37),(28,29,41,40),(30,42,44,32),(31,32,44,53,43),(33,35,46,45),(33,45,34),(34,45,50,39),(35,43,46),(36,38,49,47),(37,48,56,49,38),(39,50,48),(40,41,51),(40,51,52,42),(41,47,55,51),(42,52,44),(43,53,54,46),(44,52,58,53),(45,46,54,57,50),(47,49,55),(48,50,57,56),(49,56,59,55),(51,55,59,58,52),(53,58,54),(54,58,59,57),(56,57,59)]),
    'Truncated_icosidodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.260709,0.000000,0.965418),(-0.004587,0.260668,0.965418),(-0.219216,-0.141114,0.965418),(0.256121,0.260668,0.930835),(0.463328,-0.141114,0.874880),(-0.228391,0.380222,0.896253),(-0.313207,-0.369442,0.874880),(-0.443020,-0.021560,0.896253),(0.454153,0.380222,0.805715),(0.530464,-0.369442,0.762968),(0.661360,-0.021560,0.749759),(-0.329804,0.573664,0.749759),(-0.447607,0.239108,0.861670),(-0.537010,-0.249888,0.805715),(-0.246071,-0.597770,0.762968),(0.513867,0.573664,0.637848),(0.656772,0.239108,0.715177),(0.728496,-0.249888,0.637848),(0.436473,-0.597770,0.672430),(-0.549020,0.432550,0.715177),(-0.270090,0.767107,0.581892),(-0.693677,-0.358662,0.624639),(-0.043451,-0.738884,0.672430),(-0.402738,-0.706543,0.581892),(0.716486,0.432550,0.547310),(0.412454,0.767107,0.491354),(0.832537,-0.358662,0.422190),(0.217257,-0.738884,0.637848),(0.540514,-0.706543,0.456772),(-0.708522,0.484878,0.512728),(-0.072058,0.886661,0.456772),(-0.429592,0.819435,0.379443),(-0.853180,-0.306334,0.422190),(-0.626541,-0.586989,0.512728),(-0.200119,-0.847658,0.491354),(0.817692,0.484878,0.310278),(0.188650,0.886661,0.422190),(0.513660,0.819435,0.254323),(0.933743,-0.306334,0.185158),(0.738546,-0.586989,0.331651),(0.321298,-0.847658,0.422190),(-0.865189,0.376104,0.331651),(-0.648808,0.678320,0.344861),(-0.231560,0.938989,0.254323),(-0.786044,-0.534661,0.310278),(-0.954593,-0.112891,0.275696),(-0.096077,-0.956431,0.275696),(0.921733,0.376104,0.094620),(0.716279,0.678320,0.163785),(0.289857,0.938989,0.185158),(0.839753,-0.534661,0.094620),(0.993457,-0.112891,0.017291),(0.164631,-0.956431,0.241113),(-0.805476,0.569547,0.163785),(-0.959180,0.147777,0.241113),(-0.130354,0.991317,0.017291),(-0.820320,-0.569547,0.051874),(-0.988870,-0.147777,0.017291),(-0.130354,-0.991317,0.017291),(0.820320,0.569547,-0.051874),(0.988870,0.147777,-0.017291),(0.130354,0.991317,-0.017291),(0.805476,-0.569547,-0.163785),(0.959180,-0.147777,-0.241113),(0.130354,-0.991317,-0.017291),(-0.839753,0.534661,-0.094620),(-0.993457,0.112891,-0.017291),(-0.164631,0.956431,-0.241113),(-0.716279,-0.678320,-0.163785),(-0.921733,-0.376104,-0.094620),(-0.289857,-0.938989,-0.185158),(0.786044,0.534661,-0.310278),(0.954593,0.112891,-0.275696),(0.096077,0.956431,-0.275696),(0.648808,-0.678320,-0.344861),(0.865189,-0.376104,-0.331651),(0.231560,-0.938989,-0.254323),(-0.738546,0.586989,-0.331651),(-0.933743,0.306334,-0.185158),(-0.321298,0.847658,-0.422190),(-0.817692,-0.484878,-0.310278),(-0.513660,-0.819435,-0.254323),(-0.188650,-0.886661,-0.422190),(0.626541,0.586989,-0.512728),(0.853180,0.306334,-0.422190),(0.200119,0.847658,-0.491354),(0.708522,-0.484878,-0.512728),(0.429592,-0.819435,-0.379443),(0.072058,-0.886661,-0.456772),(-0.832537,0.358662,-0.422190),(-0.540514,0.706543,-0.456772),(-0.217257,0.738884,-0.637848),(-0.716486,-0.432550,-0.547310),(-0.412454,-0.767107,-0.491354),(0.693677,0.358662,-0.624639),(0.402738,0.706543,-0.581892),(0.043451,0.738884,-0.672430),(0.549020,-0.432550,-0.715177),(0.270090,-0.767107,-0.581892),(-0.728496,0.249888,-0.637848),(-0.436473,0.597770,-0.672430),(-0.656772,-0.239108,-0.715177),(-0.513867,-0.573664,-0.637848),(0.537010,0.249888,-0.805715),(0.246071,0.597770,-0.762968),(0.447607,-0.239108,-0.861670),(0.329804,-0.573664,-0.749759),(-0.661360,0.021560,-0.749759),(-0.530464,0.369442,-0.762968),(-0.454153,-0.380222,-0.805715),(0.443020,0.021560,-0.896253),(0.313207,0.369442,-0.874880),(0.228391,-0.380222,-0.896253),(-0.463328,0.141114,-0.874880),(-0.256121,-0.260668,-0.930835),(0.219216,0.141114,-0.965418),(0.004587,-0.260668,-0.965418),(-0.260709,0.000000,-0.965418),(0.000000,0.000000,-1.000000)],
        [(0,1,4,2),(0,2,6,13,8,3),(0,3,7,15,23,28,19,10,5,1),(1,5,11,17,9,4),(2,4,9,16,26,37,31,21,12,6),(3,8,14,7),(5,10,18,11),(6,12,20,13),(7,14,22,34,24,15),(8,13,20,30,42,55,46,33,22,14),(9,17,25,16),(10,19,29,40,27,18),(11,18,27,39,52,61,48,36,25,17),(12,21,32,43,30,20),(15,24,35,23),(16,25,36,49,38,26),(19,28,41,29),(21,31,44,32),(22,33,45,34),(23,35,47,53,41,28),(24,34,45,57,69,82,71,59,47,35),(26,38,50,37),(27,40,51,39),(29,41,53,65,77,88,75,63,51,40),(30,43,54,42),(31,37,50,62,56,44),(32,44,56,68,80,91,78,66,54,43),(33,46,58,70,57,45),(36,48,60,49),(38,49,60,72,84,96,86,74,62,50),(39,51,63,76,64,52),(42,54,66,79,67,55),(46,55,67,58),(47,59,65,53),(48,61,73,85,72,60),(52,64,73,61),(56,62,74,68),(57,70,81,69),(58,67,79,90,100,108,102,93,81,70),(59,71,83,89,77,65),(63,75,87,76),(64,76,87,98,106,111,104,95,85,73),(66,78,90,79),(68,74,86,97,92,80),(69,81,93,103,94,82),(71,82,94,83),(72,85,95,84),(75,88,99,107,98,87),(77,89,99,88),(78,91,101,109,100,90),(80,92,101,91),(83,94,103,110,115,117,113,107,99,89),(84,95,104,112,105,96),(86,96,105,97),(92,97,105,112,116,119,118,114,109,101),(93,102,110,103),(98,107,113,106),(100,109,114,108),(102,108,114,118,115,110),(104,111,116,112),(106,113,117,119,116,111),(115,118,119,117)]),
    'Snub_dodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.451209,0.000000,0.892418),(0.212779,0.397888,0.892418),(-0.250526,0.375268,0.892418),(-0.449063,-0.043953,0.892418),(-0.173008,-0.416722,0.892418),(0.557063,-0.416722,0.718348),(0.803419,-0.043953,0.593789),(0.626241,0.375268,0.683371),(0.340114,0.729203,0.593789),(-0.409529,0.692604,0.593789),(-0.659818,0.312480,0.683371),(-0.586707,-0.434486,0.683371),(-0.267464,-0.758866,0.593789),(0.171275,-0.674271,0.718348),(0.506613,-0.758866,0.409227),(0.831931,-0.434486,0.345125),(0.985320,-0.034518,0.167191),(0.698640,0.643796,0.312137),(0.353461,0.919677,0.171055),(-0.044494,0.911347,0.409227),(-0.441367,0.880872,0.171055),(-0.758030,0.572678,0.312137),(-0.927716,0.142235,0.345125),(-0.882531,-0.319416,0.345125),(-0.632604,-0.708789,0.312137),(0.082288,-0.934942,0.345125),(0.384147,-0.923246,-0.006880),(0.910524,-0.398390,-0.110598),(0.956136,0.026189,-0.291749),(0.920563,0.390534,-0.006880),(0.652176,0.745388,-0.138066),(-0.048711,0.997730,-0.046496),(-0.417724,0.860458,-0.291749),(-0.930096,0.361791,-0.063473),(-0.994168,-0.097306,-0.046496),(-0.842295,-0.535267,-0.063473),(-0.508521,-0.853917,-0.110598),(-0.066694,-0.993687,-0.090210),(0.217118,-0.873016,-0.436695),(0.633778,-0.700460,-0.328149),(0.775223,-0.316523,-0.546665),(0.784691,0.427551,-0.448843),(0.434620,0.715725,-0.546665),(0.001448,0.871681,-0.490072),(-0.343900,0.635939,-0.690879),(-0.719775,0.539649,-0.436695),(-0.887155,0.107214,-0.448843),(-0.641420,-0.601421,-0.476312),(-0.242274,-0.837337,-0.490072),(0.418377,-0.560779,-0.714484),(0.491967,-0.126969,-0.861305),(0.497819,0.332894,-0.800848),(0.094740,0.561456,-0.822066),(-0.585483,0.248299,-0.771724),(-0.669145,-0.204346,-0.714484),(-0.324935,-0.503050,-0.800848),(0.083369,-0.332128,-0.939543),(0.124252,0.127782,-0.983988),(-0.296148,-0.065760,-0.952876)],
        [(0,1,2),(0,2,3),(0,3,4),(0,4,5),(0,5,14,6,1),(1,6,7),(1,7,8),(1,8,2),(2,8,9),(2,9,20,10,3),(3,10,11),(3,11,4),(4,11,23,24,12),(4,12,5),(5,12,13),(5,13,14),(6,14,15),(6,15,16),(6,16,7),(7,16,17),(7,17,30,18,8),(8,18,9),(9,18,19),(9,19,20),(10,20,21),(10,21,22),(10,22,11),(11,22,23),(12,24,25),(12,25,13),(13,25,37,38,26),(13,26,14),(14,26,15),(15,26,27),(15,27,40,28,16),(16,28,17),(17,28,29),(17,29,30),(18,30,31),(18,31,19),(19,31,43,44,32),(19,32,20),(20,32,21),(21,32,33),(21,33,46,34,22),(22,34,23),(23,34,35),(23,35,24),(24,35,36),(24,36,25),(25,36,37),(26,38,27),(27,38,39),(27,39,40),(28,40,41),(28,41,29),(29,41,51,52,42),(29,42,30),(30,42,31),(31,42,43),(32,44,33),(33,44,45),(33,45,46),(34,46,47),(34,47,35),(35,47,55,48,36),(36,48,37),(37,48,49),(37,49,38),(38,49,39),(39,49,56,57,50),(39,50,40),(40,50,41),(41,50,51),(42,52,43),(43,52,53),(43,53,44),(44,53,45),(45,53,58,59,54),(45,54,46),(46,54,47),(47,54,55),(48,55,56),(48,56,49),(50,57,51),(51,57,58),(51,58,52),(52,58,53),(54,59,55),(55,59,56),(56,59,57),(57,59,58)]),
    'Small_ditrigonal_icosidodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.942809,0.000000,0.333333),(0.672718,0.660560,0.333333),(-0.471405,0.816497,0.333333),(-0.908421,0.252311,0.333333),(-0.471405,-0.816497,0.333333),(0.235702,-0.912871,0.333333),(0.090030,0.660560,0.745356),(0.471405,0.816497,-0.333333),(0.617077,0.252311,-0.745356),(0.471405,-0.816497,-0.333333),(-0.235702,0.912871,-0.333333),(0.908421,-0.252311,-0.333333),(0.527046,-0.408248,0.745356),(-0.617077,-0.252311,0.745356),(-0.942809,0.000000,-0.333333),(-0.527046,0.408248,-0.745356),(-0.672718,-0.660560,-0.333333),(-0.090030,-0.660560,-0.745356),(0.000000,0.000000,-1.000000)],
        [(0,1,7,13,2),(0,2,3),(0,3,14,7,4),(0,4,5),(0,5,13,14,6),(0,6,1),(1,6,12,13,10),(1,10,9),(1,9,2,12,8),(1,8,7),(2,13,12),(2,9,11),(2,11,7,8,3),(3,8,16),(3,16,4,11,15),(3,15,14),(4,7,11),(4,16,17),(4,17,14,15,5),(5,15,18),(5,18,6,17,10),(5,10,13),(6,14,17),(6,18,12),(7,14,13),(8,12,19),(8,19,11,9,16),(9,10,19,12,18),(9,18,16),(10,17,19),(11,19,15),(15,19,17,16,18)]),
    'Small_icosicosidodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.555851,0.000000,0.831282),(-0.354742,0.427935,0.831282),(-0.542335,0.121833,0.831282),(0.252320,-0.495283,0.831282),(0.756960,0.427935,0.493846),(0.912902,0.121833,0.389573),(-0.323092,-0.142645,0.935555),(-0.676407,0.625065,0.389573),(-0.153633,0.855870,0.493846),(-0.832349,-0.251616,0.493846),(-0.864000,0.318964,0.389573),(-0.019561,0.352638,0.935555),(0.305840,-0.868732,0.389573),(-0.037695,-0.868732,0.493846),(0.788610,-0.142645,0.598120),(0.778829,0.625065,-0.052137),(0.402217,0.855870,0.325128),(0.966422,-0.251616,-0.052137),(0.934772,0.318964,-0.156410),(0.536290,0.352638,0.766838),(-0.613107,-0.516094,0.598120),(-0.070772,-0.637928,0.766838),(-0.842130,0.516094,-0.156410),(-0.966422,0.251616,0.052137),(0.203418,0.977703,0.052137),(-0.778829,-0.625065,0.052137),(-0.580029,-0.746899,0.325128),(-0.662891,0.746899,0.052137),(0.181548,0.780572,0.598120),(0.140117,-0.977703,-0.156410),(0.662891,-0.746899,-0.052137),(-0.203418,-0.977703,-0.052137),(0.485079,-0.637928,0.598120),(0.842130,-0.516094,0.156410),(0.613107,0.516094,-0.598120),(0.832349,0.251616,-0.493846),(-0.140117,0.977703,0.156410),(0.676407,-0.625065,-0.389573),(0.580029,0.746899,-0.325128),(-0.934772,-0.318964,0.156410),(-0.788610,0.142645,-0.598120),(-0.485079,0.637928,-0.598120),(-0.912902,-0.121833,-0.389573),(0.037695,0.868732,-0.493846),(-0.402217,-0.855870,-0.325128),(-0.756960,-0.427935,-0.493846),(-0.305840,0.868732,-0.389573),(-0.181548,-0.780572,-0.598120),(0.864000,-0.318964,-0.389573),(0.153633,-0.855870,-0.493846),(0.323092,0.142645,-0.935555),(0.070772,0.637928,-0.766838),(0.542335,-0.121833,-0.831282),(0.354742,-0.427935,-0.831282),(-0.536290,-0.352638,-0.766838),(-0.555851,0.000000,-0.831282),(-0.252320,0.495283,-0.831282),(0.019561,-0.352638,-0.935555),(0.000000,0.000000,-1.000000)],
        [(0,1,5,17,9,2),(0,2,7,12,3),(0,3,10,27,14,4),(0,4,1),(1,4,13,31,18,6),(1,6,20,15,5),(2,9,8),(2,8,24,40,21,7),(3,12,29,37,28,11),(3,11,10),(4,14,33,22,13),(5,15,34,49,36,16),(5,16,17),(6,18,19),(6,19,39,25,29,20),(7,21,22),(7,22,33,15,20,12),(8,9,25,44,42,23),(8,23,11,28,24),(9,17,37,29,25),(10,11,23,41,46,26),(10,26,21,40,27),(12,20,29),(13,22,21,26,45,30),(13,30,31),(14,27,32),(14,32,50,38,34,33),(15,33,34),(16,36,39,19,35),(16,35,52,47,37,17),(18,31,49,34,38),(18,38,54,51,35,19),(23,42,41),(24,28,47,57,56,43),(24,43,40),(25,39,44),(26,46,45),(27,40,43,55,48,32),(28,37,47),(30,45,50,32,48),(30,48,58,53,49,31),(35,51,52),(36,49,53),(36,53,59,57,44,39),(38,50,54),(41,42,52,51,58,55),(41,55,43,56,46),(42,44,57,47,52),(45,46,56,59,54,50),(48,55,58),(51,54,59,53,58),(56,57,59)]),
    'Small_snub_icosicosidodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.644206,0.000000,0.764852),(0.279186,0.580566,0.764852),(-0.141945,0.628373,0.764852),(-0.627813,0.144402,0.764852),(-0.402219,-0.503211,0.764852),(0.279186,-0.580566,0.764852),(0.800360,-0.503211,0.325887),(0.972907,-0.144402,0.180557),(0.800360,0.503211,0.325887),(0.291502,0.939375,0.180557),(-0.305710,0.814213,0.493556),(-0.314492,0.269564,0.910181),(0.366913,0.192210,0.910181),(0.480441,0.724968,0.493556),(-0.073518,0.980813,0.180557),(-0.667196,0.669811,0.325887),(-0.980518,0.077354,0.180557),(-0.892791,-0.311002,0.325887),(-0.494650,-0.850130,0.180557),(0.115421,-0.862021,0.493556),(-0.305710,-0.814213,0.493556),(0.291502,-0.939375,0.180557),(0.667196,-0.669811,-0.325887),(0.980518,-0.077354,-0.180557),(0.876398,0.166600,0.451852),(0.597212,-0.413966,0.687001),(0.658415,-0.747166,0.090738),(0.816753,-0.358809,-0.451852),(0.892791,0.311002,-0.325887),(0.494650,0.850130,-0.180557),(0.809141,0.580566,-0.090738),(0.305710,0.814213,-0.493556),(-0.291502,0.939375,-0.180557),(-0.658415,0.747166,-0.090738),(-0.816753,0.358809,0.451852),(-0.674808,-0.269564,0.687001),(-0.040733,-0.358809,0.932522),(-0.115421,0.862021,-0.493556),(-0.800360,0.503211,-0.325887),(-0.876398,-0.166600,-0.451852),(-0.809141,-0.580566,0.090738),(-0.972907,0.144402,-0.180557),(-0.800360,-0.503211,-0.325887),(-0.480441,-0.724968,-0.493556),(0.073518,-0.980813,-0.180557),(-0.291502,-0.939375,-0.180557),(0.305710,-0.814213,-0.493556),(0.141945,-0.628373,-0.764852),(0.627813,-0.144402,-0.764852),(0.674808,0.269564,-0.687001),(0.314492,-0.269564,-0.910181),(0.402219,0.503211,-0.764852),(0.040733,0.358809,-0.932522),(-0.279186,0.580566,-0.764852),(-0.597212,0.413966,-0.687001),(-0.644206,-0.000000,-0.764852),(-0.366913,-0.192210,-0.910181),(-0.279186,-0.580566,-0.764852),(0.000000,0.000000,-1.000000)],
        [(0,1,2),(0,2,12,13,3),(0,3,4),(0,4,5),(0,5,6),(0,6,1),(1,6,7),(1,7,25,26,8),(1,8,9),(1,9,2),(2,9,10),(2,10,11),(2,11,12),(3,13,14),(3,14,15),(3,15,16),(3,16,4),(4,16,17),(4,17,36,35,18),(4,18,5),(5,18,19),(5,19,20),(5,20,37,21,6),(6,21,22),(6,22,7),(7,22,23),(7,23,24),(7,24,25),(8,26,27),(8,27,28),(8,28,29),(8,29,9),(9,29,30),(9,30,14,31,10),(10,31,32),(10,32,33),(10,33,11),(11,33,16,15,34),(11,34,35),(11,35,12),(12,35,36),(12,36,37),(12,37,13),(13,37,26),(13,26,25),(13,25,14),(14,25,31),(14,30,15),(15,30,38),(15,38,34),(16,33,39),(16,39,17),(17,39,40),(17,40,41),(17,41,36),(18,35,42),(18,42,43),(18,43,19),(19,43,46,41,44),(19,44,45),(19,45,20),(20,45,27),(20,27,26),(20,26,37),(21,37,36),(21,36,41),(21,41,46),(21,46,22),(22,46,47),(22,47,27,45,23),(23,45,48),(23,48,49),(23,49,24),(24,49,29,28,50),(24,50,31),(24,31,25),(27,47,28),(28,47,51),(28,51,50),(29,49,52),(29,52,30),(30,52,38),(31,50,32),(32,50,53),(32,53,38,52,54),(32,54,33),(33,54,39),(34,38,55),(34,55,42),(34,42,35),(38,53,55),(39,54,56),(39,56,42,55,40),(40,55,57),(40,57,44),(40,44,41),(42,56,43),(43,56,58),(43,58,46),(44,57,48),(44,48,45),(46,58,47),(47,58,51),(48,57,51,58,59),(48,59,49),(49,59,52),(50,51,53),(51,57,53),(52,59,54),(53,57,55),(54,59,56),(56,59,58)]),
    'Small_dodecicosidodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.436466,0.000000,0.899721),(-0.394788,0.186134,0.899721),(-0.023039,0.435858,0.899721),(-0.165035,-0.404062,0.899721),(0.747896,0.186134,0.637186),(0.413427,0.435858,0.799441),(0.541183,-0.404062,0.737465),(-0.559822,-0.217929,0.799441),(-0.597101,0.487304,0.637186),(-0.225353,0.737028,0.637186),(0.169435,-0.653787,0.737465),(-0.455106,-0.621991,0.637186),(0.852613,-0.217929,0.474930),(0.815334,0.487304,0.312675),(0.480865,0.737028,0.474930),(0.687578,-0.621991,0.374651),(-0.864132,-0.166483,0.474930),(-0.529663,0.788474,0.312675),(-0.887172,0.269375,0.374651),(0.086077,0.923162,0.374651),(0.315830,-0.871716,0.374651),(-0.120636,-0.871716,0.474930),(-0.759416,-0.570545,0.312675),(0.984769,-0.166483,0.050140),(0.613021,0.788474,0.050140),(0.961729,0.269375,-0.050140),(0.819734,-0.570545,-0.050140),(-0.961729,-0.269375,0.050140),(-0.819734,0.570545,0.050140),(-0.218233,0.974608,0.050140),(-0.984769,0.166483,-0.050140),(0.218233,0.974608,-0.050140),(0.218233,-0.974608,-0.050140),(-0.218233,-0.974608,0.050140),(-0.613021,-0.788474,-0.050140),(0.887172,-0.269375,-0.374651),(0.759416,0.570545,-0.312675),(0.864132,0.166483,-0.474930),(0.529663,-0.788474,-0.312675),(-0.815334,-0.487304,-0.312675),(-0.687578,0.621991,-0.374651),(-0.315830,0.871716,-0.374651),(-0.852613,0.217929,-0.474930),(0.120636,0.871716,-0.474930),(-0.086077,-0.923162,-0.374651),(-0.480865,-0.737028,-0.474930),(0.597101,-0.487304,-0.637186),(0.455106,0.621991,-0.637186),(0.559822,0.217929,-0.799441),(0.225353,-0.737028,-0.637186),(-0.747896,-0.186134,-0.637186),(-0.541183,0.404062,-0.737465),(-0.169435,0.653787,-0.737465),(-0.413427,-0.435858,-0.799441),(0.394788,-0.186134,-0.899721),(0.165035,0.404062,-0.899721),(0.023039,-0.435858,-0.899721),(-0.436466,-0.000000,-0.899721),(0.000000,-0.000000,-1.000000)],
        [(0,1,5,14,25,32,30,18,9,2),(0,2,3),(0,3,10,18,29,31,28,23,12,4),(0,4,11,7,1),(1,7,16,27,36,38,37,25,15,6),(1,6,5),(2,9,19,17,8),(2,8,12,22,21,16,13,5,6,3),(3,6,15,20,10),(4,12,8),(4,8,17,28,40,46,45,33,21,11),(5,13,24,26,14),(7,11,22,34,45,50,47,36,24,13),(7,13,16),(9,18,10),(9,10,20,32,44,53,52,43,31,19),(11,21,22),(12,23,35,34,22),(14,26,38,49,56,53,42,30,20,15),(14,15,25),(16,21,33,39,27),(17,19,29,41,52,58,54,46,35,23),(17,23,28),(18,30,42,41,29),(19,31,29),(20,30,32),(24,36,27),(24,27,39,50,57,59,56,48,37,26),(25,37,48,44,32),(26,37,38),(28,31,43,51,40),(33,45,34),(33,34,35,40,51,58,59,55,47,39),(35,46,40),(36,47,55,49,38),(39,47,50),(41,42,44,48,49,55,57,54,51,43),(41,43,52),(42,53,44),(45,46,54,57,50),(48,56,49),(51,54,58),(52,53,56,59,58),(55,59,57)]),
    'Small_stellated_dodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.894427,0.000000,-0.447214),(0.276393,0.850651,-0.447214),(-0.723607,0.525731,-0.447214),(-0.723607,-0.525731,-0.447214),(0.276393,-0.850651,-0.447214),(-0.276393,0.850651,0.447214),(-0.276393,-0.850651,0.447214),(-0.894427,0.000000,0.447214),(0.723607,-0.525731,0.447214),(0.723607,0.525731,0.447214),(0.000000,0.000000,-1.000000)],
        [(0,1,6,9,2),(0,2,8,10,3),(0,3,7,6,4),(0,4,9,8,5),(0,5,10,7,1),(1,7,11,9,4),(1,4,2,5,3),(1,3,10,11,6),(2,9,11,10,5),(2,4,6,11,8),(3,5,8,11,7),(6,7,10,8,9)]),
    'Great_dodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.894427,0.000000,0.447214),(-0.723607,0.525731,0.447214),(0.276393,-0.850651,0.447214),(0.276393,0.850651,0.447214),(-0.723607,-0.525731,0.447214),(0.723607,0.525731,-0.447214),(0.723607,-0.525731,-0.447214),(-0.894427,0.000000,-0.447214),(-0.276393,0.850651,-0.447214),(-0.276393,-0.850651,-0.447214),(0.000000,0.000000,-1.000000)],
        [(0,1,6,9,2),(0,2,8,10,3),(0,3,7,6,4),(0,4,9,8,5),(0,5,10,7,1),(1,7,11,9,4),(1,4,2,5,3),(1,3,10,11,6),(2,9,11,10,5),(2,4,6,11,8),(3,5,8,11,7),(6,7,10,8,9)]),
    'Great_dodecadodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.866025,0.000000,0.500000),(0.645497,0.577350,0.500000),(-0.866025,0.000000,0.500000),(-0.645497,-0.577350,0.500000),(0.110264,0.577350,0.809017),(0.866025,0.000000,-0.500000),(0.755761,-0.577350,-0.309017),(0.178411,0.934172,-0.309017),(0.645497,0.577350,-0.500000),(0.467086,-0.356822,0.809017),(-0.110264,-0.577350,0.809017),(-0.866025,0.000000,-0.500000),(-0.755761,0.577350,-0.309017),(-0.178411,-0.934172,-0.309017),(-0.645497,-0.577350,-0.500000),(-0.467086,0.356822,0.809017),(-0.356822,0.934172,0.000000),(-0.755761,0.577350,0.309017),(0.755761,-0.577350,0.309017),(0.000000,0.000000,-1.000000),(0.110264,0.577350,-0.809017),(-0.110264,-0.577350,-0.809017),(0.934172,0.356822,0.000000),(-0.467086,0.356822,-0.809017),(0.467086,-0.356822,-0.809017),(0.178411,0.934172,0.309017),(-0.178411,-0.934172,0.309017),(0.356822,-0.934172,-0.000000),(-0.934172,-0.356822,0.000000)],
        [(0,1,5,10,2),(0,2,8,13,3),(0,3,11,16,4),(0,4,14,7,1),(1,7,23,19,6),(1,6,21,17,5),(2,10,28,25,9),(2,9,26,23,8),(3,13,29,18,12),(3,12,22,28,11),(4,16,17,24,15),(4,15,27,29,14),(5,17,16,26,18),(5,18,29,27,10),(6,19,27,15,20),(6,20,9,25,21),(7,14,25,28,22),(7,22,24,8,23),(8,24,17,21,13),(9,20,12,18,26),(10,27,19,11,28),(11,19,23,26,16),(12,20,15,24,22),(13,21,25,14,29)]),
    'Truncated_great_dodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.513554,0.000000,0.858057),(-0.486446,0.164647,0.858057),(0.407982,-0.311912,0.858057),(0.858057,0.164647,0.486446),(0.090587,-0.311912,0.945783),(-0.865550,0.119140,0.486446),(-0.759977,0.431052,0.486446),(0.261408,0.192772,0.945783),(0.581664,-0.651949,0.486446),(0.992507,0.119140,-0.027109),(0.901920,0.431052,0.027109),(-0.249285,-0.651949,0.716114),(-0.525678,0.459177,0.716114),(-0.992507,-0.119140,0.027109),(-0.716114,0.697457,0.027109),(-0.696498,-0.045507,0.716114),(0.197929,0.669331,0.716114),(0.454706,-0.890229,0.027109),(0.716114,-0.697457,-0.027109),(0.818825,0.459177,0.344503),(0.865550,-0.119140,-0.486446),(0.628389,0.697457,-0.344503),(0.965399,-0.045507,0.256777),(-0.376242,-0.890229,0.256777),(-0.628389,-0.697457,0.344503),(-0.102711,0.771089,0.628389),(-0.818825,-0.459177,-0.344503),(-0.858057,-0.164647,-0.486446),(-0.581664,0.651949,-0.486446),(-0.371611,0.862104,-0.344503),(-0.549924,-0.550192,0.628389),(-0.075602,0.935736,0.344503),(0.241792,0.935736,0.256777),(0.794578,-0.550192,0.256777),(0.075602,-0.935736,-0.344503),(0.759977,-0.431052,-0.486446),(0.371611,-0.862104,0.344503),(0.410843,0.771089,0.486446),(0.525678,-0.459177,-0.716114),(0.486446,-0.164647,-0.858057),(0.249285,0.651949,-0.716114),(0.141943,0.862104,-0.486446),(-0.241792,-0.935736,-0.256777),(-0.901920,-0.431052,-0.027109),(-0.141943,-0.862104,0.486446),(-0.965399,0.045507,-0.256777),(-0.410843,-0.771089,-0.486446),(-0.513554,0.000000,-0.858057),(-0.454706,0.890229,-0.027109),(-0.407982,0.311912,-0.858057),(-0.794578,0.550192,-0.256777),(0.376242,0.890229,-0.256777),(-0.197929,-0.669331,-0.716114),(0.696498,0.045507,-0.716114),(0.102711,-0.771089,-0.628389),(-0.000000,0.000000,-1.000000),(-0.090587,0.311912,-0.945783),(0.549924,0.550192,-0.628389),(-0.261408,-0.192772,-0.945783)],
        [(0,1,4,11,22,42,30,15,7,2),(0,2,6,14,27,47,35,18,9,3),(0,3,8,5,1),(1,5,12,24,43,55,39,21,10,4),(2,7,16,13,6),(3,9,19,36,54,58,52,33,17,8),(4,10,20,23,11),(5,8,17,32,49,51,46,44,25,12),(6,13,26,33,52,41,57,48,28,14),(7,15,29,50,59,53,43,24,31,16),(9,18,34,37,19),(10,21,40,56,50,29,49,32,38,20),(11,23,34,18,35,53,59,57,41,22),(12,25,45,31,24),(13,16,31,45,37,34,23,20,38,26),(14,28,44,46,27),(15,30,51,49,29),(17,33,26,38,32),(19,37,45,25,44,28,48,56,40,36),(21,39,54,36,40),(22,41,52,58,42),(27,46,51,30,42,58,54,39,55,47),(35,47,55,43,53),(48,57,59,50,56)]),
    'Rhombidodecadodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.699854,0.000000,0.714286),(-0.116642,0.690066,0.714286),(-0.524891,0.462910,0.714286),(-0.368954,-0.594701,0.714286),(0.583212,0.690066,0.428571),(0.874818,0.462910,0.142857),(0.763434,-0.594701,0.251990),(-0.452802,0.036426,0.890867),(-0.602238,0.785430,0.142857),(-0.893844,-0.131791,0.428571),(-0.349927,0.925820,0.142857),(0.207758,0.403971,0.890867),(0.102875,-0.962246,0.251990),(-0.854550,-0.499336,0.142857),(0.946907,0.036426,0.319438),(0.530149,0.785430,-0.319438),(0.938398,-0.131791,-0.319438),(0.349927,0.925820,-0.142857),(0.475078,0.403971,0.781734),(0.710372,-0.499336,-0.496019),(-0.938398,0.131791,0.319438),(-0.089107,-0.617213,0.781734),(-0.202499,0.844369,-0.496019),(-0.971192,0.190729,-0.142857),(-0.946907,-0.036426,-0.319438),(-0.530149,-0.785430,0.319438),(0.382721,0.866881,0.319438),(-0.610747,0.617213,-0.496019),(0.571453,-0.249668,0.781734),(-0.382721,-0.866881,-0.319438),(0.049812,-0.866881,-0.496019),(-0.593729,-0.190729,0.781734),(0.893844,0.131791,-0.428571),(0.610747,-0.617213,0.496019),(0.593729,0.190729,-0.781734),(0.452802,-0.036426,-0.890867),(0.602238,-0.785430,-0.142857),(-0.049812,0.866881,0.496019),(0.089107,0.617213,-0.781734),(0.138919,-0.249668,0.958315),(0.971192,-0.190729,0.142857),(-0.874818,-0.462910,-0.142857),(-0.763434,0.594701,-0.251990),(-0.349927,-0.925820,0.142857),(-0.571453,0.249668,-0.781734),(-0.138919,0.249668,-0.958315),(-0.710372,0.499336,0.496019),(-0.583212,-0.690066,-0.428571),(-0.475078,-0.403971,-0.781734),(0.202499,-0.844369,0.496019),(-0.102875,0.962246,-0.251990),(0.854550,0.499336,-0.142857),(0.349927,-0.925820,-0.142857),(-0.207758,-0.403971,-0.890867),(0.524891,-0.462910,-0.714286),(0.368954,0.594701,-0.714286),(0.116642,-0.690066,-0.714286),(-0.699854,-0.000000,-0.714286),(-0.000000,0.000000,-1.000000)],
        [(0,1,5,2),(0,2,8,12,3),(0,3,10,4),(0,4,13,7,1),(1,7,17,6),(1,6,19,15,5),(2,5,16,23,9),(2,9,21,8),(3,12,27,11),(3,11,28,25,10),(4,10,26,32,14),(4,14,30,13),(5,15,33,16),(6,17,36,39,18),(6,18,38,19),(7,13,31,20),(7,20,41,37,17),(8,21,42,44,22),(8,22,29,12),(9,23,45,24),(9,24,47,43,21),(10,25,48,26),(11,27,51,38,18),(11,18,39,28),(12,29,41,52,27),(13,30,53,44,31),(14,32,47,24),(14,24,45,54,30),(15,19,40,34),(15,34,53,55,33),(16,33,56,52,35),(16,35,46,23),(17,37,57,36),(19,38,47,32,40),(20,31,49,46,35),(20,35,52,41),(21,43,58,42),(22,44,53,34),(22,34,40,50,29),(23,46,28,39,45),(25,28,46,49),(25,49,42,58,48),(26,48,57,37,50),(26,50,40,32),(27,52,56,51),(29,50,37,41),(30,54,55,53),(31,44,42,49),(33,55,59,56),(36,57,59,55,54),(36,54,45,39),(38,51,43,47),(43,51,56,59,58),(48,58,59,57)]),
    'Snub_dodecadodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.721748,0.000000,0.692156),(0.295222,0.658608,0.692156),(-0.480234,0.538791,0.692156),(-0.712807,0.113254,0.692156),(-0.394911,-0.604124,0.692156),(0.772902,-0.604124,0.194053),(0.992936,0.113254,-0.035388),(0.629839,0.696774,0.343233),(0.893447,0.289732,0.343233),(0.509494,0.859746,-0.035388),(-0.745221,0.665878,-0.035388),(-0.939228,0.006563,0.343233),(-0.416006,-0.219737,0.882414),(-0.039695,0.468796,0.882414),(-0.512702,0.786974,0.343233),(-0.906197,-0.401569,0.132471),(-0.638091,-0.769148,-0.035388),(0.082769,-0.977493,0.194053),(0.416117,-0.769148,-0.485035),(0.889939,-0.145947,-0.432098),(0.753950,-0.589311,-0.290296),(0.665511,0.043957,-0.745092),(0.078008,0.988112,-0.132471),(-0.104174,0.789751,0.604517),(0.352025,0.227978,0.907802),(0.678051,-0.418098,0.604517),(0.852489,0.281752,-0.440316),(0.506399,0.475359,-0.719439),(-0.133535,0.864239,-0.485035),(-0.626256,0.300351,-0.719439),(-0.988436,-0.073791,-0.132471),(-0.868533,0.333689,-0.366472),(-0.846151,-0.446943,-0.290296),(0.000439,-0.813104,0.582118),(0.368021,-0.201138,0.907802),(0.260905,0.914061,0.310516),(-0.582420,0.688534,-0.432098),(-0.825613,-0.046026,-0.562356),(-0.496743,-0.747909,-0.440316),(-0.322098,-0.894334,0.310516),(-0.755904,-0.299579,0.582118),(-0.059384,-0.824760,-0.562356),(-0.265405,-0.953525,-0.142657),(-0.260261,-0.533001,-0.805093),(0.854402,0.519316,-0.017549),(0.920603,-0.169915,0.351594),(0.450873,-0.796314,0.403233),(0.168291,-0.559395,-0.811638),(-0.052070,-0.163773,-0.985123),(0.100055,0.584649,-0.805093),(-0.400107,0.909568,-0.112251),(-0.788912,0.463703,0.403233),(-0.050766,-0.445265,0.893958),(0.503972,-0.863542,-0.017549),(0.611781,-0.431010,-0.663291),(0.255229,0.209118,-0.943996),(0.294417,0.832579,-0.469181),(-0.204463,0.236147,-0.949963),(-0.463514,-0.099213,-0.880518)],
        [(0,1,2),(0,2,3),(0,3,13,14,4),(0,4,5),(0,5,18,6,1),(1,6,7),(1,7,8),(1,8,25,9,2),(2,9,10),(2,10,29,11,3),(3,11,12),(3,12,13),(4,14,15),(4,15,37,38,16),(4,16,5),(5,16,40,41,17),(5,17,18),(6,18,19),(6,19,20),(6,20,46,21,7),(7,21,22),(7,22,50,23,8),(8,23,24),(8,24,25),(9,25,26),(9,26,54,55,27),(9,27,10),(10,27,57,45,28),(10,28,29),(11,29,30),(11,30,31),(11,31,52,32,12),(12,32,33),(12,33,43,34,13),(13,34,35),(13,35,14),(14,35,46,45,36),(14,36,15),(15,36,51,24,23),(15,23,37),(16,38,39),(16,39,40),(17,41,31),(17,31,30,49,42),(17,42,18),(18,42,54,43,19),(19,43,44),(19,44,58,28,20),(20,28,45),(20,45,46),(21,46,47),(21,47,40,39,48),(21,48,22),(22,48,56,55,49),(22,49,50),(23,50,37),(24,51,52),(24,52,41,53,25),(25,53,26),(26,53,47,35,34),(26,34,54),(27,55,56),(27,56,57),(28,58,29),(29,58,37,50,30),(30,50,49),(31,41,52),(32,52,51),(32,51,57,56,59),(32,59,33),(33,59,39,38,44),(33,44,43),(34,43,54),(35,47,46),(36,45,57),(36,57,51),(37,58,38),(38,58,44),(39,59,48),(40,47,53),(40,53,41),(42,49,55),(42,55,54),(48,59,56)]),
    'Ditrigonal_dodecadodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.942809,0.000000,0.333333),(0.672718,-0.660560,0.333333),(-0.471405,0.816497,0.333333),(0.235702,0.912871,0.333333),(-0.471405,-0.816497,0.333333),(-0.908421,-0.252311,0.333333),(0.090030,-0.660560,0.745356),(0.471405,0.816497,-0.333333),(0.471405,-0.816497,-0.333333),(0.617077,-0.252311,-0.745356),(0.908421,0.252311,-0.333333),(-0.235702,-0.912871,-0.333333),(0.527046,0.408248,0.745356),(-0.942809,0.000000,-0.333333),(-0.090030,0.660560,-0.745356),(-0.672718,0.660560,-0.333333),(-0.617077,0.252311,0.745356),(-0.527046,-0.408248,-0.745356),(0.000000,-0.000000,-1.000000)],
        [(0,1,7,13,2),(0,2,10,15,3),(0,3,13,17,4),(0,4,15,18,5),(0,5,17,7,6),(0,6,18,10,1),(1,10,2,11,9),(1,9,18,16,4),(1,4,11,13,8),(1,8,16,6,7),(2,13,3,14,12),(2,12,7,9,5),(2,5,14,15,11),(3,15,4,16,8),(3,8,10,12,6),(3,6,16,17,14),(4,17,5,9,11),(5,18,6,12,14),(7,17,16,19,9),(7,12,19,8,13),(8,19,11,15,10),(9,19,12,10,18),(11,19,14,17,13),(14,19,16,18,15)]),
    'Great_ditrigonal_dodecicosidodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.791367,0.000000,0.611341),(0.112651,0.783308,0.611341),(-0.682003,0.401415,0.611341),(-0.494411,-0.617916,0.611341),(0.414927,0.783308,0.462886),(0.900732,0.401415,-0.165977),(0.786049,-0.617916,-0.017523),(-0.269108,0.948700,-0.165977),(0.834396,0.299197,0.462886),(-0.754913,-0.464589,0.462886),(-0.572639,0.802830,-0.165977),(-0.008606,-0.999809,-0.017523),(-0.876170,-0.452524,-0.165977),(-0.870851,0.165392,0.462886),(0.033168,0.948700,-0.314432),(-0.143787,0.299197,0.943295),(0.827822,-0.464589,-0.314432),(0.218729,0.802830,-0.554636),(0.404289,-0.452524,-0.794841),(0.898700,0.165392,-0.406182),(0.216697,0.566807,-0.794841),(-0.763518,0.330784,-0.554636),(-0.827822,0.464589,0.314432),(0.275682,-0.184914,0.943295),(0.761487,-0.566807,0.314432),(-0.690609,-0.598394,-0.406182),(-0.033168,-0.948700,0.314432),(-0.027849,-0.330784,0.943295),(0.154425,0.936635,0.314432),(-0.577957,0.184914,-0.794841),(0.100758,-0.598394,-0.794841),(-0.154425,-0.936635,-0.314432),(-0.761487,0.566807,-0.314432),(0.027849,0.330784,-0.943295),(0.754913,0.464589,-0.462886),(0.577957,-0.184914,0.794841),(-0.216697,-0.566807,0.794841),(0.269108,-0.948700,0.165977),(0.763518,-0.330784,0.554636),(-0.275682,0.184914,-0.943295),(0.143787,-0.299197,-0.943295),(-0.100758,0.598394,0.794841),(-0.900732,-0.401415,0.165977),(-0.218729,-0.802830,0.554636),(0.870851,-0.165392,-0.462886),(-0.414927,-0.783308,-0.462886),(-0.404289,0.452524,0.794841),(0.876170,0.452524,0.165977),(0.572639,-0.802830,0.165977),(-0.834396,-0.299197,-0.462886),(0.690609,0.598394,0.406182),(0.682003,-0.401415,-0.611341),(-0.898700,-0.165392,0.406182),(-0.112651,-0.783308,-0.611341),(0.008606,0.999809,0.017523),(-0.791367,0.000000,-0.611341),(0.494411,0.617916,-0.611341),(-0.786049,0.617916,0.017523),(-0.000000,-0.000000,-1.000000)],
        [(0,1,5,16,36,51,42,24,9,2),(0,2,3),(0,3,10,28,47,53,37,16,14,4),(0,4,12,7,1),(1,7,20,9,25,45,48,39,17,6),(1,6,5),(2,9,20,21,8),(2,8,23,42,55,58,47,29,11,3),(3,11,30,26,10),(4,14,13),(4,13,32,44,43,46,27,10,26,12),(5,6,18,29,48,57,55,51,35,15),(5,15,33,14,16),(6,17,31,40,18),(7,12,31,17,38,54,52,49,32,19),(7,19,20),(8,21,30,11,18,40,33,15,34,22),(8,22,23),(9,24,25),(10,27,28),(11,29,18),(12,26,31),(13,14,33,50,53,58,56,43,23,22),(13,22,34,19,32),(15,35,34),(16,37,36),(17,39,38),(19,34,35,52,59,57,45,41,21,20),(21,41,30),(23,43,44,24,42),(24,44,49,36,37,38,39,28,27,25),(25,27,46,41,45),(26,30,41,46,56,59,54,50,40,31),(28,39,48,29,47),(32,49,44),(33,40,50),(35,51,36,49,52),(37,53,50,54,38),(42,51,55),(43,56,46),(45,57,48),(47,58,53),(52,54,59),(55,57,59,56,58)]),
    'Small_ditrigonal_dodecicosidodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.555851,0.000000,0.831282),(-0.542335,0.121833,0.831282),(-0.354742,0.427935,0.831282),(0.252320,-0.495283,0.831282),(0.912902,0.121833,0.389573),(0.756960,0.427935,0.493846),(-0.019561,0.352638,0.935555),(-0.832349,-0.251616,0.493846),(-0.864000,0.318964,0.389573),(-0.676407,0.625065,0.389573),(-0.153633,0.855870,0.493846),(-0.323092,-0.142645,0.935555),(-0.037695,-0.868732,0.493846),(0.305840,-0.868732,0.389573),(0.536290,0.352638,0.766838),(0.966422,-0.251616,-0.052137),(0.934772,0.318964,-0.156410),(0.778829,0.625065,-0.052137),(0.402217,0.855870,0.325128),(0.788610,-0.142645,0.598120),(0.181548,0.780572,0.598120),(-0.580029,-0.746899,0.325128),(-0.778829,-0.625065,0.052137),(-0.842130,0.516094,-0.156410),(-0.662891,0.746899,0.052137),(-0.966422,0.251616,0.052137),(0.203418,0.977703,0.052137),(-0.613107,-0.516094,0.598120),(-0.070772,-0.637928,0.766838),(0.485079,-0.637928,0.598120),(-0.203418,-0.977703,-0.052137),(0.140117,-0.977703,-0.156410),(0.662891,-0.746899,-0.052137),(0.676407,-0.625065,-0.389573),(0.613107,0.516094,-0.598120),(0.580029,0.746899,-0.325128),(0.832349,0.251616,-0.493846),(-0.140117,0.977703,0.156410),(0.842130,-0.516094,0.156410),(-0.934772,-0.318964,0.156410),(-0.402217,-0.855870,-0.325128),(-0.756960,-0.427935,-0.493846),(-0.788610,0.142645,-0.598120),(-0.485079,0.637928,-0.598120),(-0.305840,0.868732,-0.389573),(-0.912902,-0.121833,-0.389573),(0.037695,0.868732,-0.493846),(-0.181548,-0.780572,-0.598120),(0.153633,-0.855870,-0.493846),(0.864000,-0.318964,-0.389573),(0.354742,-0.427935,-0.831282),(0.323092,0.142645,-0.935555),(0.070772,0.637928,-0.766838),(0.542335,-0.121833,-0.831282),(-0.555851,0.000000,-0.831282),(-0.536290,-0.352638,-0.766838),(-0.252320,0.495283,-0.831282),(0.019561,-0.352638,-0.935555),(-0.000000,0.000000,-1.000000)],
        [(0,1,5,17,35,53,44,24,9,2),(0,2,7,12,3),(0,3,10,24,43,56,48,32,14,4),(0,4,1),(1,4,13,31,48,58,52,35,18,6),(1,6,20,15,5),(2,9,8),(2,8,23,41,49,34,16,5,15,7),(3,12,29,14,33,50,37,36,27,11),(3,11,10),(4,14,29,30,13),(5,16,17),(6,18,19),(6,19,38,25,26,40,22,13,30,20),(7,15,21),(7,21,27,47,57,55,42,23,28,12),(8,9,25,45,53,52,51,49,31,22),(8,22,40,28,23),(9,24,10,26,25),(10,11,19,18,37,54,58,56,46,26),(11,27,21,38,19),(12,28,29),(13,22,31),(14,32,33),(15,20,39,34,51,59,57,45,38,21),(16,34,39,50,33),(16,33,32,41,42,43,44,47,36,17),(17,36,37,18,35),(20,30,39),(23,42,41),(24,44,43),(25,38,45),(26,46,40),(27,36,47),(28,40,46,55,59,54,50,39,30,29),(31,49,41,32,48),(34,49,51),(35,52,53),(37,50,54),(42,55,46,56,43),(44,53,45,57,47),(48,56,58),(51,52,58,54,59),(55,57,59)]),
    'Icosidodecadodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.699854,0.000000,0.714286),(-0.524891,0.462910,0.714286),(-0.116642,0.690066,0.714286),(-0.368954,-0.594701,0.714286),(0.874818,0.462910,0.142857),(0.583212,0.690066,0.428571),(0.763434,-0.594701,0.251990),(0.207758,0.403971,0.890867),(-0.893844,-0.131791,0.428571),(-0.349927,0.925820,0.142857),(-0.602238,0.785430,0.142857),(-0.452802,0.036426,0.890867),(0.102875,-0.962246,0.251990),(-0.854550,-0.499336,0.142857),(0.475078,0.403971,0.781734),(0.938398,-0.131791,-0.319438),(0.349927,0.925820,-0.142857),(0.530149,0.785430,-0.319438),(0.946907,0.036426,0.319438),(0.710372,-0.499336,-0.496019),(0.571453,-0.249668,0.781734),(0.382721,0.866881,0.319438),(-0.946907,-0.036426,-0.319438),(-0.530149,-0.785430,0.319438),(-0.610747,0.617213,-0.496019),(-0.202499,0.844369,-0.496019),(-0.938398,0.131791,0.319438),(-0.971192,0.190729,-0.142857),(-0.089107,-0.617213,0.781734),(0.049812,-0.866881,-0.496019),(-0.382721,-0.866881,-0.319438),(-0.593729,-0.190729,0.781734),(0.138919,-0.249668,0.958315),(-0.049812,0.866881,0.496019),(0.452802,-0.036426,-0.890867),(0.602238,-0.785430,-0.142857),(0.089107,0.617213,-0.781734),(0.893844,0.131791,-0.428571),(0.593729,0.190729,-0.781734),(0.610747,-0.617213,0.496019),(0.971192,-0.190729,0.142857),(0.202499,-0.844369,0.496019),(-0.102875,0.962246,-0.251990),(0.854550,0.499336,-0.142857),(-0.475078,-0.403971,-0.781734),(-0.583212,-0.690066,-0.428571),(-0.138919,0.249668,-0.958315),(-0.571453,0.249668,-0.781734),(-0.763434,0.594701,-0.251990),(-0.874818,-0.462910,-0.142857),(-0.710372,0.499336,0.496019),(-0.349927,-0.925820,0.142857),(-0.207758,-0.403971,-0.890867),(0.349927,-0.925820,-0.142857),(0.116642,-0.690066,-0.714286),(0.368954,0.594701,-0.714286),(0.524891,-0.462910,-0.714286),(-0.699854,-0.000000,-0.714286),(0.000000,-0.000000,-1.000000)],
        [(0,1,5,17,10,2),(0,2,8,12,3),(0,3,11,28,14,4),(0,4,13,7,1),(1,7,20,39,18,6),(1,6,19,15,5),(2,10,25,23,9),(2,9,24,42,21,8),(3,12,29,40,19,6),(3,6,18,26,11),(4,14,32,24,9),(4,9,23,45,30,13),(5,15,33,42,36,16),(5,16,35,37,17),(7,13,31,53,35,16),(7,16,36,41,20),(8,21,41,44,22),(8,22,43,49,27,12),(10,17,34,43,22),(10,22,44,39,47,25),(11,26,47,45,50,27),(11,27,49,51,28),(12,27,50,52,29),(13,30,52,54,31),(14,28,48,53,31),(14,31,54,40,33,32),(15,19,38,56,43,34),(15,34,51,32,33),(17,37,48,28,51,34),(18,39,44,56,38),(18,38,57,53,48,26),(19,40,54,57,38),(20,41,21,29,52,30),(20,30,45,47,39),(21,42,33,40,29),(23,25,37,35,55,46),(23,46,58,50,45),(24,32,51,49,58,46),(24,46,55,36,42),(25,47,26,48,37),(35,53,57,59,55),(36,55,59,56,44,41),(43,56,59,58,49),(50,58,59,57,54,52)]),
    'Icositruncated_dodecadodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.484123,0.000000,0.875000),(0.127301,0.467086,0.875000),(-0.450049,-0.178411,0.875000),(0.312219,0.467086,0.827254),(0.817401,-0.178411,0.547746),(-0.195448,0.755761,0.625000),(0.532748,0.178411,0.827254),(-0.694122,-0.467086,0.547746),(-0.772798,0.110264,0.625000),(0.473594,0.755761,0.452254),(-0.065661,0.178411,0.981763),(0.872533,-0.467086,0.143237),(0.978775,0.110264,0.172746),(-0.312219,0.934172,0.172746),(-0.645497,0.577350,0.500000),(0.154867,-0.110264,0.981763),(0.866025,0.000000,0.500000),(-0.866025,-0.000000,0.500000),(-0.638990,-0.755761,0.143237),(-0.817401,-0.356822,0.452254),(0.356822,0.934172,0.000000),(0.806872,0.577350,0.125000),(0.339785,-0.110264,0.934017),(-0.515711,0.000000,0.856763),(0.999834,-0.000000,0.018237),(0.628460,-0.755761,-0.184017),(0.934172,-0.356822,0.000000),(-0.690100,0.645497,0.327254),(-0.178411,0.934172,-0.309017),(-0.484123,0.866025,0.125000),(0.110264,-0.577350,0.809017),(-0.017037,0.356822,0.934017),(0.821423,-0.467086,0.327254),(-0.982797,0.178411,0.047746),(-0.305712,-0.934172,-0.184017),(-0.755761,-0.577350,-0.309017),(-0.467086,-0.356822,0.809017),(-0.762269,-0.645497,0.047746),(0.762269,0.645497,-0.047746),(0.006507,0.934172,-0.356763),(0.484123,0.866025,-0.125000),(0.295183,-0.577350,0.761271),(0.467086,0.356822,0.809017),(-0.560314,-0.467086,0.684017),(0.883062,0.178411,-0.434017),(0.178411,-0.934172,-0.309017),(0.511689,-0.577350,-0.636271),(0.800364,-0.356822,0.481763),(0.690100,-0.645497,-0.327254),(-0.934172,0.356822,0.000000),(-0.339785,0.645497,0.684017),(0.154867,0.755761,-0.636271),(-0.422483,0.645497,-0.636271),(-0.133808,0.866025,0.481763),(-0.350315,0.866025,-0.356763),(-0.133808,-0.866025,0.481763),(0.443542,-0.755761,0.481763),(0.982797,-0.178411,-0.047746),(-0.821423,0.467086,-0.327254),(-0.927665,-0.110264,-0.356763),(-0.628460,-0.645497,-0.434017),(-0.350315,-0.866025,-0.356763),(-0.061640,-0.645497,0.761271),(-0.638990,0.110264,0.761271),(-0.356822,-0.934172,0.000000),(0.817401,0.356822,-0.452254),(0.628460,0.645497,0.434017),(-0.443542,0.755761,-0.481763),(0.061640,0.645497,-0.761271),(0.350315,0.866025,0.356763),(0.133808,0.866025,-0.481763),(0.350315,-0.866025,0.356763),(-0.154867,-0.755761,0.636271),(-0.883062,-0.178411,0.434017),(0.560314,0.467086,-0.684017),(0.638990,-0.110264,-0.761271),(0.339785,-0.645497,-0.684017),(0.133808,-0.866025,-0.481763),(0.422483,-0.645497,0.636271),(0.927665,0.110264,0.356763),(0.312219,-0.934172,-0.172746),(-0.978775,-0.110264,-0.172746),(-0.800364,0.356822,-0.481763),(-0.178411,0.934172,0.309017),(-0.295183,0.577350,-0.761271),(-0.511689,0.577350,0.636271),(-0.484123,-0.866025,0.125000),(-0.006507,-0.934172,0.356763),(0.866025,-0.000000,-0.500000),(-0.866025,-0.000000,-0.500000),(-0.467086,-0.356822,-0.809017),(-0.473594,-0.755761,-0.452254),(0.772798,-0.110264,-0.625000),(0.467086,0.356822,-0.809017),(0.305712,0.934172,0.184017),(-0.110264,0.577350,-0.809017),(0.755761,0.577350,0.309017),(0.484123,-0.866025,-0.125000),(0.178411,-0.934172,0.309017),(-0.999834,0.000000,-0.018237),(0.515711,-0.000000,-0.856763),(0.017037,-0.356822,-0.934017),(0.195448,-0.755761,-0.625000),(-0.817401,0.178411,-0.547746),(-0.806872,-0.577350,-0.125000),(-0.628460,0.755761,0.184017),(-0.339785,0.110264,-0.934017),(0.694122,0.467086,-0.547746),(-0.532748,-0.178411,-0.827254),(-0.312219,-0.467086,-0.827254),(0.450049,0.178411,-0.875000),(0.645497,-0.577350,-0.500000),(0.638990,0.755761,-0.143237),(-0.154867,0.110264,-0.981763),(-0.872533,0.467086,-0.143237),(0.065661,-0.178411,-0.981763),(-0.127301,-0.467086,-0.875000),(-0.484123,0.000000,-0.875000),(-0.000000,-0.000000,-1.000000)],
        [(0,1,4,11,23,43,32,16,7,2),(0,2,6,15,9,3),(0,3,8,19,35,46,26,12,5,1),(1,5,13,22,10,4),(2,7,17,25,45,75,52,29,14,6),(3,9,20,37,64,74,44,24,18,8),(4,10,21,40,68,59,34,18,24,11),(5,12,25,17,33,58,80,48,27,13),(6,14,28,51,84,106,86,54,30,15),(7,16,31,57,33,17),(8,18,34,60,36,19),(9,15,30,55,85,107,91,61,38,20),(10,22,41,70,97,113,95,67,39,21),(11,24,44,73,42,23),(12,26,47,76,45,25),(13,27,49,77,102,114,96,71,41,22),(14,29,53,83,50,28),(16,32,51,28,50,82,105,87,56,31),(19,36,62,87,105,92,65,38,61,35),(20,38,65,88,63,37),(21,39,66,94,69,40),(23,42,72,98,112,93,66,39,67,43),(26,46,77,49,81,103,112,98,78,47),(27,48,79,99,81,49),(29,52,85,55,71,96,68,40,69,53),(30,54,70,41,71,55),(31,56,72,42,73,99,79,63,88,57),(32,43,67,95,84,51),(33,57,88,65,92,110,116,101,89,58),(34,59,90,100,115,104,82,50,83,60),(35,61,91,102,77,46),(36,60,83,53,69,94,76,47,78,62),(37,63,79,48,80,97,70,54,86,64),(44,74,100,90,109,117,103,81,99,73),(45,76,94,66,93,111,108,89,101,75),(52,75,101,116,107,85),(56,87,62,78,98,72),(58,89,108,113,97,80),(59,68,96,114,109,90),(64,86,106,115,100,74),(82,104,118,110,92,105),(84,95,113,108,111,119,118,104,115,106),(91,107,116,110,118,119,117,109,114,102),(93,112,103,117,119,111)]),
    'Snub_icosidodecadodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.795261,0.000000,0.606268),(0.300162,0.736439,0.606268),(0.705509,0.367009,0.606268),(-0.073576,0.791850,0.606268),(-0.761051,0.230740,0.606268),(-0.500924,-0.617669,0.606268),(0.785835,-0.617669,-0.030804),(0.943541,0.230740,-0.237673),(0.924378,-0.316786,-0.212536),(0.826910,0.555921,-0.084684),(0.055541,0.975574,-0.212536),(-0.319325,0.188912,0.928625),(0.519999,-0.088135,0.849608),(-0.135867,0.509615,0.849608),(0.217645,-0.300478,0.928625),(0.832736,-0.459392,0.309048),(-0.317046,0.918147,-0.237673),(-0.837187,0.451228,0.309048),(-0.630041,0.771930,-0.084684),(-0.733840,-0.604953,0.309048),(-0.158558,-0.335434,0.928625),(-0.946811,0.089657,0.309048),(-0.773537,-0.587496,-0.237673),(-0.015251,-0.999409,-0.030804),(0.279959,-0.587496,-0.759257),(0.034812,-0.917492,-0.396228),(0.510207,-0.292084,-0.808935),(0.311567,0.571362,-0.759257),(0.863742,0.426525,0.268376),(0.680124,-0.358309,0.639567),(0.347460,-0.936140,0.053981),(0.122252,0.824574,-0.552388),(0.138543,0.934455,0.328024),(0.615276,0.675096,0.407041),(0.753788,0.480996,-0.447713),(-0.004331,0.424436,-0.905448),(-0.715131,0.575840,-0.396228),(-0.873285,-0.267754,0.407041),(-0.148678,-0.660364,0.736080),(0.599627,-0.753937,0.268376),(-0.158104,0.982446,0.099008),(-0.265193,-0.859529,0.436900),(0.087400,-0.940618,0.328024),(0.876554,-0.052643,-0.478416),(-0.521862,0.270710,-0.808935),(-0.797729,0.241861,-0.552388),(-0.917115,-0.394950,0.053981),(-0.493273,0.463539,0.736080),(-0.586013,-0.580251,-0.565595),(-0.329425,-0.831283,-0.447713),(-0.824977,-0.300883,-0.478416),(-0.215782,0.117903,-0.969297),(0.744117,-0.402195,-0.533413),(0.158299,-0.282485,-0.946120),(0.480975,0.741627,-0.467603),(-0.070516,-0.713968,-0.696619),(0.161026,0.093573,-0.982504),(-0.873026,0.483227,-0.065708),(-0.675792,-0.066127,-0.734120)],
        [(0,1,2),(0,2,13,14,3),(0,3,4),(0,4,5),(0,5,6),(0,6,24,7,1),(1,7,8),(1,8,16,29,9),(1,9,10),(1,10,2),(2,10,11),(2,11,37,22,12),(2,12,13),(3,14,15),(3,15,16),(3,16,8),(3,8,28,17,4),(4,17,18),(4,18,41,48,19),(4,19,5),(5,19,45,49,20),(5,20,21),(5,21,38,12,6),(6,12,22),(6,22,23),(6,23,24),(7,24,25),(7,25,31,53,26),(7,26,27),(7,27,8),(8,27,28),(9,29,30),(9,30,31),(9,31,25),(9,25,52,32,10),(10,32,33),(10,33,55,34,11),(11,34,35),(11,35,36),(11,36,37),(12,38,39),(12,39,13),(13,39,40),(13,40,53,35,34),(13,34,14),(14,34,41),(14,41,18),(14,18,47,42,15),(15,42,40),(15,40,39,30,43),(15,43,16),(16,43,50,54,44),(16,44,29),(17,28,45),(17,45,32,37,36),(17,36,46),(17,46,18),(18,46,47),(19,48,33),(19,33,32),(19,32,45),(20,49,24),(20,24,23,42,50),(20,50,43),(20,43,21),(21,43,30),(21,30,29,33,48),(21,48,38),(22,37,51),(22,51,58,47,46),(22,46,23),(23,46,36,27,26),(23,26,42),(24,49,25),(25,49,52),(26,53,40),(26,40,42),(27,36,35),(27,35,57,44,28),(28,44,54),(28,54,45),(29,44,55),(29,55,33),(30,39,31),(31,39,38,51,56),(31,56,53),(32,52,37),(34,55,41),(35,53,57),(37,52,51),(38,48,58),(38,58,51),(41,55,57,59,58),(41,58,48),(42,47,50),(44,57,55),(45,54,49),(47,58,59),(47,59,50),(49,54,59,56,52),(50,59,54),(51,52,56),(53,56,57),(56,59,57)]),
    'Great_ditrigonal_icosidodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.942809,0.000000,0.333333),(0.235702,0.912871,0.333333),(-0.471405,-0.816497,0.333333),(0.672718,-0.660560,0.333333),(-0.471405,0.816497,0.333333),(-0.908421,-0.252311,0.333333),(0.471405,-0.816497,-0.333333),(0.090030,-0.660560,0.745356),(0.471405,0.816497,-0.333333),(0.617077,-0.252311,-0.745356),(-0.090030,0.660560,-0.745356),(0.908421,0.252311,-0.333333),(-0.617077,0.252311,0.745356),(-0.672718,0.660560,-0.333333),(-0.942809,-0.000000,-0.333333),(-0.527046,-0.408248,-0.745356),(-0.235702,-0.912871,-0.333333),(0.527046,0.408248,0.745356),(-0.000000,0.000000,-1.000000)],
        [(0,1,2),(0,2,11,16,3),(0,3,4),(0,4,10,11,5),(0,5,6),(0,6,16,10,1),(1,10,9),(1,9,14,6,8),(1,8,7),(1,7,16,14,2),(2,14,13),(2,13,3,7,12),(2,12,11),(3,16,7),(3,13,15),(3,15,11,12,4),(4,12,18),(4,18,5,15,17),(4,17,10),(5,11,15),(5,18,9),(5,9,10,17,6),(6,17,8),(6,14,16),(7,8,13,14,19),(7,19,12),(8,17,19,9,18),(8,18,13),(9,19,14),(10,16,11),(12,19,15,13,18),(15,19,17)]),
    'Great_icosicosidodecahedron' : (
        [(0.000000,0.000000,1.000000),(0.791367,0.000000,0.611341),(-0.682003,0.401415,0.611341),(0.112651,0.783308,0.611341),(-0.494411,-0.617916,0.611341),(0.900732,0.401415,-0.165977),(0.414927,0.783308,0.462886),(0.786049,-0.617916,-0.017523),(-0.754913,-0.464589,0.462886),(-0.572639,0.802830,-0.165977),(-0.269108,0.948700,-0.165977),(0.834396,0.299197,0.462886),(-0.008606,-0.999809,-0.017523),(-0.870851,0.165392,0.462886),(-0.876170,-0.452524,-0.165977),(0.827822,-0.464589,-0.314432),(0.218729,0.802830,-0.554636),(0.033168,0.948700,-0.314432),(-0.143787,0.299197,0.943295),(0.898700,0.165392,-0.406182),(0.404289,-0.452524,-0.794841),(-0.690609,-0.598394,-0.406182),(-0.027849,-0.330784,0.943295),(-0.033168,-0.948700,0.314432),(0.154425,0.936635,0.314432),(-0.577957,0.184914,-0.794841),(0.216697,0.566807,-0.794841),(-0.827822,0.464589,0.314432),(-0.763518,0.330784,-0.554636),(0.761487,-0.566807,0.314432),(0.275682,-0.184914,0.943295),(0.100758,-0.598394,-0.794841),(-0.761487,0.566807,-0.314432),(-0.154425,-0.936635,-0.314432),(0.763518,-0.330784,0.554636),(0.269108,-0.948700,0.165977),(-0.275682,0.184914,-0.943295),(0.754913,0.464589,-0.462886),(0.027849,0.330784,-0.943295),(-0.216697,-0.566807,0.794841),(0.577957,-0.184914,0.794841),(-0.404289,0.452524,0.794841),(-0.414927,-0.783308,-0.462886),(0.876170,0.452524,0.165977),(0.143787,-0.299197,-0.943295),(-0.100758,0.598394,0.794841),(-0.900732,-0.401415,0.165977),(0.870851,-0.165392,-0.462886),(-0.218729,-0.802830,0.554636),(-0.834396,-0.299197,-0.462886),(0.572639,-0.802830,0.165977),(-0.112651,-0.783308,-0.611341),(0.690609,0.598394,0.406182),(0.682003,-0.401415,-0.611341),(-0.898700,-0.165392,0.406182),(-0.786049,0.617916,0.017523),(-0.791367,0.000000,-0.611341),(0.494411,0.617916,-0.611341),(0.008606,0.999809,0.017523),(0.000000,-0.000000,-1.000000)],
        [(0,1,5,16,9,2),(0,2,3),(0,3,10,28,14,4),(0,4,12,7,1),(1,7,20,38,17,6),(1,6,5),(2,9,25,21,8),(2,8,23,29,11,3),(3,11,19,26,10),(4,14,13),(4,13,32,36,31,12),(5,6,18,39,35,15),(5,15,31,36,16),(6,17,32,13,18),(7,12,21,25,26,19),(7,19,20),(8,21,31,15,34,22),(8,22,23),(9,16,24),(9,24,43,47,44,25),(10,26,44,42,46,27),(10,27,28),(11,29,30),(11,30,48,33,20,19),(12,31,21),(13,14,33,50,40,18),(14,28,38,20,33),(15,35,34),(16,36,49,54,41,24),(17,38,37),(17,37,53,51,49,32),(18,40,39),(22,34,43,24,41),(22,41,55,56,42,23),(23,42,44,47,29),(25,44,26),(27,46,48,30,45),(27,45,52,37,38,28),(29,47,57,58,45,30),(32,49,36),(33,48,50),(34,35,51,59,57,43),(35,39,54,49,51),(37,52,40,50,53),(39,40,52,58,55,54),(41,54,55),(42,56,46),(43,57,47),(45,58,52),(46,56,59,53,50,48),(51,53,59),(55,58,57,59,56)])

    })

def getPolyhedraList():
    #return _GLI.polyhedraDict.keys()
    return ['cube', 'cuboctahedron', 'dodecahedron', 
            'great ditrigonal icosidodecahedron', 'great dodecahedron',
            'great icosicosidodecahedron', 'great rhombicuboctahedron',
            'icosahedron', 'icosidodecahedron', 'octahedron',
            'octahemioctahedron', 'pentagonal antiprism', 'pentagonal prism',
            'rhombicosidodecahedron', 'rhombicuboctahedron',
            'small cubicuboctahedron', 'small dodecicosidodecahedron',
            'snub cube','snub dodecahedron',
            'tetrahedron', 'truncated cube', 'truncated cuboctahedron', 'truncated dodecahedron',
            'truncated icosahedron', 'truncated icosidodecahedron',
            'truncated octahedron', 'truncated tetrahedron']

#############################################################################
#############################################################################
#############################################################################

class Collada:

    def __init__(self, filename, stats=True):
        self.givenFilename = filename
        (self.daeFile, self.zipMode) = self.determineDAE(filename)
        self.stats = stats
        self.up_axis = None
        self.images = dict()        # key is image_id, value is pathname to image file
        self.effects = dict()       # key is effect_id, value is an MaterialEffect object
        self.materials = dict()     # key is material_id, value is effect_id
        self.geometries = dict()    # key is geometry_id, value is list of GeometryPrimitive objects
        self.nodes = dict()         # key is node_id, value is Node object
        self.visual_scenes = dict() # key is visual_scene_id, value is Node object for the Model node
        self.scene = None           # visual_scene id for primary visual_scene
        self.minx = self.miny = self.minz = float('infinity')
        self.maxx = self.maxy = self.maxz = -float('infinity')
        self.sumx = self.sumy = self.sumz = 0
        self.countVertices = 0
        self.countPolygons = 0
       
        self.read(self.daeFile)
        self.components = self.buildComponentList()

        if self.stats:
            self.avgx = self.sumx / float(self.countVertices)
            self.avgy = self.sumy / float(self.countVertices)
            self.avgz = self.sumz / float(self.countVertices)
            print("read "+self.givenFilename+" with "+str(self.countPolygons)+" polygons")
            fmt = ".3f"
            print("   x avg = " + format(self.avgx, fmt) + " ranging from " + format(self.minx, fmt) + " to " + format(self.maxx, fmt))
            print("   y avg = " + format(self.avgy, fmt) + " ranging from " + format(self.miny, fmt) + " to " + format(self.maxy, fmt))
            print("   z avg = " + format(self.avgz, fmt) + " ranging from " + format(self.minz, fmt) + " to " + format(self.maxz, fmt))           

    def determineDAE(self, givenFilename):
        if not os.path.exists(givenFilename):
            raise ValueError("ERROR: no such file: " + givenFilename)
        if givenFilename.endswith('.dae'):
            return (givenFilename, False)
        elif os.path.isdir(givenFilename):
            modelsdir = os.path.join(givenFilename, "models")
            if os.path.isdir(modelsdir):
                filelist = os.listdir(modelsdir)
                filedir = modelsdir
            else:
                filelist = os.listdir(givenFilename)
                filedir = givenFilename
            daefiles = [name for name in filelist if name.endswith('.dae')]
            if len(daefiles) > 1:
                raise ValueError('ERROR: too many .dae files in ' + givenFilename)
            if len(daefiles) == 0:
                raise ValueError('ERROR: no .dae files found in ' + givenFilename)
            return (os.path.join(filedir, daefiles[0]), False)
        elif givenFilename.endswith('.zip'):
            ziparchive = zipfile.ZipFile(givenFilename)
            zipcontents = ziparchive.namelist()
            self.ziparchiveFiles = dict()
            for original in zipcontents:
                self.ziparchiveFiles[original.lower()] = original
            daefiles = [self.ziparchiveFiles[name] for name in self.ziparchiveFiles if name.endswith('.dae')]
            if len(daefiles) > 1:
                raise ValueError('ERROR: too many .dae files in ' + givenFilename)
            if len(daefiles) == 0:
                raise ValueError('ERROR: no .dae files found in ' + givenFilename)
            daefile = ziparchive.open(daefiles[0])
            self.ziparchive = ziparchive
            return (daefile, True) 
        else:
            raise ValueError('ERROR: not a .dae file or folder: ' + givenFilename)

    @staticmethod
    def tag(tag):
        return str(xml.etree.ElementTree.QName('http://www.collada.org/2005/11/COLLADASchema', tag))

    def read(self, filename):
        print("reading " + self.givenFilename)
        self.tree = xml.etree.ElementTree.parse(filename)
        root = self.tree.getroot()
        self.readAsset(root.find(Collada.tag('asset')))
        self.images = self.readLibraryImages(root.find(Collada.tag('library_images')))
        self.effects = self.readLibraryEffects(root.find(Collada.tag('library_effects')))
        self.materials = self.readLibraryMaterials(root.find(Collada.tag('library_materials')))
        self.geometries = self.readLibraryGeometries(root.find(Collada.tag('library_geometries')))
        self.readLibraryNodes(root.find(Collada.tag('library_nodes')))
        self.visual_scenes = self.readLibraryVisualScenes(root.find(Collada.tag('library_visual_scenes')))
        self.scene = self.readScene(root.find(Collada.tag('scene')))
        
    def readAsset(self, asset):
        up_axis_element = asset.find(Collada.tag('up_axis'))
        if up_axis_element is None:
            self.up_axis = 'Z_UP'
        else:
            self.up_axis = up_axis_element.text
        assert self.up_axis in ['X_UP', 'Y_UP', 'Z_UP'], "unknown up_axis type: "+str(self.up_axis)

    def readLibraryImages(self, library_images):
        images = dict()
        if library_images is None:
            return
        imagelist = library_images.findall(Collada.tag('image'))
        for image in imagelist:
            image_id = image.get('id')
            init_from = image.find(Collada.tag('init_from'))
            image_name = init_from.text
            if not self.zipMode:
                images[image_id] = os.path.join(os.path.dirname(self.daeFile), image_name)
            else:
                image_name = self.ziparchiveFiles[image_name.lstrip('./').lower()]
                image_data = self.ziparchive.open(image_name).read()
                raise Exception("cStringIO not supported in Python 3")
                #image_file_object = cStringIO.StringIO(image_data)
                images[image_id] = (image_file_object, os.path.join(self.givenFilename, image_name))
        return images
        
    def readLibraryEffects(self, library_effects):
        effects = dict()
        effectlist = library_effects.findall(Collada.tag('effect'))
        for effect in effectlist:
            effect_id = effect.get('id')
            profile_common = effect.find(Collada.tag('profile_COMMON'))
            samplers = dict() # key is newparam sid, value is sampler source text
            surfaces = dict() # key is newparam sid, value is init_from text
            newparam_elements = profile_common.findall(Collada.tag('newparam'))
            for newparam in newparam_elements:
                newparam_id = newparam.get('sid')
                for newparam_child in newparam.getchildren():
                    if newparam_child.tag == Collada.tag('surface'):
                        init_from = newparam_child.find(Collada.tag('init_from'))
                        surfaces[newparam_id] = init_from.text
                    elif newparam_child.tag == Collada.tag('sampler2D'):
                        source = newparam_child.find(Collada.tag('source'))
                        samplers[newparam_id] = source.text
                    else:
                        assert False, 'unknown newparam type: ' + str(newparam_child.tag)
            technique = profile_common.find(Collada.tag('technique'))
            shader = technique.find(Collada.tag('lambert'))
            if shader is None:
                shader = technique.find(Collada.tag('phong'))
            if shader is not None:
                diffuse = shader.find(Collada.tag('diffuse'))
                colorElement = diffuse.find(Collada.tag('color'))
                effectType = Collada.MaterialEffect()
                if colorElement is not None:
                    diffuseColor = [float(n) for n in colorElement.text.split()]
                    assert len(diffuseColor) == 4
                    effectType.diffuse = diffuseColor
                else:
                    texture = diffuse.find(Collada.tag('texture'))
                    if texture is not None:
                        textureSampler = texture.get('texture')
                        sampler_surface = samplers[textureSampler]
                        surface_image = surfaces[sampler_surface]
                        image_file = self.images[surface_image]
                        effectType.texture = image_file
                    else:
                        assert False, "unknown diffuse type"
            else:
                shader = technique.find(Collada.tag('constant'))
                if shader is not None:
                    # really bad handling of constant shaders - this is not right
                    transparent = shader.find(Collada.tag('transparent'))
                    colorElement = transparent.find(Collada.tag('color'))
                    effectType = Collada.MaterialEffect()
                    effectType.diffuse = [float(n) for n in colorElement.text.split()]
                else:
                    print("WARNING: unknown shader type in effect " + effect_id)
                    effectType = None

            effects[effect_id] = effectType
        return effects

    def readLibraryMaterials(self, library_materials):
        materials = dict()
        materiallist = library_materials.findall(Collada.tag('material'))
        for material in materiallist:
            material_id = material.get('id')
            instance_effect = material.find(Collada.tag('instance_effect'))
            effect = instance_effect.get('url').lstrip('#')
            assert effect in self.effects
            materials[material_id] = effect
        return materials

    def readLibraryGeometries(self, library_geometries):
        geometries = dict()
        
        sources = dict()
            # key is source_id
            # value is a dictionary
            #    where key is param name(like X,Y,Z,S,T) and value is list of floats for that param
            
        vertices = dict()
            # key is vertices_id
            # value is a dictionary
            #     where key is semantic name (like POSITION,NORMAL) and value is source id
            
        for geometry in library_geometries.getchildren():
            geometry_id = geometry.get('id')
            primitives = list()
            mesh = geometry.find(Collada.tag('mesh'))
            for meshchild in mesh.getchildren():
                if (meshchild.tag == Collada.tag('source')):
                    self.readMeshSource(meshchild, sources)
                elif (meshchild.tag == Collada.tag('vertices')):
                    self.readMeshVertices(meshchild, vertices)
                elif (meshchild.tag == Collada.tag('triangles')):
                    primitives.append(self.readMeshPrimitive(meshchild, Collada.GeometryTriangles(), sources, vertices))
                elif (meshchild.tag == Collada.tag('lines')):
                    primitives.append(self.readMeshPrimitive(meshchild, Collada.GeometryLines(),sources, vertices))
                else:
                    print("WARNING: unhandled mesh type: "+meshchild.tag+" in geometry "+geometry_id)
            geometries[geometry_id] = primitives
                    
        return geometries
                    
    def readMeshSource(self, source, sources):
        source_id = source.get('id')
        assert source_id not in sources
        float_array = source.find(Collada.tag('float_array'))
        float_array_id = float_array.get('id')
        float_array_count = int(float_array.get('count'))
        float_array_text_list = float_array.text.split()
        assert len(float_array_text_list) == float_array_count, 'float array length error for '+float_array_id+' '+str(len(float_array_text_list))+' != '+str(float_array_count)
        technique_common = source.find(Collada.tag('technique_common'))
        accessor = technique_common.find(Collada.tag('accessor'))
        accessor_count = int(accessor.get('count'))
        accessor_source = accessor.get('source').lstrip('#')
        accessor_stride = int(accessor.get('stride'))
        assert accessor_source == float_array_id, 'accessor_source '+accessor_source+' != float_array_id '+float_array_id
        assert accessor_count * accessor_stride == float_array_count
        accessor_children = accessor.getchildren()
        assert len(accessor_children) == accessor_stride
        source_data = dict() # key is param name, value is data list
        for param_offset in range(len(accessor_children)):
            param = accessor_children[param_offset]
            assert param.tag == Collada.tag('param'), 'unknown accessor child: '+param.tag
            param_name = param.get('name')
            param_data = [float(float_array_text_list[i]) for i in range(param_offset, len(float_array_text_list), accessor_stride)]
            assert len(param_data) == accessor_count
            source_data[param_name] = param_data
        sources[source_id] = source_data

    def readMeshVertices(self, verticesElement, vertices):
        vertices_id = verticesElement.get('id')
        assert vertices_id not in vertices
        vertices_data = dict() # key is semantic name, value is source id
        for vertices_child in verticesElement.getchildren():
            assert vertices_child.tag == Collada.tag('input')
            vertices_input = vertices_child
            semantic = vertices_input.get('semantic')
            assert semantic in ['POSITION', 'NORMAL', 'TEXCOORD']
            source = vertices_input.get('source').lstrip('#')
            assert semantic not in vertices_data
            vertices_data[semantic] = source
        vertices[vertices_id] = vertices_data

    def readMeshPrimitive(self, element, primitive, sources, vertices):
        primitive.material = element.get('material')
        count = int(element.get('count'))
        mySources = dict()  # key is semantic, value is source id
        myOffsets = dict()  # key is semantic, value is offset
        maxoffset = 0
        inputChildren = element.findall(Collada.tag('input'))
        for inputElement in inputChildren:
            semantic = inputElement.get('semantic')
            assert semantic in ['VERTEX', 'POSITION', 'NORMAL', 'TEXCOORD']
            source = inputElement.get('source').lstrip('#')
            offset = int(inputElement.get('offset'))
            if offset > maxoffset:
                maxoffset = offset
            if semantic == 'VERTEX':
                assert source in vertices
                for vertices_semantic in vertices[source]:
                    mySources[vertices_semantic] = vertices[source][vertices_semantic]
                    myOffsets[vertices_semantic] = offset
            else:
                mySources[semantic] = source
                myOffsets[semantic] = offset
        pElement = element.find(Collada.tag('p'))
        primitive_list = map(int, pElement.text.split())
        stride = maxoffset+1
        assert len(primitive_list) == count * primitive.verticesPerPrimitive * stride
        assert 'POSITION' in mySources
        assert 'POSITION' in myOffsets
        positionIndices = [primitive_list[i] for i in range(myOffsets['POSITION'], len(primitive_list), stride)]
        assert len(positionIndices) == count*primitive.verticesPerPrimitive
        source = sources[mySources['POSITION']]
        primitive.positions = self.getXYZCoordinatesFromSource(source, positionIndices)
        self.computeStats(primitive.positions)
        assert len(primitive.positions) == count*primitive.verticesPerPrimitive
        if 'NORMAL' in mySources:
            normalIndices = [primitive_list[i] for i in range(myOffsets['NORMAL'], len(primitive_list), stride)]
            source = sources[mySources['NORMAL']]
            primitive.normals = self.getXYZCoordinatesFromSource(source, normalIndices)
        if 'TEXCOORD' in mySources:
            texcoordIndices = [primitive_list[i] for i in range(myOffsets['TEXCOORD'], len(primitive_list), stride)]
            source = sources[mySources['TEXCOORD']]
            primitive.texcoords = self.getSTCoordinatesFromSource(source, texcoordIndices)
            #primitive.texcoords = [(source['S'][i], source['T'][i]) for i in texcoordIndices]
        self.countPolygons += count
        return primitive

    def getXYZCoordinatesFromSource(self, source, indices):
        return [(source['X'][i], source['Y'][i], source['Z'][i]) for i in indices]
        #if self.up_axis == 'Y_UP':
        #    return [(source['X'][i], source['Y'][i], source['Z'][i]) for i in indices]
        #elif self.up_axis == 'Z_UP':
        #    return [(source['X'][i], source['Z'][i], -source['Y'][i]) for i in indices]
        #elif self.up_axis == 'X_UP':
        #    return [(-source['Y'][i], source['X'][i], source['Z'][i]) for i in indices]
        #assert False, "unknown up_axis: " + str(self.up_axis)

    def getSTCoordinatesFromSource(self, source, indices):
        return [(source['S'][i], source['T'][i]) for i in indices]
        #if self.up_axis == 'Y_UP':
        #    return [(source['S'][i], source['T'][i]) for i in indices]
        #elif self.up_axis == 'Z_UP':
        #    return [(source['S'][i], -source['T'][i]) for i in indices]
        #elif self.up_axis == 'X_UP':
        #    return [(source['S'][i], source['T'][i]) for i in indices]  # what should this one be?
        #assert False, "unknown up_axis: " + str(self.up_axis)


    def computeStats(self, positions):
        if self.stats:
            Xs = [x for (x,y,z) in positions]
            Ys = [y for (x,y,z) in positions]
            Zs = [z for (x,y,z) in positions]
            self.minx = min(self.minx, min(Xs))
            self.miny = min(self.miny, min(Ys))
            self.minz = min(self.minz, min(Zs))
            self.maxx = max(self.maxx, max(Xs))
            self.maxy = max(self.maxy, max(Ys))
            self.maxz = max(self.maxz, max(Zs))
            self.sumx += sum(Xs)
            self.sumy += sum(Ys)
            self.sumz += sum(Zs)
            self.countVertices += len(Xs)

    def readLibraryNodes(self, library_nodes):
        if library_nodes is not None:
            self.readChildNodes(library_nodes)

    def readChildNodes(self, parentNode):
        nodelist = list()
        nodeElementList = parentNode.findall(Collada.tag('node'))
        if nodeElementList is None:
            return nodelist
        for node_element in nodeElementList:
            node = self.readNode(node_element)
            nodelist.append(node)
        return nodelist

    def readNode(self, node_element):
        node_id = node_element.get('id')
        assert node_id not in self.nodes
        node = Collada.Node(node_id)
        self.nodes[node_id] = node
        matrix_elements = node_element.findall(Collada.tag('matrix'))
        for matrix_element in matrix_elements:
            node.matrices.append([float(n) for n in matrix_element.text.split()])
        instance_geometries = node_element.findall(Collada.tag('instance_geometry'))
        for instance_geometry_element in instance_geometries:
            geometry_id = instance_geometry_element.get('url').lstrip('#')
            assert geometry_id in self.geometries, 'unknown geometry id: '+str(geometry_id)
            instance_geometry = Collada.InstanceGeometry(geometry_id, self.geometries[geometry_id])
            bind_material = instance_geometry_element.find(Collada.tag('bind_material'))
            technique_common = bind_material.find(Collada.tag('technique_common'))
            instance_materials = technique_common.findall(Collada.tag('instance_material'))
            for instance_material in instance_materials:
                symbol = instance_material.get('symbol')
                target = instance_material.get('target').lstrip('#')
                effect = self.materials[target]
                materialEffect = self.effects[effect]
                instance_geometry.materials[symbol] = materialEffect
            node.instanceGeometries.append(instance_geometry)
        node.nodes = self.readChildNodes(node_element)
        instance_nodes = node_element.findall(Collada.tag('instance_node'))
        for instance_node in instance_nodes:
            instance_node_id = instance_node.get('url').lstrip('#')
            #assert instance_node_id in self.nodes, 'unknown instance node url: '+ str(instance_node_id)
            #node.nodes.append(self.nodes[instance_node_id])
            node.instance_nodes.append(instance_node_id)
        return node

    def readLibraryVisualScenes(self, library_visual_scenes):
        visual_scenes = dict()
        visual_scene_elements = library_visual_scenes.findall(Collada.tag('visual_scene'))
        for visual_scene in visual_scene_elements:
            visual_scene_id = visual_scene.get('id')
            mainNode = None
            node_elements = visual_scene.findall(Collada.tag('node'))
            for node_element in node_elements:
                node_id = node_element.get('id')
                if node_id not in ['Model', 'Camera']:
                    print("node_id =", node_id)
                if node_id not in ['Camera','Home']:
                    assert mainNode == None
                    mainNode = self.readNode(node_element)
            visual_scenes[visual_scene_id] = mainNode
        return visual_scenes

    def readScene(self, scene):
        instance_visual_scene = scene.find(Collada.tag('instance_visual_scene'))
        instance_visual_scene_id = instance_visual_scene.get('url').lstrip('#')
        assert instance_visual_scene_id in self.visual_scenes
        return instance_visual_scene_id
    
    def buildComponentList(self):
        rootNode = self.visual_scenes[self.scene]
        components = self.buildComponentsForNode(rootNode, [])
        return components

    def buildComponentsForNode(self, node, matrices):
        assert(matrices != None)
        components = list()
        matrices = matrices[:]
        matrices.extend(node.matrices)
        assert(matrices != None)
        for instanceGeometry in node.instanceGeometries:
            for geometryPrimitive in instanceGeometry.geometryPrimitives:
                if geometryPrimitive.getVertexCount() == 0 :
                    print("WARNING: empty geometry primitive in geometry id " + instanceGeometry.id  + " in node " + node.id)
                else:
                    cigp = Collada.InstanceGeometryPrimitive(instanceGeometry, geometryPrimitive, matrices)
                    if cigp.material is None:
                        print("WARNING: no material specified for geometry id " + instanceGeometry.id)
                    else:
                        components.append(cigp)
        for childNode in node.nodes:
            components.extend(self.buildComponentsForNode(childNode, matrices))
        for instanceNode in node.instance_nodes:
            components.extend(self.buildComponentsForNode(self.nodes[instanceNode], matrices))
        return components

    def getComponents(self):
        return self.components


    class Node:
        def __init__(self, node_id):
            self.id = node_id
            self.matrices = []
            self.instanceGeometries = list() # list of InstanceGeometry objects
            self.nodes = list()  # list of child Node objects
            self.instance_nodes = list()
            
    class MaterialEffect:
        def __init__(self):
            self.texture = None
            self.diffuse = None
            
    class GeometryPrimitive:
        def __init__(self):
            self.material = None
            self.positions = list()
            self.normals = list()
            self.texcoords = list()
        def getVertexCount(self):
            return len(self.positions)
        def getPolygonCount(self):
            return len(self.positions) / self.verticesPerPrimitive

    class GeometryTriangles(GeometryPrimitive):
        def __init__(self):
            Collada.GeometryPrimitive.__init__(self)
            self.openGLPrimitive = GL_TRIANGLES
            self.verticesPerPrimitive = 3

    class GeometryLines(GeometryPrimitive):
        def __init__(self):
            Collada.GeometryPrimitive.__init__(self)
            self.openGLPrimitive = GL_LINES
            self.verticesPerPrimitive = 2



    class InstanceGeometry:
        def __init__(self, geometry_id, geometry):
            self.id = geometry_id
            self.geometryPrimitives = geometry
            self.materials = dict()  # key is material symbol, value is MaterialEffect object

    class InstanceGeometryPrimitive:
        def __init__(self, instanceGeometry, geometryPrimitive, matrices):
            self.geometry = geometryPrimitive
            self.material = instanceGeometry.materials[geometryPrimitive.material]
            self.matrices = matrices
            #self.matrices.reverse()

#############################################################################
#############################################################################
#############################################################################
#############################################################################

class Shape3D:

    def __init__(self):
        self.selectionID = None
        self.bufferIDDict = {} # key = selection ID, value = Color Buffer ID

    class Buffers:
        def __init__(self, vertexList, normalList, colorList, texCoordList):
            self.numVertexes = len(vertexList)
            self.selectionColorBufferID = 0
            if not _GLI.useInterleavedArrays:
                self.vertexBufferID   = self.configureVBOBuffer(vertexList)
                self.normalBufferID   = self.configureVBOBuffer(normalList)
                self.colorBufferID    = self.configureVBOBuffer(colorList)
                self.texCoordBufferID = self.configureVBOBuffer(texCoordList)
            else: 
                colors = False
                textures = False
                normals = False
                colorParts = 3
                if normalList is not None and normalList != []:
                    normals = True
                if texCoordList is not None and texCoordList != []:
                    textures = True
                elif colorList is not None and colorList != []:
                    colors = True
                if normals:
                    if textures:
                        self.format = GL_T2F_N3F_V3F
                    elif colors:
                        self.format = GL_C4F_N3F_V3F
                        colorParts = 4
                    else:
                        self.format = GL_N3F_V3F
                else:
                    if textures:
                        self.format = GL_T2F_V3F
                    elif colors:
                        self.format = GL_C3F_V3F
                    else:
                        self.format = GL_V3F
                dataList = []
                for i in range(len(vertexList)):
                    if textures:
                        dataList.extend(texCoordList[i])
                    elif colors:
                        if colorParts == len(colorList[i]):
                            dataList.extend(colorList[i])
                        elif colorParts == 4 and len(colorList[i]) == 3:
                            dataList.extend(colorList[i])
                            dataList.append(1.0)
                        elif colorParts == 3 and len(colorList[i]) == 4:
                            dataList.extend(colorList[i][:3])
                    if normals:
                        dataList.extend(normalList[i])
                    dataList.extend(vertexList[i])
                self.bufferID = self.configureVBOBuffer(dataList)

                if _GLI.enableSelection:
                    self.vertexBufferID = self.configureVBOBuffer(vertexList)
                

        def configureVBOBuffer(self, dataList):
            if dataList is None or len(dataList)==0:
                return 0
            bufferID = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, bufferID)
            if _GLI.hasNumPy:
                dataArray = numpy.array(dataList, dtype=numpy.float32)
            else:
                dataArray = _GLI.arrayHandler.asArray(dataList, GL_FLOAT)
            glBufferData(GL_ARRAY_BUFFER, dataArray, GL_STATIC_DRAW)
            return bufferID

        def delete(self):
            glDeleteBuffers(1, GLuint(self.bufferID))

        def select(self):
            if _GLI.enableSelection and _GLI.selectionDrawingOn:
                glBindBuffer(GL_ARRAY_BUFFER, self.vertexBufferID)
                glVertexPointer(3, GL_FLOAT, 0, None)

                if self.selectionColorBufferID != 0:
                    glBindBuffer(GL_ARRAY_BUFFER, self.selectionColorBufferID)
                    glEnableClientState(GL_COLOR_ARRAY)
                    glColorPointer(3, GL_FLOAT, 0, None)
                else:
                    glDisableClientState(GL_COLOR_ARRAY)
                glDisableClientState(GL_TEXTURE_COORD_ARRAY)
                    
            elif _GLI.useInterleavedArrays:
                glBindBuffer(GL_ARRAY_BUFFER, self.bufferID)
                glInterleavedArrays(self.format, 0, None)
                
            else:
                # if interleaved arrays is broken (like some versions of windows)
                glBindBuffer(GL_ARRAY_BUFFER, self.vertexBufferID)
                glVertexPointer(3, GL_FLOAT, 0, None)
                
                glBindBuffer(GL_ARRAY_BUFFER, self.normalBufferID)
                if self.normalBufferID == 0:
                    glDisableClientState(GL_NORMAL_ARRAY)
                else:
                    glEnableClientState(GL_NORMAL_ARRAY)
                    glNormalPointer(GL_FLOAT, 0, None)
                    
                glBindBuffer(GL_ARRAY_BUFFER, self.colorBufferID)
                if self.colorBufferID == 0:
                    glDisableClientState(GL_COLOR_ARRAY)
                else:
                    glEnableClientState(GL_COLOR_ARRAY)
                    glColorPointer(3, GL_FLOAT, 0, None)
                    
                glBindBuffer(GL_ARRAY_BUFFER, self.texCoordBufferID)
                if self.texCoordBufferID == 0:
                    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
                else:
                    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
                    glTexCoordPointer(2, GL_FLOAT, 0, None)


    def delete(self):
        self.buffers.delete()

    def setTexture(self, texture):
        if isinstance(texture, int) or isinstance(texture,long):
            self.textureID = texture
        else:
            self.textureID = _GLI.getTextureID(texture)
        return self.textureID

    def useTexture(self, textureID=None):
        if textureID is None:
            textureID = self.textureID
        if _GLI.enableSelection and _GLI.selectionDrawingOn:
            glBindTexture(GL_TEXTURE_2D, 0)
        else:
            glBindTexture(GL_TEXTURE_2D, textureID)
    
    def countPolygons(self, numPolygons):
        _GLI.polygonCount += numPolygons

    def setSelectionID(self, selectionID):
        # this was originally written by Austin Hunter '11
        if _GLI.enableSelection and (_GLI.selectionDrawingOn or _GLI.currentMode != _GLI.DRAW_MODE):
            self.selectionID = selectionID
            if self.selectionID not in _GLI.selectColorIDDict:
                # this selectionID has never been used before - generate a new color
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                while color in _GLI.selectColorDict:
                    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                (r, g, b) = color
                floatColor = (r/255.0, g/255.0, b/255.0)
                _GLI.selectColorIDDict[self.selectionID] = floatColor # 0->1 float colors
                _GLI.selectColorDict[color] = self.selectionID # 0->255 integer colors
            if self.selectionID not in self.bufferIDDict:
                # this selectionID has never been used for this model
                floatColor = _GLI.selectColorIDDict[self.selectionID]
                if isinstance(self, ObjModel3D):
                    for component in self.componentsList:
                        colorList = [floatColor] * component.buffers.numVertexes
                        component.buffers.selectionColorBufferID = component.buffers.configureVBOBuffer(colorList)
                        component.bufferIDDict[self.selectionID] = component.buffers.selectionColorBufferID
                else:
                    colorList = [floatColor] * self.buffers.numVertexes
                    self.buffers.selectionColorBufferID = self.buffers.configureVBOBuffer(colorList)
                    self.bufferIDDict[self.selectionID] = self.buffers.selectionColorBufferID
            else:
                # this selectionID has been used on this model before
                if isinstance(self, ObjModel3D):
                    for component in self.componentsList:
                        component.buffers.selectionColorBufferID = component.bufferIDDict[self.selectionID]
                else:
                    self.buffers.selectionColorBufferID = self.bufferIDDict[self.selectionID]

#############################################################################

def enableSelection():
    _GLI.enableSelection = True

def disableSelection():
    _GLI.enableSelection = False

def setSelectionLabel(model, label):
    model.setSelectionID(label)

def getSelectedObject(x, y):
    if _GLI.enableSelection:
            
        _GLI.selectionDrawingOn = True
 #      glDrawBuffer(GL_BACK)   # was GL_AUX1
        if _GLI.fogMode != 0:
            glDisable(GL_FOG)
        if _GLI.lightingEnabled:
            glDisable(GL_LIGHTING)            
        _render()
 #       glDrawBuffer(GL_BACK)
        _GLI.selectionDrawingOn = False
        if _GLI.fogMode != 0:
            glEnable(GL_FOG)
        if _GLI.lightingEnabled:
            glEnable(GL_LIGHTING)            
        
 #       glReadBuffer(GL_BACK)  # was GL_AUX1
        data = glReadPixels(x, getWindowHeight() - y, 1, 1, GL_RGB, GL_UNSIGNED_BYTE)
 #       glReadBuffer(GL_BACK)
        (r, g, b) = struct.unpack("BBB", data)
        if (r, g, b) in _GLI.selectColorDict:
            ID = _GLI.selectColorDict[(r, g, b)]
            return ID
    return None
    
#############################################################################
#############################################################################

class GridShape3D(Shape3D):
  
    def __init__(self, rows, cols, colors, texture, textureTiles=False):
        Shape3D.__init__(self)
        self.rows = rows
        self.cols = cols
        self.colors = colors
        self.setTexture(texture)
        self.textureTiles = textureTiles
        self.vertices = []
        self.normals = []
        self.textures = []
        for row in range(self.rows+1):
            self.vertices.append([0]*(cols+1))
            self.normals.append([0]*(cols+1))
            self.textures.append([0]*(cols+1))

    def save(self):
        self.vertexList = []
        self.colorList = []
        self.normalList = []
        self.texCoordList = []
        colorIndex = 0
        for row in range(self.rows):
            colorIndex = row % len(self.colors)
            for col in range(self.cols):
                self.saveVertex(row, col,     1,1)
                self.saveVertex(row, col+1,   0,1)
                self.saveVertex(row+1, col+1, 0,0)
                self.saveVertex(row+1, col,   1,0)
                color = self.colors[colorIndex]
                self.colorList.extend([lookupColor3D(color)] * 4)
                colorIndex = (colorIndex+1) % len(self.colors)
        if self.textureID == 0:
            self.texCoordList = None
        else:
            self.colorList = None
        self.buffers = self.Buffers(self.vertexList, self.normalList, self.colorList, self.texCoordList)  

    def saveVertex(self, r, c, u, v):
        vertex = self.vertices[r][c]
        self.vertexList.append( (vertex[0], vertex[1], vertex[2]) )
        normal = self.normals[r][c]
        self.normalList.append( (normal[0], normal[1], normal[2]) )
        texture = self.textures[r][c]
        if self.textureTiles:
            self.texCoordList.append( (u,v) )
        else:
            self.texCoordList.append( (texture[0], texture[1]) )

    def draw(self):
        self.useTexture()
        self.buffers.select()
        glDrawArrays(GL_QUADS, 0, self.rows*self.cols*4)
        self.countPolygons(self.rows*self.cols)
    
#############################################################################

class Sphere3D(GridShape3D):
    def __init__(self, radius, detailLevel=12, colors=[(0,0,0),(1,1,1)], texture=None, textureTiles=False):
        rows = detailLevel
        cols = detailLevel*2
        GridShape3D.__init__(self, rows, cols, colors, texture, textureTiles)
        self.radius = float(radius)
        for row in range(rows+1):
            for col in range(cols+1):
                sliceangle = row * (math.pi / rows)
                r = self.radius * math.sin(sliceangle)
                y = self.radius * math.cos(sliceangle)
                wedgeangle = col * (2*math.pi / cols)
                x = r * math.cos(wedgeangle)
                z = r * math.sin(wedgeangle)
                self.vertices[row][col] = (x, y, z)
                self.normals[row][col] = (x/self.radius, y/self.radius, z/self.radius)
                self.textures[row][col] = ( (cols-col)/float(cols), (rows-row)/float(rows) )
        self.save()

#######################################################################################

class Hemisphere3D(GridShape3D):
    def __init__(self, radius, detailLevel=12, colors=[(0,0,0),(1,1,1)], texture=None, textureTiles=False):
        rows = detailLevel//2
        cols = detailLevel*2
        GridShape3D.__init__(self, rows, cols, colors, texture, textureTiles)
        self.radius = float(radius)
        for row in range(rows+1):
            for col in range(cols+1):
                sliceangle = row * ((math.pi/2) / rows)
                r = self.radius * math.sin(sliceangle)
                y = self.radius * math.cos(sliceangle)
                wedgeangle = col * (2*math.pi / cols)
                x = r * math.cos(wedgeangle)
                z = r * math.sin(wedgeangle)
                self.vertices[row][col] = (x, y, z)
                self.normals[row][col] = (x/self.radius, y/self.radius, z/self.radius)
                self.textures[row][col] = ( (cols-col)/float(cols), (rows-row)/float(rows) )
        self.save()

#######################################################################################

class Ellipsoid3D(GridShape3D):
    def __init__(self, xradius, yradius, zradius, detailLevel=12, colors=[(0,0,0),(1,1,1)], texture=None, textureTiles=False):
        rows = detailLevel
        cols = detailLevel*2
        GridShape3D.__init__(self, rows, cols, colors, texture, textureTiles)
        self.xradius = float(xradius)
        self.yradius = float(yradius)
        self.zradius = float(zradius)
        for row in range(rows+1):
            for col in range(cols+1):
                sliceangle = row * (math.pi / rows) - (math.pi/2)
                wedgeangle = col * (2*math.pi / cols) - math.pi                
                x = self.xradius * math.cos(sliceangle) * math.cos(wedgeangle)
                z = self.zradius * math.cos(sliceangle) * math.sin(wedgeangle)
                y = -self.yradius * math.sin(sliceangle)
                self.vertices[row][col] = (x, y, z)
                self.normals[row][col] = (2*x/self.xradius**2, 2*y/self.yradius**2, 2*z/self.zradius**2)
                #self.textures[row][col] = ((rows-row)/float(rows),  (cols-col)/float(cols) )
                
                self.textures[row][col] = ( (cols-col)/float(cols), (rows-row)/float(rows) )
                
        self.save()        


#######################################################################################

class Cylinder3D(GridShape3D):
    def __init__(self, height, radius, slices=6, wedges=12, colors=[(0,0,0),(1,1,1)], texture=None, textureTiles=False):
        GridShape3D.__init__(self, slices, wedges, colors, texture, textureTiles)
        self.height = float(height)
        self.radius = float(radius)
        thickness = self.height / slices
        for row in range(self.rows+1):
            for col in range(self.cols+1):
                y = thickness*(self.rows/2.0) - thickness*row
                wedgeangle = col * (2*math.pi / self.cols)
                x = self.radius * math.cos(wedgeangle)
                z = self.radius * math.sin(wedgeangle)
                self.vertices[row][col] = (x, y, z)
                self.normals[row][col] = (x/self.radius, 0, z/self.radius)
                self.textures[row][col] = ( (self.cols-col)/float(self.cols), (self.rows-row)/float(self.rows) )
        self.save()

#######################################################################################

class Cone3D(GridShape3D):
    def __init__(self, height, radius, slices=6, wedges=12, colors=[(0,0,0),(1,1,1)], texture=None, textureTiles=False):
        GridShape3D.__init__(self, slices, wedges, colors, texture, textureTiles)
        self.height = float(height)
        self.radius = float(radius)
        thickness = self.height / slices
        radius_step = float(radius) / slices
        for row in range(self.rows+1):
            for col in range(self.cols+1):
                y = self.height - thickness*row
                wedgeangle = col * (2*math.pi / self.cols)
                radius = self.radius - (row * radius_step)
                x = radius * math.cos(wedgeangle)
                z = radius * math.sin(wedgeangle)
                self.vertices[row][col] = (x, y, z)
                self.normals[row][col] = (x/self.radius, 0, z/self.radius)  # wrong!!!
                self.textures[row][col] = ( (self.cols-col)/float(self.cols), (self.rows-row)/float(self.rows) )
        self.save()

#######################################################################################

class Torus3D(GridShape3D):
    def __init__(self, majorRadius, minorRadius, slices=12, wedges=8, colors=[(0,0,0),(1,1,1)], texture=None, textureTiles=False):
        GridShape3D.__init__(self, slices, wedges, colors, texture, textureTiles)
        self.majorRadius = float(majorRadius)
        self.minorRadius = float(minorRadius)
        for row in range(self.rows+1):
            for col in range(self.cols+1):
                sliceangle = row * (2*math.pi / self.rows)
                cx = majorRadius * math.cos(sliceangle)
                cz = majorRadius * math.sin(sliceangle)      
                wedgeangle = col * (2*math.pi / self.cols)      
                y = minorRadius * math.sin(wedgeangle)
                x = cx + minorRadius * math.cos(sliceangle) * math.cos(wedgeangle)
                z = cz + minorRadius * math.sin(sliceangle) * math.cos(wedgeangle)
                self.vertices[row][col] = (x, y, z)
                self.normals[row][col] = (x-cx, y, z-cz)
                #self.textures[row][col] = ( (self.cols-col)/float(self.cols), (self.rows-row)/float(self.rows) )
                self.textures[row][col] = ( (col)/float(self.cols), (row)/float(self.rows) )
        self.save()

###############################################################################################################

class Rect3D(GridShape3D):
    def __init__(self, width=1, height=1, colors=[(0,0,0),(1,1,1)], texture=None, textureRepeat=1):
        self.width = float(width)
        self.height = float(height)
        if width == height:
            rows = textureRepeat
            cols = textureRepeat
        elif width > height:
            cols = textureRepeat
            rows = int(math.ceil((self.height / (self.width/textureRepeat))))
        else:
            rows = textureRepeat
            cols = int(math.ceil(self.width / (self.height/textureRepeat)))

        GridShape3D.__init__(self, rows, cols, colors, texture, False)
        
        w = self.width/2.0
        h = self.height/2.0
        xstep = self.width/cols
        ystep = self.height/rows

        for row in range(rows+1):
            for col in range(cols+1):
                x = col * xstep - w
                y = row * ystep - h
                z = 0
                self.vertices[row][col] = (x,y,z)
                self.normals[row][col] = (0,0,1)
                self.textures[row][col] = ( col, row )
        self.save()


class Box3D(Shape3D):
    def __init__(self, width=1, height=1, depth=1, colors=[(1,0,0), (0,1,0), (0,0,1), (1,1,0), (1,0,1), (0,1,1)], texture=None):
        Shape3D.__init__(self)
        self.width = width
        self.height = height
        self.depth = depth
        self.setTexture(texture)
        w = float(width)/2.0
        h = float(height)/2.0
        d = float(depth)/2.0
        vertices = [ (-w,h,-d), (-w,h,d), (w,h,d), (w,h,-d),        # top
                     (-w,-h,d), (-w,-h,-d), (w,-h,-d), (w,-h,d),    # bottom
                     (-w,h,d), (-w,-h,d), (w,-h,d), (w,h,d),        # front
                     (w,h,d), (w,-h,d), (w,-h,-d), (w,h,-d),        # right
                     (w,h,-d), (w,-h,-d), (-w,-h,-d), (-w,h,-d),    # back
                     (-w,h,-d), (-w,-h,-d), (-w,-h,d), (-w,h,d) ]   # left
        normals = [ (0,1,0), (0,1,0), (0,1,0), (0,1,0),
                    (0,-1,0), (0,-1,0), (0,-1,0), (0,-1,0),
                    (0,0,1), (0,0,1), (0,0,1), (0,0,1),
                    (1,0,0), (1,0,0), (1,0,0), (1,0,0),
                    (0,0,-1), (0,0,-1), (0,0,-1), (0,0,-1),
                    (-1,0,0), (-1,0,0), (-1,0,0), (-1,0,0) ]
        colorList = None
        texCoords = None
        if self.textureID == 0:
            colorList = []
            for side in range(6):
                colorList.extend([lookupColor3D(colors[side])] * 4)
        else:
            texCoords = [ (0,1), (0,0), (1,0), (1,1) ] * 6
        self.buffers = self.Buffers(vertices, normals, colorList, texCoords)
        
    def draw(self):
        self.useTexture()
        self.buffers.select()
        glDrawArrays(GL_QUADS, 0, 24)
        self.countPolygons(6)

#############################################################################

class Lines3D(Shape3D):
    def __init__(self, vertices, color=(1,1,1), width=1):
        Shape3D.__init__(self)
        self.textureID = 0
        self.numVertices = len(vertices)
        self.width = width
        if self.numVertices % 2 == 1:
            raise ValueError("the number of vertices in your lines must be even")
        #vertices = [ ( float(x1), float(y1), float(z1) ),
        #             ( float(x2), float(y2), float(z2) ) ]
        normals = None
        texCoords = None
        color = lookupColor3D(color)
        colorList = [color] * self.numVertices
        self.buffers = self.Buffers(vertices, vertices, colorList, texCoords)
        
    def draw(self):
        #self.useTexture()
        glLineWidth(self.width)
        self.buffers.select()
        glDrawArrays(GL_LINES, 0, self.numVertices)
        self.countPolygons(self.numVertices/2)

#############################################################################

#######################################################################################

def vectorCrossProduct(vectorA, vectorB):
    (ax,ay,az) = vectorA
    (bx,by,bz) = vectorB
    return (ay*bz-az*by, az*bx-ax*bz, ax*by-ay*bx)
def vectorDotProduct(vectorA, vectorB):
    (ax,ay,az) = vectorA
    (bx,by,bz) = vectorB
    return ax*bx + ay*by + az*bz
def unitVector(v):
    (x,y,z) = v
    length = math.sqrt(x*x+y*y+z*z)
    if length > 0:
        return (x/length, y/length, z/length)
    else:
        return v
def vectorSubtract(vectorA, vectorB):
    (ax,ay,az) = vectorA
    (bx,by,bz) = vectorB    
    return (ax-bx, ay-by, az-bz)
def vectorAdd(vectorA, vectorB):
    (ax,ay,az) = vectorA
    (bx,by,bz) = vectorB        
    return (ax+bx, ay+by, az+bz)

def normalVector(v1, v2, v3):
    (v1x,v1y,v1z) = v1
    (v2x,v2y,v2z) = v2
    (v3x,v3y,v3z) = v3
    ax = v2x-v1x
    ay = v2y-v1y
    az = v2z-v1z
    bx = v3x-v1x
    by = v3y-v1y
    bz = v3z-v1z
    return unitVector(vectorCrossProduct((ax,ay,az), (bx,by,bz)))

# takes a list of 3D vertex tuples for a 3D polygon,
#  and returns a list of 2D vertex tuples for the same polygon
#   rotated onto a 2D plane
# this is intended to be used for texture coordinates
#from http://stackoverflow.com/questions/26369618/getting-local-2d-coordinates-of-vertices-of-a-planar-polygon-in-3d-space
def rotatePolygonOntoPlane(polygon):
    normal = normalVector(polygon[0], polygon[1], polygon[2])
    locx = unitVector(vectorSubtract(polygon[1], polygon[0]))
    locy = unitVector(vectorCrossProduct(normal, locx))
    polygon2D = [(vectorDotProduct(vectorSubtract(p,polygon[0]), locx),
                  vectorDotProduct(vectorSubtract(p,polygon[0]), locy))
                 for p in polygon]
    return polygon2D

def rescaleTexCoords(texCoords):
    texX = [x for (x,y) in texCoords]
    texY = [y for (x,y) in texCoords]
    minTexX = min(texX)
    maxTexX = max(texX)
    minTexY = min(texY)
    maxTexY = max(texY)
    return [((x-minTexX) / (maxTexX-minTexX),
             (y-minTexY) / (maxTexY-minTexY))
            for (x,y) in texCoords]


class CustomPolygons3D(Shape3D):
    # colors is a list, or
    #  a dictionary where keys are number of sides and
    #     each value is the color to use for faces with that number of sides
    def __init__(self, vertices, faces, colors=[(1,0,0), (0,1,0), (0,0,1)], texture=None):
        Shape3D.__init__(self)
        self.setTexture(texture)
        glvertices = []
        normals = []
        if self.textureID == 0:
            texCoords = None
            colorList = []
            if isinstance(colors,dict):
                colorDictMode = True
            else:
                colorDictMode = False
                colorIndex = 0
        else:
            texCoords = []
            colorList = None
        self.numPolygons = 0
        for face in faces:
            vface = [vertices[i] for i in face]
            numTriangles = len(face) - 2
            self.numPolygons += numTriangles
            for i in range(2,len(vface)):
                glvertices.extend([vface[0], vface[i-1], vface[i]])
            normal = normalVector(vface[0], vface[1], vface[2])
            normals.extend([normal]*(3*numTriangles))
            if self.textureID == 0:
                if colorDictMode:
                    colorKey = len(vface)
                    color = colors[colorKey]
                else:
                    color = colors[colorIndex]
                    colorIndex = (colorIndex+1) % len(colors)
                colorList.extend([lookupColor3D(color)]*(3*numTriangles))
            else:
                vface2D = rotatePolygonOntoPlane(vface)
                for i in range(2,len(vface)):
                    texCoords.extend([vface2D[0], vface2D[i-1], vface2D[i]])
        if self.textureID != 0:
            texCoords = rescaleTexCoords(texCoords)
        self.numVertices = len(glvertices)
        self.buffers = self.Buffers(glvertices, normals, colorList, texCoords)

    def draw(self):
        self.useTexture()
        self.buffers.select()
        glDrawArrays(GL_TRIANGLES, 0, self.numVertices)
        self.countPolygons(self.numPolygons)


class Polyhedron3D(CustomPolygons3D):
    def __init__(self, name, colors=[(1,0,0), (0,1,0), (0,0,1)], texture=None):
        if name not in _GLI.polyhedraDict:
            raise ValueError(name + " is not a known polyhedron")
        self.name = name
        (vertices, faces) = _GLI.polyhedraDict[name]
        CustomPolygons3D.__init__(self, vertices, faces, colors, texture)


class Triangles3D(Shape3D):
    def __init__(self, vertices, colors=[(1,0,0), (0,1,0), (0,0,1)], texture=None):
        Shape3D.__init__(self)
        self.numVertices = len(vertices)
        if self.numVertices % 3 != 0:
            raise ValueError("the number of vertices in your triangles must be a multiple of 3")
        self.numPolygons = self.numVertices / 3
        self.setTexture(texture)
        normals = []
        if self.textureID == 0:
            texCoords = None
            colorList = []
            colorIndex = 0
        else:
            texCoords = []
            colorList = None
        for i in range(0,self.numVertices,3):
            normal = normalVector(vertices[i], vertices[i+1], vertices[i+2])
            normals.extend([normal]*3)
            if self.textureID == 0:
                color = colors[colorIndex]
                colorIndex = (colorIndex+1) % len(colors)
                colorList.extend([lookupColor3D(color)]*3)
            else:
                vface2D = rotatePolygonOntoPlane(vertices[i:i+3])
                texCoords.extend([vface2D[0], vface2D[1], vface2D[2]])                
        if self.textureID != 0:
            texCoords = rescaleTexCoords(texCoords)
        self.buffers = self.Buffers(vertices, normals, colorList, texCoords)
        
    def draw(self):
        self.useTexture()
        self.buffers.select()
        glDrawArrays(GL_TRIANGLES, 0, self.numVertices)
        self.countPolygons(self.numPolygons)
            


class Terrain3D(Shape3D):
    def __init__(self, heights, cellSize=1, colors=["black","white"], texture=None, textureRepeat=1):
        Shape3D.__init__(self)
        self.heights = heights
        self.size = len(heights) - 1
        self.cellSize = cellSize
        self.textureRepeat = textureRepeat
        self.textureCells = self.size // self.textureRepeat
        self.setTexture(texture)

        vertices = []
        texCoords = []
        for x in range(self.size):
            for z in range(self.size):
                vertices += self.triangle(x,z, x,z+1, x+1,z+1)
                if texture is not None:
                    texCoords += [self.tex2(x,0,z,0), self.tex2(x,0,z,1), self.tex2(x,1,z,1)]
                vertices += self.triangle(x,z, x+1,z+1, x+1,z)
                if texture is not None:
                    texCoords += [self.tex2(x,0,z,0), self.tex2(x,1,z,1), self.tex2(x,1,z,0)]
        self.numVertices = len(vertices)
        normals = []
        for i in range(0,self.numVertices,3):
            normals.append(normalVector(vertices[i], vertices[i+1], vertices[i+2]))
            normals.append(normalVector(vertices[i+1], vertices[i+2], vertices[i]))
            normals.append(normalVector(vertices[i+2], vertices[i], vertices[i+1]))
        colors = [lookupColor3D(color) for color in colors]
        colors3 = []
        for color in colors:
            colors3 += [color,color,color]
        colorList = colors3 * (self.numVertices//len(colors3) + 1)
        self.buffers = self.Buffers(vertices, normals, colorList, texCoords)

    def draw(self):
        self.useTexture()
        self.buffers.select()
        glDrawArrays(GL_TRIANGLES, 0, self.numVertices)
        self.countPolygons(self.numVertices//3)

    def shift(self, coord):
        return (coord-self.size//2) * self.cellSize
    def triangle(self, x1,z1, x2,z2, x3,z3):
        return [(self.shift(x1), self.heights[x1][z1], self.shift(z1)),
                (self.shift(x2), self.heights[x2][z2], self.shift(z2)),
                (self.shift(x3), self.heights[x3][z3], self.shift(z3))]
    def tex(self, coord, offset):
        coord = (coord + offset) % self.textureCells
        if coord == 0 and offset == 1:
            return 1.0
        else:
            return coord / float(self.textureCells)
    def tex2(self, x,dx,z,dz):
        return (self.tex(x,dx), self.tex(z,dz))

 
class Surface3D(Shape3D):
    def __init__(self, points, colors=["black","white"], texture=None, textureRepeat=1):
        Shape3D.__init__(self)
        self.points = points  # must be a list of lists of (x,y,z) tuples
        self.size = len(points) - 1
        self.textureRepeat = textureRepeat
        self.textureCells = self.size // self.textureRepeat
        self.setTexture(texture)

        vertices = []
        texCoords = []
        for x in range(self.size):
            for z in range(self.size):
                vertices += self.triangle(x,z, x,z+1, x+1,z+1)
                if texture is not None:
                    texCoords += [self.tex2(x,0,z,0), self.tex2(x,0,z,1), self.tex2(x,1,z,1)]
                vertices += self.triangle(x,z, x+1,z+1, x+1,z)
                if texture is not None:
                    texCoords += [self.tex2(x,0,z,0), self.tex2(x,1,z,1), self.tex2(x,1,z,0)]
        self.numVertices = len(vertices)
        normals = []
        for i in range(0,self.numVertices,3):
            normals.append(normalVector(vertices[i], vertices[i+1], vertices[i+2]))
            normals.append(normalVector(vertices[i+1], vertices[i+2], vertices[i]))
            normals.append(normalVector(vertices[i+2], vertices[i], vertices[i+1]))
        colors = [lookupColor3D(color) for color in colors]
        colors3 = []
        for color in colors:
            colors3 += [color,color,color]
        colorList = colors3 * (self.numVertices//len(colors3) + 1)
        self.buffers = self.Buffers(vertices, normals, colorList, texCoords)

    def draw(self):
        self.useTexture()
        self.buffers.select()
        glDrawArrays(GL_TRIANGLES, 0, self.numVertices)
        self.countPolygons(self.numVertices//3)

    def triangle(self, x1,z1, x2,z2, x3,z3):
        return [self.points[x1][z1], self.points[x2][z2], self.points[x3][z3]]
    def tex(self, coord, offset):
        coord = (coord + offset) % self.textureCells
        if coord == 0 and offset == 1:
            return 1.0
        else:
            return coord / float(self.textureCells)
    def tex2(self, x,dx,z,dz):
        return (self.tex(x,dx), self.tex(z,dz)) 
 
 
#############################################################################

class ObjModel3D(Shape3D):
    def __init__(self, filename, color=(0.5,0.5,0.5), translate=(0,0,0), stats=True):
        Shape3D.__init__(self)
        if stats:
            print("reading OBJ file:", filename)
        (self.translateX, self.translateY, self.translateZ) = translate
        self.defaultColor = lookupColor3D(color)
        self.stats = stats
        objVertices = []
        objVertexNormals = []
        objVertexTexes = []
        self.numPolygons = 0

        class Material:
            def __init__(self, name, objmodel):
                self.name = name
                self.color = None
                self.texture = None
                self.textureID = 0
                self.objmodel = objmodel
            
            # texture is pathname to texture image file
            def setTexture(self, texture):
                self.texture = texture
                self.textureID = self.objmodel.setTexture(texture)
                #print("texture", texture, "has id", self.textureID)
            
            # color is [R,G,B] list
            def setColor(self, color):
                self.color = color

        self.materials = dict()  # key is material name string, value is Material object
        self.components = dict() # key is texture name (or 'color'), value is Component object
        defaultMaterial = Material(None, self)
        defaultMaterial.setColor(self.defaultColor)
        currentMaterial = defaultMaterial
        currentComponent = None

        class Component:
            def __init__(self, material):
                self.material = material
                self.vertices = []
                self.normals = []
                self.colors = []
                self.texCoords = []
                self.numPolygons = 0
                self.objmodel = self.material.objmodel
                self.bufferIDDict = {} # key = selection ID, value = Color Buffer ID
            
            def finish(self):
                self.numVertices = len(self.vertices)
                if self.material.texture is None or None in self.texCoords:
                    self.texCoords = []
                self.buffers = self.objmodel.Buffers(self.vertices, self.normals, self.colors, self.texCoords)
                
                # create normal vectors for drawing
                #self.normalvectors = []
                #for i in range(len(self.vertices)):
                #    v = self.vertices[i]
                #    n = self.normals[i]
                #    self.normalvectors.append(v)
                #    self.normalvectors.append((v[0]+n[0], v[1]+n[1], v[2]+n[2]))
                #self.lines = Lines3D(self.normalvectors, "green", 1)
            
            def draw(self):
                self.objmodel.useTexture(self.material.textureID)
                self.buffers.select()
                glDrawArrays(GL_TRIANGLES, 0, self.numVertices)
                self.objmodel.countPolygons(self.numPolygons)
                #if self.objmodel.showNormals:
                #    self.lines.draw()
                        
        def getComponent(material):                
            if material.texture is None:
                componentName = 'color'
            else:
                componentName = material.texture
            if componentName in self.components:
                return self.components[componentName]
            else:
                newComponent = Component(material)
                self.components[componentName] = newComponent
                return newComponent


        def readMaterialLibrary(materialFilename):
            #for materialFilename in materialFilenames:
                materialPath = os.path.join(os.path.dirname(filename), materialFilename)
                if not os.path.exists(materialPath):
                    print('ERROR: missing material library:', materialPath)
                    return
                materialFile = open(materialPath, 'r')
                material = None
                for line in materialFile:
                    line = line.strip()
                    if line == '' or line[0] == '#': continue
                    fields = line.split()
                    keyword = fields[0]
                    if keyword == 'newmtl':
                        name = fields[1]
                        material = Material(name, self)
                        self.materials[name] = material
                    elif keyword == 'Kd':
                        material.setColor([float(c) for c in fields[1:4]])                      
                    elif keyword == 'map_Kd':
                        textureFilename = fields[1]
                        texturePathname = os.path.join(os.path.dirname(materialPath), textureFilename)
                        if os.path.exists(texturePathname):
                            material.setTexture (texturePathname)
                        else:
                            print('ERROR: missing texture: ', texturePathname)
                materialFile.close()                       

        def parseFaceVertex(v):
            def lookupIndex(i, objList):
                if i < len(v) and v[i] != '':
                    i = int(v[i])
                    if i > 0:
                        i -= 1
                    return objList[i]
                else:
                    return None
            v = v.split('/')
            vertex = lookupIndex(0, objVertices)
            vertex = (vertex[0] + self.translateX, vertex[1] + self.translateY, vertex[2] + self.translateZ)
            tex = lookupIndex(1, objVertexTexes)
            normal = lookupIndex(2, objVertexNormals)
            return (vertex, tex, normal)

        def addFace(faceVertices):
            color = currentMaterial.color
            vface = [parseFaceVertex(v) for v in faceVertices]
            numTriangles = len(vface) - 2
            currentComponent.numPolygons += numTriangles
            for i in range(2,len(vface)):                
                currentComponent.vertices.extend([vface[0][0], vface[i-1][0], vface[i][0]])
                currentComponent.colors.extend([color]*3)
                if vface[0][2] is None:
                    normal = normalVector(vface[0][0], vface[i-1][0], vface[i][0])
                    currentComponent.normals.extend([normal] * 3)
                else:
                    currentComponent.normals.extend([vface[0][2], vface[i-1][2], vface[i][2]])
                currentComponent.texCoords.extend([vface[0][1], vface[i-1][1], vface[i][1]])

        # init
        mysteryKeywords = {}        
        objfile = open(filename, 'r')
        for line in objfile:
            line = line.strip()
            if line == '' or line[0] == '#': continue
            fields = line.split()
            keyword = fields[0]
            try:
                if keyword == 'v':
                    objVertices.append([float(n) for n in fields[1:]])
                elif keyword == 'vt':
                    objVertexTexes.append([float(n) for n in fields[1:3]])
                elif keyword == 'vn':
                    objVertexNormals.append([float(n) for n in fields[1:]])
                elif keyword == 'f':
                    if currentComponent is None:
                        #print 'using default color material'
                        currentComponent = getComponent(currentMaterial)
                    addFace(fields[1:])
                elif keyword == 'mtllib':
                    readMaterialLibrary(line.split(' ',1)[1])
                elif keyword == 'usemtl':
                    materialName = fields[1]
                    if materialName in self.materials:
                        currentMaterial = self.materials[materialName]
                        #print 'using material', materialName
                        currentComponent = getComponent(currentMaterial)
                    else:
                        print("ERROR: unknown material", materialName)
                elif keyword == 'g': # group
                    if len(fields) > 1:
                        groupname = fields[1]
                elif keyword == 's': # smoothing
                    pass
                else:
                    if keyword not in mysteryKeywords:
                        print("WARNING: skipped line: " + line)
                        mysteryKeywords[keyword] = True
            except ValueError:
                print("ERROR: ValueError on line: " + line)
        objfile.close()
        
        self.componentsList = []
        for componentName in self.components:
            component = self.components[componentName]
            component.finish()
            self.componentsList.append(component)
            self.numPolygons += component.numPolygons
        
        if self.stats:
            xcoords = [x for c in self.componentsList for (x,y,z) in c.vertices]
            ycoords = [y for c in self.componentsList for (x,y,z) in c.vertices]
            zcoords = [z for c in self.componentsList for (x,y,z) in c.vertices]
            print("  contains", len(self.components), "components and", self.numPolygons, "polygons")
            print("  mean x:", sum(xcoords)/len(xcoords), "min x:", min(xcoords), "max x", max(xcoords))
            print("  mean y:", sum(ycoords)/len(ycoords), "min y:", min(ycoords), "max y", max(ycoords))
            print("  mean z:", sum(zcoords)/len(zcoords), "min z:", min(zcoords), "max z", max(zcoords))
                
    def draw(self):
        for component in self.componentsList:
            component.draw()

#############################################################################

class ColladaModel3D(Shape3D):
    def __init__(self, filename, stats=False):
        Shape3D.__init__(self)
        self.model = Collada(filename, stats)
        self.components = list()
        colorList = None
        for component in self.model.getComponents():
            geometry = component.geometry
            material = component.material
            material.textureID = 0
            if material.texture is not None:
                material.textureID = self.setTexture(material.texture)
            elif material.diffuse is None:
                print("WARNING: no diffuse color or texture")
            component.buffers = self.Buffers(geometry.positions, geometry.normals, None, geometry.texcoords)
            self.components.append(component)
        print("   contains " + str(len(self.components)) + " subcomponents")
        
    
    def draw(self):
        glDisable(GL_COLOR_MATERIAL)
        glEnable(GL_RESCALE_NORMAL)
        glPushMatrix()
        glRotate(-90,1,0,0)
        for component in self.components:
            geometry = component.geometry
            material = component.material
            self.useTexture(material.textureID)
            if material.diffuse is not None:
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, material.diffuse)
            else:
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, (1,1,1,1))
            if component.matrices != []:
                glPushMatrix()
                for matrix in component.matrices:
                    glMultTransposeMatrixf(matrix)
            component.buffers.select()
            glDrawArrays(geometry.openGLPrimitive, 0, geometry.getVertexCount())
            if component.matrices != []:
                glPopMatrix()
            self.countPolygons(geometry.getPolygonCount())
        glPopMatrix()
        glDisable(GL_RESCALE_NORMAL)
        glEnable(GL_COLOR_MATERIAL)

###################################################################
# Backward Compatibility

addKeyPressedListener = onKeyPress
addKeyReleasedListener = onKeyRelease
addMousePressedListener = onMousePress
addMouseReleasedListener = onMouseRelease
addWheelForwardListener = onWheelForward
addWheelBackwardListener = onWheelBackward
addMouseMotionListener = onMouseMotion
addGameControllerStickListener = onGameControllerStick
addGameControllerDPadListener = onGameControllerDPad
addGameControllerButtonPressedListener = onGameControllerButtonPress
addGameControllerButtonReleasedListener = onGameControllerButtonRelease
addTimerListener = onTimer
keyPressedNow = isKeyPressed

#############

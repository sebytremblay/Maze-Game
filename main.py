# Final Project 
# Made By: Seby
# Last Edited: 6/5/20

from graphics3d import *

makeGraphicsWindow(1920,1080,True)

# Distance of Object
def distance(x1,y1,z1,x2,y2,z2):
    x = abs(x1-x2)
    y = abs(y1-y2)
    z = abs(z1-z2)
    distance = (x**2+y**2+z**2)**0.5
    return distance   
# Wall / Trap Contact
def inBox(world,x,z,objectList,buffer):
    for obj in objectList:
        if abs(obj.x - x) <= buffer and abs(obj.z - z) <= buffer and world.newY >= world.startY:
            return True
# Camera Moves With Mouse
def mouseMotion(world,newX,newY,changeX,changeY,mb1,mb2,mb3):
    adjustCameraRotation(-0.1*changeX,-0.1*changeY,0)
# Resets world
def reset(world):
    # Resets camera
    setCameraRotation(0,0,0)
    setCameraPosition(world.startX,world.startY,world.startZ)    
    # Resets game booleans
    world.fall = False
    world.jump = False
    # Resets prizes
    for prize in world.prizes:
        prize.obtained = False
    # Resets scoring stars
    world.thicknessStar1 = 0
    world.thicknessStar2 = 0
    world.thicknessStar3 = 0
    # Resets timer
    resetTime()    
# Jump 
def jump(world):
    if world.game == True and world.jump == False:
        world.jumpX = 1.1*(world.newX - world.oldX)
        world.jumpZ = 1.1*(world.newZ - world.oldZ)
        world.jump = True
# Initializes world
def buildWorld(world,fileName,startX,startY,startZ,wallTexture):
    # Starts time
    resetTime() 
    # Start Coords
    world.startX = startX
    world.startY = startY
    world.startZ  = startZ
    # Initializes camera
    setCameraPosition(startX,startY,startZ)
    moveMouse(960,540)    
    # Object lists
    world.walls = []
    world.prizes = []
    world.traps = []        
    # Opens and analyzes map
    mapFile = open(fileName,"r")
    z = 5
    for line in mapFile:
        line = line.strip()
        x = 5
        for char in line: 
            # Looks for wall
            if char == "X":
                wall = Wall(x,z,wallTexture)
                world.walls.append(wall)
            # Looks for prize
            if char == "o":
                prize = Prize(world,x,z)
                world.prizes.append(prize)
            # Looks for trap
            if char == "T":
                trap = Trap(x,z)
                world.traps.append(trap)
            x += 10
        z += 10
# Menu Navigation
def mouseClick(world,mouseX,mouseY,button):
    # Start Menu
    if world.start == True:
        # Play button
        if 660 <= mouseX <= 1260 and 337.5 <= mouseY <= 462.5:          
            world.start = False
            world.level = True 
        # Skin button
        elif 660 <= mouseX <= 1260 and 537.5 <= mouseY <= 662.5:
            world.start = False
            world.skin = True
        # Help button
        elif 660 <= mouseX <= 1260 and 737.5 <= mouseY <= 862.5:
            world.start = False
            world.help = True
    # Level Selector
    elif world.level == True:
        # Level 1
        if 220 <= mouseX <= 620 and 414 <= mouseY <= 514:
            world.mode = 1
            loadLevel(world)
            world.level = False
            world.game = True
        # Level 2
        if 760 <= mouseX <= 1160 and 414 <= mouseY <= 514:
            world.mode = 2
            loadLevel(world)
            world.level = False
            world.game = True
        # Level 3
        if 1300 <= mouseX <= 1700 and 414 <= mouseY <= 514:
            world.mode = 3
            loadLevel(world)
            world.level = False
            world.game = True
        # Level 4
        if 220 <= mouseX <= 620 and 650 <= mouseY <= 750:
            world.mode = 4
            loadLevel(world)
            world.level = False
            world.game = True
        # Level 5
        if 760 <= mouseX <= 1160 and 650 <= mouseY <= 750:
            world.mode = 5
            loadLevel(world)
            world.level = False
            world.game = True
        # Level 6
        if 1300 <= mouseX <= 1700 and 650 <= mouseY <= 750:
            world.mode = 6
            loadLevel(world)
            world.level = False
            world.game = True
        # Back Button
        if 760 <= mouseX <= 1160 and 865 <= mouseY <= 965:
            world.level = False
            world.start = True
    elif world.skin == True:
        # Back Button
        if 50 <= mouseX <= 450 and 62.5 <= mouseY <= 162.5:
            world.skin = False
            world.start = True
        # Pizza Skin
        if 575 <= mouseX <= 975 and (63 <= mouseY <= 363 or 388 <= mouseY <= 488):
            world.prize = "pepperoni pizza.obj"
            world.skin = False
            world.start = True
            skinData = open("data.txt","w")
            skinData.write(world.prize)
            skinData.close()
        # Trophy Skin
        if 575 <= mouseX <= 975 and (563 <= mouseY <= 863 or 888.5 <= mouseY <= 988.5):
            world.prize = "trophy.obj"
            world.skin = False
            world.start = True
            skinData = open("data.txt","w")
            skinData.write(world.prize)
            skinData.close()            
        # Key Skin
        if 1200 <= mouseX <= 1600 and (63 <= mouseY <= 363 or 388 <= mouseY <= 488):
            world.prize = "Key.obj"
            world.skin = False
            world.start = True
            skinData = open("data.txt","w")
            skinData.write(world.prize)
            skinData.close()              
        # Gift Skin
        if 1200 <= mouseX <= 1600 and (563 <= mouseY <= 863 or 888.5 <= mouseY <= 988.5):
            world.prize = "gift.obj"
            world.skin = False
            world.start = True
            skinData = open("data.txt","w")
            skinData.write(world.prize)
            skinData.close()              
    elif world.help == True:
        # Back button 
        if 660 <= mouseX <= 1260 and 873 <= mouseY <= 973:
            world.help = False
            world.start = True
    elif world.win == True:
        # Reset
        if 500 <= mouseX <= 900 and 550 <= mouseY <= 650:
            world.game = True
            world.win = False
            hideMouse()
            reset(world)
            loadLevel(world)
        # Next Level
        if 1020 <= mouseX <= 1420 and 550 <= mouseY <= 650:
            world.game = True
            world.win = False            
            reset(world)
            hideMouse()
            world.mode += 1
            loadLevel(world)
        # Return to menu
        if 660 <= mouseX <= 1260 and 775 <= mouseY <= 875:
            world.level = True
            world.win = False            
            reset(world)
# Loads new level
def loadLevel(world):
    hideMouse()
    setCameraRotation(0,0,0)
    if world.mode in world.mapFiles.keys():
        buildWorld(world,world.mapFiles[world.mode][0],world.mapFiles[world.mode][1],world.mapFiles[world.mode][2],world.mapFiles[world.mode][3],"wall1.jpg")
    else:
        world.mode = 1
        buildWorld(world,world.mapFiles[world.mode][0],world.mapFiles[world.mode][1],world.mapFiles[world.mode][2],world.mapFiles[world.mode][3],"wall1.jpg")  
# Dot Product
def dotProduct(cameraVector,objectVector):
    (x1,y1,z1) = cameraVector
    (x2,y2,z2) = objectVector
    return x1*x2+z1*z2
# Camera Vector    
def drawDecision(world,self):
    length = distance(world.newX,world.newY,world.newZ,self.x,self.y,self.z)
    cameraVector = sphericalToCartesian(world.rotationX,world.rotationZ,length)
    objectVector = (self.x-world.newX,self.y-world.newY,self.z-world.newZ)
    if dotProduct(cameraVector,objectVector) >= 0:
        return True
    else:
        return False
class Wall:
    def __init__(self,x,z,wallTexture):
        # Location of Wall
        self.x = x
        self.z = z
        self.y = 5
        # Defines 3D Object
        # Y-Value is Twice the Height Because Drawn From Center
        self.box = Box3D(10,self.y*2,10,texture=wallTexture)
    def draw(self,world):
        # Determines if wall is in front of camera
        if drawDecision(world,self) == True:
            # Draws wall
            draw3D(self.box,self.x,self.y,self.z)
class Prize:
    def __init__(self,world,x,z):
        # Defines prize
        self.radius = 5
        self.prize = ObjModel3D(world.prize)
        # Prize Location
        self.x = x
        self.y = 3
        self.z = z
        # Determines if prize is gathered
        self.obtained = False
        # Rotation
        self.rotation = 0
    def draw(self,world):
        # Draws and Rotates Prize
        if self.obtained == False:
            # Determines if prize is in front of camera
            if drawDecision(world,self) == True:
                if world.prize == "pepperoni pizza.obj":
                    self.rotation += 1.75
                    draw3D(self.prize,self.x,self.y,self.z,anglex=15,anglez=45,angley=self.rotation,scale=1.5)
                elif world.prize == "Key.obj":
                    self.rotation += 2.25
                    draw3D(self.prize,self.x,self.y+1,self.z,anglez=45,angley=self.rotation,scale=0.01)
                elif world.prize == "trophy.obj":
                    self.rotation += 1.5
                    draw3D(self.prize,self.x,self.y+0.5,self.z,angley=self.rotation,scale=7.5)
                elif world.prize == "gift.obj":
                    self.rotation += 2.25
                    draw3D(self.prize,self.x,self.y+1.5,self.z,angley=self.rotation,scale=15)
    def contact(self,world,x,y,z):
        # Only happens if not gotten already
        if self.obtained == False:
            # Determines if prize is in front of camera
            if drawDecision(world,self) == True:
                # Finds distance to prize
                cameraDistance = distance(self.x,self.y,self.z,x,y,z)
                # Detects contact
                if cameraDistance <= (self.radius + 0.15):
                    self.obtained = True
class Trap:
    def __init__(self,x,z):
        # Location of Trap
        self.x = x
        self.z = z
        self.y = -0.05
        # Defines 3D Object
        self.box = Box3D(10,0.1,10,colors=["black","black","black","black","black","black"])
    def draw(self,world):
        # Determines if trap is in front of camera
        if drawDecision(world,self) == True:
            # Draws Trap
            draw3D(self.box,self.x,self.y,self.z)
          
def startWorld(world):
    # Screens
    world.startScreen = loadImage("startScreen.png")
    world.levelScreen = loadImage("levelMenu.png")
    world.instructionScreen = loadImage("instructions.png")
    world.nextLevel = loadImage("nextLevel.png")
    world.skinScreen = loadImage("skinSelect.png")
    # Worlds
    world.start = True
    world.level = False
    world.game = False
    world.skin = False
    world.help = False
    # Clicking for menus
    onMousePress(mouseClick)    
    # Load Prize Skin
    world.prizeData = open("data.txt","r")
    world.prize = world.prizeData.read()
    world.prizeData.close()
    # Map Dictionary
    # World Name: Text File,startX,startY,startZ,timeStar1,timeStar2,timeStar3
    world.mapFiles = {1:["map1.txt",45,4,65,30,20,10],2:["map2.txt",40,4,60,30,20,10],3:["map3.txt",50,4,45,30,20,10],4:["map4.txt",55,4,55,30,20,10],5:["map5.txt",50,4,89,30,20,10],6:["map6.txt",45,4,45,35,25,15]}
    world.mode = 1  
    # Initializes world   
    world.floor = Rect3D(100,100,texture="floor1.png",textureRepeat=10)
    world.sky = Hemisphere3D(100,texture="sky1.jpg")    
    # Scoring
    world.score = 0
    world.scoreboard = Canvas2D(1920,1080)
    world.star1 = [(0.0, 135.0), (15.0, 135.0), (25.0, 120.0), (35.0, 135.0), (50.0, 135.0), (35.0, 145.0), (40.0, 160.0), (25.0, 150.0), (10.0, 160.0), (15.0, 145.0)]
    world.thicknessStar1 = 0
    world.timeStar1 = world.mapFiles[world.mode][4]
    world.star2 = [(60.0, 135.0), (75.0, 135.0), (85.0, 120.0), (95.0, 135.0), (110.0, 135.0), (95.0, 145.0), (100.0, 160.0), (85.0, 150.0), (70.0, 160.0), (75.0, 145.0)]
    world.thicknessStar2 = 0
    world.timeStar2 = world.mapFiles[world.mode][5]
    world.star3 = [(120.0, 135.0), (135.0, 135.0), (145.0, 120.0), (155.0, 135.0), (170.0, 135.0), (155.0, 145.0), (160.0, 160.0), (145.0, 150.0), (130.0, 160.0), (135.0, 145.0)]
    world.thicknessStar3 = 0
    world.timeStar3 = world.mapFiles[world.mode][6]
    # Final score
    world.finalStar1 = [(750.0, 412.5), (787.5, 412.5), (812.5, 375.0), (837.5, 412.5), (875.0, 412.5), (837.5, 437.5), (850.0, 475.0), (812.5, 450.0), (775.0, 475.0), (787.5, 437.5)]
    world.finalThickness1 = 0
    world.finalStar2 = [(900.0, 412.5), (937.5, 412.5), (962.5, 375.0), (987.5, 412.5), (1025.0, 412.5), (987.5, 437.5), (1000.0, 475.0), (962.5, 450.0), (925.0, 475.0), (937.5, 437.5)]
    world.finalThickness2 = 0
    world.finalStar3 = [(1050.0, 412.5), (1087.5, 412.5), (1112.5, 375.0), (1137.5, 412.5), (1175.0, 412.5), (1137.5, 437.5), (1150.0, 475.0), (1112.5, 450.0), (1075.0, 475.0), (1087.5, 437.5)]
    world.finalThickness3 = 0    
    # Loose / Winnning
    world.resetScreen = Canvas2D(700,100)
    world.fall = False
    world.lose = False
    world.win = False
    # Jumping
    world.jumpX = 0
    world.jumpZ = 0
    world.jump = False
    world.jumpVelocity = 0.4
    onKeyPress(jump,"space")
    # Testing
    world.wallTest = Wall(50,50,"wall1.jpg")
def updateWorld(world):
    if world.game == True:
        # Initial Camera Rotation
        (world.rotationX,world.rotationY,world.rotationZ) = getCameraRotation()
        # Initial Camera Position
        (world.oldX,world.oldY,world.oldZ) = getCameraPosition()   
        # Timer
        world.timer = 0.001* getElapsedTime()
        world.timerString = format(world.timer,'.0f')
        # Lose Screen
        if world.timer > 2:
            world.lose = False
            world.win = False
        # Camera moves with mouse
        onMouseMotion(mouseMotion)
        # Controls
        if world.jump == False:
            # Move Forward / Backward
            if isKeyPressed("w"):
                moveCameraForward(0.6,True)
            if isKeyPressed("s"):
                moveCameraBackward(0.25,True)
            # Strafe Left / Right
            if isKeyPressed("a"):
                strafeCameraLeft(0.15,True)
            if isKeyPressed("d"):
                strafeCameraRight(0.15,True)
        # New Camera Position
        (world.newX,world.newY,world.newZ) = getCameraPosition()
        # Jumping
        # If space bar has been press, a trap hasn't been triggered, and your new position won't be in a wall, then jump forward
        if world.jump == True and world.fall == False and inBox(world,(world.oldX + world.jumpX),(world.oldZ + world.jumpZ), world.walls,5.1) != True:
                adjustCameraPosition(world.jumpX,world.jumpVelocity,world.jumpZ)
                world.jumpVelocity -= 0.04
        # If your jump would land you in a wall, stop moving forward
        elif inBox(world,world.oldX + world.jumpX,world.oldZ + world.jumpZ, world.walls,5.15) == True:
            world.jumpX = 0
            world.jumpZ = 0
        # Jump Landing
        if world.jump == True and world.oldY < world.startY and world.fall == False:
            world.jump = False
            setCameraPosition(world.oldX,world.startY,world.oldZ)
            world.jumpVelocity = 0.4
        # Wall Contact
        if inBox(world,world.newX,world.newZ,world.walls,5.15) == True:
            if inBox(world,world.newX,world.oldZ,world.walls,5.15) == True:
                if inBox(world,world.oldX,world.newZ,world.walls,5.15) == True:
                    setCameraPosition(world.oldX,world.startY,world.oldZ)
                else:
                    setCameraPosition(world.oldX,world.startY,world.newZ)      
            else:
                setCameraPosition(world.newX,world.startY,world.oldZ)    
        # Prize Contact
        world.score = 0
        for prize in world.prizes:
            prize.contact(world,world.newX,world.newY,world.newZ)
            if prize.obtained == True:
                world.score += 1
        # Trap Contact
        if inBox(world,world.newX,world.newZ,world.traps,4.5) == True or world.fall == True:
            # Allows you to jump over traps
            if world.newY <= world.startY:
                world.fall = True
                adjustCameraPosition(0,-0.30,0)
                if world.newY <= -20:
                    reset(world)
                    world.lose = True
        # Timer Stars
        if world.timer >= world.timeStar1:
            world.thicknessStar1 = 1
        elif world.timer >= world.timeStar2:
            world.thicknessStar2 = 1
        elif world.timer >= world.timeStar3:
            world.thicknessStar3 = 1
        elif world.timer <= world.timeStar3:
            world.thicknessStar1 = 0
            world.thicknessStar2 = 0
            world.thicknessStar3 = 0
        # Game Won
        if world.score == len(world.prizes):
            showMouse()
            world.win = True
            world.game = False
def drawWorld(world):
    if world.game == True:
        # Draws floor and sky
        draw3D(world.floor,50,-0.01,50,anglex=90)  
        draw3D(world.sky,50,0,50)
        # Draws Walls
        for wall in world.walls:
            wall.draw(world)
        # Draws Prizes
        for prize in world.prizes:
            prize.draw(world)
        # Draws Trap
        for trap in world.traps:
            trap.draw(world)
        # Draws Score
        draw2D(world.scoreboard,0,0)
        clearCanvas2D(world.scoreboard)
        drawString2D(world.scoreboard,"Score: "+str(world.score),0,0,color="white",size=50)
        drawString2D(world.scoreboard,"Prizes Remaining: "+str(len(world.prizes)-world.score),0,40,color="white",size=50)
        drawString2D(world.scoreboard,"Time: "+world.timerString,0,80,color="white",size=50)
        drawString2D(world.scoreboard,format(getActualFrameRate(),'.0f'),1880,0,color="limegreen",size=40)
        # Scoring Stars
        pygame.draw.polygon(world.scoreboard.image,(255,223,0),world.star1,world.thicknessStar1)
        pygame.draw.polygon(world.scoreboard.image,(255,223,0),world.star2,world.thicknessStar2) 
        pygame.draw.polygon(world.scoreboard.image,(255,223,0),world.star3,world.thicknessStar3)    
        # Lose Screen
        if world.lose == True:
            draw2D(world.resetScreen,625,475)
            clearCanvas2D(world.resetScreen)
            drawString2D(world.resetScreen,"You died! Level resetting...",0,0,color="white",size=75)
    # Next Level Screen
    elif world.win == True:          
        # Next Level Screen
        draw2D(world.scoreboard,0,0)
        clearCanvas2D(world.scoreboard)
        drawImage2D(world.scoreboard,world.nextLevel,960,540)
        # Scoring Stars
        world.finalThickness1 = world.thicknessStar1
        world.finalThickness2 = world.thicknessStar2
        world.finalThickness3 = world.thicknessStar3
        pygame.draw.polygon(world.scoreboard.image,(255,223,0),world.finalStar1,world.finalThickness1)
        pygame.draw.polygon(world.scoreboard.image,(255,223,0),world.finalStar2,world.finalThickness2) 
        pygame.draw.polygon(world.scoreboard.image,(255,223,0),world.finalStar3,world.finalThickness3)        
    # Start Menu
    elif world.start == True:
        draw2D(world.scoreboard,0,0)
        clearCanvas2D(world.scoreboard)
        drawImage2D(world.scoreboard,world.startScreen,960,540)
    # Level Menu
    elif world.level == True:
        draw2D(world.scoreboard,0,0)
        clearCanvas2D(world.scoreboard)
        drawImage2D(world.scoreboard,world.levelScreen,960,540)
    # Skin Selection
    elif world.skin == True:
        draw2D(world.scoreboard,0,0)
        clearCanvas2D(world.scoreboard)
        drawImage2D(world.scoreboard,world.skinScreen,960,540)        
    # Instructions
    elif world.help == True:
        draw2D(world.scoreboard,0,0)
        clearCanvas2D(world.scoreboard)
        drawImage2D(world.scoreboard,world.instructionScreen,960,540)

runGraphics(startWorld, updateWorld, drawWorld)

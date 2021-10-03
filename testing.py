

#def inBox(x,z,objectList,buffer):
    #for pair in objectList:
        #(wallX,wallZ) = pair
        #if abs(wallX - x) <= buffer and abs(wallZ - z) <= buffer:
            #return True

#wallCoords = [(5, 5), (15, 5), (25, 5), (35, 5), (45, 5), (55, 5), (65, 5), (75, 5), (85, 5), (95, 5), (5, 15), (55, 15), (95, 15), (5, 25), (95, 25), (5, 35), (35, 35), (45, 35), (55, 35), (65, 35), (75, 35), (95, 35), (5, 45), (45, 45), (95, 45), (5, 55), (15, 55), (25, 55), (65, 55), (95, 55), (5, 65), (65, 65), (95, 65), (5, 75), (25, 75), (45, 75), (55, 75), (65, 75), (95, 75), (5, 85), (95, 85), (5, 95), (15, 95), (25, 95), (35, 95), (45, 95), (55, 95), (65, 95), (75, 95), (85, 95), (95, 95)]

#print(inBox(23.23,10.23,wallCoords,5.15))
#43.223327359932135 61.872576346845406
#38.81917140859953 54.71971858453798
#35.06527786025815 49.29654510939608
#31.172661411785764 44.73081550600307
#26.741568827664487 41.4194081751322
#23.215477526405397 37.329584169630095
#19.708364712293534 32.48164910174731
#18.44768291848767 26.688767202949403

#from graphics3d import *

#makeGraphicsWindow(1920, 1080,True)

#def startWorld(world):
    #world.star1 = [(860, 490), (890, 490), (910, 460), (930, 490), (960, 490), (930, 510), (940, 540), (910, 520), (880, 540), (890, 510)]
    #world.scoreboard = Canvas2D(1920,1080)

#def updateWorld(world):
    #pass

#def drawWorld(world):
    #draw2D(world.scoreboard,0,0)
    #clearCanvas2D(world.scoreboard)    
    #pygame.draw.polygon(world.scoreboard.image,(255,223,0),world.star1,0)
    
#runGraphics(startWorld, updateWorld, drawWorld)

coordinates =[(900.0, 412.5), (937.5, 412.5), (962.5, 375.0), (987.5, 412.5), (1025.0, 412.5), (987.5, 437.5), (1000.0, 475.0), (962.5, 450.0), (925.0, 475.0), (937.5, 437.5)]
newList = []

for pair in coordinates:
    (x,y) = pair
    x += 150
    newList.append((x,y))

print(newList)

'''
XXXXXXXXXX
X....X...X
X.T...oT.X
Xo.XXXXX.X
XT..X.o..X
XXX...X.TX
X.....X.oX
X.XTXXXT.X
X..o.....X
XXXXXXXXXX
'''
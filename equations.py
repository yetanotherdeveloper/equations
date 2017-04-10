#!/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtSvg
from PyQt4 import QtCore
import sys
import random
import subprocess
import os
import pickle
from os.path import expanduser 
from os import listdir
import datetime
import argparse
import time
import math

# TODO:
# config: one time session length, ULR to open
# division fibonacci, derivatives
# Open netflix in kids profile
# Make a function with setting comnmandline (avoid copy paste)
# Dungeon keeper on an other game to start alternatively to netflix
# TODO: fix unit test so it show a maze
# TODO: Render of prince and princess
# TODO: move key handling into separate function

class Maze():

    class Sector:
        def __init__(self,left,right,up,down):
            self.visited = False
            self.up = up  
            self.down = down
            self.right = right
            self.left = left

    def __init__(self, mazeHeight, mazeWidth):
        # maze generation
        self.width = mazeWidth
        self.height = mazeHeight
        self.sectors = []
        for j in range(0,mazeHeight):
            for i in range(0,mazeWidth):
                self.sectors.append(
                    self.Sector(self.calculateSectorIndex(j,i-1),
                            self.calculateSectorIndex(j,i+1),
                            self.calculateSectorIndex(j-1,i),
                            self.calculateSectorIndex(j+1,i)))

        self.generateMaze(mazeHeight,mazeWidth)


    def generateMaze(self, mazeHeight, mazeWidth):
        """ Pick a random sector and start generating"""
        random.seed()
        startx = random.randint(0,mazeWidth-1)
        starty = random.randint(0,mazeHeight-1)
        # Pick random location
        self.traverseSector(starty,startx,"none")
        # Revert all negative , and clear other fields
        self.clearSectors()
        return 

    def calculateSectorIndex(self, posy, posx):
        if posx < 0 or posx >= self.width:
            return "none"
        if posy < 0 or posy >= self.height:
            return "none"
        return posy*self.width + posx 
        
    def traverseSector(self, posy, posx, movingDirection):
        currentSector = self.calculateSectorIndex(posy,posx)
        if currentSector == "none" or self.sectors[currentSector].visited == True :
            return

        # mark sector as visited
        self.sectors[currentSector].visited = True
        
        # put into this sector where we came from 
        noGoDirection = "none"
        if movingDirection == "none":
            pass
        elif movingDirection == "left":
            # if we moved left then previous sector is on the right and we do not go right
            self.sectors[currentSector].right = self.sectors[currentSector].right *(-1)
            prevSector = self.calculateSectorIndex(posy,posx+1)
            self.sectors[prevSector].left = self.sectors[prevSector].left *(-1)
            noGoDirection = "right"
        elif movingDirection == "right":
            self.sectors[currentSector].left = self.sectors[currentSector].left *(-1)
            prevSector = self.calculateSectorIndex(posy,posx-1)
            self.sectors[prevSector].right = self.sectors[prevSector].right *(-1)
            noGoDirection = "left"
        elif movingDirection == "up":
            self.sectors[currentSector].down = self.sectors[currentSector].down *(-1)
            prevSector = self.calculateSectorIndex(posy+1,posx)
            self.sectors[prevSector].up = self.sectors[prevSector].up *(-1)
            noGoDirection = "down"
        elif movingDirection == "down":
            self.sectors[currentSector].up = self.sectors[currentSector].up *(-1)
            prevSector = self.calculateSectorIndex(posy-1,posx)
            self.sectors[prevSector].down = self.sectors[prevSector].down *(-1)
            noGoDirection = "up"
        
        # Choose next sector from does not visited
        directions = ["left","right","up","down"]
        # No point of going where we came from
        if noGoDirection != "none":
            directions.remove(noGoDirection)
        while len(directions) > 0:
            direction = random.choice(directions)
            directions.remove(direction)
            if direction == "left":
                nextPosX = posx-1
                nextPosY = posy
            elif  direction == "right":
                nextPosX = posx+1
                nextPosY = posy
            elif  direction == "up":
                nextPosX = posx
                nextPosY = posy-1
            elif  direction == "down":
                nextPosX = posx
                nextPosY = posy+1

            self.traverseSector(nextPosY,nextPosX,direction)

    # TODO: Sector 0???
    def clearSectors(self):
        for sector in self.sectors:
            assert(sector.visited == True)
            if sector.left > 0 :    
                sector.left = "none"
            elif sector.left < 0:
                sector.left = sector.left*(-1)
            if sector.right > 0 :    
                sector.right = "none"
            elif sector.right < 0:
                sector.right = sector.right*(-1)
            if sector.up > 0 :    
                sector.up = "none"
            elif sector.up < 0:
                sector.up = sector.up*(-1)
            if sector.down > 0 :    
                sector.down = "none"
            elif sector.down < 0:
                sector.down = sector.down*(-1)
        return

class EquationsConfig:
    """Class to define object for serialization"""
    def __init__(self, args):
        self.terminate = False
        self.data = { 'num_adds' : 1, 'num_subs' : 1,'num_muls' : 1,'num_divs' : 1, 'num_lang_puzzles' : 1,
                      'num_mazes' : 1, 'day' : 0 , 'daily_counter' : 0, 'maximum_daily_counter' : 3,
                      'maximum_bears' : 15 , 'maximum_value' : 10}

        # If there is a file unpickle it
        # then check the data
        # if data is obsolete then reinstantate date and zero the counter of daily watching
        # if data is present then read counter 
        # if counter meets maximum then prevent from watching
        # If counter is not in maximal state then increment 
        configDir = expanduser("~")+"/.equations/" 
        if os.path.isfile(configDir+"config"):
            configFile = open(configDir+"config","r")
            self.data = pickle.load(configFile)

            # Add
            if args.set_num_adds > -1:
                self.data['num_adds'] = args.set_num_adds
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;
            # Sub
            if args.set_num_subs > -1:
                self.data['num_subs'] = args.set_num_subs
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;
            # Mul
            if args.set_num_muls > -1:
                self.data['num_muls'] = args.set_num_muls
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;
           # Div
            if args.set_num_divs > -1:
                self.data['num_divs'] = args.set_num_divs
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;

           # Language Puzzles
            if args.set_num_lang_puzzles > -1:
                self.data['num_lang_puzzles'] = args.set_num_lang_puzzles
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;

           # Maze Puzzles
            if args.set_num_mazes > -1:
                self.data['num_mazes'] = args.set_num_mazes
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;

            if args.set_daily_counter > 0:
                self.data['daily_counter'] = args.set_daily_counter
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;

            if args.set_maximum_daily_counter > 0:
                self.data['maximum_daily_counter'] = args.set_maximum_daily_counter
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;

            if args.set_maximum_value >= 0:
                self.data['maximum_value'] = args.set_maximum_value
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;

            if args.set_maximum_bears >= 0:
                self.data['maximum_bears'] = args.set_maximum_bears
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;

            # If there was option to print config then
            # do so, and make program terminated 
            if args.print_config == True:
                self.print_config();
                self.terminate = True;
                return;
            
            if self.data['day'] != datetime.datetime.now().day:
                self.data['day'] = datetime.datetime.now().day
                self.data['daily_counter'] = 1
                self.run = True
            elif self.data['daily_counter'] < self.data['maximum_daily_counter']:
                self.data['daily_counter'] = self.data['daily_counter'] + 1
                self.run = True
            else:
                self.run = False
        else:
            if args.print_config == True:
                print("\n No Config found!\n");
                self.terminate = True;
                return;
            # If there is no file then create one a by pickling this object
            if os.path.isdir(configDir) == False:
                os.mkdir(configDir)
            # Fill in new data
            self.data['day'] = datetime.datetime.now().day
            self.data['daily_counter'] = 1
            self.run = True
        configFile = open(configDir+"config","w")
        pickle.dump(self.data,configFile)

    def print_config(self):
        print(""" Configuration: 
                        num_adds: %d
                        num_subs: %d
                        num_muls: %d
                        num_divs: %d
                        num_lang_puzzles: %d
                        num_mazes: %d
                        day: %d   
                        daily_counter: %d
                        maximum_daily_counter: %d
                        maximum_value: %d
                        maximum_bears: %d
                                    """ %
                         (self.data['num_adds'],self.data['num_subs'],self.data['num_muls'],self.data['num_divs'],
self.data['num_lang_puzzles'], self.data['num_mazes'],self.data['day'],self.data['daily_counter'],self.data['maximum_daily_counter'],self.data['maximum_value'],self.data['maximum_bears']))
        
    def shouldRun(self):
        """ Function to decide if this session is legitimate to play cartoons"""
        return self.run

    def shouldTerminate(self):
        return self.terminate

    def getMaximumValue(self):
        return self.data['maximum_value']

    def getMaximumBears(self):
        return self.data['maximum_bears']

    def isEnabled(self, key):
        return self.data[key]

class Stop(QtGui.QWidget):
    def __init__(self,args):
        super(Stop, self).__init__()
        # TODO make it in the middle
        pic = QtGui.QLabel(self)
        pic.setGeometry(300,100,757,767)
        pic.setPixmap(QtGui.QPixmap(os.path.realpath(__file__).replace("equations.py","") + "/stop.png"))
        pic.show()
        self.update()
        if args.dry_run == False:
            subprocess.call(["sudo","shutdown","-h","+1"])
        elif args.dry_run == "Test":
            pass
        else:
            exit()
        self.showFullScreen()

class Equation(QtGui.QWidget):
    def __init__(self,args, num_adds, num_subs, num_muls, num_divs, num_lang_puzzles, num_mazes, maximum_value, maximum_bears):
        super(Equation, self).__init__()
        # Inicjalizacja
        random.seed()
        self.args = args
        self.resourcesPath = os.path.realpath(__file__).replace("equations.py","")
        self.images = self.resourcesPath + "/data/images/"
        self.voices = { 'failure' : QtGui.QSound(self.resourcesPath + "/Dontfail_vbr.mp3")}
        self.tasks = []
        self.tempImages = []
        self.tempMedals = []
        self.lenBaseText = []
        self.pixmaps = []   # Pixmap to be set on Label
        self.sizeOfAnimal = self.geometry().height()/3
        self.visualized = False
        self.errorOnPresentTask = False # Flag indicating if was already some mistake in current puzzle
        self.numMistakes = 0;  # Number of mistakes done
        # For maximum operation value of 0, we do not make a equations
        if maximum_value != 0:
            operations = ['+','-','*']
            operations = []
            
            for i in range(0,num_adds):
                operations.append('+')
            for i in range(0,num_subs):
                operations.append('-')
            for i in range(0,num_muls):
                operations.append('*')
            for i in range(0,num_divs):
                operations.append('/')
            # Add num_lang_puzzles param
            for i in range(0,num_lang_puzzles):
                operations.append('lang')
            # Add num_mazes param
            for i in range(0,num_mazes):
                operations.append('maze')
           
            while len(operations) > 0 : 
                operation = random.choice(operations)
                operations.remove(operation)
                self.tasks.append(self.makeRandomEquation(operation,maximum_value))
                self.lenBaseText.append(len(self.tasks[len(self.tasks)-1][0]))   # length of basic equation (this should be preserved)
        
        if maximum_bears != 0:
            self.tasks.append(self.makeRandomEquation("?",maximum_bears))
            self.lenBaseText.append(len(self.tasks[len(self.tasks)-1][0]))   # length of basic equation (this should be preserved)
        self.iter = 0;
        self.showFullScreen()
    def paintEvent(self,event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        if self.iter < len(self.tasks) and self.tasks[self.iter][3] == "?" and self.visualized == False:
            self.tempImages = []
            for pos in range(0,self.tasks[self.iter][1]):
                pic = QtSvg.QSvgWidget(self.resourcesPath + "/bear.svg", self)
                x = self.geometry().x()
                y = self.geometry().y()
                width = self.geometry().width()
                height = self.geometry().height()
                sizeOfBear = width/10
                if (pos+1)*sizeOfBear >= width:
                    posx = x+(pos+1)*sizeOfBear - width
                    posy = y+sizeOfBear
                else:
                    posx = x+pos*sizeOfBear
                    posy = y
                pic.setGeometry(posx,posy,sizeOfBear,sizeOfBear)
                pic.show()
                self.tempImages.append(pic)
                self.visualized = True
        elif self.iter < len(self.tasks) and  self.tasks[self.iter][3] == "lang" and self.visualized == False:
            # TODO: put this in the middle
            self.pixmaps[0] = self.pixmaps[0].scaledToWidth(self.sizeOfAnimal)
            self.hideImages(self.tempImages)
            self.tempImages = []
            pic = QtGui.QLabel(self)
            startx = self.geometry().width()/2 - self.sizeOfAnimal/2
            starty = 0
            pic.setGeometry(startx,starty,self.sizeOfAnimal,self.sizeOfAnimal)
            pic.setPixmap(self.pixmaps[0])
            pic.show()
            self.tempImages.append(pic)
            self.visualized = True
            time.sleep(1)
            self.say(self.makeDescriptionOfLangPuzzle(self.tasks[self.iter][0]))
        elif self.iter < len(self.tasks) and self.tasks[self.iter][3] == "maze":
            self.renderMaze(self.tasks[self.iter][4],event,qp)
            # Render the dynamic elements
        qp.end()
        self.update()

    def renderMaze(self,maze, event, qp):
        """ Draw actual labirynth based on parameter named maze"""
        # Get dimensions of screen and adjust sector width accordingly
        # 80% of width and height can be used for maze at maximum
        # Sectors are squared so, choose smaller of dimensions
        wSecLen = self.geometry().width()*0.8/maze.width
        hSecLen = self.geometry().height()*0.8/maze.height
        secLen = min(wSecLen,hSecLen)
        # Get Left-top corner of maze (left top corner of sector 0)
        startX = self.geometry().width()*0.1
        startY = self.geometry().height()*0.1

        # Load a princess image
        if self.visualized == False:
            maze.princess = QtSvg.QSvgWidget(self.resourcesPath + "/princess.svg", self)
            #TODO: establish princess coords
            maze.princess.setGeometry(startX,startY,secLen,secLen)
            maze.princess.show()
            maze.knight = QtSvg.QSvgWidget(self.resourcesPath + "/knight.svg", self)
            #TODO: establish knight coords
            maze.knight.setGeometry(startX+ 4*secLen,startY+ 4*secLen,secLen,secLen)
            maze.knight.show()
            self.visualized = True

        qp.setPen(QtGui.QPen(QtCore.Qt.black, 10, QtCore.Qt.SolidLine))
#        print("maze startx=%d starty=%d width=%d height=%d" %(startX,startY,maze.width,maze.height))
        for j in range(0,maze.height):
            for i in range(0,maze.width):
                self.renderSector(startY+j*secLen,startX+i*secLen, secLen, maze.sectors[maze.calculateSectorIndex(j,i)],qp)
        return

    def renderSector(self, startY, startX, secLen, sector, qp):
#        print("Render sector at %d,%d , left=%s right=%s up=%s down=%s\n" 
#            %(startX,startY,str(sector.left),str(sector.right),str(sector.up),str(sector.down)))
        if sector.left == "none" :    
            qp.drawLine(startX,startY,startX,startY+secLen)
        if sector.right == "none" :    
            qp.drawLine(startX+secLen,startY,startX+secLen,startY+secLen)
        if sector.up == "none":    
            qp.drawLine(startX,startY,startX+secLen,startY)
        if sector.down == "none" :    
            qp.drawLine(startX,startY+secLen,startX+secLen,startY+secLen)
        return

    def drawText(self, event, qp):
        if self.iter < len(self.tasks) :
            qp.setPen(QtGui.QColor(0,0,255))
            if self.tasks[self.iter][3] == "lang":
                qp.setFont(QtGui.QFont('Decorative',50))
            else:
                qp.setFont(QtGui.QFont('Decorative',200))
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.tasks[self.iter][0])

    def makeRandomEquation(self, matop, matMaxValue):
        data = ""   # additional data if needed
        if matop == "+":
            a = random.randint(0,matMaxValue)
            b = random.randint(0,matMaxValue-a)
            equation_string=str(a)+"+"+str(b)+"="
        elif matop == "-":
            a = random.randint(matMaxValue/2,matMaxValue)
            b = random.randint(0,matMaxValue/2)
            equation_string=str(a)+"-"+str(b)+"="
        elif matop == "*":
            # a = sqrt(Max) , b_i+1 = a*b_i <= max
            a = random.randint(0,int(math.sqrt(matMaxValue)))
            b = matMaxValue
            while a * b > matMaxValue and b >0:
               b = b - 1 
            # After finding maximal coefficient of multiplication
            # choose randomly among minimal (0) and maximal (the one found)
            b = random.randint(0,b)
            equation_string=str(a)+"*"+str(b)+"="
        elif matop == "/":
            a = random.randint(0,matMaxValue)
            b = 2
            a = int(a/b) * b
            equation_string=str(a)+"/"+str(b)+"="
        # Draw bears
        elif matop == "?":
            a = random.randint(1,matMaxValue)
            b = random.randint(0,0)
            equation_string="? ="
        elif matop == "lang":
            badAnswers = ["",""]
            picture, goodAnswer, badAnswers[0], badAnswers[1] = self.prepareTestData(self.images)
            self.pixmaps.append(picture)
            # TODO Remeber which answer is proper one        
            a = random.randint(1,3)
            b = self.addPrefix(goodAnswer)
            equation_string = ""
            baddies_index = 0
            for i in range(1,4):
                if i == a:
                    equation_string+=str(i) + ") " + goodAnswer +"\n"
                else:
                    equation_string+=str(i) + ") " + badAnswers[baddies_index] +"\n"
                    baddies_index +=1
            equation_string += "\n\nAnswer: " 
        elif matop == "maze":
            # Size of maze
            a = 8
            b = 10
            # Maze is enerated here
            equation_string = "" 
            data = Maze(a,b) 

        return (equation_string, a, b, matop,data)

    def keyPressEvent(self, e):
        self.proceedEquationKeys(e)
        self.proceedMazeKeys(e)
                
        self.update()

    def proceedMazeKeys(self,e):
        """ Key handling routine for maze puzzles"""
        if self.tasks[self.iter][3] != "maze":
            return

        return        

    def proceedEquationKeys(self,e):
        """ Key handling routine for equation and lang puzzles"""
        if self.tasks[self.iter][3] == "maze":
            return
        key2str = {
                   QtCore.Qt.Key_0 : "0",
                   QtCore.Qt.Key_1 : "1",
                   QtCore.Qt.Key_2 : "2",
                   QtCore.Qt.Key_3 : "3",
                   QtCore.Qt.Key_4 : "4",
                   QtCore.Qt.Key_5 : "5",
                   QtCore.Qt.Key_6 : "6",
                   QtCore.Qt.Key_7 : "7",
                   QtCore.Qt.Key_8 : "8",
                   QtCore.Qt.Key_9 : "9",
                    }
        if(e.isAutoRepeat() != True):
            if((e.key() == QtCore.Qt.Key_Backspace) and (len(self.tasks[self.iter][0]) > self.lenBaseText[self.iter])):
               self.tasks[self.iter] = (self.tasks[self.iter][0][:-1], self.tasks[self.iter][1], self.tasks[self.iter][2], self.tasks[self.iter][3]) 
            elif((e.key() in key2str) and (len(self.tasks[self.iter][0]) < self.lenBaseText[self.iter] + 3)): # No more than three characters
                self.tasks[self.iter] = ( self.tasks[self.iter][0] + key2str[e.key()], self.tasks[self.iter][1], self.tasks[self.iter][2], self.tasks[self.iter][3]) 
            elif((e.key() == QtCore.Qt.Key_Enter) or (e.key() == QtCore.Qt.Key_Return)):
                # Validate and Execute
                self.validateAndExecute()

    def validateAndExecute(self):
        if(self.validateEquation() == True):

            # If error was made in this answer (at some point)
            # then no medal is given
            if self.errorOnPresentTask == True:
                self.numMistakes += 1

            # Calculate number of group medals and single medals
            num_medals = self.iter + 1 - self.numMistakes; 
            num_groups_medals = num_medals/5
            num_medals = num_medals - num_groups_medals*5 
            x = self.geometry().x()
            y = self.geometry().y()
            width = self.geometry().width()
            height = self.geometry().height()
            sizeOfMedal = height/4
            # Put medals starting from bottom left
            group_idx = num_groups_medals
            idx = 0
            self.hideImages(self.tempMedals)
            self.tempMedals = []
            while num_groups_medals > 0:
                self.tempMedals.append(QtSvg.QSvgWidget(self.resourcesPath + "/medals.svg", self))
                self.tempMedals[-1].setGeometry(x+idx*sizeOfMedal,y + height - sizeOfMedal,sizeOfMedal,sizeOfMedal)
                self.tempMedals[-1].show()
                idx = idx + 1
                num_groups_medals = num_groups_medals -1

            while num_medals > 0:
                self.tempMedals.append(QtSvg.QSvgWidget(self.resourcesPath + "/medal.svg", self))
                self.tempMedals[-1].setGeometry(x+idx*sizeOfMedal,y + height - sizeOfMedal,sizeOfMedal,sizeOfMedal)
                self.tempMedals[-1].show()
                idx = idx + 1
                num_medals = num_medals - 1

            self.update()
            self.tasks[self.iter] = ( "", self.tasks[self.iter][1], self.tasks[self.iter][2], self.tasks[self.iter][3]) 
            # If there was an error in present puzzle then be less optimistic on
            # in congratualtions
            if self.errorOnPresentTask == True:
                congrats = ["OK!","Finally!","Approved!"]
            else:
                congrats = ["Correct!","Excellent!","Great!","Very good!","Amazing!","Perfect!","Well done!","Awesome!"]
            self.say(random.choice(congrats))
            if self.tasks[self.iter][3] == "lang":
                time.sleep(1)
                self.say("This is " + self.tasks[self.iter][2])
                time.sleep(1)
                self.visualized = False
                self.pixmaps.remove(self.pixmaps[0])
            self.iter+=1
            self.visualized=False
            self.hideImages(self.tempImages)
            self.errorOnPresentTask = False
            if self.iter == len(self.tasks):
                self.runCartoons()
        else:
            self.say("Wrong!")
            self.errorOnPresentTask = True
        return

    def hideImages(self,widgets):
        for widget in widgets:
            widget.setHidden(True)

    def runCartoons(self):
        self.hideImages(self.tempMedals)
        if self.args.dry_run == False:
            # Calculate time allowed for watching cartoons
            timeToWatch = 20 
            if self.iter > self.numMistakes:
                timeToWatch +=  (self.iter  - self.numMistakes) * 2
            subprocess.call(["sudo","shutdown","-h","+"+str(timeToWatch)])
            subprocess.Popen(["google-chrome",
                             "--start-maximized",
                             "--app=http://www.netflix.com"])
        else:
            exit()
        return

    def validateEquation(self):
        # Get result typed and convert it to number
        if(len(self.tasks[self.iter][0]) == self.lenBaseText[self.iter]):
            return False
        typed_result = int(self.tasks[self.iter][0][self.lenBaseText[self.iter]:])
        computed_result = 0
        if self.tasks[self.iter][3] == "+":
            computed_result = self.tasks[self.iter][1] + self.tasks[self.iter][2]
        elif self.tasks[self.iter][3] == "-":
            computed_result = self.tasks[self.iter][1] - self.tasks[self.iter][2]
        elif self.tasks[self.iter][3] == "*":
            computed_result = self.tasks[self.iter][1] * self.tasks[self.iter][2]
        elif self.tasks[self.iter][3] == "/":
            computed_result = self.tasks[self.iter][1] / self.tasks[self.iter][2]
        elif self.tasks[self.iter][3] == "?":
            computed_result = self.tasks[self.iter][1]
            #print("computed=%d typed=%d\n" %(computed_result,typed_result))
        elif self.tasks[self.iter][3] == "lang":
            computed_result = self.tasks[self.iter][1]
        elif self.tasks[self.iter][3] == "maze":
            computed_result = self.tasks[self.iter][1]
        # compare typed result with computed result
        if(typed_result == computed_result):
            return True
        else:
            return False

    def prepareTestData(self, imagesDirPath):
        """# Load images randomly
         os listdir , choose randomyl 3 files
         diffrent ones, then one should be read eg. image loaded
         and printed, other just need as invalid answer
         proper answer randomly to be set and storedc"""
        # TODO: make sure it is only files not directories
        imagesNames = listdir(imagesDirPath)
        # Get Randomly imagename to be proper answer and its picture
        correctOneName = random.choice(imagesNames)
        picture = QtGui.QPixmap(imagesDirPath +"/"+ correctOneName)
        # Here is name of animal that corresspond to picture
        correctAnimalName = correctOneName.replace("-wt.gif","").replace("-vt.gif","")
        incorrectAnimalName1, incorrectAnimalName2 = self.getIncorrectAnswers(imagesNames, correctOneName)
        return picture,correctAnimalName, incorrectAnimalName1,incorrectAnimalName2

    def getIncorrectAnswers(self, imagesNames, correctAnswer):
        """ Get Name of animal different from given correctAnswer"""
        badPool = imagesNames
        badPool.remove(correctAnswer)
        firstBadAnswer = random.choice(badPool)
        badPool.remove(firstBadAnswer)
        firstBadAnswer = firstBadAnswer.replace("-wt.gif","").replace("-vt.gif","")                
        secondBadAnswer = random.choice(badPool)
        badPool.remove(secondBadAnswer)
        secondBadAnswer = secondBadAnswer.replace("-wt.gif","").replace("-vt.gif","")
        return firstBadAnswer,secondBadAnswer

    def say(self, text):
        # This is one is for espeak tts
        #subprocess.Popen(["espeak","-s 150",text])
        # this one is for festival tts
        p1 = subprocess.Popen(["echo",text], stdout=subprocess.PIPE)
        subprocess.Popen(["festival","--tts"], stdin=p1.stdout)
    def addPrefix(self, text):
        if text[0] =='a' or text[0] =='u' or text[0] =='i' or text[0] =='e' or text[0] =='y' or text[0] =='o':
           return "an " + text 
        else:
            return "a " + text
    def makeDescriptionOfLangPuzzle(self,stringToPrint):
        """ Function that generates message to be uttered when Lang puzzle is presented"""
        return "What is on the picture? Possible answers: " + stringToPrint.replace("Answer:","") 

# main function starts here        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--print_config", help="Print configuration file", action="store_true")
    parser.add_argument("--set_daily_counter", help="Set daily_counter value in configuration file", type=int, default=-1)
    parser.add_argument("--set_maximum_daily_counter", help="Set maximum_daily_counter value in configuration file", type=int, default=-1)
    parser.add_argument("--set_maximum_value", help="Set maximal_value in operations to configuration file", type=int, default=-1)
    parser.add_argument("--set_maximum_bears", help="Set maximum_bears to configuration file", type=int, default=-1)
    parser.add_argument("--dry_run", help=" Makes program running without shutdown setting and Netflix launching", action="store_true")
    # Number of specific riddles
    parser.add_argument("--set_num_adds", help="Number of Adding riddles", type=int, default=-1)
    parser.add_argument("--set_num_subs", help="Number of Subtracting riddles", type=int, default=-1)
    parser.add_argument("--set_num_muls", help="Number of Multiplication riddles", type=int, default=-1)
    parser.add_argument("--set_num_divs", help="Number of Division riddles", type=int, default=-1)
    parser.add_argument("--set_num_lang_puzzles", help="Number of Language riddles", type=int, default=-1)
    parser.add_argument("--set_num_mazes", help="Number of Maze riddles", type=int, default=-1)

    args = parser.parse_args()
    config = EquationsConfig(args)

    if config.shouldTerminate() == True:
        exit()

    app = QtGui.QApplication(sys.argv)
    if config.shouldRun() == True:
        rownanko = Equation(args,
                            config.isEnabled('num_adds'),
                            config.isEnabled('num_subs'),
                            config.isEnabled('num_muls'),
                            config.isEnabled('num_divs'),
                            config.isEnabled('num_lang_puzzles'),
                            config.isEnabled('num_mazes'),
                            config.getMaximumValue(),
                            config.getMaximumBears())       # some initialization has to be done
    else:
        print "Daily limit exhausted" 
        stop = Stop(args)    
    sys.exit(app.exec_())

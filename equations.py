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
# config: one time session length, 
# division fibonacci, derivatives
# Open netflix in kids profile
# Make a function with setting comnmandline (avoid copy paste)
# Dungeon keeper on an other game to start alternatively to netflix
# TODO: fix unit test so it show a maze
# TODO: make a unit tests for maze generation , eg. longest route calculation
# TODO: make rectungalar mazes
# TODO: unit tests for clock puzzle

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
        self.routeLength = 0
        self.longestRoute = 0
        self.distantSector = 0
        self.traverseSector(starty,startx,"none")
#        print("Route: %d Longest route: %d finalSector=%d" %(self.routeLength,self.longestRoute,self.distantSector))
        # Revert all negative , and clear other fields
        self.clearSectors()
        self.princessPosX = startx
        self.princessPosY = starty
        self.knightPosX = self.distantSector % mazeWidth
        self.knightPosY =  self.distantSector / mazeWidth

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

            # If current route is longer that 
            # the longest among routes then update
            # the longest command
            self.routeLength = self.routeLength + 1
            if self.routeLength > self.longestRoute:
                self.longestRoute = self.routeLength
                self.distantSector = currentSector 
            self.traverseSector(nextPosY,nextPosX,direction)
            self.routeLength = self.routeLength - 1

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
                      'num_clock_puzzles' : 1,  'num_text_puzzles' : 1, 'num_buying_puzzles' : 1, 'num_mazes' : 1, 'day' : 0 , 'daily_counter' : 0,
                      'maximum_daily_counter' : 3, 'maximum_bears' : 15 , 'maximum_value' : 10,
                      'maze_size' : 8, 'content' : {}}
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

           # Text Puzzles
            if args.set_num_text_puzzles > -1:
                self.data['num_text_puzzles'] = args.set_num_text_puzzles
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;

           # Buying Puzzles
            if args.set_num_buying_puzzles > -1:
                self.data['num_buying_puzzles'] = args.set_num_buying_puzzles
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;

           # Clock Puzzles
            if args.set_num_clock_puzzles > -1:
                self.data['num_clock_puzzles'] = args.set_num_clock_puzzles
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

            if args.set_daily_counter >= 0:
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

            if args.set_maze_size>= 0:
                self.data['maze_size'] = args.set_maze_size
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

            if args.add_content != "":
                self.terminate = True;
                self.add_content(args.add_content)
                self.list_content()
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return

            if args.remove_content != -1:
                self.terminate = True;
                self.remove_content(args.remove_content)
                self.list_content()
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return

            # If there was option to print config then
            # do so, and make program terminated 
            if args.print_config == True:
                self.print_config();
                self.terminate = True;
                return;

            # List pool of content
            if args.list_content == True:
                self.list_content()
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
                        num_clock_puzzles: %d
                        num_mazes: %d
                        num_text_puzzles: %d
                        num_buying_puzzles: %d
                        day: %d   
                        daily_counter: %d
                        maximum_daily_counter: %d
                        maximum_value: %d
                        maze_size: %d
                        maximum_bears: %d
                        content: %d
                                    """ %
                         (self.data['num_adds'],self.data['num_subs'],self.data['num_muls'],self.data['num_divs'],
self.data['num_lang_puzzles'], self.data['num_clock_puzzles'],   self.data['num_mazes'],  self.data['num_text_puzzles'], self.data['num_buying_puzzles'], self.data['day'],self.data['daily_counter'],self.data['maximum_daily_counter'],self.data['maximum_value'],self.data['maze_size'],self.data['maximum_bears'],len(self.data['content'])))

    def list_content(self):
        i = 0
        print("Content:\n")
        for entry in self.data['content']:
            print(str(i)+" "+entry+" : "+self.data['content'][entry])
            i+=1
        return

    def add_content(self, entry):
        command = entry[0:entry.find(':')]
        picture =  entry[entry.find(':')+1:]
        if os.path.isfile(picture) and command != "":
           self.data['content'][command] = picture 
        else:
            print("\nError adding content! eg. --add_content <command>:<path to picture>") 
        return

    def remove_content(self, index):
        i = 0
        import pdb; pdb.set_trace()
        if index < 0 or index > len(self.data['content']):
            print("Error removing content: invalid index")
            return
        key = ""
        for entry in self.data['content']:
            print(str(i)+" "+entry)
            if i == index:
                key = entry
            i+=1
        self.data['content'].pop(key, None)
        return


    def shouldRun(self):
        """ Function to decide if this session is legitimate to play cartoons"""
        return self.run

    def shouldTerminate(self):
        return self.terminate

    def getMaximumValue(self):
        return self.data['maximum_value']

    def getMazeSize(self):
        return self.data['maze_size']

    def getMaximumBears(self):
        return self.data['maximum_bears']

    def getContent(self):
        return self.data['content']

    def isEnabled(self, key):
        # In case of unknown key (there is not updated config stored on platform
        # create relevant entry and set value to 1
        if self.data.has_key(key) == False:
            self.data[key] = 1
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
    class Choice:
        def __init__(self,choices,resourcesPath,parent, startx, starty, width, height, dry_run, timeToWatch):
            self.candidates = {}
            # Let's make a list of URL(key) and images to represent URLs
            i = 0 
            self.dry_run = dry_run
            self.startx = startx
            self.starty = starty
            self.timeToWatch = timeToWatch
            self.width = width
            self.height = height
            self.stepx = int(1.5*width)
            self.stepy = int(1.5*height)
            self.chosen = False
            self.parent = parent
            self.x = startx
            self.y = starty
            self.executions = []
            for url in sorted(choices):
                # Based on extension of file, load SVG or PNG
                if choices[url][-4:] == ".svg":
                    pic = QtSvg.QSvgWidget(resourcesPath + choices[url], self.parent)
                else:
                    pixmap = QtGui.QPixmap(choices[url]) 
                    pic = QtGui.QLabel(self.parent)
                    pic.setPixmap(pixmap)
                pic.setGeometry(self.startx + i*self.stepx,self.starty,self.width,self.height)
                self.candidates[url] = pic
                self.executions.append(url)
                i += 1

        def render(self,qp):
            if self.chosen == True:
                return
            # Draw all choices
            for url in self.candidates:
                self.candidates[url].show()
            # Draw rectangule of choice
            self.drawRectangle(self.x - (self.stepx - self.width)/2, self.y - (self.stepy - self.height)/2, self.stepx, self.stepy,qp)

        def drawRectangle(self,x,y,width,height,qp):
            qp.setPen(QtGui.QPen(QtCore.Qt.blue, 10, QtCore.Qt.SolidLine))
            qp.drawLine(x,y,x + width, y)
            qp.drawLine(x, y, x, y + height )
            qp.drawLine(x,y + height, x + width, y + height)
            qp.drawLine(x + width, y, x + width, y + height)

        def processKeys(self,e):
            if self.chosen == True:
                return
            if e.key() == QtCore.Qt.Key_Left and self.x > self.startx:
                self.x -= self.stepx 
            elif e.key() == QtCore.Qt.Key_Right and self.x <  self.startx + self.stepx*(len(self.candidates) - 1):
                self.x += self.stepx 
            elif((e.key() == QtCore.Qt.Key_Enter) or (e.key() == QtCore.Qt.Key_Return)):
                # Get chosen URL
                i = int((self.x - self.startx)/self.stepx)
                for key in self.candidates:
                    self.parent.hideImages([self.candidates[key]])
                self.chosen = True
                self.runContent(self.executions[i])
                del self.candidates


        def runContent(self,content):
            # Draw pictures of netflix and youtube
            if self.dry_run == False:
                # Calculate time allowed for watching cartoons
                subprocess.call(["sudo","shutdown","-h","+"+str(self.timeToWatch)])
                # If HTTP is at the beginning then use browser
                if content[0:4] == "http":                 
                    subprocess.Popen(["google-chrome",
                                     "--start-maximized",
                                     "--app="+content])
                else:
                    # Run game
                    subprocess.Popen([content])
            else:
                exit()
            return

                

    def __init__(self,args, num_adds, num_subs, num_muls, num_divs, num_lang_puzzles, num_clock_puzzles, num_mazes,
                            num_text_puzzles, num_buying_puzzles, maximum_value, maze_size, maximum_bears, content):
        super(Equation, self).__init__()
        # Inicjalizacja
        random.seed()
        self.args = args
        self.resourcesPath = os.path.realpath(__file__).replace("equations.py","")
        self.images = self.resourcesPath + "/data/images/"
        self.description = ""
        self.content = content
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
        operations = []
        if maximum_value != 0:
            
            for i in range(0,num_adds):
                operations.append('+')
            for i in range(0,num_subs):
                operations.append('-')
            for i in range(0,num_muls):
                operations.append('*')
            for i in range(0,num_divs):
                operations.append('/')

        # Add num_clock_puzzles param
        for i in range(0,num_clock_puzzles):
            operations.append('clock')
        # Add num_lang_puzzles param
        for i in range(0,num_lang_puzzles):
            operations.append('lang')
        # Add num_text_puzzles param
        for i in range(0,num_text_puzzles):
            operations.append('text')
        # Add num_buying_puzzles param
        for i in range(0,num_buying_puzzles):
            operations.append('buying')
        # Add num_mazes param
        if maze_size > 0:
            for i in range(0,num_mazes):
                operations.append('maze')
           
        while len(operations) > 0 : 
            operation = random.choice(operations)
            operations.remove(operation)
            if operation == "maze":
                self.tasks.append(self.makeRandomEquation(operation,maze_size))
            else:
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
            self.description = self.makeDescriptionOfBearsPuzzle() 
            time.sleep(1)
            self.say(self.description)
            self.visualized = True
        elif self.iter < len(self.tasks) and  self.tasks[self.iter][3] == "text" and self.visualized == False:
            for pos in range(0,self.tasks[self.iter][2]):
                pic = QtSvg.QSvgWidget(self.resourcesPath + "/ice_cream.svg", self)
                x = self.geometry().x()
                y = self.geometry().y()
                width = self.geometry().width()
                height = self.geometry().height()
                sizeOfItem = width/10
                if (pos+1)*sizeOfItem >= width:
                    posx = x+(pos+1)*sizeOfItem - width
                    posy = y+sizeOfItem
                else:
                    posx = x+pos*sizeOfItem
                    posy = y
                pic.setGeometry(posx,posy,sizeOfItem,sizeOfItem)
                pic.show()
                self.tempImages.append(pic)
            self.visualized = True
            time.sleep(1)
            self.description = self.makeDescriptionOfTextPuzzle(self.tasks[self.iter][2], self.tasks[self.iter][4])
            self.say(self.description)
        elif self.iter < len(self.tasks) and  self.tasks[self.iter][3] == "buying":
            width = self.geometry().width()
            height = self.geometry().height()
            sizeOfItem = width/10
            if self.visualized == False:
                answer = self.tasks[self.iter][1]
                pocket_coins = self.tasks[self.iter][2]
                item_file = self.tasks[self.iter][4]
                data = item_file.split('-')
                pos = 0
                # TODO: Make various items to be chosen
                pic = QtSvg.QSvgWidget(self.resourcesPath + "/" + item_file, self)
                x = self.geometry().x()
                y = self.geometry().y()
                if (pos+1)*sizeOfItem >= width:
                    posx = x+(pos+1)*sizeOfItem - width
                    posy = y+sizeOfItem
                else:
                    posx = x+pos*sizeOfItem
                    posy = y
                pic.setGeometry(posx,posy,sizeOfItem,sizeOfItem)
                pic.show()
                self.tempImages.append(pic)
                # Presenting pocket money
                self.drawCoins(pocket_coins,0,sizeOfItem*1.75,sizeOfItem,sizeOfItem*0.75)

                self.visualized = True
                time.sleep(1)
                # TODO: Unit test 
                self.description = self.makeDescriptionOfBuyingPuzzle(data[0].replace("_"," "),data[1], data[2].replace(".svg",""))
                self.say(self.description)
            qp.setPen(QtGui.QColor(0,0,100))
            qp.setFont(QtGui.QFont('Decorative',50))
            qp.drawText(sizeOfItem,sizeOfItem/2, QtCore.QString(self.price))
            qp.setPen(QtGui.QColor(0,0,100))
            qp.setFont(QtGui.QFont('Decorative',50))
            qp.drawText(0,sizeOfItem*1.6, QtCore.QString("Pocket money:"))

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
            self.description = self.makeDescriptionOfLangPuzzle(self.tasks[self.iter][0])
            self.say(self.description)
        elif self.iter < len(self.tasks) and  self.tasks[self.iter][3] == "clock" :
            # TODO: put this in the middle
            #self.hideImages(self.tempImages) ?????
            sizeOfClock = self.geometry().width()/5
            if self.visualized == False:
                self.tempImages = []

                pic = QtSvg.QSvgWidget(self.resourcesPath + "/clock.svg", self)
                x = self.geometry().x()
                y = self.geometry().y()
                width = self.geometry().width()
                height = self.geometry().height()
                posx = self.geometry().width()/2 - sizeOfClock/2
                posy = 0
                pic.setGeometry(posx,posy,sizeOfClock,sizeOfClock)
                self.tempImages.append(pic)
                self.visualized = True
                time.sleep(1)
                self.description = self.makeDescriptionOfClockPuzzle(self.tasks[self.iter][0])
                self.say(self.description)
                pic.show()
            # Get degree of rotation of clock pointer
            correctAnswer = self.tasks[self.iter][1]
            # remove answer enumeration and leave only hour
            degrees = correctAnswer * 360/12 
            # Big pointer
            midx = self.geometry().width()/2
            midy = sizeOfClock*0.42
            qp.setPen(QtGui.QPen(QtCore.Qt.black, 10, QtCore.Qt.SolidLine))
            qp.drawLine(midx,midy,midx,0 + sizeOfClock*0.2 )
            # small pointer
            qp.setPen(QtGui.QPen(QtCore.Qt.black, 13, QtCore.Qt.SolidLine))
            qp.translate(midx,midy)
            qp.rotate(degrees)
            qp.drawLine(0,0,0 , 0 - sizeOfClock*0.15)

        elif self.iter < len(self.tasks) and self.tasks[self.iter][3] == "maze":
            self.renderMaze(self.tasks[self.iter][4],event,qp)
            # Render the dynamic elements
        elif self.iter == len(self.tasks):
            if hasattr(self,'choice'):
                self.choice.render(qp)
            self.visualized = True
            #
        qp.end()
        self.update()
    
    def drawCoin(self,image_file,startx,starty,coin_size,amount):

        for i in range(0,amount):
            pic = QtSvg.QSvgWidget(image_file, self)
            x = self.geometry().x()
            y = self.geometry().y()
            width = self.geometry().width()
            height = self.geometry().height()
            if (i+1)*coin_size >= width:
                posx = startx+x+(i+1)*coin_size - width
                posy = starty+y+coin_size
            else:
                posx = startx+x+i*coin_size
                posy = starty+y
            pic.setGeometry(posx,posy,coin_size,coin_size)
            pic.show()
            self.tempImages.append(pic)
        return


    def drawCoins(self,pocket_coins,startx,starty,zloty_size,grosz_size):

        posx = startx
        posy = starty
        fives = pocket_coins[(5,0)]
        self.drawCoin(self.resourcesPath + "/piec.svg",posx,posy,zloty_size,fives)
        posx += fives*zloty_size

        twos = pocket_coins[(2,0)]
        self.drawCoin(self.resourcesPath + "/dwa.svg",posx,posy,zloty_size,twos)
        posx += twos*zloty_size

        ones = pocket_coins[(1,0)]
        self.drawCoin(self.resourcesPath + "/jeden.svg",posx,posy,zloty_size,ones)
        posx += ones*zloty_size


        fives = pocket_coins[(0,50)]
        self.drawCoin(self.resourcesPath + "/50cents.svg",posx,posy,grosz_size,fives)
        posx += fives*grosz_size

        twos = pocket_coins[(0,20)]
        self.drawCoin(self.resourcesPath + "/20cents.svg",posx,posy,grosz_size,twos)
        posx += twos*grosz_size

        ones = pocket_coins[(0,10)]
        self.drawCoin(self.resourcesPath + "/10cents.svg",posx,posy,grosz_size,ones)
        posx += ones*grosz_size
        return

    def renderMaze(self,maze, event, qp):
        """ Draw actual labirynth based on parameter named maze"""
        # Get dimensions of screen and adjust sector width accordingly
        # 80% of width and height can be used for maze at maximum
        # Sectors are squared so, choose smaller of dimensions
        wSecLen = self.geometry().width()*0.9/maze.width
        hSecLen = self.geometry().height()*0.75/maze.height
        secLen = min(wSecLen,hSecLen)
        # Get Left-top corner of maze (left top corner of sector 0)
        startX = self.geometry().width()*0.05
        startY = self.geometry().height()*0.05

        # Load a princess image
        if self.visualized == False:
            maze.princess = QtSvg.QSvgWidget(self.resourcesPath + "/princess.svg", self)
            maze.princess.show()
            maze.knight = QtSvg.QSvgWidget(self.resourcesPath + "/knight.svg", self)
            maze.knight.show()
            self.visualized = True
            # Prepare speech for maze
            self.say(self.makeMazeSpeech())
        else:
            maze.princess.setGeometry(startX+maze.princessPosX*secLen,
                                      startY+maze.princessPosY*secLen,
                                      secLen,
                                      secLen)
            maze.knight.setGeometry(startX+ maze.knightPosX*secLen,
                                    startY+ maze.knightPosY*secLen,
                                    secLen,
                                    secLen)
            

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
            if self.tasks[self.iter][3] == "lang" or self.tasks[self.iter][3] == "clock" or self.tasks[self.iter][3] == "text" or self.tasks[self.iter][3] == "buying":
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
        elif matop == "text":
            data, a, b = self.prepareTextPuzzle(matMaxValue)  
            equation_string = "\nAmount of Katie ice creams =  " 
        elif matop == "buying":
            data, a, b = self.prepareBuyingPuzzle()  
            # TODO: Replace Items with what is to be actually sold
            equation_string = "\nAmount of Items that can be bought =  " 
        elif matop == "clock":
            a = self.prepareClockTestData()
            b = 0
            baddies_index = 0
            equation_string = "\n\nAnswer: " 
        elif matop == "maze":
            # Size of maze
            a = matMaxValue
            b = matMaxValue
            # Maze is enerated here
            equation_string = "" 
            data = Maze(a,b) 

        return (equation_string, a, b, matop,data)

    def keyPressEvent(self, e):
        self.proceedChoiceKeys(e)
        self.proceedEquationKeys(e)
        self.proceedMazeKeys(e)
        self.update()


    def proceedChoiceKeys(self,e):
        if self.iter != len(self.tasks):
            return
        if(e.isAutoRepeat() != True):
            if hasattr(self,'choice'):
                self.choice.processKeys(e)
        return

    def proceedMazeKeys(self,e):
        """ Key handling routine for maze puzzles"""
        if self.iter == len(self.tasks):
            return
        if self.tasks[self.iter][3] != "maze" or self.visualized == False:
            return
        knightX = self.tasks[self.iter][4].knightPosX
        knightY = self.tasks[self.iter][4].knightPosY
        currentKnightSectorIndex = self.tasks[self.iter][4].calculateSectorIndex(knightY,knightX)
        sector = self.tasks[self.iter][4].sectors[currentKnightSectorIndex]
        
        if(e.isAutoRepeat() != True):
            # Move in requested direction if possible
            # eg. if there is a sector up available
            if e.key() == QtCore.Qt.Key_Up and sector.up != "none":
                self.tasks[self.iter][4].knightPosY = knightY - 1
            elif e.key() == QtCore.Qt.Key_Down and sector.down != "none":
                self.tasks[self.iter][4].knightPosY = knightY + 1
            elif e.key() == QtCore.Qt.Key_Left and sector.left != "none":
                self.tasks[self.iter][4].knightPosX = knightX - 1
            elif e.key() == QtCore.Qt.Key_Right and sector.right != "none":
                self.tasks[self.iter][4].knightPosX = knightX + 1
            # Check for success
            if(self.validateEquation() == True):
                self.hideImages([self.tasks[self.iter][4].princess, self.tasks[self.iter][4].knight])
                del self.tasks[self.iter][4].princess
                del self.tasks[self.iter][4].knight
                self.executeOnSuccess()
        return        

    def proceedEquationKeys(self,e):
        """ Key handling routine for equation and lang puzzles"""
        if self.iter == len(self.tasks):
            return
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
            if e.key() == QtCore.Qt.Key_R:
                self.say(self.description)
            elif((e.key() == QtCore.Qt.Key_Backspace) and (len(self.tasks[self.iter][0]) > self.lenBaseText[self.iter])):
               self.tasks[self.iter] = (self.tasks[self.iter][0][:-1], self.tasks[self.iter][1], self.tasks[self.iter][2], self.tasks[self.iter][3]) 
            elif((e.key() in key2str) and (len(self.tasks[self.iter][0]) < self.lenBaseText[self.iter] + 3)): # No more than three characters
                self.tasks[self.iter] = ( self.tasks[self.iter][0] + key2str[e.key()], self.tasks[self.iter][1], self.tasks[self.iter][2], self.tasks[self.iter][3]) 
            elif((e.key() == QtCore.Qt.Key_Enter) or (e.key() == QtCore.Qt.Key_Return)):
                # Validate and Execute
                if(self.validateEquation() == True):
                    self.executeOnSuccess()
                else:
                    self.say("Wrong!")
                    self.errorOnPresentTask = True

    def executeOnSuccess(self):
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
            sizeOfMedal = height/5
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
                self.pixmaps.remove(self.pixmaps[0])
            if self.tasks[self.iter][3] == "clock":
                time.sleep(1)
                self.say("It is " + str(self.tasks[self.iter][1]) + " o'clock")
                time.sleep(1)
            self.iter+=1
            self.visualized=False
            self.description = ""  # Reset description of puzzle
            self.hideImages(self.tempImages)
            self.visualized = False
            self.errorOnPresentTask = False
            if self.iter == len(self.tasks):
                self.prepareChoice()
        return

    def hideImages(self,widgets):
        for widget in widgets:
            widget.setHidden(True)


    def prepareChoice(self):
        self.hideImages(self.tempMedals)
        choices = {"http://www.netflix.com" : "./netflix.svg", "http://youtube.com" : "./youtube.svg"}
        # Extend chocies with user defined content
        for entry in self.content:
           choices[entry] = self.content[entry]       
 
        # Calculate time to play cartoons for
        timeToWatch = 20 
        if self.iter > self.numMistakes:
            timeToWatch +=  (self.iter  - self.numMistakes) 
        width = self.geometry().width()/len(choices)/2
        height = self.geometry().height()/len(choices)/2
        self.choice = self.Choice(choices,
                                  self.resourcesPath,
                                  self,
                                  self.geometry().width()/5,
                                  self.geometry().height()/5,
                                  width,
                                  height,
                                  self.args.dry_run,
                                  timeToWatch)


    def validateEquation(self):
        # Get result typed and convert it to number
        if(len(self.tasks[self.iter][0]) == self.lenBaseText[self.iter]) and self.tasks[self.iter][3] != "maze":
            return False
        # For maze we do not have a string values
        if self.tasks[self.iter][3] == "+":
            typed_result = int(self.tasks[self.iter][0][self.lenBaseText[self.iter]:])
            computed_result = self.tasks[self.iter][1] + self.tasks[self.iter][2]
        elif self.tasks[self.iter][3] == "-":
            typed_result = int(self.tasks[self.iter][0][self.lenBaseText[self.iter]:])
            computed_result = self.tasks[self.iter][1] - self.tasks[self.iter][2]
        elif self.tasks[self.iter][3] == "*":
            typed_result = int(self.tasks[self.iter][0][self.lenBaseText[self.iter]:])
            computed_result = self.tasks[self.iter][1] * self.tasks[self.iter][2]
        elif self.tasks[self.iter][3] == "/":
            typed_result = int(self.tasks[self.iter][0][self.lenBaseText[self.iter]:])
            computed_result = self.tasks[self.iter][1] / self.tasks[self.iter][2]
        elif self.tasks[self.iter][3] == "?":
            typed_result = int(self.tasks[self.iter][0][self.lenBaseText[self.iter]:])
            computed_result = self.tasks[self.iter][1]
            #print("computed=%d typed=%d\n" %(computed_result,typed_result))
        elif self.tasks[self.iter][3] == "lang":
            typed_result = int(self.tasks[self.iter][0][self.lenBaseText[self.iter]:])
            computed_result = self.tasks[self.iter][1]
        elif self.tasks[self.iter][3] == "text":
            typed_result = int(self.tasks[self.iter][0][self.lenBaseText[self.iter]:])
            computed_result = self.tasks[self.iter][1]
        elif self.tasks[self.iter][3] == "buying":
            typed_result = int(self.tasks[self.iter][0][self.lenBaseText[self.iter]:])
            computed_result = self.tasks[self.iter][1]
        elif self.tasks[self.iter][3] == "clock":
            typed_result = int(self.tasks[self.iter][0][self.lenBaseText[self.iter]:])
            computed_result = self.tasks[self.iter][1]
        elif self.tasks[self.iter][3] == "maze":
            # If coords of princess and knight are the same
            # then puzzle of maze is solved eg. knight met princess
            computed_result = self.tasks[self.iter][4].princessPosY*self.tasks[self.iter][4].width + self.tasks[self.iter][4].princessPosX
            typed_result = self.tasks[self.iter][4].knightPosY*self.tasks[self.iter][4].width + self.tasks[self.iter][4].knightPosX
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
        # Here is name of animal that corresponds to picture
        correctAnimalName = correctOneName.replace("-wt.gif","").replace("-vt.gif","").replace("-vb.gif","").replace("-wb.gif","").replace(".gif","")
        incorrectAnimalName1, incorrectAnimalName2 = self.getIncorrectAnswers(imagesNames, correctAnimalName)
        return picture,correctAnimalName, incorrectAnimalName1,incorrectAnimalName2

    def computeAnswerAndTotal(self, param_pair, maxValue):
        # Kasia_items * coeff[0] + coeff[1] + Kasia_items < maxValue <=> (maxValue - coeff[1])/(1 + coeff[0]) >= Kasia_items
        # max(2,2 - param_pair[1]) as 2 - 3 may give -1 for stephane items
        kasia_items =  random.randint(max(2,2 - param_pair[1]), int((maxValue - param_pair[1])/(1 + param_pair[0])))
        stephane_items = kasia_items*param_pair[0] + param_pair[1]
        if stephane_items != int(stephane_items):
            stephane_items = int(stephane_items)
            kasia_items = (stephane_items - param_pair[1])/param_pair[0]
        sum_items = int(kasia_items + kasia_items*param_pair[0] + param_pair[1])
        return kasia_items, sum_items

    def prepareTextPuzzle(self, maxValue):
        """Generate Text puzzle and return in a form of: relation(text), correct answer, total number of items"""
            
        # TODO: Add unit test , mandatory
        # Stephany has... 
        relations = {"three more than": (1,3) ,"two more than": (1,2) ,"one more than" : (1,1), "one less than" : (1,-1), "two less than" : (1,-2), "three less than" : (1,-3), "twice as much as" : (2,0), "half of what" : (0.5, 0)} 
        relation = random.choice(relations.keys())
        kasia_items, sum_items = self.computeAnswerAndTotal(relations[relation],maxValue)
        return relation, kasia_items, sum_items 

    # TODO: Add unit test
    def generateCoins(self, total):
        """ Based on provided total money generate coins that add up to given total"""
        available_coins = [ (0,10) , (0,20), (0,50), (1,0), (2,0), (5,0)] 
        pocket_coins = { (0,10) : 0 , (0,20) : 0, (0,50) : 0, (1,0) : 0 , (2,0) : 0, (5,0) : 0} 
        value = 0
        while value < total:
            # Choose coin by random
            (coin_zlotys, coin_groszys) = random.choice(available_coins)
            #if coins alothogether do not exceed total sum of pocket money then
            potential_value = value + coin_zlotys*100 + coin_groszys
            if potential_value > total:
                continue
            value += coin_zlotys*100 + coin_groszys
            # add coin to pocket money and update sum of coins accordingly
            pocket_coins[(coin_zlotys,coin_groszys)] += 1
        return pocket_coins 

    def prepareBuyingPuzzle(self):
        # TODO : Add more items
        items = ["ice_cream-0-50.svg","bear-2-0.svg","lollipop-0-20.svg","cookie-0-30.svg"]
        item_to_buy = random.choice(items)
        # Get base name of item and its price
        data = item_to_buy.split('-')
        (zlotys,groszys) = (int(data[1]) , int(data[2].replace(".svg","")))
        # Generate pocket money (multiplication of 10 groszys)
        item_value = zlotys*100 + groszys
        pocket_money = (random.randint(int(item_value*0.75),4*(item_value)))/10*10;
        # Compute potential number of items to buy
        answer = int(pocket_money / item_value)
        # Generate coins
        coins = self.generateCoins(pocket_money)
        return item_to_buy, answer, coins, 



    def prepareClockTestData(self):
        """ Load a clock face image , generate good answer and bad ones """
        houres = [1 , 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        correctHour = random.choice(houres)
        return correctHour 

    def getIncorrectAnswers(self, imagesNames, correctAnswer):
        """ Get Name of animal different from given correctAnswer"""
        badPool = imagesNames
        # Remove all variants of correct answer
        extensions = ["-wt.gif","-vt.gif","-vb.gif","-wb.gif",".gif"]
        for ex in extensions:
            if correctAnswer+ex in badPool:
                badPool.remove(correctAnswer+ex)
        firstBadAnswer = random.choice(badPool)
        badPool.remove(firstBadAnswer)
        firstBadAnswer = firstBadAnswer.replace("-wt.gif","").replace("-vt.gif","").replace("-vb.gif","").replace("-wb.gif","").replace(".gif","")                
        secondBadAnswer = random.choice(badPool)
        badPool.remove(secondBadAnswer)
        secondBadAnswer = secondBadAnswer.replace("-wt.gif","").replace("-vt.gif","").replace("-vb.gif","").replace("-wb.gif","").replace(".gif","")
        return firstBadAnswer,secondBadAnswer

    def say(self, text):
        # This is one is for espeak tts
        #subprocess.Popen(["espeak","-s 150",text])
        # this one is for festival tts
        p1 = subprocess.Popen(["echo",text], stdout=subprocess.PIPE)
        subprocess.Popen(["padsp","/opt/festival/bin/festival","--tts"], stdin=p1.stdout)
    def addPrefix(self, text):
        if text[0] =='a' or text[0] =='u' or text[0] =='i' or text[0] =='e' or text[0] =='y' or text[0] =='o':
           return "an " + text 
        else:
            return "a " + text

    def makeDescriptionOfBearsPuzzle(self):
        return "How many bears You can see?"

    def makeDescriptionOfTextPuzzle(self,sumItems, relationText):
        return "Katie and Stephanie have " + str(sumItems) + " ice creams all together. Stephanie has " + relationText + " Katie has. How many ice creams does Katie have?"

    def makeDescriptionOfBuyingPuzzle(self,item, zlotys, groszys):
        items = item + "s"
        price = ""
        if zlotys <> "0":
            price += zlotys+ " dollars "

        if groszys <> "0":
            if zlotys <> "0":
                price += "and "
            price += groszys+ " cents "
        self.price = "= "+str(zlotys)+"."+str(groszys)+" $"
        return "One " + item + " costs " + price +". How many "+items+" can You buy?" 


    def makeDescriptionOfLangPuzzle(self,stringToPrint):
        """ Function that generates message to be uttered when Lang puzzle is presented"""
        return "What is on the picture? Possible answers: " + stringToPrint.replace("Answer:","") 

    def makeDescriptionOfClockPuzzle(self,stringToPrint):
        """ Function that generates message to be uttered when Clock puzzle is presented"""
        return "What time is it?" 

    def makeMazeSpeech(self):
        """ Function that generates message to be uttered when Maze puzzle is presented"""
        return "Princess is lost in a maze. Please find her" 

# main function starts here        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--print_config", help="Print configuration file", action="store_true")
    parser.add_argument("--set_daily_counter", help="Set daily_counter value in configuration file", type=int, default=-1)
    parser.add_argument("--set_maximum_daily_counter", help="Set maximum_daily_counter value in configuration file", type=int, default=-1)
    parser.add_argument("--set_maximum_value", help="Set maximal_value in operations to configuration file", type=int, default=-1)
    parser.add_argument("--set_maze_size", help="Set maze_size in operations to configuration file", type=int, default=-1)
    parser.add_argument("--set_maximum_bears", help="Set maximum_bears to configuration file", type=int, default=-1)
    parser.add_argument("--dry_run", help=" Makes program running without shutdown setting and Netflix launching", action="store_true")
    # Number of specific riddles
    parser.add_argument("--set_num_adds", help="Number of Adding riddles", type=int, default=-1)
    parser.add_argument("--set_num_subs", help="Number of Subtracting riddles", type=int, default=-1)
    parser.add_argument("--set_num_muls", help="Number of Multiplication riddles", type=int, default=-1)
    parser.add_argument("--set_num_divs", help="Number of Division riddles", type=int, default=-1)
    parser.add_argument("--set_num_lang_puzzles", help="Number of Language riddles", type=int, default=-1)
    parser.add_argument("--set_num_mazes", help="Number of Maze riddles", type=int, default=-1)
    parser.add_argument("--set_num_clock_puzzles", help="Number of Clock riddles", type=int, default=-1)
    parser.add_argument("--set_num_text_puzzles", help="Number of Text riddles", type=int, default=-1)
    parser.add_argument("--set_num_buying_puzzles", help="Number of Buying riddles", type=int, default=-1)
    parser.add_argument("--add_content", help="<command to execute>:<picture>", type=str, default="")
    parser.add_argument("--remove_content", help="remove selected content (use list_content to get number)", type=int, default=-1)
    parser.add_argument("--list_content", help="Lists pool of commands to execute", action="store_true")

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
                            config.isEnabled('num_clock_puzzles'),
                            config.isEnabled('num_mazes'),
                            config.isEnabled('num_text_puzzles'),
                            config.isEnabled('num_buying_puzzles'),
                            config.getMaximumValue(),
                            config.getMazeSize(),
                            config.getMaximumBears(),       # some initialization has to be done
                            config.getContent())       
    else:
        print "Daily limit exhausted" 
        stop = Stop(args)    
    sys.exit(app.exec_())

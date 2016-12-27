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
import datetime
import argparse
import time

# TODO:
# limit of two houres per day
# commandline line support: setting equationsconfig , run without shutdown, netflix
# commandline: show current config
# relative positioning of images
# positioning a medal so it put along bottom edge not on fixed position
# config: one time session length, day limit, ULR to open
# subtracting, multiplying, fibonacci, derivatives
# Open netflix in kids profile
# MAke a function with setting comnmandline (avoid copy paste)

# Class to define object for serialization eg.
class EquationsConfig:
    def __init__(self, args):
        self.terminate = False
        self.data = { 'day' : 0 , 'daily_counter' : 0, 'maximum_daily_counter' : 3, 'maximum_bears' : 15 , 'maximum_value' : 10}

        # If there is a file unpickle it
        # then check the data
        # if data is obsolete then reinstantate date and zero the counter of daily watching
        # if data is present then read counter 
        # if counter meets maximum then prevent from watching
        # If counter is not in maximal state then increment 
#        import pdb; pdb.set_trace()
        configDir = expanduser("~")+"/.equations/" 
        if os.path.isfile(configDir+"config"):
            configFile = open(configDir+"config","r")
            self.data = pickle.load(configFile)

            if args.set_daily_counter !=0:
                self.data['daily_counter'] = args.set_daily_counter
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;

            if args.set_maximum_daily_counter !=0:
                self.data['maximum_daily_counter'] = args.set_maximum_daily_counter
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;

            if args.set_maximum_value !=0:
                self.data['maximum_value'] = args.set_maximum_value
                self.terminate = True;
                self.print_config();
                configFile = open(configDir+"config","w")
                pickle.dump(self.data,configFile)
                return;

            if args.set_maximum_bears !=0:
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
                        day: %d   
                        daily_counter: %d
                        maximum_daily_counter: %d
                        maximum_value: %d
                        maximum_bears: %d
                                    """ %
                         (self.data['day'],self.data['daily_counter'],self.data['maximum_daily_counter'],self.data['maximum_value'],self.data['maximum_bears']))
        
    def shouldRun(self):
        """ Function to decide if this session is legitimate to play cartoons"""
        return self.run

    def shouldTerminate(self):
        return self.terminate

    def getMaximumValue(self):
        return self.data['maximum_value']

    def getMaximumBears(self):
        return self.data['maximum_bears']

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
        else:
            exit()
        self.showFullScreen()

class Equation(QtGui.QWidget):
    def __init__(self,args, maximum_value, maximum_bears):
        super(Equation, self).__init__()
        # Inicjalizacja
        random.seed()
        self.args = args
        self.resourcesPath = os.path.realpath(__file__).replace("equations.py","")
        self.voices = { 'failure' : QtGui.QSound(self.resourcesPath + "/Dontfail_vbr.mp3")}
        self.text = [0,0,0]
        self.tempImages = []
        self.a = [0,0,0]
        self.b = [0,0,0]
        self.op = [0,0,0]
        self.text[0], self.a[0], self.b[0], self.op[0] = self.makeRandomEquation("+",maximum_value)
        self.text[1], self.a[1], self.b[1], self.op[1] = self.makeRandomEquation("-",maximum_value)
        self.text[2], self.a[2], self.b[2], self.op[2] = self.makeRandomEquation("?",maximum_bears)
        self.lenBaseText = [0,0,0]
        self.lenBaseText[0] = len(self.text[0])   # length of basic equation (this should be preserved)
        self.lenBaseText[1] = len(self.text[1])   # length of basic equation (this should be preserved)
        self.lenBaseText[2] = len(self.text[2])   # length of basic equation (this should be preserved)
        self.iter = 0;
        self.showFullScreen()
    def paintEvent(self,event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()
        if self.op[self.iter] == "?" and len(self.tempImages) == 0:
            sizeOfBear = 200
            for pos in range(0,self.a[self.iter]):
                pic = QtSvg.QSvgWidget(self.resourcesPath + "/bear.svg", self)
                x = self.geometry().x()
                y = self.geometry().y()
                width = self.geometry().width()
                height = self.geometry().height()
                if (pos+1)*sizeOfBear >= width:
                    posx = x+(pos+1)*sizeOfBear - width
                    posy = y+sizeOfBear
                else:
                    posx = x+pos*sizeOfBear
                    posy = y
                pic.setGeometry(posx,posy,sizeOfBear,sizeOfBear)
                pic.show()
                self.tempImages.append(pic)
        self.update()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(0,0,255))
        qp.setFont(QtGui.QFont('Decorative',200))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text[self.iter])

    def makeRandomEquation(self, matop, matMaxValue):
        if matop == "+":
            a = random.randint(0,matMaxValue)
            b = random.randint(0,matMaxValue-a)
            equation_string=str(a)+"+"+str(b)+"="
        elif matop == "-":
            a = random.randint(matMaxValue/2,matMaxValue)
            b = random.randint(0,matMaxValue/2)
            equation_string=str(a)+"-"+str(b)+"="
        elif matop == "?":
            a = random.randint(1,matMaxValue)
            b = random.randint(0,0)
            equation_string="Ile? ="
            # Draw bears
        return equation_string, a, b, matop

    def keyPressEvent(self, e):
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
            if((e.key() == QtCore.Qt.Key_Backspace) and (len(self.text[self.iter]) > self.lenBaseText[self.iter])):
               self.text[self.iter] = self.text[self.iter][:-1]         
            elif((e.key() in key2str) and (len(self.text[self.iter]) < self.lenBaseText[self.iter] + 3)): # No more than three characters
                self.text[self.iter]+=key2str[e.key()]
            elif((e.key() == QtCore.Qt.Key_Enter) or (e.key() == QtCore.Qt.Key_Return)):
                if(self.validateEquation() == True):
                    # Put medals starting from bottom left
                    pic = QtGui.QLabel(self)
                    x = self.geometry().x()
                    y = self.geometry().y()
                    width = self.geometry().width()
                    height = self.geometry().height()
                    pic.setGeometry(x+self.iter*300,y + height - 300,300,300)
                    pic.setPixmap(QtGui.QPixmap( self.resourcesPath + "/smiley300.png"))
                    pic.show()
                    self.update()
                    self.text[self.iter] = ""
                    self.iter+=1
                    if self.iter == len(self.text):
                        if self.args.dry_run == False:
                            subprocess.call(["sudo","shutdown","-h","+30"])
                            subprocess.Popen(["google-chrome",
                                             "--start-maximized",
                                             "--app=http://www.netflix.com"])
                        else:
                            exit()
                        self.text.append("")
                else:
                    self.voices['failure'].play() 
                
            self.update()

    def validateEquation(self):
        # Get result typed and convert it to number
        if(len(self.text[self.iter]) == self.lenBaseText[self.iter]):
            return False
        typed_result = int(self.text[self.iter][self.lenBaseText[self.iter]:])
        computed_result = 0
        if self.op[self.iter] == "+":
            computed_result = self.a[self.iter] + self.b[self.iter]
        elif self.op[self.iter] == "-":
            computed_result = self.a[self.iter] - self.b[self.iter]
        elif self.op[self.iter] == "?":
            computed_result = self.a[self.iter]
        # compare typed result with computed result
        if(typed_result == computed_result):
            return True
        else:
            return False

# main function starts here        
parser = argparse.ArgumentParser()
parser.add_argument("--print_config", help="Print configuration file", action="store_true")
parser.add_argument("--set_daily_counter", help="Set daily_counter value in configuration file", type=int, default=0)
parser.add_argument("--set_maximum_daily_counter", help="Set maximum_daily_counter value in configuration file", type=int, default=0)
parser.add_argument("--set_maximum_value", help="Set maximal_value in operations to configuration file", type=int, default=0)
parser.add_argument("--set_maximum_bears", help="Set maximum_bears to configuration file", type=int, default=0)
parser.add_argument("--dry_run", help=" Makes program running without shutdown setting and Netflix launching", action="store_true")
args = parser.parse_args()
config = EquationsConfig(args)

if config.shouldTerminate() == True:
    exit()

app = QtGui.QApplication(sys.argv)
if config.shouldRun() == True:
    rownanko = Equation(args,config.getMaximumValue(),config.getMaximumBears())       # some initialization has to be done
else:
    print "Daily limit exhausted" 
    stop = Stop(args)    
sys.exit(app.exec_())

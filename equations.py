#!/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import random
import subprocess
import os
import pickle
from os.path import expanduser 
import datetime

# TODO:
# limit of two houres per day
# commandline line support: setting equationsconfig , run without shutdown, netflix
# positioning a medal so it put along bottom edge not on fixed position
# config: one time session length, day limit, ULR to open
# subtracting, multiplying, fibonacci, derivatives
# Open netflix in kids profile

# Class to define object for serialization eg.
class EquationsConfig:
    def __init__(self):
        self.data = { 'day' : 0 , 'daily_counter' : 0, 'maximum_daily_counter' : 4 }
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
            if self.data['day'] != datetime.datetime.now().day:
                self.data['day'] = datetime.datetime.now().day
                self.data['daily_counter'] = 1
                self.data['maximum_daily_counter'] = 4
                self.run = True
            elif self.data['daily_counter'] < self.data['maximum_daily_counter']:
                self.data['daily_counter'] = self.data['daily_counter'] + 1
                self.run = True
            else:
                self.run = False
        else:
            # If there is no file then create one a by pickling this object
            if os.path.isdir(configDir) == False:
                os.mkdir(configDir)
            # Fill in new data
            self.data['day'] = datetime.datetime.now().day
            self.data['daily_counter'] = 1
            self.data['maximum_daily_counter'] = 4
            self.run = True
        configFile = open(configDir+"config","w")
        pickle.dump(self.data,configFile)

    def shouldRun(self):
        """ Function to decide if this session is legitimate to play cartoons"""

        return self.run

class Equation(QtGui.QWidget):
    def __init__(self):
        super(Equation, self).__init__()
        # Inicjalizacja
        random.seed()
        self.resourcesPath = os.path.realpath(__file__).replace("equations.py","")
        self.voices = { 'failure' : QtGui.QSound(self.resourcesPath + "/Dontfail_vbr.mp3")}
        self.text = [0,0]
        self.a = [0,0]
        self.b = [0,0]
        self.op = [0,0]
        self.text[0], self.a[0], self.b[0], self.op[0] = self.makeRandomEquation("+")
        self.text[1], self.a[1], self.b[1], self.op[1] = self.makeRandomEquation("-")
        self.lenBaseText = [0,0]
        self.lenBaseText[0] = len(self.text[0])   # length of basic equation (this should be preserved)
        self.lenBaseText[1] = len(self.text[1])   # length of basic equation (this should be preserved)
        self.iter = 0;
        self.showFullScreen()
    def paintEvent(self,event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(0,0,255))
        qp.setFont(QtGui.QFont('Decorative',200))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text[self.iter])

    def makeRandomEquation(self, matop):
        if matop == "+":
            a = random.randint(0,5)
            b = random.randint(0,5)
            equation_string=str(a)+"+"+str(b)+"="
        elif matop == "-":
            a = random.randint(5,10)
            b = random.randint(0,5)
            equation_string=str(a)+"-"+str(b)+"="
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
                    pic = QtGui.QLabel(self)
                    pic.setGeometry(0+self.iter*300,650,300,300)
                    pic.setPixmap(QtGui.QPixmap( self.resourcesPath + "/smiley300.png"))
                    pic.show()
                    self.update()
                    self.text[self.iter] = ""
                    self.iter+=1
                    if self.iter == len(self.text):
                        subprocess.call(["sudo","shutdown","-h","+30"])
                        subprocess.Popen(["google-chrome",
                                         "--start-maximized",
                                         "--app=http://www.netflix.com"])
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
        # compare typed result with computed result
        if(typed_result == computed_result):
            return True
        else:
            return False
        
if EquationsConfig().shouldRun() == True:
    app = QtGui.QApplication(sys.argv)
    rownanko = Equation()       # some initialization has to be done
    sys.exit(app.exec_())
else:
   print "Daily limit exhusted" 

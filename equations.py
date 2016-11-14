#!/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import random
import subprocess
import os

# TODO:
# subtracting, multiplying, fibonacci, derivatives
# Open netflix in kids profile

class Equation(QtGui.QWidget):
    def __init__(self):
        super(Equation, self).__init__()
        # Inicjalizacja
        random.seed()
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
                    pic.setPixmap(QtGui.QPixmap(os.path.realpath(__file__).replace("equations.py","") + "/smiley300.png"))
                    print("Sciezka do skryptu: %s" %(os.path.realpath(__file__)))
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
                    print("ZLE!!")
                
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
        
app = QtGui.QApplication(sys.argv)
rownanko = Equation()       # some initialization has to be done
sys.exit(app.exec_())

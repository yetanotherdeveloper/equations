#!/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import random

# TODO:
# subtracting, multiplying, fibonacci, derivatives

class Equation(QtGui.QWidget):
    def __init__(self):
        super(Equation, self).__init__()
        # Inicjalizacja
        random.seed()
        self.text = self.makeRandomEquation()
        self.lenBaseText = len(self.text)   # length of basic equation (this should be preserved)
        self.showFullScreen()
    def paintEvent(self,event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(0,0,255))
        qp.setFont(QtGui.QFont('Decorative',200))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)

    def makeRandomEquation(self):
        #TODO: Support for other operations (-, *)
        self.a = random.randint(1,5)
        self.b = random.randint(1,5)
        equation_string=str(self.a)+"+"+str(self.b)+"="
        #print("Equation string %s" %(equation_string))
        return equation_string

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
            if((e.key() == QtCore.Qt.Key_Backspace) and (len(self.text) > self.lenBaseText)):
               self.text = self.text[:-1]         
            elif((e.key() in key2str) and (len(self.text) < self.lenBaseText + 3)): # No more than three characters
                self.text+=key2str[e.key()]
            elif((e.key() == QtCore.Qt.Key_Enter) or (e.key() == QtCore.Qt.Key_Return)):
                #TODO verify if anwser is ok
                if(self.validateEquation() == True):
                    print("SUPER KASIA")
                else:
                    print("ZLE!!")
                
            self.update()

    def validateEquation(self):
        # Get result typed and convert it to number
        if(len(self.text) == self.lenBaseText):
            return False
        typed_result = int(self.text[self.lenBaseText:])
        computed_result = self.a + self.b
        # compare typed result with computed result
        if(typed_result == computed_result):
            return True
        else:
            return False
        
app = QtGui.QApplication(sys.argv)
#w = QtGui.QWidget()
#w.resize(300,400)
#w.move(0,0)
#w.show()
rownanko = Equation()       # some initialization has to be done
sys.exit(app.exec_())

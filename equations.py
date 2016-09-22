#!/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import random

# TODO:
# - fullscreen
# - Input field to be done

class Equation(QtGui.QWidget):
    def __init__(self):
        super(Equation, self).__init__()
        # Inicjalizacja
        random.seed()
        self.text = self.makeRandomEquation()
        self.setGeometry(0,0,600,800)
        self.show()
    def paintEvent(self,event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(0,0,255))
        qp.setFont(QtGui.QFont('Decorative',100))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)

    def makeRandomEquation(self):
        # TODO: write a body of equation
        a = random.randint(1,5)
        b = random.randint(1,5)
        equation_string=str(a)+"+"+str(b)
        #print("Equation string %s" %(equation_string))
        return equation_string

app = QtGui.QApplication(sys.argv)
#w = QtGui.QWidget()
#w.resize(300,400)
#w.move(0,0)
#w.show()
rownanko = Equation()       # some initialization has to be done
sys.exit(app.exec_())

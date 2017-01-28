import equations
from PyQt4 import QtGui
from PyQt4 import QtSvg
from PyQt4 import QtCore
import sys
import random
import subprocess
import os
import pickle
import time

def test_getIncorrectAnswers(qtbot):
    eqobj = equations.Equation("none",0,0,0,0,0,0,0)
    qtbot.addWidget(eqobj)
    firstBadAnswer, secondBadAnswer = eqobj.getIncorrectAnswers(["bear-wt.gif","dog-wt.gif","lion-wt.gif"],"dog-wt.gif")
    assert( (firstBadAnswer == "bear" and secondBadAnswer == "lion") or (firstBadAnswer == "lion" and secondBadAnswer == "bear"))

def test_prepareTestData(qtbot):
    eqobj = equations.Equation("none",0,0,0,0,0,0,0)
    imagesPath = os.path.realpath(__file__).replace("test_equations.py","") + "/data/images/"
    qtbot.addWidget(eqobj)
    correctPicture,correctAnimalName, incorrectAnimalName1,incorrectAnimalName2 = eqobj.prepareTestData(imagesPath)

#    image = QtGui.QLabel()
#    image.setGeometry(300,100,200,200)
#    import pdb; pdb.set_trace()
#    image.setPixmap(QtGui.QPixmap("data/images/bear-wt.gifsdf"))
#    qtbot.addWidget(image)
#    image.show()


    assert(3 * 4 == 12)
    

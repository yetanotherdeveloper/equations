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
    assert((correctAnimalName != incorrectAnimalName1) and(correctAnimalName != incorrectAnimalName2)) 

#def test_generateMaze(qtbot):
 
def test_calculateSectorIndex(qtbot):       
   assert(equations.Maze(4,3).calculateSectorIndex(4,4) == -1)
   assert(equations.Maze(4,3).calculateSectorIndex(-1,3) == -1)
   assert(equations.Maze(4,3).calculateSectorIndex(3,2) == 11)
   assert(equations.Maze(4,3).calculateSectorIndex(0,4) == -1)


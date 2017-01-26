import equations
from PyQt4 import QtGui
from PyQt4 import QtSvg
from PyQt4 import QtCore
import sys
import random
import subprocess
import os
import pickle

def test_getIncorrectAnswers():
    app = QtGui.QApplication(sys.argv)
    firstBadAnswer, secondBadAnswer = equations.Equation("none",0,0,0,0,0,0,0).getIncorrectAnswers(["bear-wt.gif","dog-wt.gif","lion-wt.gif"],"dog-wt.gif")
    assert( (firstBadAnswer == "bear" and secondBadAnswer == "lion") or (firstBadAnswer == "lion" and secondBadAnswer == "bear"))

#TODO test prepare language test



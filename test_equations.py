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

def testcomputeAnswerAndTotal(qtbot):
    def checkConsistency(eqobj, maximum_items, param_pair):
        kasia_items, sum_items = eqobj.computeAnswerAndTotal(param_pair,maximum_items)
        assert(kasia_items == int(kasia_items))
        assert(sum_items == int(sum_items))
        stephany_items = kasia_items*param_pair[0] + param_pair[1]                      
        assert(stephany_items == int(stephany_items))
 
    eqobj = equations.Equation("none",0,0,0,0,0,0,0,0,0,0,0)
    qtbot.addWidget(eqobj)
    
    checkConsistency(eqobj, 10, (1,3)) 
    checkConsistency(eqobj, 10, (1,2)) 
    checkConsistency(eqobj, 10, (1,1)) 
    checkConsistency(eqobj, 10, (1,-1)) 
    checkConsistency(eqobj, 10, (1,-2)) 
    checkConsistency(eqobj, 10, (1,-3)) 
    checkConsistency(eqobj, 10, (2,0)) 
    checkConsistency(eqobj, 10, (0.5,0)) 

    checkConsistency(eqobj, 7, (1,3)) 
    checkConsistency(eqobj, 7, (1,2)) 
    checkConsistency(eqobj, 7, (1,1)) 
    checkConsistency(eqobj, 7, (1,-1)) 
    checkConsistency(eqobj, 7, (1,-2)) 
    checkConsistency(eqobj, 7, (1,-3)) 
    checkConsistency(eqobj, 7, (2,0)) 
    checkConsistency(eqobj, 7, (0.5,0)) 

def testmakeDescriptionOfTextPuzzle(qtbot):
    eqobj = equations.Equation("none",0,0,0,0,0,0,0,0,0,0,0)
    qtbot.addWidget(eqobj)
    description = eqobj.makeDescriptionOfTextPuzzle(10, "half of what")
    assert(description == "Katie and Stephanie have 10 ice creams all together. Stephanie has half of what Katie has. How many ice creams does Katie have?" )

def testPrepareTextPuzzle(qtbot):
    eqobj = equations.Equation("none",0,0,0,0,0,0,0,0,0,0,0)
    qtbot.addWidget(eqobj)
    random.seed(1)
    # It should be "half of what" , 6 , 9
    relation_text, answer_items, sum_items  = eqobj.prepareTextPuzzle(10)
    assert(relation_text == "two more than" and answer_items == 4 and sum_items == 10 )

def testGetIncorrectAnswers(qtbot):
    eqobj = equations.Equation("none",0,0,0,0,0,0,0,0,0,0,0)
    qtbot.addWidget(eqobj)
    firstBadAnswer, secondBadAnswer = eqobj.getIncorrectAnswers(["bear-wt.gif","dog-wt.gif","lion-wt.gif"],"dog")
    assert( (firstBadAnswer == "bear" and secondBadAnswer == "lion") or (firstBadAnswer == "lion" and secondBadAnswer == "bear"))
    firstBadAnswer, secondBadAnswer = eqobj.getIncorrectAnswers(["bear-wt.gif","bear-vt.gif","lion-wt.gif","cow-wt.gif"],"bear")
    assert( (firstBadAnswer == "cow" and secondBadAnswer == "lion") or (firstBadAnswer == "lion" and secondBadAnswer == "cow"))

def testPrepareTestData(qtbot):
    eqobj = equations.Equation("none",0,0,0,0,0,0,0,0,0,0,0)
    imagesPath = os.path.realpath(__file__).replace("test_equations.py","") + "/data/images/"
    qtbot.addWidget(eqobj)
    correctPicture,correctAnimalName, incorrectAnimalName1,incorrectAnimalName2 = eqobj.prepareTestData(imagesPath)
    assert((correctAnimalName != incorrectAnimalName1) and(correctAnimalName != incorrectAnimalName2)) 

#def test_generateMaze(qtbot):
 
def testCalculateSectorIndex(qtbot):       
   assert(equations.Maze(4,3).calculateSectorIndex(4,4) == "none")
   assert(equations.Maze(4,3).calculateSectorIndex(-1,3) == "none")
   assert(equations.Maze(4,3).calculateSectorIndex(3,2) == 11)
   assert(equations.Maze(4,3).calculateSectorIndex(0,4) == "none")

def testMaze(qtbot):
#    testMaze = equations.Maze(3,3)    
#    qtbot.addWidget(testMaze)
#    testMaze.show()
#    time.sleep(1)
    class Args():
        def __init__(self):
            self.dry_run = "Test"
    args = Args()
    testStop = equations.Stop(args) 
    testStop.show()
    qtbot.addWidget(testStop)
#    qtbot.waitExposed(testStop,1000)
    qtbot.waitForWindowShown(testStop)
    return

def testClearSectors(qtbot):
    testMaze = equations.Maze(3,3)    
    refTestMaze = equations.Maze(3,3)    
    assert(refTestMaze.width == 3) 
    assert(refTestMaze.height == 3) 
    # Fill the sectors with some data 
    # corressponding to one that may be generated
    testMaze.sectors[0] = equations.Maze.Sector(left = "none" ,right = -1, up = "none", down = 3)
    testMaze.sectors[1] = equations.Maze.Sector(left = 0 ,right = -2, up = "none", down = 4)
    testMaze.sectors[2] = equations.Maze.Sector(left = -1 ,right = "none", up = "none", down = -5)
    testMaze.sectors[3] = equations.Maze.Sector(left = "none" ,right = -4, up = 0, down = -6)
    testMaze.sectors[4] = equations.Maze.Sector(left = -3 ,right = -5, up = 1, down = 7)
    testMaze.sectors[5] = equations.Maze.Sector(left = -4 ,right = "none", up = -2, down = 8)
    testMaze.sectors[6] =equations.Maze.Sector(left = "none" ,right = -7, up = -3, down = "none")
    testMaze.sectors[7] =equations.Maze.Sector(left = -6 ,right = -8, up = 4, down = "none")
    testMaze.sectors[8] = equations.Maze.Sector(left = -7 ,right = "none", up = 5, down = "none")
    for sector in testMaze.sectors:
        sector.visited = True

    # Fill target /reference maze date
    refTestMaze.sectors[0] = equations.Maze.Sector(left = "none" ,right = 1, up = "none", down = "none")
    refTestMaze.sectors[1] = equations.Maze.Sector(left = 0 ,right = 2, up = "none", down = "none")
    refTestMaze.sectors[2] = equations.Maze.Sector(left = 1 ,right = "none", up = "none", down = 5)
    refTestMaze.sectors[3] = equations.Maze.Sector(left = "none" ,right = 4, up = 0, down = 6)
    refTestMaze.sectors[4] = equations.Maze.Sector(left = 3 ,right = 5, up = "none", down = "none")
    refTestMaze.sectors[5] = equations.Maze.Sector(left = 4 ,right = "none", up = 2, down = "none")
    refTestMaze.sectors[6] =equations.Maze.Sector(left = "none" ,right = 7, up = 3, down = "none")
    refTestMaze.sectors[7] =equations.Maze.Sector(left = 6 ,right = 8, up = "none", down = "none")
    refTestMaze.sectors[8] = equations.Maze.Sector(left = 7 ,right = "none", up = "none", down = "none")
    for sector in refTestMaze.sectors:
        sector.visited = True

    testMaze.clearSectors()

    for i in range(0,len(testMaze.sectors)):
        assert(testMaze.sectors[i].left == refTestMaze.sectors[i].left)
        assert(testMaze.sectors[i].right == refTestMaze.sectors[i].right)
        assert(testMaze.sectors[i].up == refTestMaze.sectors[i].up)
        assert(testMaze.sectors[i].down == refTestMaze.sectors[i].down)
        assert(testMaze.sectors[i].visited == refTestMaze.sectors[i].visited)

    return

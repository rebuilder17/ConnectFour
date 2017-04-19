# -*- coding: utf-8 -*-


import connect4
from MCSolver import *


judgeobj	= connect4.Judge()

#judgeobj.setPlayer1Solver(connect4.HumanSolver('Player1Human'))
#judgeobj.setPlayer1Solver(connect4.RandomSolver('Player1Random'))
#judgeobj.setPlayer1Solver(MCSolver('Player1MC', 0.0))
judgeobj.setPlayer1Solver(MCSolver('Player1MC v2', 0.9))

#judgeobj.setPlayer2Solver(connect4.HumanSolver('Player2Human'))
#judgeobj.setPlayer2Solver(connect4.RandomSolver('Player2Random'))
#judgeobj.setPlayer2Solver(MCSolver('Player2MC v2', 0.9))
judgeobj.setPlayer2Solver(MCSolver('Player2MC v3', 0.95, 50000))

judgeobj.setJudgeOutput(connect4.SimpleJudgeOutput())

result		= judgeobj.runUntilFinish()


#judgeobj._placeMove(3, 0, True)
#judgeobj._placeMove(4, 0, False)
#judgeobj._placeMove(3, 1, True)
#judgeobj._placeMove(5, 0, False)
#judgeobj._placeMove(4, 1, True)
#judgeobj._placeMove(3, 2, False)
#judgeobj._placeMove(5, 1, True)

#judgeobj.doNextMove()


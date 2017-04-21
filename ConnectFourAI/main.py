# -*- coding: utf-8 -*-


import connect4
import ipcutils
from MCSolver import *
from IPCOutput import *
from IPCInputSolver import *


judge = connect4.Judge()

# player1
judge.addPlayer1Solver(IPCInputSolver('P1 IPCInputSolver'))
judge.addPlayer1Solver(MCSolver('P1 MCSolver v3', 0.95, 50000))

# player2
judge.addPlayer2Solver(IPCInputSolver('P2 IPCInputSolver'))
judge.addPlayer2Solver(MCSolver('P2 MCSolver v3', 0.95, 50000))

# output
judge.setJudgeOutput(IPCOutput())


keepRunning = True

while keepRunning:
	# choose solver
	print ('waiting for solver index...')
	ipcutils.sendAwait()
	solverIndex	= int(ipcutils.receive())
	result		= judge.doNextMove(solverIndex)

	if result != connect4.Judge.STATUS_PLAYING:
		keepRunning = False

ipcutils.sendTerminate()

# -*- coding: utf-8 -*-


if __name__ == '__main__':

	import multiprocessing
	multiprocessing.freeze_support()

	import connect4
	import ipcutils
	from MCSolver import *
	from IPCOutput import *
	from IPCInputSolver import *


	judge = connect4.Judge()

	# player1
	judge.addPlayer1Solver(IPCInputSolver('P1 IPCInputSolver'))
	judge.addPlayer1Solver(MCSolver('P1 MCSolver v4', 0.9, 20000, threadcount=8, initialtrycount=8000))

	# player2
	judge.addPlayer2Solver(IPCInputSolver('P2 IPCInputSolver'))
	judge.addPlayer2Solver(MCSolver('P2 MCSolver v4', 0.9, 20000, threadcount=8, initialtrycount=8000))

	# output
	judge.setJudgeOutput(IPCOutput())


	keepRunning = True

	while keepRunning:
		# choose solver
		print ('waiting for solver index... ', __name__)
		ipcutils.sendAwait()
		solverIndex	= int(ipcutils.receive())
		result		= judge.doNextMove(solverIndex)

		if result != connect4.Judge.STATUS_PLAYING:
			keepRunning = False

	ipcutils.sendTerminate()

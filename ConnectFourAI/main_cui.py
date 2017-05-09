# -*- coding: utf-8 -*-


if __name__ == '__main__':

	import connect4
	import ipcutils
	from MCSolver import *
	from RuleSolver import *


	judge = connect4.Judge()

	# player1
	judge.addPlayer1Solver(connect4.HumanSolver('P1 HumanSolver'))
	judge.addPlayer1Solver(MCSolver('P1 MCSolver v5', 0.95, 10000, threadcount=8, initialtrycount=5000))
	judge.addPlayer1Solver(RuleSolver('P1 RuleSolver'))

	# player2
	judge.addPlayer2Solver(connect4.HumanSolver('P2 HumanSolver'))
	judge.addPlayer2Solver(MCSolver('P2 MCSolver v5', 0.95, 10000, threadcount=8, initialtrycount=5000))
	judge.addPlayer2Solver(RuleSolver('P2 RuleSolver'))

	# output
	judge.setJudgeOutput(connect4.SimpleJudgeOutput())


	keepRunning = True

	while keepRunning:
		solverIndex = int(input('Solver 종류 입력 (0:직접 착수, 1:Search Algorithm, 2:Rule) : '))
		result		= judge.doNextMove(solverIndex)
		if result != connect4.Judge.STATUS_PLAYING:
			keepRunning = False

	input('\nEnter를 누르면 종료합니다.')

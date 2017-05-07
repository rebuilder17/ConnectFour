# -*- coding: utf-8 -*-


if __name__ == '__main__':

	import connect4
	from MCSolver import *
	from RuleSolver import *

	targetiter = 10000
	print('Rule Solver Unit Test - target iteration : ', targetiter)

	resultDict = {}

	for i in range(targetiter):
		judgeobj = connect4.Judge()
		judgeobj.setPlayer1Solver(connect4.RandomSolver('P1 RandomSolver'))
		#judgeobj.setPlayer1Solver(MCSolver('P1 MCSolver simple', 0.9, 10000, threadcount=1))
		judgeobj.setPlayer2Solver(RuleSolver('P2 RuleSolver'))
		judgeobj.setJudgeOutput(connect4.SimpleJudgeOutput())

		result = judgeobj.runUntilFinish()
		try:
			resultDict[result] += 1
		except KeyError:
			resultDict[result] = 1

	print('Unit Test result')
	for code in resultDict:
		print('result code {} : {}'.format(code, resultDict[code]))
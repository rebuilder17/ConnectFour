# -*- coding: utf-8 -*-

import connect4
import ipcutils

# 프로세서 간 통신을 위해서 별도로 구현하는 output 클래스
class IPCOutput(connect4.BaseJudgeOutput):
	def showTurnStart(self, judge, solvername):
		print('solver start : ' + solvername)
		ipcutils.sendMessage('solverStart')

	def showMoveTry(self, judge, x, y, solvername, comment):
		print('solver end : {},{} ({})'.format(x, y, comment))
		ipcutils.sendMessage('move:{},{},{}'.format(x, y, comment))

	def showTurnResult(self, judge, resultStatus):
		ipcutils.sendMessage('result:{}'.format(resultStatus))

# -*- coding: utf-8 -*-

import connect4
import ipcutils

# ipc를 통해 보내온 착수점에 두는 Solver
class IPCInputSolver(connect4.BaseSolver):
	def nextMove(self, judge):
		print ('need manual coordinate for a move')
		ipcutils.sendAwait()

		line	= ipcutils.receive()
		x, y	= [int(i.strip()) for i in line.split(',')]

		return x, y, '직접 착수함'
	
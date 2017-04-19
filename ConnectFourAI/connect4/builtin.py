# -*- coding: utf-8 -*-

from .baseclass import *
from .judge import *
import random
import time


# 샘플 Solver 클래스. 사람이 직접 입력하는 착수점에 두는 Solver
class HumanSolver(BaseSolver):
	def nextMove(self, judge):
		strinp	= input('[{}] 착수점을 입력하세요 [x, y] : '.format(self.getName()))
		x, y	= [int(i.strip()) for i in strinp.split(',')]

		return x - 1, y - 1, '사람이 착수함'

# 샘플 Solver 클래스. 랜덤하게 착수함
class RandomSolver(BaseSolver):
	def __init__(self, name):
		super().__init__(name)
		random.seed()

	def nextMove(self, judge):
		xposSeq	= list(range(Judge.BOARD_WIDTH))
		random.shuffle(xposSeq)

		for x in xposSeq:
			for y in range(Judge.BOARD_HEIGHT):
				if judge.canPlaceOn(x, y):
					return x, y, '랜덤 착수'

		return 0, 0, '에러'



# 샘플 JudgeOutput 클래스. 간단하게 콘솔으로 상태를 표시해준다.
class SimpleJudgeOutput(BaseJudgeOutput):
	def __init__(self):
		super().__init__()

		self._startTime	= 0

	def showTurnStart(self, judge, solvername):
		print('[{}] 문제 해결 시작'.format(solvername))
		self._startTime	= time.time()

	def showMoveTry(self, judge, x, y, solvername, comment):
		playerNum	= judge.getTurn() % 2 + 1

		print('[{}] 플레이어 {} 착수 시도 : {}, {} ({})'.format(solvername, playerNum, x + 1, y + 1, comment))

	def showTurnResult(self, judge, resultStatus):
		elapsedTime	= time.time() - self._startTime

		print("**** TURN {} ****".format(judge.getTurn()))

		gameover	= False

		if resultStatus == Judge.STATUS_ERROR_PLAYER1:
			print('플레이어1의 착수 에러로 게임 종료')
			gameover	= True
		elif resultStatus == Judge.STATUS_ERROR_PLAYER2:
			print('플레이어2의 착수 에러로 게임 종료')
			gameover	= True

		elif resultStatus == Judge.STATUS_WIN_PLAYER1:
			print('플레이어1 승리')
			gameover	= True
		elif resultStatus == Judge.STATUS_WIN_PLAYER2:
			print('플레이어2 승리')
			gameover	= True

		elif resultStatus == Judge.STATUS_NOMOREMOVES:
			print('수를 더 놓을 수 없습니다')
			gameover	= True

		#if gameover:	# 게임오버시에 보드판 보여주기
		#	self._showBoard(judge)

		self._showBoard(judge)

		print('(걸린 시간 : {})'.format(elapsedTime))

	# 숫자 -> 전각 문자로 변환하기 위한 테이블
	_intToWideNumber = ['０', '１', '２', '３', '４', '５', '６', '７', '８', '９']

	def _showBoard(self, judge):
		for y in range(Judge.BOARD_HEIGHT - 1, -1, -1):
			line	= SimpleJudgeOutput._intToWideNumber[y + 1]
			for x in range(Judge.BOARD_WIDTH):
				move	= judge.getMoveOnBoard(x, y)
				symbol	= '　'
				if move is not None:
					if move.type == Judge.Move.MOVETYPE_PLAYER1:
						symbol	= '●'
					elif move.type == Judge.Move.MOVETYPE_PLAYER2:
						symbol	= '○'
				line	+= symbol

			print(line)

		numline	= ''
		for n in range(Judge.BOARD_WIDTH + 1):
			numline	+= SimpleJudgeOutput._intToWideNumber[n] if n > 0 else '　'
		print(numline)

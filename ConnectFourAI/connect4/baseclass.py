# -*- coding: utf-8 -*-


from abc import ABC, abstractmethod

#
class BaseSolver(ABC):
	def __init__(self, name):
		self.name	= name			# solver 이름

	def getName(self):
		return self.name

	# 넘겨받은 judge 인터페이스를 바탕으로 다음 수를 계산해서 넘겨준다.
	# judge : Judge.InterfaceForSolver 인스턴스.
	# 리턴값 : 튜플 (x좌표, y좌표, 추가 정보 문자열 혹은 None)
	@abstractmethod
	def nextMove(self, judge):
		return 0, 0, None



class BaseJudgeOutput(ABC):
	def __init__(self):
		pass

	# 턴 넘어와서 solver가 문제 해결 시작할 때 표시
	@abstractmethod
	def showTurnStart(self, judge, solvername):
		pass

	# 착수하려 하는 지점을 표시한다.
	# judge : 인터페이스
	# x, y : 착수지점
	# solvername : solver에 지정한 이름
	# comment : solver에서 해당 착수에 관해 붙인 코멘트. None일 수 있음
	@abstractmethod
	def showMoveTry(self, judge, x, y, solvername, comment):
		pass

	# 해당 턴이 어떻게 종료되었는지 표시한다.
	# judge : 인터페이스
	# resultStatus : Judge.STATUS_XXX 시리즈 값
	@abstractmethod
	def showTurnResult(self, judge, resultStatus):
		pass

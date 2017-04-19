# -*- coding: utf-8 -*-


# 지정된 Solver를 사용하여 게임을 진행하고 JudgeOutput 오브젝트로 결과를 내보내는 클래스
class Judge:

	# 각 착수를 나타냄
	class Move:

		# constants

		MOVETYPE_NONE       = 0									# 착수 종류 : 아무것도 놓지 않음
		MOVETYPE_PLAYER1    = 1									# 착수 종류 : 플레이어1이 놓음
		MOVETYPE_PLAYER2    = 2									# 착수 종류 : 플레이어2가 놓음


		# member funcs

		def __init__(self):
			self.type       = Judge.Move.MOVETYPE_NONE			# 착수 종류 (없음/플레이어1/플레이어2)
			self.turn		= 0									# 몇번째 턴에 착수했는지
			self.x			= 0
			self.y			= 0

	# Solver 클래스에 넘겨주는 인터페이스. Judge 전체 기능 중 일부만 사용할 수 있게 하기 위함.
	# Solver 등 클래스에서는 judge 오브젝트가 아니라 이 오브젝트를 인자로 넘겨받는다.
	# 여기 구현된 각 메서드는 Judge 클래스에 있는 동명의 메서드와 동일하다.
	class Interface:
		def __init__(self, judge):
			self._judge = judge

		def boundaryCheck(self, x, y):
			return self._judge.boundaryCheck(x, y)

		def hasMoveOn(self, x, y):
			return self._judge.hasMoveOn(x, y)

		def canPlaceOn(self, x, y):
			return self._judge.canPlaceOn(x, y)

		def getMoveOnBoard(self, x, y):
			return self._judge.getMoveOnBoard(x, y)

		def getLastMove(self):
			return self._judge.getLastMove()

		def getTurn(self):
			return self._judge.getTurn()

		def nextTurnIsP1(self):
			return self._judge.nextTurnIsP1()

		def checkNextMoveIsFinisher(self, x, y):
			return self._judge.checkNextMoveIsFinisher(x, y)

	###########################################################################

	# constants

	BOARD_WIDTH				= 7									# 판 가로
	BOARD_HEIGHT			= 6									# 판 세로

	# 상태값들
	STATUS_READY			= 0									# 준비(아직 시작 안함)
	STATUS_PLAYING			= 1									# 게임 계속 진행 가능
	STATUS_NOMOREMOVES		= 2									# 더이상 둘 데 없음

	STATUS_WIN_PLAYER1		= 10								# 게임 종료, 플레이어1이 이김
	STATUS_WIN_PLAYER2		= 11								# 게임 종료, 플레이어2가 이김

	STATUS_ERROR_PLAYER1	= 20								# 게임 종료, 플레이어1이 잘못 착수함
	STATUS_ERROR_PLAYER2	= 21								# 게임 종료, 플레이어2가 잘못 착수함


	def __init__(self):
		self.moveList   = []                    				# 지금까지 둔 수 리스트 (Move객체들)
		self.board		= list([None] * Judge.BOARD_WIDTH
								for y in range(Judge.BOARD_HEIGHT))		# 보드 현재 상태

		self._status	= Judge.STATUS_READY					# 현재 상태

		self._solverP1	= None									# 각 플레이어에 해당하는 Solver객체
		self._solverP2	= None
		self._output	= None									# 결과 출력용 객체
		
		self._interface	= Judge.Interface(self)					# solver에게 전달하기 위한 인터페이스 객체


	# 플레이어1에 해당하는 solver 지정
	def setPlayer1Solver(self, solver):
		self._solverP1	= solver

	# 플레이어2에 해당하는 solver 지정
	def setPlayer2Solver(self, solver):
		self._solverP2	= solver

	# 아웃풋 객체 지정
	def setJudgeOutput(self, output):
		self._output	= output

	# 해당 위치가 게임판을 벗어나지 않는 위치일 때만 True 리턴
	def boundaryCheck(self, x, y):
		return 0 <= x < Judge.BOARD_WIDTH and 0 <= y < Judge.BOARD_HEIGHT

	# 판 위에 놓인 Move 객체를 가져온다. 아무것도 놓여있지 않으면 None 리턴.
	# x, y : 좌표값. 좌하단이 0, 0
	# 리턴값 : Move 오브젝트 혹은 None (착수된 게 없으면)
	def getMoveOnBoard(self, x, y):
		return self.board[y][x] if self.boundaryCheck(x, y) else None

	# 해당 위치에 이미 수를 놓았는지 여부 체크. 게임판을 벗어나는 좌표면 언제나 false
	def hasMoveOn(self, x, y):
		return self.boundaryCheck(x, y) and self.board[y][x] is not None

	# 해당 위치에 놓을 수 있는지 여부 체크 (착수 가능 여부)
	def canPlaceOn(self, x, y):
		# 해당 위치에 아무것도 놓여있지 않으면서 맨 아랫줄이거나 아래에 이미 착수되었을 때만 true
		return self.boundaryCheck(x, y) and (not self.hasMoveOn(x, y)) and (y == 0 or self.hasMoveOn(x, y - 1))

	# 가장 최근에 놓은 Move 객체를 가져온다. 아무것도 놓지 않았으면 None 리턴
	def getLastMove(self):
		return self.moveList[-1] if len(self.moveList) > 0 else None

	# 현재 몇번째 턴인지. 현재까지 착수한 턴을 기준으로 한다. 아무것도 두지 않았을 때는 0턴임.
	def getTurn(self):
		return len(self.moveList)
	
	# "이번에 두는" 사람이 플레이어 1이면 (NOTE : 방금 둔 사람 턴 아님)
	def nextTurnIsP1(self):
		return self.getTurn() % 2 == 0

	# 현재 상태
	def getStatus(self):
		return self._status

	# 원점에 type값이 moveType인 Move가 놓일 시 승리 조건 (4개 늘어섬) 을 달성하는지 체크
	def _checkMoveIsFinisher(self, x, y, moveType):
		if not self.boundaryCheck(x, y):							# 바운더리 체크. 게임판을 벗어나면 언제나 false
			return False

		# NOTE : 위쪽 수직방향으로는 검색할 필요가 없지만, 대각선 위쪽으로는 검색해야 하는 경우가 있다.
		# (위에서 아래로, 대각선 방향으로 착수를 한 경우 위쪽 대각선으로 체크해봐야한다.)

		return self._countConnected(moveType, x, y, -1, 0) + self._countConnected(moveType, x, y, 1, 0) >= 3 or \
				self._countConnected(moveType, x, y, -1, 1) + self._countConnected(moveType, x, y, 1, -1) >= 3 or \
				self._countConnected(moveType, x, y, -1, -1) + self._countConnected(moveType, x, y, 1, 1) >= 3 or \
				self._countConnected(moveType, x, y, 0, -1) >= 3


	# 원점을 기준으로, 원점을 제외하고 특정 방향 + 반대방향으로 type값이 moveType과 일치하는 Move가 몇 개 연속했는지 리턴
	def _countConnected(self, moveType, origX, origY, stepX, stepY):
		x			= origX
		y			= origY
		count		= 0

		for i in range(3):
			x		+= stepX
			y		+= stepY
			move	= self.getMoveOnBoard(x, y)
			if move is None or move.type != moveType:	# 착수 안된 지점을 만나거나 다른 플레이어가 둔 수를 만나면 카운트 중지
				break
			else:
				count += 1

		return count


	# 현재 상태에서 다음에 해당 위치에 두면 게임을 이길 수 있는지 체크
	def checkNextMoveIsFinisher(self, x, y):
		p1TurnNow	= self.nextTurnIsP1()						# 이번에 두는 플레이어가 P1인지 (false면 P2)
		moveType	= Judge.Move.MOVETYPE_PLAYER1 if p1TurnNow else Judge.Move.MOVETYPE_PLAYER2
		return self._checkMoveIsFinisher(x, y, moveType)

	# 가장 마지막에 둔 수로 게임을 이겼는지 체크
	def checkLastMoveIsFinisher(self):
		move		= self.getLastMove()
		return self._checkMoveIsFinisher(move.x, move.y, move.type)

	# 보드 꽉찼는지
	def _boardIsFull(self):
		# 어차피 같은 위치에 중복해서 둘 수 없으므로 지금까지 둔 수 갯수가 보드를 꽉 채울 정도가 되었는지 본다.
		return len(self.moveList) >= Judge.BOARD_WIDTH * Judge.BOARD_HEIGHT


	def _placeMove(self, x, y, isP1):
		newMove			= Judge.Move()
		newMove.turn	= self.getTurn() + 1
		newMove.type	= Judge.Move.MOVETYPE_PLAYER1 if isP1 else Judge.Move.MOVETYPE_PLAYER2
		newMove.x		= x
		newMove.y		= y

		self.board[y][x]	= newMove								# 보드에 배치
		self.moveList.append(newMove)								# 수 리스트에 추가

	# 플레이어 순서에 맞는 Solver를 호출해서 수를 두고 보드 상태를 리턴한다.
	def doNextMove(self):
		if self._status	== Judge.STATUS_READY:						# 준비 상태에 있었다면 플레이 상태로 전환
			self._status = Judge.STATUS_PLAYING

		if self._status	!= Judge.STATUS_PLAYING:					# 게임 진행 상태가 아니면 그냥 리턴
			print('the game is already over')
			return self._status

		p1TurnNow		= self.nextTurnIsP1()		  				# 이번에 두는 플레이어가 P1인지 (false면 P2)
		nextSolver		= self._solverP1 if p1TurnNow else self._solverP2

		if self._output is not None:
			self._output.showTurnStart(self._interface, nextSolver.name)	# (output) 턴 시작 표시

		x, y, comment	= nextSolver.nextMove(self._interface)		# 다음 수 계산

		if self._output is not None:
			self._output.showMoveTry(self._interface, x, y, nextSolver.name, comment)	# output

		if not self.canPlaceOn(x, y):								# 착수 불가능한 수를 뒀다면 에러로 게임 끝내기
			self._status	= Judge.STATUS_ERROR_PLAYER1 if p1TurnNow else Judge.STATUS_ERROR_PLAYER2

		else:
			self._placeMove(x, y, p1TurnNow)						# 일단 착수
			if self.checkLastMoveIsFinisher():						# 방금 수를 둬서 게임이 끝났다면
				self._status	= Judge.STATUS_WIN_PLAYER1 if p1TurnNow else Judge.STATUS_WIN_PLAYER2

			elif self._boardIsFull():								# 승패가 갈리지 않았는데 보드가 꽉찼다면
				self._status	= Judge.STATUS_NOMOREMOVES

		if self._output is not None:
			self._output.showTurnResult(self._interface, self._status)		# output

		return self._status											# 상태값 리턴하고 끝


	# 게임 끝날 때까지 계속 진행
	def runUntilFinish(self):
		if self._status	== Judge.STATUS_READY:						# 준비 상태에 있었다면 플레이 상태로 전환
			self._status = Judge.STATUS_PLAYING

		while self._status == Judge.STATUS_PLAYING:					# 진행 상태일 때만 루프 진행
			self.doNextMove()

		return self._status




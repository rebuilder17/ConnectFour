# -*- coding: utf-8 -*-


import connect4
import random

random.seed()


# Monte Carlo 방법을 쓰는 Solver
class MCSolver(connect4.BaseSolver):
	class Board:
		def __init__(self, origboard=None):
			self.width	= connect4.Judge.BOARD_WIDTH
			self.height	= connect4.Judge.BOARD_HEIGHT

			if origboard:	# 원본 보드가 지정되었으면 복제
				self.board = list(list(row) for row in origboard.board)
			else:
				self.board = list([None] * self.width for y in range(self.height))

		def copyFromJudge(self, judge):
			for y in range(self.height):
				for x in range(self.width):
					move = judge.getMoveOnBoard(x, y)
					if move:
						self.board[y][x] = move.type == connect4.Judge.Move.MOVETYPE_PLAYER1

		def boundaryCheck(self, x, y):
			return 0 <= x < self.width and 0 <= y < self.height

		def canPlace(self, x, y):
			return self.boundaryCheck(x, y) and self.board[y][x] is None

		def placeAndCheck(self, x, y, moveType):
			self.board[y][x] = moveType

			return self._samerowcheck(moveType, x, y, 1, 0) + self._samerowcheck(moveType, x, y, -1, 0) >= 3 or \
					self._samerowcheck(moveType, x, y, 1, 1) + self._samerowcheck(moveType, x, y, -1, -1) >= 3 or \
					self._samerowcheck(moveType, x, y, 1, -1) + self._samerowcheck(moveType, x, y, -1, 1) >= 3 or \
					self._samerowcheck(moveType, x, y, 0, -1) >= 3

		def _samerowcheck(self, moveType, origx, origy, stepx, stepy):
			x = origx
			y = origy
			count = 0
			for n in range(3):
				x += stepx
				y += stepy
				if (not self.boundaryCheck(x, y)) or self.board[y][x] != moveType:
					break
				else:
					count += 1
			return count

	class Tree:
		class Node:
			def __init__(self, parent=None):
				# parent 노드의 보드를 복제한다. 수를 두지는 않음.
				self.parent		= parent
				if parent:
					self.board	= MCSolver.Board(parent.board)

				if parent:
					self.key	= parent.key
				else:
					self.key	= ""

				self.p1count		= 0  # p1이 이긴 횟수
				self.p2count		= 0  # p2가 이긴 횟수

				self.x				= None
				self.y				= None
				self.finished		= False
				self.finisherIsP1	= None

			# 승부가 났으면 True 아니면 False
			def place(self, x, y, isP1):
				# note : canPlace 체크는 바깥에서 해야한다.
				self.x = x
				self.y = y

				if self.board.placeAndCheck(x, y, isP1):
					self.finished		= True
					self.finisherIsP1	= isP1
					self.propagateWinCount()
					return True
				return False

			# 부모 노드까지 거슬러올라가면서 승리 카운트
			def propagateWinCount(self):
				node = self
				while node:
					if self.finisherIsP1:
						node.p1count += 1
					else:
						node.p2count += 1
					node = node.parent


		def __init__(self, rootBoard, isP1Turn):
			self.nodeDict	= {}
			self.root		= MCSolver.Tree.Node()
			self.root.board	= rootBoard
			self.isP1Turn	= isP1Turn

			self.weightedSearchProb = 0.9
			self.trycount	= 10000

		def startSearch(self):
			self.nodeDict = {'': self.root}
			#nodeStack = [self.root]
			print('weightedSearchProb : {}, trycount : {}'.format(self.weightedSearchProb, self.trycount))

			for trycount in range(self.trycount):						# 지정한 횟수만큼 탐색을 반복한다.
				node			= self.root
				currentP1Turn	= self.isP1Turn

				while node:												# 다음에 검색할 노드가 없을 때까지 반복
					nextNode	= None
					shouldBreak	= False
					xlist		= None
					width		= self.root.board.width

					if random.random() >= self.weightedSearchProb:		# 일정 확률로 동일하게 랜덤으로 찾는다.
						xlist	= list(range(width))
						random.shuffle(xlist)
					else:												# 나머지 확률로 weight를 따진다.
						xweight	= [0] * width

						# 승리 횟수로 weight 계산
						for x in range(width):
							newKey		= node.key + str(x)
							if newKey in self.nodeDict:
								pick	= self.nodeDict[newKey]
								# p1차례면 p1에게 유리한 쪽으로, p2차례면 p2에게 유리한 쪽으로 weight를 준다.
								xweight[x] += (pick.p1count-pick.p2count) * (1 if currentP1Turn else -1)

						minw	= min(xweight) - 1
						if minw < 0:									# weight 최소값이 1이 되도록 맞춰준다. (0, 음수값 weight 방지)
							for x in range(width):
								xweight[x] -= minw

						xlist	= []
						indexes	= list(range(width))
						#print("weights:{}, xlist:{}".format(str(xweight), str(xlist)))
						while len(xlist) < width:						# weight에 따라 모든 x좌표를 뽑는다.
							pick	= random.choices(indexes, xweight)[0]
							pickInd	= indexes.index(pick)
							del indexes[pickInd]
							del xweight[pickInd]
							xlist.append(pick)

						#print("weights:{}, xlist:{}".format(str(xweight), str(xlist)))

					# x좌표 후보 리스트에서 하나씩 뽑는다.
					for x in xlist:
						if nextNode:											# 다음 턴을 진행할 노드를 찾았다면 x좌표 찾는 루프를 빠져나온다.
							break
						if shouldBreak:											# 루프를 깨야하는 경우 (승부가 난 경우)
							break

						for y in range(node.board.height):						# y좌표를 올라가면서 착수점을 찾는다.
							if node.board.canPlace(x, y):						# 둘 수 있는 곳을 찾았으면
								newKey = node.key + str(x)  					# key 생성 (x 좌표만으로 구성된 sequence)
								#print("check key : " + newKey)

								if newKey in self.nodeDict:						# 같은 키를 지닌 수가 이미 있다면 가져온다.
									cached	= self.nodeDict[newKey]
									if cached.finished:							# 승부가 이미 난 노드라면, 다시 한 번 승률 카운트를 해준다.
										cached.propagateWinCount()
										shouldBreak	= True						# x좌표를 새로 찾을 필요 없음. 다음 회차로 넘어가도록 한다
									else:										# 승부가 안 난 경우엔 계속 검색
										nextNode	= cached
								else:  											# 새로운 수일 경우, 새로 노드를 만들어야함
									newNode					= MCSolver.Tree.Node(node)
									newNode.key				= newKey
									self.nodeDict[newKey]	= newNode			# 캐싱하기

									if not newNode.place(x, y, currentP1Turn):	# 두었는데 승부가 나지 않았다면 계속 검색해야한다
										nextNode			= newNode
									else:										# 승부가 난 경우
										#print ("new finish : " + newKey)
										shouldBreak			= True				# x좌표를 새로 찾을 필요 없음. 다음 회차로 넘어가도록 한다

								break											# 수를 둔 뒤에는 위쪽 y좌표를 찾는 게 무의미함

					node			= nextNode									# 위에서 찾은 "다음 노드"를 사용
					currentP1Turn	= not currentP1Turn							# 턴이 넘어가므로 플래그 반전


	def __init__(self, name, weightedSearchProb = 0.9, trycount = 10000):
		super().__init__(name)
		self.weightedSearchProb	= weightedSearchProb			# 비중에 따른 서치를 얼마만큼 비율로 할지
		self.trycount			= trycount						# 탐색 횟수

	def nextMove(self, judge):
		isP1	= judge.nextTurnIsP1()							# 검색을 시작하는 시점에서 누구 턴인지 판단
		board	= MCSolver.Board()								# 보드 생성 (현재 보드 상태를 복제해온다)
		board.copyFromJudge(judge)

		tree					= MCSolver.Tree(board, isP1)	# 검색용 트리 생성
		tree.weightedSearchProb	= self.weightedSearchProb
		tree.trycount			= self.trycount
		tree.startSearch()										# 계산 시작

		placelist	= []
		for x in range(board.width):							# 트리의 루트에서 각 x좌표마다 자식 노드가 있는지 검색해본다 
			xkey	= str(x)
			if xkey in tree.nodeDict:							# 실제로는 dictionary에서 문자열 키로 검색
				node	= tree.nodeDict[xkey]
				p1c		= node.p1count
				p2c		= node.p2count
				csum	= max(1, p1c + p2c)

				newplace	= { 'x':node.x, 'y':node.y, 'p1prob' : p1c/csum, 'p2prob' : p2c/csum}
				print('({},{}) - p1c : {}, p2c : {}'.format(newplace['x'], newplace['y'], newplace['p1prob'], newplace['p2prob']))
				placelist.append(newplace)

		placelist.sort(key=lambda item:item['p1prob'], reverse=isP1)	# 현재 턴에 맞는 승률 높은 쪽으로 정렬
		choosen	= placelist[0]

		return choosen['x'], choosen['y'], 'MCsearch'


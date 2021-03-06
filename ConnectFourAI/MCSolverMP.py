# -*- coding: utf-8 -*-


import connect4
import random
#import threading
import multiprocessing
import array
import collections
import os

random.seed()

_WIDTH	= connect4.Judge.BOARD_WIDTH
_HEIGHT	= connect4.Judge.BOARD_HEIGHT
_MOVETYPE_PLAYER1 = connect4.Judge.Move.MOVETYPE_PLAYER1

_PROT_getnode = 0x1001
_PROT_findypos = 0x1002
_PROT_wincount = 0x1003
_PROT_newnodeplace = 0x1004
_PROT_getallnextnode = 0x1005
_PROT_iterover = 0x2000

_PROT_noreturn = object()



# Monte Carlo 방법을 쓰는 Solver
class MCSolverMP(connect4.BaseSolver):
	class Board:
		__slots__ = ['board']
		_emptyboard = [0 for x in range(_WIDTH * _HEIGHT)]

		def __init__(self, origboard=None):
			if origboard:	# 원본 보드가 지정되었으면 복제
				#self.board = [x for x in origboard.board]
				self.board = array.array('b', origboard.board)
			else:
				#self.board = [None for x in range(_WIDTH * _HEIGHT)]
				self.board = array.array('b', MCSolverMP.Board._emptyboard)

		def positionToIndex(self, x, y):
			return y * _WIDTH + x

		def copyFromJudge(self, judge):
			for y in range(_HEIGHT):
				for x in range(_WIDTH):
					move = judge.getMoveOnBoard(x, y)
					if move:
						self.board[self.positionToIndex(x, y)] = 1 if move.type == _MOVETYPE_PLAYER1 else 2

		def boundaryCheck(self, x, y):
			return 0 <= x < _WIDTH and 0 <= y < _HEIGHT

		def canPlace(self, x, y):
			#return self.boundaryCheck(x, y) and self.board[self.positionToIndex(x, y)] is None
			return self.boundaryCheck(x, y) and self.board[self.positionToIndex(x, y)] == 0

		def placeAndCheck(self, x, y, moveType):
			moveType = 1 if moveType == True else 2
			self.board[self.positionToIndex(x, y)] = moveType

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
				if (not self.boundaryCheck(x, y)) or self.board[self.positionToIndex(x, y)] != moveType:
					break
				else:
					count += 1
			return count

	class Tree:
		class Node:
			__slots__ = ['parent', 'board', 'key', 'p1count', 'p2count', 'x', 'y', 'finished', 'finisherIsP1']

			def __init__(self, parent=None, copyFrom=None):
				if copyFrom:			# 다른 노드의 복제본을 만드는 경우. (Tree끼리 합성할 때)

					self.parent		= None	# 복제하는 경우엔 별도 과정을 통해서 parent를 지정한다.
					self.board		= MCSolverMP.Board(copyFrom.board)
					self.key		= copyFrom.key
					self.p1count	= copyFrom.p1count
					self.p2count	= copyFrom.p2count
					self.x			= copyFrom.x
					self.y			= copyFrom.y
					self.finished	= copyFrom.finished
					self.finisherIsP1 = copyFrom.finisherIsP1

				else:					# 새로 노드를 만들거나, parent 지정하는 경우 (검색중)

					# parent 노드의 보드를 복제한다. 수를 두지는 않음.
					self.parent		= parent
					if parent:
						self.board	= MCSolverMP.Board(parent.board)

					# Note : key를 정수 타입으로 바꿈. 아무런 수도 두지 않은 상태에서의 기본값은 1.
					# 수를 한번 둘 때마다 기존 키 * width + 새로운 x좌표로 인코딩된다.
					if parent:
						self.key	= parent.key
					else:
						self.key	= 1

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

			def createNextKey(self, x):
				return self.key * _WIDTH + x

			def getPrevKey(self):
				return self.key // _WIDTH

			# nodeDict에서 parent를 찾아 연결한다. (트리 복제시 사용)
			def findParentFromNodeDict(self, nodeDict):
				prevKey	= self.getPrevKey()
				if prevKey != 0:			# root가 아닌 경우 (root의 key는 1이므로 정수나눗셈하면 0이 된다.)
					self.parent	= nodeDict[prevKey]

			# 다른 node의 결과를 더한다. (트리 합성시 사용)
			def addNode(self, node):
				self.p1count += node.p1count
				self.p2count += node.p2count
				# NOTE : 나머지 멤버들은 더해도 의미가 없거나 같으리라고 가정함.
				# 애당초 노드 합성, 복제는 지정된 횟수만큼 이터레이션이 완료된 트리들끼리 처리하는 것이므로,
				# 같은 key를 지니는 노드들끼리는 승리 카운터 이외의 모든 정보가 동일해야 한다.


		'''
		# 프로세스끼리 Node 정보를 공유하기 위한 클래스
		class NodeData:
			__slots__ = ('key', 'finished', 'p1count', 'p2count')
			def __init__(self, key, finished, p1count, p2count):
				self.key = key
				self.finished = finished
				self.p1count = p1count
				self.p2count = p2count
		'''

		def __init__(self, rootBoard = None, isP1Turn = None, originalTreeList = None):

			if originalTreeList is None:		# 일반 트리 생성
				#self.nodeDict	= {}
				self.root		= MCSolverMP.Tree.Node()
				self.root.board = rootBoard
				self.nodeDict	= {1: self.root}
				self.isP1Turn	= isP1Turn

				self.weightedSearchProb = 0.9
				self.trycount = 10000

			else:								# 트리 합성
				self.nodeDict = {}
				nodeDict = self.nodeDict

				for origTree in originalTreeList:			# 트리마다 루프

					self.isP1Turn	= origTree.isP1Turn
					self.weightedSearchProb = origTree.weightedSearchProb
					self.trycount = origTree.trycount

					origDict		= origTree.nodeDict
					for key in origDict:					# 원본 트리의 key를 하나씩 가져온다
						origNode	= origDict[key]

						try:								# 현재 트리에 해당 key를 지닌 노드가 있다면 더해주기
							node	= nodeDict[key]
							node.addNode(origNode)
						except KeyError:					# 해당 키가 없다면 원본 노드를 복제해서 dict에 넣는다
							node	= MCSolverMP.Tree.Node(copyFrom=origDict[key])
							nodeDict[key] = node

				for key in nodeDict:						# 현재 딕셔너리에서 키 하나씩 가져오기
					node	= nodeDict[key]
					node.findParentFromNodeDict(nodeDict)	# 각 노드마다 parent 찾아서 설정하기

				self.root	= nodeDict[1]					# root 노드 세팅하기

		# 이 Tree 객체를 조작하거나 조회하는 파이프라인 메세지를 처리
		def processPipe(self, recv):
			msg = recv[0]

			if msg == _PROT_getnode:	# parameter 1:key
				key = recv[1]
				try:
					node = self.nodeDict[key]
					return { 'key':node.key, 'finished':node.finished }
				except KeyError:
					return None

			elif msg == _PROT_findypos: # parameter 1:key 2:x
				key = recv[1]
				x = recv[2]
				node = self.nodeDict[key]
				board = node.board
				for y in range(_HEIGHT):
					if board.canPlace(x, y):
						return y
				return None

			elif msg == _PROT_wincount:	# parameter 1:key
				key = recv[1]
				node = self.nodeDict[key]
				node.propagateWinCount()
				return _PROT_noreturn

			elif msg == _PROT_newnodeplace:	# parameter 1:parentkey 2:newkey 3:x, 4:y, 5:currentP1Turn
				key = recv[1]
				newKey = recv[2]
				node = self.nodeDict[key]
				newNode = MCSolverMP.Tree.Node(node)
				newNode.key = newKey
				self.nodeDict[newKey] = newNode
				#return newNode.place(recv[3], recv[4], recv[5])
				if newNode.place(recv[3], recv[4], recv[5]):	# 수를 둬서 끝난 경우엔 None 리턴
					return None
				else:											# 아직 안끝난 경우엔 새로 생성한 노드 자체를 리턴
					return { 'key' : newNode.key, 'finished': newNode.finished }

			elif msg == _PROT_getallnextnode:	# parameter 1:key
				key = recv[1]
				nextNodeList = [None for x in range(_WIDTH)]
				for x in range(_WIDTH):
					nextKey = key * _WIDTH + x
					try:
						node = self.nodeDict[nextKey]
						nextNodeList[x] = { 'p1count':node.p1count, 'p2count':node.p2count }
					except KeyError:
						pass
				return nextNodeList

			elif msg == _PROT_iterover:
				return 'iterover'

			print('wrong message : ' , msg)
			raise Exception


		# pipe를 사용하는 search
		def startSearch_withProtocol(self, pipesend, piperecv):
			# self.nodeDict = {1 : self.root}
			# nodeStack = [self.root]
			print('weightedSearchProb : {}, trycount : {}'.format(self.weightedSearchProb, self.trycount))

			# 최적화 위한 local cacheing
			width = _WIDTH
			height = _HEIGHT
			indexes = [x for x in range(width)]
			shuffledIdx = [x for x in range(width)]
			random_random = random.random
			random_shuffle = random.shuffle
			random_choices = random.choices
			nodeDict = self.nodeDict
			weightedSearchProb = self.weightedSearchProb
			##############################

			for trycount in range(self.trycount):  # 지정한 횟수만큼 탐색을 반복한다.
				if trycount % 1000 == 0 and trycount != 0:
					print('iteration ' , trycount)

				#node = self.root
				pipesend.send((_PROT_getnode, 1))
				node = piperecv.recv() # return : NodeData
				currentP1Turn = self.isP1Turn

				while node:  # 다음에 검색할 노드가 없을 때까지 반복
					nextNode = None
					shouldBreak = False
					xlist = None

					key = node['key']

					if random_random() >= weightedSearchProb:  # *** 일정 확률로 동일하게 랜덤으로 찾는다.
						random_shuffle(shuffledIdx)
						xlist = shuffledIdx
					else:  # *** 나머지 확률로 weight를 따진다.
						xweight = [0 for x in range(width)]

						# 승리 횟수로 weight 계산
						pipesend.send((_PROT_getallnextnode, key))
						nextNodeList = piperecv.recv()
						for x in range(width):
							pick = nextNodeList[x]
							if pick:
								# p1차례면 p1에게 유리한 쪽으로, p2차례면 p2에게 유리한 쪽으로 weight를 준다.
								xweight[x] = (pick['p1count'] - pick['p2count']) * (1 if currentP1Turn else -1)

						minw = min(xweight) - 1
						if minw < 0:  # weight 최소값이 1이 되도록 맞춰준다. (0, 음수값 weight 방지)
							for x in range(width):
								xweight[x] -= minw

						xlist = []
						for i in range(width):
							pick = random_choices(indexes, xweight)[0]
							xweight[pick] = 0  # weight를 0으로 둬서 픽되지 않게 한다
							xlist.append(pick)

					# x좌표 후보 리스트에서 하나씩 뽑는다.
					for x in xlist:
						if nextNode:  # 다음 턴을 진행할 노드를 찾았다면 x좌표 찾는 루프를 빠져나온다.
							break
						if shouldBreak:  # 루프를 깨야하는 경우 (승부가 난 경우)
							break

						pipesend.send((_PROT_findypos, key, x))
						y = piperecv.recv()
						if y is not None:  # 둘 수 있는 곳을 찾았으면 #### PROTOCOL
							#newKey = node_createNextKey(x)  # key 생성 (x 좌표만으로 구성된 sequence) #### PROTOCOL
							newKey = key * _WIDTH + x

							#cached = nodeDict[newKey]  #### PROTOCOL
							pipesend.send((_PROT_getnode, newKey))						# 같은 키를 지닌 수가 이미 있다면 가져온다.
							cached = piperecv.recv()

							if cached:
								if cached['finished']:  # 승부가 이미 난 노드라면, 다시 한 번 승률 카운트를 해준다.
									#cached.propagateWinCount() #### PROTOCOL
									pipesend.send((_PROT_wincount, cached['key']))
									#piperecv.recv() # returns None
									shouldBreak = True  # x좌표를 새로 찾을 필요 없음. 다음 회차로 넘어가도록 한다
								else:  # 승부가 안 난 경우엔 계속 검색
									#nextNode = cached #### PROTOCOL
									pipesend.send((_PROT_getnode, cached['key']))
									nextNode = piperecv.recv()
							else:											# 새로운 수일 경우, 새로 노드를 만들어야함
								#newNode = MCSolverMP.Tree.Node(node) #### PROTOCOL
								#newNode.key = newKey
								#nodeDict[newKey] = newNode  # 캐싱하기

								pipesend.send((_PROT_newnodeplace, key, newKey, x, y, currentP1Turn))
								nextNode = piperecv.recv()	# 두었는데 승부가 안난 경우엔 검색을 계속하기 위해 새 nextNode가 지정된다.
								if nextNode is None:		# 승부가 난 경우 (리턴값 None)
									shouldBreak = True  # x좌표를 새로 찾을 필요 없음. 다음 회차로 넘어가도록 한다

								#if not newNode.place(x, y, currentP1Turn):  # 두었는데 승부가 나지 않았다면 계속 검색해야한다 #### PROTOCOL
								#if not win:  # 두었는데 승부가 나지 않았다면 계속 검색해야한다 #### PROTOCOL
									#pipesend.send((_PROT_getnode, newKey))
									#nextNode = piperecv.recv()
								#else:  # 승부가 난 경우
									# print ("new finish : " + newKey)
									#shouldBreak = True  # x좌표를 새로 찾을 필요 없음. 다음 회차로 넘어가도록 한다

					node = nextNode  # 위에서 찾은 "다음 노드"를 사용
					currentP1Turn = not currentP1Turn  # 턴이 넘어가므로 플래그 반전

			print ('iteration finished')
			pipesend.send((_PROT_iterover, ))


	# multiprocessing용
	def _tree_process(self, board, isP1, wsp, tc, pipesend, piperecv):
		tree = MCSolverMP.Tree(board, isP1)	# 더미 트리 만들기
		tree.weightedSearchProb = wsp
		tree.trycount = tc
		tree.startSearch_withProtocol(pipesend, piperecv)  # 검색 시작


	def __init__(self, name, weightedSearchProb = 0.9, trycount = 10000, phasecount = 1, threadcount = 8):
		super().__init__(name)
		self.weightedSearchProb	= weightedSearchProb			# 비중에 따른 서치를 얼마만큼 비율로 할지
		self.trycount			= trycount						# 탐색 횟수
		self.phasecount			= phasecount					# 페이즈 수
		self.threadcount		= threadcount					# 쓰레드 수

	def nextMove(self, judge):
		isP1	= judge.nextTurnIsP1()							# 검색을 시작하는 시점에서 누구 턴인지 판단
		board	= MCSolverMP.Board()							# 보드 생성 (현재 보드 상태를 복제해온다)
		board.copyFromJudge(judge)

		tree					= MCSolverMP.Tree(board, isP1)	# 검색용 트리 생성
		tree.weightedSearchProb	= self.weightedSearchProb
		tree.trycount			= self.trycount

		#tree.startSearch()										# 계산 시작 (Single Threaded)

		##### multi threaded #####
		for phase in range(self.phasecount):					# 페이즈 횟수만큼 반복
			print('phase start : ', phase + 1)
			processlist		= []
			pipesendlist	= []
			piperecvlist	= []
			for tidx in range(self.threadcount):				# 쓰레드 수 만큼 반복
				p_child_recv, p_parent_send = multiprocessing.Pipe(duplex=False)
				p_parent_recv, p_child_send = multiprocessing.Pipe(duplex=False)

				p		= multiprocessing.Process(target=self._tree_process, args=(board, isP1, self.weightedSearchProb, self.trycount, p_child_send, p_child_recv,))
				p.start()
				processlist.append(p)
				pipesendlist.append(p_parent_send)
				piperecvlist.append(p_parent_recv)

			alivecount = self.threadcount
			while alivecount > 0:									# 파이프라인 메세지 처리 루프
				for i in range(self.threadcount):
					p = processlist[i]
					if p.is_alive():								# 살아있는 프로세스만 처리 (join된 건 스킵)
						piperecv = piperecvlist[i]
						#if piperecv.poll():							# 데이터가 있을 때만 처리
						recv = piperecv.recv()
						send = tree.processPipe(recv)
						if send == 'iterover':
							p.join()
							alivecount -= 1
						else:
							if send != _PROT_noreturn:
								pipesendlist[i].send(send)


		placelist	= []
		for x in range(_WIDTH):									# 트리의 루트에서 각 x좌표마다 자식 노드가 있는지 검색해본다
			xkey	= 1 * _WIDTH + x
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


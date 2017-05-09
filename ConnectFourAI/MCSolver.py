# -*- coding: utf-8 -*-


import connect4
import random
import multiprocessing
import array
import math
import time

random.seed()

_WIDTH	= connect4.Judge.BOARD_WIDTH
_HEIGHT	= connect4.Judge.BOARD_HEIGHT
_MOVETYPE_PLAYER1 = connect4.Judge.Move.MOVETYPE_PLAYER1


# Monte Carlo 방법을 쓰는 Solver
class MCSolver(connect4.BaseSolver):
	class Board:
		__slots__ = ['board']
		_emptyboard = [0 for x in range(_WIDTH * _HEIGHT + 1)]	# NOTE : 맨 마지막 원소는 지금까지 몇수나 뒀는지 나타냄
		_countIdx = _WIDTH * _HEIGHT

		def __init__(self, origboard=None):
			if origboard:	# 원본 보드가 지정되었으면 복제
				self.board = array.array('b', origboard.board)
			else:
				self.board = array.array('b', MCSolver.Board._emptyboard)

		def positionToIndex(self, x, y):
			return y * _WIDTH + x

		def copyFromJudge(self, judge):
			count = 0
			for y in range(_HEIGHT):
				for x in range(_WIDTH):
					move = judge.getMoveOnBoard(x, y)
					if move:
						self.board[self.positionToIndex(x, y)] = 1 if move.type == _MOVETYPE_PLAYER1 else 2
						count += 1
			self.board[MCSolver.Board._countIdx] = count

		def boundaryCheck(self, x, y):
			return 0 <= x < _WIDTH and 0 <= y < _HEIGHT

		def canPlace(self, x, y):
			return self.boundaryCheck(x, y) and self.board[self.positionToIndex(x, y)] == 0

		def placeAndCheck(self, x, y, moveType):
			moveType = 1 if moveType == True else 2
			self.board[self.positionToIndex(x, y)] = moveType
			self.board[MCSolver.Board._countIdx] += 1

			return self._samerowcheck(moveType, x, y, 1, 0) + self._samerowcheck(moveType, x, y, -1, 0) >= 3 or \
					self._samerowcheck(moveType, x, y, 1, 1) + self._samerowcheck(moveType, x, y, -1, -1) >= 3 or \
					self._samerowcheck(moveType, x, y, 1, -1) + self._samerowcheck(moveType, x, y, -1, 1) >= 3 or \
					self._samerowcheck(moveType, x, y, 0, -1) >= 3

		def boardFull(self):
			return self.board[MCSolver.Board._countIdx] == _WIDTH * _HEIGHT

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
			__slots__ = ['parent', 'board', 'key', 'p1count', 'p2count', 'x', 'y', 'finisherIsP1']

			def __init__(self, parent=None, copyFrom=None):
				if copyFrom:			# 다른 노드의 복제본을 만드는 경우. (Tree끼리 합성할 때)

					self.parent		= None	# 복제하는 경우엔 별도 과정을 통해서 parent를 지정한다.
					self.board		= MCSolver.Board(copyFrom.board)
					self.key		= copyFrom.key
					self.p1count	= copyFrom.p1count
					self.p2count	= copyFrom.p2count
					self.x			= copyFrom.x
					self.y			= copyFrom.y
					self.finisherIsP1 = copyFrom.finisherIsP1

				else:					# 새로 노드를 만들거나, parent 지정하는 경우 (검색중)

					# parent 노드의 보드를 복제한다. 수를 두지는 않음.
					self.parent		= parent
					if parent:
						self.board	= MCSolver.Board(parent.board)

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
					self.finisherIsP1	= None

			# 승부가 났으면 True 아니면 False
			def place(self, x, y, isP1, starterIsP1):
				# note : canPlace 체크는 바깥에서 해야한다.
				self.x = x
				self.y = y

				if self.board.placeAndCheck(x, y, isP1):
					self.finisherIsP1	= isP1
					self.propagateWinCount(starterIsP1)
					return True
				return False

			# 부모 노드까지 거슬러올라가면서 승리 카운트
			def propagateWinCount(self, starterIsP1):
				node = self

				if self.finisherIsP1:
					while node:
						node.p1count += 2
						node = node.parent
				else:
					while node:
						node.p2count += 2
						node = node.parent
			
			# 부모 노드까지 거슬러올라가면서 '무승부' 카운트
			def propagateDrawCount(self, starterIsP1):
				node = self

				while node:
					node.p1count += 1
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



		def __init__(self, rootBoard = None, isP1Turn = None, originalTreeList = None):

			if originalTreeList is None:		# 일반 트리 생성
				self.root		= MCSolver.Tree.Node()
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
							node	= MCSolver.Tree.Node(copyFrom=origDict[key])
							nodeDict[key] = node

				for key in nodeDict:						# 현재 딕셔너리에서 키 하나씩 가져오기
					node	= nodeDict[key]
					node.findParentFromNodeDict(nodeDict)	# 각 노드마다 parent 찾아서 설정하기

				self.root	= nodeDict[1]					# root 노드 세팅하기
				


		def startSearch(self):
			#print('weightedSearchProb : {}, trycount : {}'.format(self.weightedSearchProb, self.trycount))

			# 최적화 위한 local cacheing
			width			= _WIDTH
			height			= _HEIGHT
			indexes			= [x for x in range(width)]
			shuffledIdx		= [x for x in range(width)]
			random_random	= random.random
			random_shuffle	= random.shuffle
			random_choices	= random.choices
			nodeDict		= self.nodeDict
			weightedSearchProb	= self.weightedSearchProb
			starterIsP1		= self.isP1Turn
			forceEqualWeight= weightedSearchProb == 0
			##############################

			exhaustedKey = set()  # 검색을 끝낸 key 목록

			for trycount in range(self.trycount):						# 지정한 횟수만큼 탐색을 반복한다.
				node			= self.root
				currentP1Turn	= starterIsP1
				searchLimit		= 0

				useExpansionSearch = random_random() < 0.3				# 일정 확률로 이미 탐색한 노드를 피해서 검색하는 방법을 쓴다.

				while node:												# 다음에 검색할 노드가 없을 때까지 반복
					if searchLimit > 100:								# 지나치게 오래 검색하는 상황을 방지. 현재는 아주 드물게 발생한다.
						print('node search limit reached!')
						break
					searchLimit += 1

					nextNode	= None
					shouldBreak	= False		# 조건에 맞는 노드를 찾아 처리해서 검색을 종료하는 경우 올리는 플래그.
					forceExhaustX = False	# 강제로 x좌표 리스트를 전부 사용한 것처럼 취급, shouldBreak하고는 사용처가 다름
					xlist		= None

					# cacheing
					node_createNextKey	= node.createNextKey

					# *** 일정 확률로 동일하게 랜덤으로 찾는다. 단 착수자 차례일 때만...
					if forceEqualWeight or starterIsP1 == currentP1Turn and random_random() >= weightedSearchProb:
						random_shuffle(shuffledIdx)
						xlist	= shuffledIdx

					else:	# *** 나머지 확률로 weight를 따진다.
						xweight	= [0 for x in range(width)]
						wsign	= 1 if currentP1Turn else -1

						# 승리 횟수로 weight 계산
						for x in range(width):
							newKey		= node_createNextKey(x)
							try:
								pick	= nodeDict[newKey]
								# p1차례면 p1에게 유리한 쪽으로, p2차례면 p2에게 유리한 쪽으로 weight를 준다. (wsign)
								p1c = pick.p1count
								p2c = pick.p2count
								w = (p1c - p2c) * wsign
								xweight[x] = w
							except KeyError:
								pass

						minw	= min(xweight) - 1	# weight 최소값이 1이 되도록 맞춰준다. (0, 음수값 weight 방지)
						for x in range(width):
							w = xweight[x]
							w -= minw
							xweight[x] = w ** 2

						xlist	= []
						for i in range(width):
							pick	= random_choices(indexes, xweight)[0]
							xweight[pick] = 0		# 이미 뽑은 건 weight를 0으로 둬서 픽되지 않게 한다
							xlist.append(pick)


					# x좌표 후보 리스트에서 하나씩 뽑는다.
					for x in xlist:
						if nextNode:											# 다음 턴을 진행할 노드를 찾았다면 x좌표 찾는 루프를 빠져나온다.
							break
						if shouldBreak:											# 루프를 깨야하는 경우 (적합한 노드를 찾아 승점 평가를 한 경우)
							break
						if forceExhaustX:										# 루프를 깨야하는 경우 (확장검색 중 x좌표 리스트를 모두 쓴 것처럼 취급해야 할 때)
							break

						newKey = node_createNextKey(x)  # key 생성 (x 좌표만으로 구성된 sequence)

						for y in range(height):									# y좌표를 올라가면서 착수점을 찾는다.
							if node.board.canPlace(x, y):						# 둘 수 있는 곳을 찾았으면

								try:
									cached	= nodeDict[newKey]					# 같은 키를 지닌 수가 이미 있다면 가져온다.

									if cached.finisherIsP1 is not None:			# 승패가 난 노드면, 다시 승리 카운트를 한다.
										cached.propagateWinCount(starterIsP1)

										if not useExpansionSearch or (currentP1Turn != starterIsP1):	# 확장검색이 아니거나 상대방 턴일 경우 x좌표를 새로 찾지 않고 다음 회차로
											shouldBreak = True
										else:									# 착수자 턴이면 x검색을 취소하고 상위 노드로 되돌아간다.
											forceExhaustX = True

									elif cached.board.boardFull():				# 혹은, 보드가 꽉찬 경우엔 다시 한 번 비김 처리
										cached.propagateDrawCount(starterIsP1)

										if not useExpansionSearch or (currentP1Turn != starterIsP1):	# 확장검색이 아니거나 상대방 턴일 경우 x좌표를 새로 찾지 않고 다음 회차로
											shouldBreak = True
										else:									# 착수자 턴이면 x검색을 취소하고 상위 노드로 되돌아간다.
											forceExhaustX = True

									else:
										# 확장검색이면서 exhaustedKey인 경우가 아니거나 현재 상대방 턴일 경우, 이 노드로 계속 검색한다.
										if (not (useExpansionSearch and (newKey in exhaustedKey))) or (currentP1Turn != starterIsP1):
											nextNode = cached
										# 그 외의 경우, 다음 x 좌표를 찾게 둔다.

									# 이외의 경우엔 (내 턴이면서 해당 x좌표로는 검색을 끝낸 경우) 그냥 다른 x좌표를 검색한다.

								except KeyError:								# 새로운 수일 경우, 새로 노드를 만들어야함
									newNode					= MCSolver.Tree.Node(node)
									newNode.key				= newKey
									nodeDict[newKey]		= newNode			# dictionary에 노드 등록

									if not newNode.place(x, y, currentP1Turn, starterIsP1):	# 두었는데 승부가 나지 않았다면...
										if newNode.board.boardFull():			# 만약 비긴 경우엔(보드꽉참) 비김 체크, 다음 회차로.
											newNode.propagateDrawCount(starterIsP1)
											shouldBreak		= True
											exhaustedKey.add(newKey)			# 이 노드는 다음엔 검색하지 않아야 함
										else:									# 그 외의 경우엔 (게임 안끝남) 검색 계속
											nextNode		= newNode
									else:										# 승부가 난 경우
										shouldBreak			= True				# x좌표를 새로 찾을 필요 없음. 다음 회차로 넘어가도록 한다
										exhaustedKey.add(newKey)				# 이 노드는 다음엔 검색하지 않아야 함

								break											# x,y좌표를 찾은 뒤에는 위쪽 y좌표를 찾는 게 무의미함


					if useExpansionSearch and (not shouldBreak and nextNode is None):	# 확장검색 사용시, x좌표 후보중에서 적합한 노드를 전혀 찾지 못했다면,
						if currentP1Turn == starterIsP1:						# 내 턴일 경우, 현재 노드는 exhausted 상태로 바꾼다. (다음 회차에 검색할 게 없으므로)
							exhaustedKey.add(node.key)

							if node.parent is not None:							# parent가 존재하면
								nextNode = node.parent.parent					# parent의 parent로 돌아간다. (적 턴을 건너뛴다)

								# FIX : 더이상 탐색 못하는 node에 도달했을 때 parent.parent로 되돌아가서도 같은 선택을 하지 못하도록, 부모 노드도 exhausted 표시를 한다.
								exhaustedKey.add(node.parent.key)
							else:												# 아닌 경우는 다음 검색 노드를 지정하지 않는다 (root 도달)
								nextNode = None
							# 아군 -> 아군 턴으로 건너뛰므로 currentP1Turn 플래그 반전은 하지 않는다.

						else:													# 상대방 턴일 경우,
							nextNode = node.parent								# parent노드로 돌아간다. (내 턴이 된다.)
							currentP1Turn = starterIsP1

						# NOTE : parent가 None인 경우(root인 경우)엔 조건에 따라서 알아서 루프를 끝낸다.

					else:														# 그외 일반적인 경우 (확장검색이 아니거나 적합한 노드를 찾았거나 x검색 끝내는 경우)
						currentP1Turn = not currentP1Turn						# 다음 노드를 정했다면 턴이 넘어가는 상황이므로 플래그 반전

					node			= nextNode									# 위에서 찾은 "다음 노드"를 사용 (None일 수도 있으며 이때는 iteration 1회차 끝)



	def __init__(self, name, weightedSearchProb = 0.9, trycount = 10000, threadcount = 4, initialtrycount = 5000):
		super().__init__(name)
		self.weightedSearchProb	= weightedSearchProb			# 비중에 따른 서치를 얼마만큼 비율로 할지
		self.trycount			= trycount						# 탐색 횟수
		self.threadcount		= threadcount					# 쓰레드 수
		self.initialtrycount	= initialtrycount				# 1차 트리 계산시 시행 횟수

	def _genSummaryFromNodes(self, nodes):
		validnode	= None
		p1c		= 0
		p2c		= 0
		vncount	= 0
		for node in nodes:			# Node들을 하나로 합성한다.
			if node:
				vncount += 1
				validnode = node
				p1c += node.p1count
				p2c += node.p2count

		if vncount > 0:
			p1c = p1c // vncount	# 숫자가 너무 커지는 것을 방지한다.
			p2c = p2c // vncount

		csum	= max(1, p1c + p2c)
		resultdict = {'key':validnode.key, 'x': validnode.x, 'y': validnode.y, 'p1prob': p1c / csum, 'p2prob': p2c / csum, 'p1count':p1c, 'p2count':p2c}

		return resultdict

	def _genSummaryFromTree(self, tree):
		resultlist = []
		for x in range(_WIDTH):  # x좌표 리스트를 뽑아본다
			xkey = 1 * _WIDTH + x
			if xkey in tree.nodeDict:
				node = tree.nodeDict[xkey]
				summary = self._genSummaryFromNodes((node,))
				resultlist.append(summary)

		return resultlist

	def _genSummaryFromNodeListList(self, nodell):
		resultlist = []
		for x in range(_WIDTH):			# 같은 x좌표에 있는 것들끼리 모으기 위해서...
			nodes = []
			for l in nodell:
				node = l[x]
				if node:				# None이 아닌 것들만 nodes 리스트에 넣는다
					nodes.append(node)
			
			if len(nodes) > 0:
				summary = self._genSummaryFromNodes(nodes)
				resultlist.append(summary)

		return resultlist

	def _genSummaryFromProcessNodeList(self, nodelist):
		tempdict = {}
		for node in nodelist:	# nodelist에서 같은 key값을 갖는 node들의 list를 key값으로 매칭한 딕셔너리를 만든다.
			if node.key in tempdict:
				tempdict[node.key].append(node)
			else:
				tempdict[node.key] = [node]

		resultlist = []
		for key in tempdict:
			nodelist = tempdict[key]
			resultlist.append(self._genSummaryFromNodes(nodelist))	# 각 같은 키값의 노드들을 하나로 합성한다.

		return resultlist

	def nextMove(self, judge):
		startTime	= time.time()

		isP1	= judge.nextTurnIsP1()										# 검색을 시작하는 시점에서 누구 턴인지 판단
		board	= MCSolver.Board()											# 보드 생성 (현재 보드 상태를 복제해온다)
		board.copyFromJudge(judge)

		tree					= MCSolver.Tree(board, isP1)				# 검색용 트리 생성
		nodelist				= None

		if self.threadcount == 1:											# single threaded
			tree.weightedSearchProb = self.weightedSearchProb
			tree.trycount = self.trycount
			tree.startSearch()  # 계산 시작 (Single Threaded)

		else:																# multithreaded
			tree.weightedSearchProb	= 0
			tree.trycount			= self.initialtrycount
			print('phase 1 start')
			tree.startSearch()												# 계산 시작 (Single Threaded) - 초벌 서치?

			# 미리 계산한 결과를 토대로 각 트리마다 분할 search을 시킬 준비를 한다.
			xlist = self._genSummaryFromTree(tree)							# level-1 노드 summary 긁어오기
			xlist.sort(key=lambda item: item['p1prob'], reverse=not isP1)	# 현재 턴에 맞는 승률 낮은 쪽으로 정렬
			xgroupelemc = math.ceil(len(xlist) / self.threadcount)			# 각 x좌표 그룹마다 몇개씩 나눠넣어야할지

			# 각 분할 search마다 주목해야할 x좌표 그룹 리스트
			xgroup = [[d['x'] for d in xlist[i * xgroupelemc : (i + 1) * xgroupelemc]] for i in range(self.threadcount)]



			##### multi threaded #####
			print('phase 2 start')
			processlist	= []
			pipelist	= []
			nodelist	= []

			tree.weightedSearchProb = self.weightedSearchProb
			tree.trycount = self.trycount

			for tidx in range(self.threadcount):				# 쓰레드 수 만큼 반복
				p_parent, p_child = multiprocessing.Pipe()
				p		= multiprocessing.Process(target=_tree_process, args=(tree, p_child, xgroup[tidx], ))
				p.start()
				processlist.append(p)
				pipelist.append(p_parent)

			tree = None

			for i in range(self.threadcount):					# 각 프로세스에서 1차 결과 받아오기
				nodelist += pipelist[i].recv()

			tempsumlist = None
			chistory = [1.0]

			print('extra phase (3 ~ ) start')

			for phase in range(3, 30):
				if time.time() - startTime >= 90:							# 추가 페이즈 실행중에 90초(1분 30초) 넘어가면 루프 종료
					break

				oldtsumlist = None
				if tempsumlist:												# 이전 중간결과가 있다면 백업
					oldtsumlist = tempsumlist

				tempsumlist = self._genSummaryFromProcessNodeList(nodelist)  # 중간 결과 수집

				# TEST : level-1 노드의 승률 추적
				tmpdict = {}
				for sum in tempsumlist:
					key = sum['key']
					if key // _WIDTH == 1:
						tmpdict[key] = sum
				tpstr = ''
				for x in range(_WIDTH):
					key = 1 * _WIDTH + x
					if key in tmpdict:
						ppair = tmpdict[key]
						tpstr += '({0:.3f}/{1:.3f}) '.format(ppair['p1prob'], ppair['p2prob'])
					else:
						tpstr += '(None) '
				print(tpstr)
				#####################################

				if oldtsumlist:												# 이전 중간결과와 비교
					sumpairdict = {}
					for oldsum in oldtsumlist:
						key = oldsum['key']
						if key // _WIDTH == 1:	# level-1만 취급
							sumpairdict[oldsum['key']] = [oldsum, None]

					for newsum in tempsumlist:
						key = newsum['key']
						if key in sumpairdict:
							sumpairdict[key][1] = newsum

					changes = []
					for key in sumpairdict:
						pair = sumpairdict[key]
						old = pair[0]
						new = pair[1]
						if old and new:
							changes.append(math.fabs(old['p1prob'] - new['p1prob']))

					changecnt = len(changes)
					if changecnt > 0:
						sum = 0
						for c in changes:
							sum += c
						avg = sum / changecnt
						print('(평균 승률 변화 P : {})'.format(avg))

						chistory.append(avg)
						'''
						if max(chistory[-2:]) < 0.001:	# 마지막 두 변화률이 일정 수치 이하면 안정화된 것으로 본다
							print('승률 안정화된 것으로 추정, 계산 종료')
							break
						'''

				for i in range(self.threadcount):							# 중간 결과를 다시 각 프로세스로 보내기
					pipelist[i].send(tempsumlist)

				nodelist = []
				for i in range(self.threadcount):							# 결과 받아오기
					nodelist += pipelist[i].recv()


			for i in range(self.threadcount):								# 종료하기
				pipelist[i].send('halt')									# 메세지 보내기
				processlist[i].join()										# 프로세스 종료 대기

			processlist = None
			queuelist	= None

			print('synthesizing results from each processes...')


		placelist	= []
		if self.threadcount == 1:
			placelist	= self._genSummaryFromTree(tree)
		else:
			tempsumlist = self._genSummaryFromProcessNodeList(nodelist)
			tempdict = {}
			for sum in tempsumlist:				# summary 리스트에서 1level 노드 것들만 뽑아온다
				if sum['key'] // _WIDTH == 1:
					tempdict[sum['x']] = sum

			for x in range(_WIDTH):				# 1차원 리스트에 인덱스=x좌표값 형태로 정렬한다.
				try:
					sum = tempdict[x]
					placelist.append(sum)
				except KeyError:
					pass
			

		for summary in placelist:
			if summary:
				print('({},{}) - p1c : {}, p2c : {}'.format(summary['x'], summary['y'], summary['p1prob'], summary['p2prob']))

		placelist.sort(key=lambda item:item['p1prob'], reverse=isP1)	# 현재 턴에 맞는 승률 높은 쪽으로 정렬
		choosen	= placelist[0]

		return choosen['x'], choosen['y'], 'MCsearch'




############ multiprocessing용 코드 #####################################

def _tree_process(treeOriginal, pipe, accentXList = []):
	tree = MCSolver.Tree(originalTreeList=[treeOriginal])  # 트리 복제하기
	treeOriginal = None

	##### phase 2 #####

	_tree_accenting(tree, accentXList, tree.trycount * 1)	# 지정한 X좌표에 충분히 포인트를 줘서 이쪽을 주로 search하도록...
	tree.startSearch()										# 검색 시작
	_tree_accenting(tree, accentXList, -tree.trycount * 1)  # 포인트 다시 원상복구

	pipe.send(_tree_extranodelist(tree))					# 트리 노드들 보내기

	##### phase 3~ #####

	tree.trycount	= 4000		# 작은 단위로 계속 반복한다

	while True:
		sums = pipe.recv()
		if sums == 'halt':		# 종료 메세지를 받았으면 루프 깨기
			break

		for sum in sums:		# 아니면 전달받은 정보를 트리에 적용해야한다
			key = sum['key']
			try:
				# 받아온 중간 결과를 각 노드에 직접 대입 (각 승리 횟수)
				node = tree.nodeDict[key]
				node.p1count = sum['p1count']
				node.p2count = sum['p2count']
			except KeyError:
				pass

		sums =  None
		tree.startSearch()  # 다시 검색 시작

		pipe.send(_tree_extranodelist(tree))					# 트리 노드들 보내기


def _tree_accenting(tree, accentXList, amount):
	for x in accentXList:		# 강조할 X 좌표 설정하기
		nextKey = tree.root.createNextKey(x)
		node = tree.nodeDict[nextKey]
		if node:
			if tree.isP1Turn:
				node.p1count += amount
			else:
				node.p2count += amount
			#print('accenting {} - {}/{}'.format(x, node.p1count, node.p2count))

def _tree_lv1nodelist(tree):
	childs = []
	for x in range(_WIDTH):
		key = 1 * _WIDTH + x
		node = None
		try:
			node = tree.nodeDict[key]
		except KeyError:
			pass
		childs.append(node)

	return childs

def _tree_extranodelist(tree, iter = 4):
	nodelist = []
	_tree_extranodelist_iter(tree, nodelist, 1, iter)
	return nodelist

def _tree_extranodelist_iter(tree, nodelist, prevkey, iter):
	for x in range(_WIDTH):
		key = prevkey * _WIDTH + x

		try:
			node = tree.nodeDict[key]
			nodelist.append(node)
		except KeyError:
			pass

		if iter > 1:
			_tree_extranodelist_iter(tree, nodelist, key, iter - 1)
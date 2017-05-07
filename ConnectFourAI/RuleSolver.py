# -*- coding: utf-8 -*-
## 위의 코드는 Python 3.X 버전에서 한글을 표시할 수 있도록 하기 위한 설정입니다.

## 아래 코드는 일부 수정되었습니다. 서지민이 추가한 주석은 이와 같이 ##으로 시작합니다.
## 코드의 좌측에 붙은 주석은 # 하나만 사용하였습니다.

## 2017-05-06-23:00 Rule 1 ~ 9까지 구현 완료
## 2017-05-06-23:45 Rule 5, 6, 7에 대해 추가 조항 만듦: 해당 칸 위에 3, 4, 5가 있는 경우 놓지 않는다.
## 2017-05-07-01:00 Rule 3, 6에 대해 추가 조항 만듦: 위 방향으로도 확인한다.(이전까지는 아래로만 확인)


import connect4


class RuleSolver(connect4.BaseSolver):

    def __init__(self, name, player=None):

        super().__init__(name)
        ## 아래의 코드는 다음의 행렬을 구성하기 위한 코드입니다.
        ## | [-1, 7]  [0, 7]  [1, 7]  ...
        ## | [-1, 6]  [0, 6]  [1, 6]  ...
        ## | [-1, 5]  [0, 5]  [1, 5]  ...

#        self.moveType = 1 if judge.nextTurnIsP1() else 2
        self.moveType = player
        self.foeMoveType = None if player == None else 3 - player # 상대의 수를 기준으로 판단한다.

        self.BOARD_WIDTH = connect4.Judge.BOARD_WIDTH
        self.BOARD_HEIGHT = connect4.Judge.BOARD_HEIGHT


    ## 아래는 각각 Rule을 먼저 찾아내는 부분입니다. 그 번호가 작을 수록 우선순위가 부여됩니다.
    ## self.checkType을 이용하므로, 지금 있는 칸은 비어있어야 합니다; 여기서는 x, y에 둘때 어떤 결과가 나오는지 확인하기 위함입니다
    ## Rule 1은 3번 내의 수일 경우입니다.
    def Rule_1(self, judge):
        threshold = 6 if self.moveType == 1 else 2
        return 1 if (judge.getTurn() < threshold) else 9

    ## Rule 2는 이기는 수가 자신에게 있는 경우입니다.
    ## 이 경우 기존의 코드에서 가져왔습니다.
    def Rule_2(self, x, y, judge):
        return 2 if judge.checkNextMoveIsFinisher(x, y) else 9

    ## Rule 3는 수직으로 3개 이상 연속되는 수가 상대에게 있는 경우입니다.
    ## 어차피 맨 아래에 둘 수 없으므로 밑으로만 확인하게 됩니다.
    def Rule_3(self, x, y, judge):
        vert =  self.checkType(x, y-1, judge) and self.checkType(x, y-2, judge) and self.checkType(x, y-3, judge)
        diag_left = self.checkType(x-1, y-1, judge) and self.checkType(x-2, y-2, judge) and self.checkType(x-3, y-3, judge)
        diag_right = self.checkType(x+1, y-1, judge) and self.checkType(x+2, y-2, judge) and self.checkType(x+3, y-3, judge)

        diag_left_up = self.checkType(x+1, y+1, judge) and self.checkType(x+2, y+2, judge) and self.checkType(x+3, y+3, judge)
        diag_right_up = self.checkType(x-1, y+1, judge) and self.checkType(x-2, y+2, judge) and self.checkType(x-3, y+3, judge)
        return 3 if(vert or diag_left or diag_right or diag_left_up or diag_right_up) else 9

    ## Rule 4는 수평으로 3개 이상 연속되는 수가 상대에게 있는 경우입니다.
    def Rule_4(self, x, y, judge):
        horiz_left = self.checkType(x-3, y, judge) and self.checkType(x-2, y, judge) and self.checkType(x-1, y, judge)
        horiz_right= self.checkType(x+1, y, judge) and self.checkType(x+2, y, judge) and self.checkType(x+3, y, judge)

        ## 추가로, 두개가 있고 하나가 떨어진 경우에도 이에 해당합니다. 이는 다른 함수 Rule_4_5로 구성하였습니다.



        return 4 if (horiz_left or horiz_right or self.Rule_4_5(x, y, judge)) else 9

    def Rule_4_5(self, x, y, judge):
        horiz_left = self.checkType(x-1, y, judge) and self.checkType(x+1, y, judge) and self.checkType(x+2, y, judge)
        horiz_right = self.checkType(x-2, y, judge) and self.checkType(x-1 ,y, judge) and self.checkType(x+1, y, judge)

        diag_left = self.checkType(x-1, y-1, judge) and self.checkType(x+1, y+1, judge) and self.checkType(x+2 ,y+2, judge)
        diag_left_up = self.checkType(x-2, y-2, judge) and self.checkType(x-1, y-1, judge) and self.checkType(x+1, y+1, judge)

        diag_right = self.checkType(x+1, y-1, judge)  and self.checkType(x-1, y+1, judge) and self.checkType(x-2, y+2, judge)
        diag_right_up = self.checkType(x+2, y-2, judge) and self.checkType(x+1, y-1, judge) and self.checkType(x-1, y+1, judge)

        return horiz_left or horiz_right or diag_left or diag_right or diag_left_up or diag_right_up

    ## Rule 5는 상대의 수가 한칸 띄우고 연속적으로 있는 경우입니다.
    def Rule_5(self, x, y, judge):
        horiz = self.checkType(x-1, y, judge) and  self.checkType(x+1, y, judge)
        diag_left = self.checkType(x-1, y-1, judge) and self.checkType(x+1, y+1, judge)
        diag_right = self.checkType(x+1, y-1, judge) and self.checkType(x-1, y+1, judge)
        return 5 if (horiz or diag_left or diag_right) else 9

    ## Rule 6은 상대의 수가 수직으로 두 개 연속인 경우입니다.
    def Rule_6(self, x, y, judge):
        vert = self.checkType(x, y-1, judge) and  self.checkType(x, y-2, judge)
        diag_left = self.checkType(x-1, y-1, judge) and self.checkType(x-2, y-2, judge)
        diag_right = self.checkType(x+1, y-1, judge) and self.checkType(x+2, y-2, judge)

        diag_left_up = self.checkType(x-1, y+1, judge) and self.checkType(x-2, y+2, judge)  # 이 부분을 추가 하지 않으면 멀뚱멀뚱 보다가 지는 경우가 발생한다.
        diag_right_up = self.checkType(x+1, y+1, judge) and self.checkType(x+2, y+2, judge)
        return 6 if (vert or diag_left or diag_right or diag_left_up or diag_right_up) else 9

    ## Rule 7은 상대의 수가 수평으로 두 개 연속인 경우입니다.
    def Rule_7(self, x, y, judge):
        horiz_left = self.checkType(x+1, y, judge) and self.checkType(x+2, y, judge)
        horiz_right = self.checkType(x-1, y, judge) and self.checkType(x-2, y, judge)
        return 7 if (horiz_left or horiz_right) else 9

    ## Rule 8은 상대의 수 위로 두는 경우입니다. 위 모든 경우가 아닌 경우 해당되지만, 둘 수 없는 경우엔 랜덤으로 두어야 합니다.
    def Rule_8(self, x, y, judge):
        move = judge.getLastMove()
        x_foe = move.x
        y_foe = move.y

        return 8 if (x == x_foe and y == (y_foe+1)) else 9

    def getRuleNum(self, x, y, judge):

        rule1 = self.Rule_1(judge)
        rule2 = self.Rule_2(x, y, judge)
        rule3 = self.Rule_3(x, y, judge)
        rule4 = self.Rule_4(x, y, judge)
        rule5 = self.Rule_5(x, y, judge)
        rule6 = self.Rule_6(x, y, judge)
        rule7 = self.Rule_7(x, y, judge)
        rule8 = self.Rule_8(x, y, judge)

        return min(rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8)

    ## 아래의 메소드는 가능한 공간을 고려하지 않고 두는 방식이다.
    def nextMove(self, judge):

        if self.moveType == None:
            self.moveType = 1 if judge.nextTurnIsP1() else 2  # 처음에는 비어있으므로 처음에 둘 때만 확인한다.
            self.foeMoveType = 3 - self.moveType

        ## 아래의 점수판에서, 10은 기초 값을 의미합니다; None과 int값은 비교할 수 없기에 이 값을 넣었습니다.
        scoreboard = [[10 for j in range(self.BOARD_HEIGHT)] for i in range(self.BOARD_WIDTH)]
        ## 아래의 어디에 놓을 수 있을까, 하는 것에서는
        possiblePlaceOn  = [9 for i in range(self.BOARD_WIDTH)]

        ## Rule number들을 가져오는 과정
        for x in range(self.BOARD_WIDTH):
            buffer = [7]
            for y in range(self.BOARD_HEIGHT):
                move = judge.getMoveOnBoard(x, y)
                if move == None :  # 당초에는 judge.canPlaceOn을 썼지만, 이것은 그 밑 칸도 확인하므로 적절하지 않았다.
                    ## 비어있는 칸은 모두 둘 가능성이 있으므로, 비어있는 칸들을 확인해야 한다.
                    scoreboard[x][y] = self.getRuleNum(x, y, judge)
                    buffer.append(y)

            possiblePlaceOn[x] = min(buffer)  # 리스트 중 가장 작은 값으로 업데이트

        ## 아래의 메소드는 확인을 위해 Rule들의 값을 불러온다.
#        self.printScoreboard(scoreboard)
#        print('\nPossible Places\n {}  {}  {}  {}  {}  {}  {}' .format(possiblePlaceOn[0], possiblePlaceOn[1], possiblePlaceOn[2],
#                                                                possiblePlaceOn[3], possiblePlaceOn[4], possiblePlaceOn[5],
#                                                                possiblePlaceOn[6]))

        ## 위에서 얻은 scoreboard는 점수판으로, 룰 번호를 가져오게 된다.
        ## 다음으로 해야할 것은 룰 번호가 낮은 순서대로 둘 곳을 정하는 것이다.
        candidates = []

        for x in range(self.BOARD_WIDTH):
            if possiblePlaceOn[x] < 7:
                pnt = scoreboard[x][possiblePlaceOn[x]]
                pnt_above = scoreboard[x][possiblePlaceOn[x] + 1] if possiblePlaceOn[x] < 5 else 9
                candidates.append(9 if pnt in [5, 6, 7, 8] and pnt_above in [3, 4] else pnt )
            else:
                candidates.append(10)

#        print('\nCandidates\n {}  {}  {}  {}  {}  {}  {}' .format(candidates[0], candidates[1], candidates[2],
#                                                                candidates[3], candidates[4], candidates[5],
#                                                                candidates[6]))

        next_move_chosen  = candidates.index(min(candidates))

        if min(candidates) == 1:
            return 3, possiblePlaceOn[3], 'Rule 1 applied'
        elif min(candidates) == 10:
            return 0, 0, 'Nowhere to Place; End of game'

        message = 'Rule' + str(min(candidates)) +'적용'

        return next_move_chosen, possiblePlaceOn[next_move_chosen], message



    ## 여기서 칸을 넘어가는 경우에는 에러가 뜰 수 있으므로, 애초에 칸이 인덱스를 벗어나면 제외한다.
    def checkType(self, x, y, judge):
        move = judge.getMoveOnBoard(x, y)
        if (0 <= x < self.BOARD_WIDTH) and (0 <= y < self.BOARD_HEIGHT) and move != None:
            return move.type == self.foeMoveType
        else:
            return False


    def printScoreboard(self, scoreboard):

        for y in range(self.BOARD_HEIGHT-1, -1, -1):
            print('{} {} {} {} {} {} {}' .format(scoreboard[0][y],scoreboard[1][y],scoreboard[2][y],scoreboard[3][y],scoreboard[4][y],scoreboard[5][y],scoreboard[6][y]))

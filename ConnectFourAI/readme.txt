Solver를 구현할 때 알아야 할 주요 클래스는 Judge.Interface와 Judge.Move가 있습니다.


* Judge.Interface 멤버

boundaryCheck(x, y) : x, y 좌표가 보드 영역을 벗어나는지 체크합니다. boolean 리턴

hasMoveOn(x, y) : 해당 x, y 좌표에 수를 뒀는지 확인합니다. 리턴값이 True면 이미 둔 수가 있는 것.

canPlaceOn(x, y) : 해당 x, y 좌표에 새로 착수 가능한지 확인합니다. boolean 리턴.

getMoveOnBoard(x, y) : 해당 위치에 있는 착수점 데이터를 가져옵니다. Judge.Move 인스턴스 혹은 None (해당 위치에 착수하지 않았을 때) 을 리턴.

getLastMove() : 가장 마지막에 둔 수를 리턴합니다. Judge.Move 인스턴스 혹은 None 리턴

getTurn() : 현재 턴 수를 구합니다. (정수값) 유의할 점은, 현재 두어야 할 차례가 아니라 가장 마지막에 착수한 턴 수를 구한다는 것입니다. 따라서 아무도 수를 두지 않은 상태에서는 0턴이고, 플레이어 1이 착수한 뒤에는 1턴이 됩니다.

nextTurnIsP1() : 바로 이번에 플레이어 1이 수를 둘 차례인지 구합니다. True를 리턴하면 이번에 플레이어 1이 둘 차례, False면 플레이어 2가 둘 차례입니다.

checkNextMoveIsFinisher() : 해당 위치에 수를 놓으면 게임이 끝나는지 여부를 구합니다. 실제로 보드에 수를 두지는 않습니다.



* Judge.Move 멤버

멤버 메서드 없이 필드만 존재하는 클래스입니다.

x : x 좌표값. 0부터 시작합니다.
y : y 좌표값. 0부터 시작합니다.
type : 착수 종류. Judge.Move.MOVETYPE_PLAYER1 (=1) 이면 플레이어 1이 둔 수, Judge.Move.MOVETYPE_PLAYER2 (=2) 면 플레이어 2가 둔 수입니다.
turn : 해당 수를 놓았을 때의 턴 수입니다.



Solver를 구현할 때는 우선 connect4 모듈을 임포트하고, BaseSolver 클래스를 상속하여 구현합니다.

nextMove(judge) 메서드를 오버라이드해서 로직 구현을 하면 됩니다. judge 파라미터로는 Judge.Interface 인스턴스가 전달되며, 각 턴에서의 판 상태를 이 오브젝트를 통해 확인할 수 있습니다. 리턴값으로는 착수 지점 x좌표, y좌표, 그리고 메세지를 넘겨주면 됩니다.


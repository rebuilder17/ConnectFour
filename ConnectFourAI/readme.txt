** 요구 사항 **

Python 3.6 환경에서 구동 가능합니다. Windows 64bit 환경에서 개발하고 테스트하였으며, 32bit python 인터프리터에서도 동작은 가능할 것으로 예상하나 정상 작동을 보장하지는 않습니다.

Intel 2~3세대 이상, 최소 4개의 물리 코어를 탑재한 프로세서를 장착한 PC에서 구동할 것을 권장합니다. Laptop에서도 구동 가능하나 Full performance를 낼 수 있도록 전원 공급을 해줘야 합니다.

RAM 여유공간은 적어도 2~3GB 정도 확보한 상태에서 구동하기를 권장합니다.




** 실행 방법에 관해서 **

CUI 버전은 main_cui.py 를 실행하면 됩니다. main.py는 GUI와 통신을 위한 코드이므로 실행은 가능해도 정상적인 CUI로 동작하지는 않습니다.

GUI는 별도로 포함한 패키지를 참고해주세요.




** GUI와 연동 방법 **

GUI와 컴파일한 Python 코드끼리 IPC를 통해 통신하는 구조이므로, 이를 위해서는 GUI의 특정 경로에 실행 파일을 복사해넣어야만 합니다.

GUI의 내부 데이터 폴더 중 StreamingAssets 폴더에 cx_Freeze로 컴파일한 코드를 복사하면 됩니다.
(이미 GUI 패키지에 미리 컴파일된 python 코드가 포함되어있으므로, 단순히 실행해보는 것이 목적이라면 굳이 새로 컴파일할 필요는 없습니다.)

cx_Freeze는 Python 내부의 pip 스크립트를 통해 다운로드, 설치할 수 있습니다.

cx_Freeze 설치 후 Python36 인터프리터의 파라미터로 "setup.py build" 커맨드를 입력하여 실행하면 실행파일 패키지를 컴파일합니다.

GUI가 Windows 64bit 환경을 타겟으로 컴파일되었으므로 cx_Freeze 역시 해당 환경에서 실행하여 컴파일해야 합니다.








** Solver 구현에 관해서 **

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


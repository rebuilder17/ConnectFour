using UnityEngine;
using System.Collections;

public class Engine : MonoBehaviour
{
	// Constants

	const int				c_solverIndex_Human		= 0;
	const int				c_solverIndex_Search	= 1;
	const int				c_solverIndex_Rule		= 2;

	// Properties

	[SerializeField]
	GameStateController		m_gameStateCtrl;


	// Members

	GameState				m_gameState;
	
	/// <summary>
	/// 내부 스테이트
	/// </summary>
	enum State
	{
		Ready,					// 게임 시작 전 (모드 선택 등)
		Playing,				// 게임 진행중
		Solving,				// 솔버 응답 기다리는중
		GameOver,				// 게임 종료, 다시 시작하거나 복기할 수 있음
	}

	State			m_state;

	enum PlayerType
	{
		Selectable,				// 매턴 선택한다.
		Human,					// 항상 사람이 착수한다.
		AI,						// 항상 AI가 착수한다.
	}

	PlayerType		m_player1Type;
	PlayerType		m_player2Type;




	
	private void Awake()
	{
		m_state			= State.Ready;


	}

	private IEnumerator Start()
	{
		yield return null;

		// TEST
		m_player1Type	= PlayerType.Human;
		m_player2Type	= PlayerType.Human;
		

		// 게임 초기화

		m_gameState		= new GameState();
		m_gameState.newMovePlaced += OnNewMove;
		m_gameState.statusReport += OnGameStatusReport;

		m_gameStateCtrl.MakeNewConnection(m_gameState);

		// 바로 턴 시작 - ready 과정 스킵
		StartTurn();
	}

	/// <summary>
	/// 현재 턴 시작. 사용자 입력을 기다리거나 등등등을 처리한다.
	/// </summary>
	void StartTurn()
	{
		m_state				= State.Playing;			// 상태 세팅
		
		var nextPlayer		= m_gameState.nextPlayer;
		var nextPlayType	= nextPlayer == GameState.PlayerTurn.One? m_player1Type : m_player2Type;

		switch(nextPlayType)							// 플레이 타입에 따라서 적절한 UI/게임 상태 세팅
		{
			case PlayerType.Human:						// 사람이 착수해야 하는 경우, 입력 UI 표시
				SetForHumanInput();
				break;
		}
	}

	/// <summary>
	/// 사람 입력용 상태로 세팅
	/// </summary>
	void SetForHumanInput()
	{
		StartCoroutine(co_setForHumanInput());
	}

	IEnumerator co_setForHumanInput()
	{
		if (!m_gameStateCtrl.waitingForInput)					// 입력 기다리는 상태가 될 때까지 대기한다
			yield return null;

		m_gameStateCtrl.InputSolverIndex(c_solverIndex_Human);	// 사람 입력을 받는 걸로 모듈쪽에 전송

		var ui				= OverlayUI.instance;
		ui.boardUI.ShowInputs(m_gameState.lastBoardSnapshot, OnMoveInput);	// 입력 UI 표시
	}

	/// <summary>
	/// 착수점 입력 들어왔을 때 호출
	/// </summary>
	/// <param name="x"></param>
	void OnMoveInput(int x)
	{
		var board	= m_gameState.lastBoardSnapshot;
		var y		= 0;
		if (board != null)									// 첫째판이 아니라면 해당 X좌표에서 착수 가능한 Y지점을 찾는다
		{
			while (y < GameState.c_boardHeight && board.GetMove(x, y) != null)
				y++;
		}

		StartCoroutine(co_sendMovePosition(x, y));
	}

	IEnumerator co_sendMovePosition(int x, int y)
	{
		if (!m_gameStateCtrl.waitingForInput)				// 입력 기다리는 상태가 될 때까지 대기한다
			yield return null;

		m_gameStateCtrl.InputMovePosition(x, y);			// 찾은 좌표를 모듈 쪽으로 보낸다.

		m_state = State.Solving;							// 솔버 응답 기다리는 상태로 (거의 즉시 답이 돌아오겠지만...)
	}

	/// <summary>
	/// 게임 내에서 착수가 발생했을 때
	/// </summary>
	/// <param name="snapshot"></param>
	void OnNewMove(GameState.IBoardSnapshot snapshot)
	{
		OverlayUI.instance.boardUI.ShowNewMove(snapshot.lastMove);
	}

	/// <summary>
	/// 게임 내 상태값 리포트. 뭔가 동작이 끝났을 때마다 호출된다.
	/// </summary>
	/// <param name="gstatus"></param>
	void OnGameStatusReport(GameState.Status gstatus)
	{
		Debug.LogFormat("status report : {0}", gstatus);
		switch(gstatus)
		{
			case GameState.Status.Playing:			// 계속 진행
				StartTurn();						// 다음 턴 시작
				break;
		}
	}
}

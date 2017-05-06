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

	public enum PlayerType
	{
		Selectable,				// 매턴 선택한다.
		Human,					// 항상 사람이 착수한다.
		AI,						// 항상 AI가 착수한다.
	}

	PlayerType		m_player1Type;
	PlayerType		m_player2Type;




	
	private void Awake()
	{
		Application.targetFrameRate	= 60;
		QualitySettings.vSyncCount	= 1;

		m_state			= State.Ready;
	}

	private IEnumerator Start()
	{
		yield return null;

		ShowGameSettingDialog();								// 게임 세팅 다이얼로그 부르기
	}

	public void RestartGame()
	{
		if (m_state != State.GameOver)
		{
			Debug.LogError("Cannot restart the game that is not over yet.");
			return;
		}

		var ui	= OverlayUI.instance;
		ui.HideInfoPanels();									// 정보 패널 전부 감추기
		ui.boardUI.Clear();										// 보드 클리어

		ShowGameSettingDialog();								// 게임 세팅 다이얼로그 부르기
	}

	/// <summary>
	/// 게임 세팅 다이얼로그 부르기
	/// </summary>
	void ShowGameSettingDialog()
	{
		m_state			= State.Ready;

		var ui			= OverlayUI.instance;
		var dialog		= ui.GetDialog<GameSettingDialog>();
		dialog.SetCallback((p1, p2) =>							// 확인 버튼 눌렀을 때 동작
		{
			m_player1Type	= p1;
			m_player2Type	= p2;

			InitializeGame();									// 게임 초기화
		});

		ui.OpenDialog<GameSettingDialog>();						// 다이얼로그 호출
	}

	/// <summary>
	/// 게임 초기화 후 시작
	/// </summary>
	void InitializeGame()
	{
		m_gameState					= new GameState();
		m_gameState.newMovePlaced	+= OnNewMove;
		m_gameState.statusReport	+= OnGameStatusReport;

		m_gameStateCtrl.MakeNewConnection(m_gameState);

		m_state						= State.Playing;			// 상태 세팅

		StartTurn();											// 첫번째 턴 시작
	}

	/// <summary>
	/// 현재 턴 시작. 사용자 입력을 기다리거나 등등등을 처리한다.
	/// </summary>
	void StartTurn()
	{
		OverlayUI.instance.ShowPlayingInfo(m_gameState);	// 현재 턴 정보 UI에 표시
		
		var nextPlayer		= m_gameState.nextPlayer;
		var nextPlayType	= nextPlayer == GameState.PlayerTurn.One? m_player1Type : m_player2Type;

		switch(nextPlayType)							// 플레이 타입에 따라서 적절한 UI/게임 상태 세팅
		{
			case PlayerType.Human:						// 사람이 착수해야 하는 경우, 입력 UI 표시
				SetForHumanInput();
				break;

			case PlayerType.AI:							// AI가 착수해야 하는 경우, 바로 Search 솔버 선택하기
				SetForSearchSolving();
				break;

			case PlayerType.Selectable:					// 유저한테 고르게 해야하는 경우
				PromptForSolverSelect();
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
		yield return null;

		while (!m_gameStateCtrl.waitingForInput)				// 입력 기다리는 상태가 될 때까지 대기한다
			yield return null;

		//Debug.Log("waiting for input passed");
		m_gameStateCtrl.InputSolverIndex(c_solverIndex_Human);	// 사람 입력을 받는 걸로 모듈쪽에 전송

		var ui				= OverlayUI.instance;
		ui.boardUI.ShowInputs(m_gameState.lastBoardSnapshot, OnMoveInput);	// 입력 UI 표시
	}

	/// <summary>
	/// AI 처리 (Search) 상태로 세팅
	/// </summary>
	void SetForSearchSolving()
	{
		StartCoroutine(co_setForSolverWaiting(c_solverIndex_Search));
	}

	/// <summary>
	/// AI 처리 (Rule) 상태로 세팅
	/// </summary>
	void SetForRuleSolving()
	{
		StartCoroutine(co_setForSolverWaiting(c_solverIndex_Rule));
	}

	IEnumerator co_setForSolverWaiting(int solverIndex)
	{
		yield return null;

		while (!m_gameStateCtrl.waitingForInput)				// 입력 기다리는 상태가 될 때까지 대기한다
			yield return null;
		
		m_state = State.Solving;								// 솔버 응답 기다리는 상태로

		m_gameStateCtrl.InputSolverIndex(solverIndex);
		OverlayUI.instance.OpenDialog<WaitingDialog>();
	}

	/// <summary>
	/// 유저한테 솔버 고르게 하는 다이얼로그 표시
	/// </summary>
	void PromptForSolverSelect()
	{
		var ui		= OverlayUI.instance;
		ui.GetDialog<SolverSelectDialog>().Setup(m_gameState, SetForHumanInput, SetForSearchSolving, SetForRuleSolving);
		ui.OpenDialog<SolverSelectDialog>();
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
		while (!m_gameStateCtrl.waitingForInput)			// 입력 기다리는 상태가 될 때까지 대기한다
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
		var ui		= OverlayUI.instance;
		ui.GetDialog<WaitingDialog>().SafeClose();			// 착수 대기 다이얼로그가 열려있다면 닫기
		ui.boardUI.ShowNewMove(snapshot.lastMove);			// 게임판 UI에 새 착수 보내기
	}

	/// <summary>
	/// 게임 오버 다이얼로그 확인한 후
	/// </summary>
	void OnAfterResultDialog()
	{
		m_state = State.GameOver;

		OverlayUI.instance.ShowHistory(m_gameState);		// 착수 리스트 보여주기
	}

	/// <summary>
	/// 게임 내 상태값 리포트. 뭔가 동작이 끝났을 때마다 호출된다.
	/// </summary>
	/// <param name="gstatus"></param>
	void OnGameStatusReport(GameState.Status gstatus)
	{
		//Debug.LogFormat("status report : {0}", gstatus);

		var ui		= OverlayUI.instance;
		
		switch(gstatus)
		{
			case GameState.Status.Playing:			// 계속 진행
				StartTurn();						// 다음 턴 시작
				break;

			case GameState.Status.Win:				// 누군가 이겼을 때
				{
					var result	= m_gameState.lastPlayer == GameState.PlayerTurn.One?
																ResultDialog.Result.Player1Win : ResultDialog.Result.Player2Win;
					ui.GetDialog<ResultDialog>().Setup(result, OnAfterResultDialog);
					ui.OpenDialog<ResultDialog>();
				}
				break;

			case GameState.Status.Error:			// 착수 에러
				{
					var result	= m_gameState.lastPlayer == GameState.PlayerTurn.One?
																ResultDialog.Result.Player1Error : ResultDialog.Result.Player2Error;
					ui.GetDialog<ResultDialog>().Setup(result, OnAfterResultDialog);
					ui.OpenDialog<ResultDialog>();
				}
				break;

			case GameState.Status.Draw:				// 무승부
				ui.GetDialog<ResultDialog>().Setup(ResultDialog.Result.Draw, OnAfterResultDialog);
				ui.OpenDialog<ResultDialog>();
				break;
		}
	}
}

using UnityEngine;
using System.Collections;

/// <summary>
/// GameState를 IPCConnection을 이용하여 통제할 수 있게 해주는 컴포넌트
/// </summary>
public class GameStateController : MonoBehaviour
{
	// Constants

	const string		c_processPath	= "solver/exe.win-amd64-3.6/main.exe";		// StreamingAssets 기준으로 solver 프로세스 경로

	const string		c_msgHeader_result		= "result:";
	const string		c_msgHeader_solverStart	= "solverStart";
	const string		c_msgHeader_move		= "move:";



	// Members

	IPCConnection			m_connection;
	GameState			m_gameState;

	bool				m_waitForInput	= false;

	/// <summary>
	/// 입력받을 종류
	/// </summary>
	public enum InputType
	{
		None,

		SolverIndex,
		MovePosition,
	}

	/// <summary>
	/// 
	/// </summary>
	enum State
	{
		Ready,

		SelectSolver,
		WaitingInput,
		WaitingSolver,
		SolverAnswered,

		GameOver,
	}

	InputType			m_requestedInput;
	State				m_state;

	/// <summary>
	/// 입력 기다리는 중인지
	/// </summary>
	public bool waitingForInput
	{
		get { return m_waitForInput; }
	}

	/// <summary>
	/// 어떤 인풋 종류를 기다리는지
	/// </summary>
	public InputType requestedInput
	{
		get { return m_requestedInput; }
	}

	/// <summary>
	/// solver index 입력
	/// </summary>
	/// <param name="index"></param>
	public void InputSolverIndex(int index)
	{
		if (!m_waitForInput)
		{
			Debug.LogError("not waiting for input");
			return;
		}

		if (m_requestedInput != InputType.SolverIndex)
		{
			Debug.LogError("wrong input type");
			return;
		}

		m_connection.Send(index.ToString());	// 인덱스 정수값 보내기
		m_waitForInput	= false;				// 플래그 내리기
	}

	public void InputMovePosition(int x, int y)
	{
		if (!m_waitForInput)
		{
			Debug.LogError("not waiting for input");
			return;
		}

		if (m_requestedInput != InputType.MovePosition)
		{
			Debug.LogError("wrong input type");
			return;
		}

		m_connection.Send(string.Format("{0},{1}", x, y));	// 좌표값 보내기
		m_waitForInput	= false;				// 플래그 내리기
	}

	public void MakeNewConnection(GameState state)
	{
		if (m_connection != null)
			m_connection.Kill();

		m_gameState		= state;
		m_connection	= new IPCConnection();
		m_connection.Connect(Application.streamingAssetsPath + "/" + c_processPath);

		StartCoroutine(co_mainLoop());
	}

	/// <summary>
	/// 메세지를 폴링하고 처리할 수 있는 것들은 처리하고, 외부에서 처리해야할 메세지는 리턴한다.
	/// </summary>
	/// <returns></returns>
	IPCConnection.Message ProcessMessage()
	{
		IPCConnection.Message	message	= null;
		while((message = m_connection.PollReceive()) != null)				// polling하다가 null을 만나버린 경우엔 그냥 루프를 빠져나온다.
		{
			if (message.header == IPCConnection.Message.Header.Terminate)	// 프로세스가 갑자기 종료되는 경우, 에러 처리
			{
				m_gameState.SetStatus(GameState.Status.Error);				// gamestate는 에러 상태로 맞추기
				m_state	= State.GameOver;
				break;	// Terminate 메세지가 리턴된다.
			}
			else if (message.header == IPCConnection.Message.Header.Await)	// Await를 만나면 그대로 리턴한다.
			{
				break;	// Await 메세지가 리턴된다.
			}
			else
			{
				var msg	= message.message;
				//Debug.Log("[message] " + msg);

				if (msg == c_msgHeader_solverStart)							// solverStart 메세지를 만난 경우, 스테이트 변경
				{
					m_state = State.WaitingSolver;
					break;	// 메세지 리턴된다.
				}
				else if (msg.StartsWith(c_msgHeader_move))					// solver가 수를 둔 경우, 스테이트 변경하고 리턴
				{
					m_state	= State.SolverAnswered;
					break;	// 메세지 리턴된다.
				}
				else if (msg.StartsWith(c_msgHeader_result))				// 게임이 종료되는 경우, 스테이트 변경하고 리턴
				{
					var code	= int.Parse(msg.Split(':')[1]);
					switch (code)											// result code에 따라 gamestate세팅
					{
						case 1:
							// 게임 진행중일 때에도 스테이트는 보내줘야한다.
							m_gameState.SetStatus(GameState.Status.Playing);
							break;

						case 2:
							m_gameState.SetStatus(GameState.Status.Draw);
							m_state = State.GameOver;
							break;

						case 10:
						case 11:
							m_gameState.SetStatus(GameState.Status.Win);
							m_state = State.GameOver;
							break;

						case 20:
						case 21:
							m_gameState.SetStatus(GameState.Status.Error);
							m_state = State.GameOver;
							break;
					}
					
					break;	// 메세지 리턴된다.
				}
			}
		}

		return message;
	}

	IEnumerator co_mainLoop()
	{
		m_state			= State.Ready;

		IPCConnection.Message message	= null;

		while (m_state != State.GameOver)	// 게임오버 스테이트에 도달할 때까지 계속 반복
		{
			// 1. solver index 입력
			
			m_requestedInput	= InputType.SolverIndex;		// solver index를 골라야함

			while ((message = ProcessMessage()) == null)		// 유의미한 메세지 리턴받을 때까지 기다린다.
				yield return null;

			if (m_state == State.GameOver)						// 게임 종료시 루프 빠져나오기
			{
				break;
			}
				
			
			if (message.header == IPCConnection.Message.Header.Await)	// 입력 기다리는 경우 - solver index임!
			{
				//Debug.Log("Solver index await");
				m_state				= State.SelectSolver;
				m_waitForInput		= true;

				//Debug.Log("waiting for input : " + m_requestedInput);
			}

			while (m_waitForInput)									// 입력 해결될 때까지 기다린다.
				yield return null;



			// 2. SolverStart 기다리기

			while ((message = ProcessMessage()) == null)		// 유의미한 메세지 리턴받을 때까지 기다린다.
				yield return null;

			if (m_state == State.GameOver)						// 게임 종료시 루프 빠져나오기
			{
				break;
			}

			if (m_state != State.WaitingSolver)					// WaitingSolver 상태가 아닌 경우엔 뭔가 잘못된 것임
			{
				Debug.LogErrorFormat("wrong state {0} - must be WaitingSolver", m_state);
				m_state	= State.GameOver;
				break;
			}
				
			// 3. Solver answer 혹은 유저입력

			m_requestedInput = InputType.MovePosition;
			
			while ((message = ProcessMessage()) == null)		// 유의미한 메세지 리턴받을 때까지 기다린다.
				yield return null;

			if (m_state == State.GameOver)						// 게임 종료시 루프 빠져나오기
			{
				break;
			}

			if (message.header == IPCConnection.Message.Header.Await)	// 입력 기다리는 경우 - solver index임!
			{
				m_state				= State.SelectSolver;
				m_waitForInput		= true;

				//Debug.Log("waiting for input : " + m_requestedInput);

				while (m_waitForInput)									// 입력 해결될 때까지 기다린다.
					yield return null;

				while ((message = ProcessMessage()) == null)			// Solver Answer까지 기다린다
					yield return null;

				if (m_state == State.GameOver)							// 게임 종료시 루프 빠져나오기
				{
					break;
				}
			}
			
			// 3-1. 진짜로 solver 응답 처리
			
			if (m_state == State.SolverAnswered)				// solver가 답을 준 경우 (아마 이 경우밖에 없을것임)
			{
				var paramStr	= message.message.Split(new char[] { ':' }, 2)[1];
				var paramArr	= paramStr.Split(new char[] { ',' }, 3);

				m_gameState.PlaceNewMove(int.Parse(paramArr[0]), int.Parse(paramArr[1]), paramArr[2]);
			}

			// 4. result 기다리기

			while ((message = ProcessMessage()) == null)		// 유의미한 메세지 리턴받을 때까지 기다린다.
				yield return null;
		}

		Debug.Log("Game Over!");

		// connection을 정리한다.

		m_connection.Kill();// 보험...
		m_connection	= null;
	}

	private void Update()
	{
		if (m_connection != null)
		{
			// stdout, stderr 출력해주기

			var msgout	= (string)null;
			while((msgout = m_connection.PollStdOut()) != null)
			{
				Debug.Log(msgout);
			}

			while ((msgout = m_connection.PollStdErr()) != null)
			{
				Debug.LogError(msgout);
			}
		}
	}

	private void OnApplicationQuit()
	{
		if (m_connection != null)
			m_connection.Kill();								// 종료될 때는 외부 프로세스도 죽이기
	}
}

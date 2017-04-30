using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 게임 상태 추적용 클래스. 게임 1판의 진행을 전부 보관한다.
/// </summary>
public class GameState
{
	// Constants

	public const int		c_boardWidth	= 7;		// 게임판 가로
	public const int		c_boardHeight	= 6;		// 게임판 세로


	/// <summary>
	/// 수를 둔 플레이어
	/// </summary>
	public enum PlayerTurn
	{
		None	= 0,

		One,
		Two,
	}

	/// <summary>
	/// 현재 게임 상태
	/// </summary>
	public enum Status
	{
		Playing		= 0,				// 계속 진행중

		Win,							// 현재 턴 둔 사람이 이김
		Draw,							// 게임 비긴 상태로 종료
		Error,							// 현재 둔 사람이 착수 에러
	}


	public interface IBoardSnapshot
	{
		IMove lastMove { get; }
		IMove GetMove(int x, int y);
	}

	public interface IMove
	{
		int			x			{ get; }
		int			y			{ get; }
		int			turn		{ get; }
		PlayerTurn	who			{ get; }
		string		comment		{ get; }
	}

	/// <summary>
	/// 게임 보드 상태
	/// </summary>
	class Board : IBoardSnapshot
	{
		public class Move : IMove
		{
			public int x		{ get; private set; }
			public int y		{ get; private set; }
			public int turn		{ get; private set; }

			public PlayerTurn who	{ get; private set; }

			public string comment { get; private set; }


			public Move(int x, int y, int turn, PlayerTurn who, string comment = null)
			{
				this.x			= x;
				this.y			= y;
				this.turn		= turn;
				this.who		= who;
				this.comment	= comment;
			}
		}

		// Members

		IMove []				m_board;					// 게임판. 1차 배열을 2차원 배열처럼 사용한다.
		IMove					m_lastMove;					// 이 게임판 상태에서 가장 최근에 둔 수. 아직 수를 두지 않았다면 null

		/// <summary>
		/// 가장 최근에 둔 수
		/// </summary>
		public IMove lastMove
		{
			get { return m_lastMove; }
		}

		public Board()
		{
			m_board	= new Move[c_boardWidth * c_boardHeight];
		}

		public Board(Board original) : this()
		{
			if (original != null)
			{
				// 원본 보드에서 상태를 복제해온다.
				original.m_board.CopyTo(m_board, 0);

				// NOTE : 복제시에는 m_lastMove는 복사하지 않는다. 새로 수를 두기 위해서 보드를 복제하는 것이므로.
			}
		}

		/// <summary>
		/// x,y 좌표값을 배열 인덱스로 변환
		/// </summary>
		/// <param name="x"></param>
		/// <param name="y"></param>
		/// <returns></returns>
		private int CoordinateToIndex(int x, int y)
		{
			if (x < 0 || x >= c_boardWidth || y < 0 || y >= c_boardHeight)
				throw new System.InvalidOperationException("coordinate is out of range");

			return y * c_boardWidth + x;
		}

		/// <summary>
		/// 수를 둔다
		/// </summary>
		/// <param name="move"></param>
		public void PlaceMove(IMove move)
		{
			if (m_lastMove != null)
				throw new System.InvalidOperationException("You cannot place more than one move on Board.");

			m_lastMove	= move;
			m_board[CoordinateToIndex(move.x, move.y)]	= move;
		}

		/// <summary>
		/// 해당 좌표의 수 데이터를 가져온다.
		/// </summary>
		/// <param name="x"></param>
		/// <param name="y"></param>
		/// <returns></returns>
		public IMove GetMove(int x, int y)
		{
			return m_board[CoordinateToIndex(x, y)];
		}
	}

	//

	

	// Members

	List<Board>			m_boardSnapshotList	= new List<Board>();		// 각 턴마다 보드 스냅샷 리스트

	/// <summary>
	/// 새로 수를 뒀을 때 호출하는 이벤트
	/// </summary>
	public event System.Action<IBoardSnapshot>	newMovePlaced;
	/// <summary>
	/// 상태 변경되었을 때 호출하는 이벤트
	/// </summary>
	public event System.Action<Status>			statusReport;


	/// <summary>
	/// 턴 카운트
	/// </summary>
	public int turnCount
	{
		get { return m_boardSnapshotList.Count; }
	}

	/// <summary>
	/// 가장 최근 보드 상태
	/// </summary>
	public IBoardSnapshot lastBoardSnapshot
	{
		get
		{
			var count	= m_boardSnapshotList.Count;
			if (m_boardSnapshotList.Count == 0)
				return null;
			else
				return m_boardSnapshotList[count - 1];
		}
	}
	
	/// <summary>
	/// 현재 게임 상태
	/// </summary>
	public Status		status { get; private set; }

	/// <summary>
	/// 마지막에 수를 둔 플레이어
	/// </summary>
	public PlayerTurn lastPlayer
	{
		get
		{
			var stateCount	= m_boardSnapshotList.Count;
			if (stateCount == 0)										// 아직 아무도 두지 않았다면 None 리턴
				return PlayerTurn.None;
			else
				return stateCount % 2 == 0 ? PlayerTurn.Two : PlayerTurn.One;
		}
	}

	/// <summary>
	/// 이번에 수를 둘 플레이어
	/// </summary>
	public PlayerTurn nextPlayer
	{
		get
		{
			var stateCount	= m_boardSnapshotList.Count;
			return stateCount % 2 == 0 ? PlayerTurn.One : PlayerTurn.Two;
		}
	}

	/// <summary>
	/// 현재 둬야 할 플레이어의 입장에서 수 두기
	/// </summary>
	/// <param name="x"></param>
	/// <param name="y"></param>
	/// <param name="comment"></param>
	public void PlaceNewMove(int x, int y, string comment = null)
	{
		var newBoard	= new Board(lastBoardSnapshot as Board);			// 보드 상태 복제하기
		var newMove		= new Board.Move(x, y, turnCount, nextPlayer, comment);
		newBoard.PlaceMove(newMove);										// 수 두기

		m_boardSnapshotList.Add(newBoard);									// 리스트에 달아두기

		if (newMovePlaced != null)											// 이벤트 호출
			newMovePlaced(newBoard);
	}

	/// <summary>
	/// 상태 설정
	/// </summary>
	/// <param name="status"></param>
	public void SetStatus(Status status)
	{
		this.status		= status;

		if (statusReport != null)											// 이벤트 호출
			statusReport(status);
	}

	/// <summary>
	/// 특정 턴에서의 보드 상태 구하기
	/// </summary>
	/// <param name="index"></param>
	/// <returns></returns>
	public IBoardSnapshot GetBoardSnapshot(int index)
	{
		return m_boardSnapshotList[index];
	}
}

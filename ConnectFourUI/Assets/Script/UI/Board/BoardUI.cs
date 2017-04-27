using UnityEngine;
using System.Collections;
using UnityEngine.UI;
using UnityEngine.EventSystems;

/// <summary>
/// 게임판 UI
/// </summary>
public class BoardUI : MonoBehaviour
{
	// Properties

	[SerializeField]
	int				m_boardWidth	= 7;
	[SerializeField]
	int				m_boardHeight	= 6;
	[SerializeField]
	GameObject		m_stoneOriginal	= null;		// 게임판 돌 객체 (오리지널)
	[SerializeField]
	CanvasGroup		m_buttonGroup;
	[SerializeField]
	Button []		m_buttons;


	// Members

	BoardStone []		m_stoneObjs;			// 돌 객체 배열
	System.Action<int>	m_inputCallback;		// 라인 선택시 콜백


	private void Awake()
	{
		// 돌 객체 생성/초기화

		var scount		= m_boardWidth * m_boardHeight;		// 돌 최대 갯수
		m_stoneObjs		= new BoardStone[scount];

		m_stoneOriginal.SetActive(true);					// 원래 오브젝트 활성화해놓기 (초기화 문제)
		var stoneParent	= m_stoneOriginal.transform.parent;
		for (var i = 0; i < scount; i++)
		{
			// NOTE : GridLayout을 쓴다는 가정 하에 위치는 신경쓰지 않고 객체를 생성한다.

			var newGo	= Instantiate<GameObject>(m_stoneOriginal, stoneParent, false);
			var newObj	= newGo.GetComponent<BoardStone>();

			m_stoneObjs[i]	= newObj;
		}

		m_stoneOriginal.SetActive(false);					// 원래 오브젝트 다시 비활성화
															//


		var lcount		= m_buttons.Length;
		for (var i = 0; i < lcount; i++)					// 버튼 이벤트 핸들러 설정
		{
			var x = i;
			m_buttons[i].onClick.AddListener(() =>
			{
				OnInput(x);
			});
		}

		DisableInputs();									// 초기에는 입력 감춘 상태로
	}

	/// <summary>
	/// 판 지우기
	/// </summary>
	public void Clear()
	{
		var count	= m_stoneObjs.Length;
		for (var i = 0; i < count; i++)
		{
			m_stoneObjs[i].Hide();
		}
	}

	/// <summary>
	/// 판 전체를 특정 보드 스냅샷으로 덮어쓰기
	/// </summary>
	/// <param name="boardSnapshot"></param>
	public void ShowBoard(GameState.IBoardSnapshot boardSnapshot)
	{
		for (var y = 0; y < m_boardHeight; y++)
		{
			for (var x = 0; x < m_boardWidth; x++)
			{
				var move	= boardSnapshot.GetMove(x, y);
				var stone	= GetStoneAtPos(x, y);
				if (move != null)
				{
					var colorPreset	= move.who == GameState.PlayerTurn.One ?
															BoardStone.ColorPreset.Player1
														:	BoardStone.ColorPreset.Player2;
					stone.Show(colorPreset, false);
				}
				else
				{
					stone.Hide();
				}
			}
		}
	}

	/// <summary>
	/// 현재 판 상태에 새롭게 수 하나 표시
	/// </summary>
	/// <param name="newMove"></param>
	public void ShowNewMove(GameState.IMove newMove)
	{
		var colorPreset	= newMove.who == GameState.PlayerTurn.One ?
															BoardStone.ColorPreset.Player1
														:	BoardStone.ColorPreset.Player2;
		GetStoneAtPos(newMove.x, newMove.y).Show(colorPreset, true);
	}

	BoardStone GetStoneAtPos(int x, int y)
	{
		return m_stoneObjs[y * m_boardWidth + x];
	}


	void DisableInputs()
	{
		m_buttonGroup.interactable	= false;
	}

	/// <summary>
	/// 입력 가능한 라인에 버튼을 보여주고 입력을 받으면 콜백을 호출해준다.
	/// </summary>
	/// <param name="currentBoard"></param>
	public void ShowInputs(GameState.IBoardSnapshot currentBoard, System.Action<int> callback)
	{
		for (var x = 0; x < GameState.c_boardWidth; x++)
		{
			// 맨 윗쪽줄에 아무것도 없으면 착수 가능한 걸로 본다
			m_buttons[x].interactable	= currentBoard == null || currentBoard.GetMove(x, GameState.c_boardHeight - 1) == null;
		}
		m_inputCallback	= callback;
		m_buttonGroup.interactable	= true;	// 전체 그룹 입력 활성화
	}

	void OnInput(int x)
	{
		EventSystem.current.SetSelectedGameObject(null);	// 버튼 선택 비활성화
		DisableInputs();									// 전체 그룹 비활성화

		var cb			= m_inputCallback;
		m_inputCallback	= null;

		cb(x);
	}
}

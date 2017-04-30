using UnityEngine;
using System.Collections;
using System;
using UnityEngine.UI;

public class HistoryListItem : FSNBaseListItem<GameState.IBoardSnapshot>
{
	// Properties

	[SerializeField]
	Image			m_stone;
	[SerializeField]
	Text			m_text;


	// Members

	GameState.IBoardSnapshot	m_boardSnapshot;

	public override void SetupData(GameState.IBoardSnapshot parameter)
	{
		m_boardSnapshot	= parameter;

		var lastmove	= parameter.lastMove;
		m_text.text		= string.Format("턴 : {0} ({1},{2})", lastmove.turn + 1, lastmove.x + 1, lastmove.y + 1);

		var colorPreset	= lastmove.who	== GameState.PlayerTurn.One? BoardStone.ColorPreset.Player1 : BoardStone.ColorPreset.Player2;
		m_stone.color	= BoardStone.GetColorFromPreset(colorPreset);
	}

	public void OnClick()
	{
		OverlayUI.instance.boardUI.ShowBoard(m_boardSnapshot);		// 바로 보드 UI에 스냅샷 내용 표시
	}
}

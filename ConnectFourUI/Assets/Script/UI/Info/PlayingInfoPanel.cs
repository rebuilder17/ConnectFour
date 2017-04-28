using UnityEngine;
using System.Collections;
using UnityEngine.UI;

public class PlayingInfoPanel : MonoBehaviour
{
	// Properties

	[SerializeField]
	Image			m_stoneImage;
	[SerializeField]
	Text			m_player;
	[SerializeField]
	Text			m_turn;

	
	public void ShowInfo(GameState curstate)
	{
		int playerNum;
		BoardStone.ColorPreset playerColor;

		switch(curstate.nextPlayer)
		{
			case GameState.PlayerTurn.One:
				playerNum	= 1;
				playerColor	= BoardStone.ColorPreset.Player1;
				break;

			case GameState.PlayerTurn.Two:
			default:
				playerNum	= 2;
				playerColor	= BoardStone.ColorPreset.Player2;
				break;
		}

		m_stoneImage.color	= BoardStone.GetColorFromPreset(playerColor);
		m_player.text		= string.Format("플레이어 {0} 차례", playerNum);
		m_turn.text			= string.Format("현재 턴 : {0}", curstate.turnCount + 1);
	}
}

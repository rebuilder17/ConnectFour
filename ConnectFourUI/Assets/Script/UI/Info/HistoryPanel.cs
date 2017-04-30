using UnityEngine;
using System.Collections;

public class HistoryPanel : MonoBehaviour
{
	// Properties

	[SerializeField]
	HistoryListUI	m_listUI;


	// Members


	public void ShowPopulateHistory(GameState gameState)
	{
		m_listUI.Clear();

		var count	= gameState.turnCount;
		for (var i = 0; i < count; i++)
		{
			var snapshot	= gameState.GetBoardSnapshot(i);
			m_listUI.AddItem(snapshot);
		}
	}
}

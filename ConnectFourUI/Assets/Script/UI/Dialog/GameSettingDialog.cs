using UnityEngine;
using System.Collections;

public class GameSettingDialog : FSNBaseOverlayDialog
{
	// Properties

	[SerializeField]
	PlayerTypePanel		m_player1;
	[SerializeField]
	PlayerTypePanel		m_player2;


	// Members

	System.Action<Engine.PlayerType, Engine.PlayerType> m_delCallback;
	
	protected override void Initialize()
	{
		base.Initialize();

		m_player1.SetPlayerMark(BoardStone.ColorPreset.Player1);
		m_player2.SetPlayerMark(BoardStone.ColorPreset.Player2);
	}

	public void SetCallback(System.Action<Engine.PlayerType, Engine.PlayerType> cb)
	{
		m_delCallback = cb;
	}

	public void OnOK()
	{
		CloseSelf();

		m_delCallback(m_player1.selectedType, m_player2.selectedType);
	}
}

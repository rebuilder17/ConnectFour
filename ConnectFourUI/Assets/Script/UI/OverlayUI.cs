using UnityEngine;
using System.Collections;

public class OverlayUI : FSNBaseOverlayUI
{
	// Properties

	[SerializeField]
	BoardUI			m_boardUI;

	[SerializeField]
	PlayingInfoPanel	m_playingInfoPanel;



	// Members

	public static OverlayUI instance { get; private set; }


	public BoardUI boardUI
	{
		get { return m_boardUI; }
	}

	protected override void Initialize()
	{
		base.Initialize();

		instance	= this;

		HideInfoPanels();
	}
	//

	public void HideInfoPanels()
	{
		m_playingInfoPanel.gameObject.SetActive(false);
	}

	public void ShowPlayingInfo(GameState curstate)
	{
		m_playingInfoPanel.gameObject.SetActive(true);

		m_playingInfoPanel.ShowInfo(curstate);
	}
}

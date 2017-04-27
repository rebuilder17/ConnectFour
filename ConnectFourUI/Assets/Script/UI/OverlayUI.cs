using UnityEngine;
using System.Collections;

public class OverlayUI : FSNBaseOverlayUI
{
	// Properties

	[SerializeField]
	BoardUI			m_boardUI;



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
	}
}

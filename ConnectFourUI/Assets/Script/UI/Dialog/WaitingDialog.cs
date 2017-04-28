using UnityEngine;
using System.Collections;
using UnityEngine.UI;

public class WaitingDialog : FSNBaseOverlayDialog
{
	// Properties

	[SerializeField]
	Text			m_timerText;


	// Members

	float			m_startTime;


	protected override void OnOpen()
	{
		base.OnOpen();

		m_startTime	= Time.realtimeSinceStartup;			// 다이얼로그 열릴 당시의 시간 기록
	}

	private void Update()
	{
		var elapsed	= Time.realtimeSinceStartup - m_startTime;
		var min		= Mathf.FloorToInt(elapsed / 60f);
		var sec		= Mathf.FloorToInt(elapsed % 60f);
		
		m_timerText.text	= string.Format("{0}:{1:00}", min, sec);
	}

	public void SafeClose()
	{
		if (IsOpened)
		{
			CloseSelf();
		}
	}
}

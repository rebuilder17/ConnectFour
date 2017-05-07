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
	bool			m_openCompletely;
	bool			m_reservedToClose;


	protected override void OnOpen()
	{
		base.OnOpen();
		m_openCompletely	= false;
		m_startTime	= Time.realtimeSinceStartup;			// 다이얼로그 열릴 당시의 시간 기록
	}

	protected override void OnOpenComplete()
	{
		base.OnOpenComplete();

		m_openCompletely	= true;
		if (m_reservedToClose)								// 완전히 열린 뒤 닫도록 플래그를 세워뒀다면...
		{
			m_reservedToClose	= false;
			Debug.Log("need to close as reserved");
			CloseSelf();
		}
	}

	protected override void OnClose()
	{
		base.OnClose();

		m_openCompletely	= false;
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
		if (IsOpened)							// 열린 상태에서만...
		{
			if (m_openCompletely)				// 완전히 열린 상태에서는 바로 close
			{
				CloseSelf();
			}
			else
			{									// 아닌 경우, 완전히 열린 상태에서 바로 닫도록...
				Debug.Log("reserve");
				m_reservedToClose	= true;
			}
		}
	}
}

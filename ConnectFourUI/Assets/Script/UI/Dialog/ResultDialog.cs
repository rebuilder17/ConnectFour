using UnityEngine;
using System.Collections;
using UnityEngine.UI;

public class ResultDialog : FSNBaseOverlayDialog
{
	public enum Result
	{
		Player1Win,
		Player2Win,

		Draw,

		Player1Error,
		Player2Error,
	}

	// Properties

	[SerializeField]
	Image			m_stoneImage;
	[SerializeField]
	Text			m_text;


	// Members

	System.Action	m_callback;
	
	

	public void Setup(Result result, System.Action callback)
	{
		m_callback	= callback;

		bool showImage;
		Color imageColor	= Color.white;
		string message;

		switch(result)
		{
			case Result.Player1Win:
				showImage	= true;
				imageColor	= BoardStone.GetColorFromPreset(BoardStone.ColorPreset.Player1);
				message		= "플레이어 1 승리!";
				break;

			case Result.Player2Win:
				showImage	= true;
				imageColor	= BoardStone.GetColorFromPreset(BoardStone.ColorPreset.Player2);
				message		= "플레이어 2 승리!";
				break;

			case Result.Player1Error:
				showImage	= true;
				imageColor	= BoardStone.GetColorFromPreset(BoardStone.ColorPreset.Player1);
				message		= "착수 에러 발생 (플레이어 1)";
				break;

			case Result.Player2Error:
				showImage	= true;
				imageColor	= BoardStone.GetColorFromPreset(BoardStone.ColorPreset.Player2);
				message		= "착수 에러 발생 (플레이어 2)";
				break;

			case Result.Draw:
			default:
				showImage	= false;
				message		= "무승부!";
				break;
		}

		m_stoneImage.gameObject.SetActive(showImage);
		m_stoneImage.color	= imageColor;
		m_text.text	= message;
	}

	public void OnBtnOK()
	{
		CloseSelf();

		var cb	= m_callback;
		m_callback	= null;

		cb();
	}
}

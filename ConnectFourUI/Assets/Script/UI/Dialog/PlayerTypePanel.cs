using UnityEngine;
using System.Collections;
using UnityEngine.UI;

public class PlayerTypePanel : MonoBehaviour
{
	// Properties

	[SerializeField]
	Image			m_stone;
	[SerializeField]
	Toggle []		m_toggles;


	// Members

	Engine.PlayerType	m_curPlayerType;


	public Engine.PlayerType selectedType
	{
		get { return m_curPlayerType; }
	}

	private void Awake()
	{
		var tcount	= m_toggles.Length;
		for(var i = 0; i < tcount; i++)
		{
			var index = i;
			m_toggles[i].onValueChanged.AddListener((value) =>
			{
				if (value)
					m_curPlayerType = (Engine.PlayerType)index;
			});
		}

		m_toggles[0].isOn	= true;					// 첫번째 바로 선택
	}

	public void SetPlayerMark(BoardStone.ColorPreset color)
	{
		m_stone.color	= BoardStone.GetColorFromPreset(color);
	}
}

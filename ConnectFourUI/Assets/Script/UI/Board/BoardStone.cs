using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.UI;

/// <summary>
/// 게임판의 돌
/// </summary>
public class BoardStone : MonoBehaviour
{
	public enum ColorPreset
	{
		Player1,
		Player2,
	}

	static readonly Dictionary<ColorPreset, Color> c_colorDict = new Dictionary<ColorPreset, Color>()
	{
		{ ColorPreset.Player1, new Color(1, 1, 1) },
		{ ColorPreset.Player2, new Color(0.2f, 0.2f, 0.2f) },
	};

	public static Color GetColorFromPreset(ColorPreset preset)
	{
		return c_colorDict[preset];
	}


	// Properties

	[SerializeField]
	Image			m_image;					// 실제로 이미지 표시하는데 사용할 Image 객체



	// Members

	RectTransform	m_imageTr;
	Coroutine		m_animCo;


	private void Awake()
	{
		m_imageTr		= m_image.rectTransform;
		m_image.enabled	= false;
	}

	/// <summary>
	/// 돌 표시
	/// </summary>
	/// <param name="color"></param>
	/// <param name="showAnim"></param>
	public void Show(ColorPreset color, bool showAnim)
	{
		m_image.enabled	= true;

		if (m_animCo != null)					// 애니메이션 실행중인 게 있으면 취소
			StopCoroutine(m_animCo);

		var realColor	= c_colorDict[color];
		m_image.color	= realColor;

		System.Action finalSetFunc	= () =>
		{
			m_imageTr.anchoredPosition = Vector2.zero;
			m_image.color	= realColor;
		};

		if (showAnim)							// 애니메이션 재생하는 경우
		{
			m_animCo	= this.StartLerpingCoroutine(0.2f, (t) =>
			{
				m_imageTr.anchoredPosition	= new Vector2(0, (1f - t) * 100);
				var c			= m_image.color;
				c.a				= t;
				m_image.color	= c;
			}, finalSetFunc);
		}
		else
		{										// 애니메이션 재생하지 않는 경우, 마지막 상태로 바로 세팅
			m_animCo	= null;
			finalSetFunc();
		}
	}

	/// <summary>
	/// 돌 숨기기
	/// </summary>
	public void Hide()
	{
		m_image.enabled	= false;			// 우선은 그냥 비활성화만...
	}
}

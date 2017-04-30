using UnityEngine;
using System.Collections;
using UnityEngine.UI;
using System;

public class SolverSelectDialog : FSNBaseOverlayDialog
{
	class Transition_Slide : BaseTransition
	{
		public Vector2 to { get; set; }

		Vector2 m_startPos;

		public Transition_Slide(FSNBaseOverlayDialog target) : base(target)
		{

		}


		public override void TransitionReady()
		{
			m_startPos	= transform.anchoredPosition;
			alpha		= 1;
		}

		public override void TransitionDo(float t)
		{
			transform.anchoredPosition = Vector2.Lerp(m_startPos, to, Mathf.Pow(t, 0.5f));
		}

		public override void TransitionFinish()
		{
			transform.anchoredPosition = to;
		}
	}



	// Properties

	[SerializeField]
	Image			m_stone;


	// Members

	System.Action		m_delHuman;
	System.Action		m_delSearch;
	System.Action		m_delRule;



	protected override void OnSetupTransition()
	{
		base.OnSetupTransition();

		var transOpen	= new Transition_Slide(this);
		transOpen.to	= new Vector2(0, 0);
		var transClose	= new Transition_Slide(this);
		transClose.to	= GetComponent<RectTransform>().anchoredPosition;

		SetTransitionObject(TransitionType.Open, transOpen);
		SetTransitionObject(TransitionType.Close, transClose);
	}


	public void Setup(GameState state, System.Action delHuman, System.Action delSearch, System.Action delRule)
	{
		var color		= state.nextPlayer == GameState.PlayerTurn.One ? BoardStone.ColorPreset.Player1 : BoardStone.ColorPreset.Player2;
		m_stone.color	= BoardStone.GetColorFromPreset(color);

		m_delHuman		= delHuman;
		m_delSearch		= delSearch;
		m_delRule		= delRule;
	}
	
	
	void CallAndClose(System.Action cb)
	{
		CloseSelf();

		m_delHuman	= null;
		m_delSearch	= null;
		m_delRule	= null;

		cb();
	}
	
	public void OnSelectHuman()
	{
		CallAndClose(m_delHuman);
	}

	public void OnSelectSearch()
	{
		CallAndClose(m_delSearch);
	}

	public void OnSelectRule()
	{
		CallAndClose(m_delRule);
	}
}

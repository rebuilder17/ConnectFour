using UnityEngine;
using System.Collections;
using System;

public partial class FSNBaseOverlayDialog
{
	/// <summary>
	/// 화면 전환의 기본형
	/// </summary>
	protected abstract class BaseTransition
	{
		// Members

		private FSNBaseOverlayDialog m_dialog;



		protected RectTransform transform
		{
			get { return m_dialog.m_trans; }
		}

		protected float alpha
		{
			get { return m_dialog.m_canvasGroup.alpha; }
			set { m_dialog.m_canvasGroup.alpha = value; }
		}


		public BaseTransition(FSNBaseOverlayDialog targetDialog)
		{
			m_dialog    = targetDialog;
		}

		public abstract void TransitionReady();
		public abstract void TransitionDo(float t);
		public abstract void TransitionFinish();
	}

	//============================================================

	/// <summary>
	/// 열기 : 확대된 스케일에서 원래 스케일로
	/// </summary>
	protected class TrOpen_ScaleIn : BaseTransition
	{
		public TrOpen_ScaleIn(FSNBaseOverlayDialog target) : base(target) { }

		public override void TransitionReady()
		{
		}

		public override void TransitionDo(float t)
		{
			alpha					= Mathf.Lerp(0, 1, t);
			transform.localScale	= Vector3.one * Mathf.Lerp(c_transitionSclae, 1, Mathf.Pow(t, c_transitionTimeT));
		}

		public override void TransitionFinish()
		{
			alpha					= 1;
			transform.localScale	= Vector3.one;
		}
	}

	/// <summary>
	/// 닫기 : 원래 스케일에서 확대된 스케일로
	/// </summary>
	protected class TrClose_ScaleOut : BaseTransition
	{
		public TrClose_ScaleOut(FSNBaseOverlayDialog target) : base(target) { }

		public override void TransitionReady()
		{
		}

		public override void TransitionDo(float t)
		{
			alpha                   = Mathf.Lerp(1, 0, t);
			transform.localScale    = Vector3.one * Mathf.Lerp(1, c_transitionSclae, Mathf.Pow(t, c_transitionTimeT));
		}

		public override void TransitionFinish()
		{
			alpha     = 0;
		}
	}

	/// <summary>
	/// 뒤로 가기 : 아주 옅은 알파까지 페이드아웃
	/// </summary>
	protected class TrBack_FadeOut : BaseTransition
	{
		public TrBack_FadeOut(FSNBaseOverlayDialog target) : base(target) { }


		float   m_startAlpha;

		public override void TransitionReady()
		{
			m_startAlpha	= alpha;
		}

		public override void TransitionDo(float t)
		{
			alpha = Mathf.Lerp(m_startAlpha, 0.1f, t);
		}

		public override void TransitionFinish()
		{
			alpha     = 0.1f;
		}
	}

	/// <summary>
	/// 앞으로 복귀 : 알파값 1로 복귀
	/// </summary>
	protected class TrForth_FadeIn : BaseTransition
	{
		public TrForth_FadeIn(FSNBaseOverlayDialog target) : base(target) { }


		float m_startAlpha;

		public override void TransitionReady()
		{
			m_startAlpha      = alpha;
		}

		public override void TransitionDo(float t)
		{
			alpha = Mathf.Lerp(m_startAlpha, 1, t);
		}

		public override void TransitionFinish()
		{
			alpha     = 1;
		}
	}
}

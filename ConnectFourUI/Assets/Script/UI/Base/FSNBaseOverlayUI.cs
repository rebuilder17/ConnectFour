using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using System.Collections;


/// <summary>
/// 오버레이 UI를 관리하는 컴포넌트
/// </summary>
[RequireComponent(typeof(Canvas))]
public abstract partial class FSNBaseOverlayUI : MonoBehaviour
{
	// Properties
	
	[SerializeField]
	FSNBaseOverlayDialog[]	m_dialogs;                  // OverlayUI에서 관리할 다이얼로그들
	


	// Members
	
	DialogStack		m_dialogStack;						// 다이얼로그 스택


	/// <summary>
	/// 다이얼로그가 열려있는지
	/// </summary>
	public bool dialogOpened
	{
		get { return !m_dialogStack.IsEmpty; }
	}
	

	private void Awake()
	{
		// 다이얼로그 스택 초기화

		m_dialogStack			= new DialogStack();
		var dialogCount			= m_dialogs.Length;
		for (var i = 0; i < dialogCount; i++)							// 다이얼로그들 스택에 미리 등록
		{
			var dialog			= m_dialogs[i];
			dialog.RegisterDialogProtocol(m_dialogStack);

			// 강제로 활성화->비활성화해서 다이얼로그 오브젝트 워밍업, 그리고 다이얼로그가 전부 비활성 상태로 시작하도록 강제한다
			dialog.gameObject.SetActive(true);
			dialog.gameObject.SetActive(false);
		}

		Initialize();													// 그외 초기화 코드 호출
	}

	protected virtual void Initialize() { }


	private void Update()
	{
		OnUpdate();
	}

	protected virtual void OnUpdate() { }


	//==============================================================

	// 다이얼로그 관련

	/// <summary>
	/// 다이얼로그 객체 얻어오기
	/// </summary>
	/// <typeparam name="T"></typeparam>
	/// <returns></returns>
	public T GetDialog<T>() where T : FSNBaseOverlayDialog
	{
		return m_dialogStack.GetDialog<T>();
	}

	/// <summary>
	/// 다이얼로그 열기
	/// </summary>
	/// <typeparam name="T"></typeparam>
	public void OpenDialog<T>() where T : FSNBaseOverlayDialog
	{
		m_dialogStack.Open<T>();
	}

	/// <summary>
	/// 다이얼로그 닫기
	/// </summary>
	/// <typeparam name="T"></typeparam>
	public void CloseDialog<T>() where T : FSNBaseOverlayDialog
	{
		m_dialogStack.Close<T>();
	}
}

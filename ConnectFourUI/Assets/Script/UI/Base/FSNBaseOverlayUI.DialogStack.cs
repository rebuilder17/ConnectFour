using UnityEngine;
using System.Collections;
using System.Collections.Generic;


public partial class FSNBaseOverlayUI
{
	/// <summary>
	/// 외부에서 다이얼로그 프로토콜을 추가하기 위한 인터페이스
	/// </summary>
	public interface IDialogProtocolAdd
	{
		void AddDialogProtocol(System.Type dialogType, FSNBaseOverlayDialog.Protocol protocol);
	}

	/// <summary>
	/// 각 다이얼로그의 상태 등 조작
	/// </summary>
	class DialogStack : IDialogProtocolAdd
	{
		Dictionary<System.Type, FSNBaseOverlayDialog.Protocol>	m_nameToProtocol;	// 다이얼로그 타입 -> 프로토콜 매칭
		Stack<FSNBaseOverlayDialog.Protocol>					m_stack;			// 다이얼로그 스택

		/// <summary>
		/// 스택이 비었는지
		/// </summary>
		public bool IsEmpty
		{
			get { return m_stack.Count == 0; }
		}


		public DialogStack()
		{
			m_stack				= new Stack<FSNBaseOverlayDialog.Protocol>();
			m_nameToProtocol	= new Dictionary<System.Type, FSNBaseOverlayDialog.Protocol>();
		}

		public void AddDialogProtocol(System.Type dialogType, FSNBaseOverlayDialog.Protocol protocol)
		{
			m_nameToProtocol[dialogType] = protocol;

			// 콜백 등록 (다이얼로그 스스로 열고 닫게 하기 위해서)
			protocol.CallOpenCB		= () => Open(dialogType);
			protocol.CallCloseCB	= () => Close(dialogType);

			protocol.Initialize();					// 초기화
		}

		public T GetDialog<T>() where T : FSNBaseOverlayDialog
		{
			return m_nameToProtocol[typeof(T)].DialogRef as T;
		}


		/// <summary>
		/// 다이얼로그 열기
		/// </summary>
		public void Open<T>() where T : FSNBaseOverlayDialog
		{
			Open(typeof(T));
		}

		/// <summary>
		/// 다이얼로그 열기
		/// </summary>
		public void Open(System.Type dialogType)
		{
			var dialogp				= m_nameToProtocol[dialogType];			// 새로 열 다이얼로그
			if(dialogp.DialogRef.IsOpened)									// * 다이얼로그가 이미 열려있다면 메세지 표시 후 무시
			{
				Debug.LogWarning("Cannot open the dialog which is already opened.");
				return;
			}

			if (!IsEmpty)													// 현재 다이얼로그가 하나라도 열려있다면 추가 체크
			{
				var curdialog		= m_stack.Peek();
				
				if(curdialog.DialogRef.shouldCloseWhenOtherDialogPops)		// 현재 열린 다이얼로그가 다른 다이얼로그가 열리면 닫혀야 하는 것일 경우
				{
					Close(curdialog.DialogRef.GetType());					// 먼저 닫아준다
				}
				else
				{															// 닫는 경우가 아니므로, 입력 불가능한 상태로 만들어준다
					curdialog.Interactable = false;
					curdialog.ToBack();										// 뒤로 보내기 애니메이션
				}
			}

			dialogp.Reset();												// 열기 전에 리셋
			if(dialogp.Open())												// 다이얼로그 열기
			{
				dialogp.DialogRef.transform.SetAsLastSibling();				// 순서 맨 아래로 당기기 (= Z 순서상 제일 위)
				m_stack.Push(dialogp);										// 스택에 추가
			}
			else
			{
				Debug.LogWarningFormat("Cannot open dialog {0}", dialogType.Name);
			}
			
		}

		/// <summary>
		/// 다이얼로그 닫기
		/// </summary>
		public void Close<T>() where T : FSNBaseOverlayDialog
		{
			Close(typeof(T));
		}

		/// <summary>
		/// 다이얼로그 닫기
		/// </summary>
		public void Close(System.Type dialogType)
		{
			if (IsEmpty)														// 다이얼로그가 열려있는 것이 하나도 없다면 당연히 무시해야함
			{
				Debug.LogWarning("There's no dialog opened.");
				return;
			}

			var curdialog	= m_stack.Peek();
			if (curdialog != m_nameToProtocol[dialogType])						// 스택 최상층에 있는 다이얼로그가 아니면 닫을 수 없음
			{
				Debug.LogWarningFormat("Cannot close dialog {0} which is not at the top of the stack.", dialogType.Name);
				return;
			}

			if (curdialog.Close())												// 다이얼로그 닫기
			{
				m_stack.Pop();													// 스택에서 내리기
			}
			else
			{
				Debug.LogWarningFormat("Cannot close dialog {0}", dialogType.Name);
				return;
			}

			if (!IsEmpty)													// 다이얼로그가 남아있다면, 해당 다이얼로그의 입력 방지 해제
			{
				var prevdialog	= m_stack.Peek();
				prevdialog.Interactable	= true;
				prevdialog.ToForth();							// 앞으로 보내기 애니메이션
			}
		}
	}
}

using UnityEngine;
using System.Collections;
using System.Collections.Generic;


/// <summary>
/// 리스트 계열 UI 에 부착하는 컴포넌트
/// </summary>
public abstract class FSNBaseListUI<ChildT, ParamT> : MonoBehaviour
	where ChildT : FSNBaseListItem<ParamT>
{
	// Properties

	[SerializeField]
	ChildT          m_originalItem;							// 원본 아이템



	// Members

	List<ChildT>    m_itemList  = new List<ChildT>();		// 아이템 목록
	
	

	void Awake()
	{
		m_originalItem.gameObject.SetActive(false);		// 원본 아이템은 비활성화해놓기
	}

	/// <summary>
	/// 리스트 모두 지우기
	/// </summary>
	public void Clear()
	{
		var count       = m_itemList.Count;
		for(int i = 0; i < count; i++)
		{
			var item    = m_itemList[i];
			item.Remove();
		}

		m_itemList.Clear();
	}

	/// <summary>
	/// 아이템 생성
	/// </summary>
	/// <param name="parameter"></param>
	public void AddItem(ParamT parameter)
	{
		var newGO				= Instantiate<GameObject>(m_originalItem.gameObject);   // 원본해서 복제한다.
		newGO.SetActive(true);															// 복제본 active상태로
		newGO.transform.SetParent(m_originalItem.transform.parent, false);				// 원본과 같은 부모 아래에 둔다

		var comp				= newGO.GetComponent<ChildT>();                         // 컴포넌트 구하기
		comp.SetupData(parameter);														// 내용 채우기

		m_itemList.Add(comp);															// 리스트에 추가한다.
	}

	/// <summary>
	/// 이미 생성된 아이템을 업데이트
	/// </summary>
	/// <param name="index"></param>
	/// <param name="parameter"></param>
	public void UpdateItem(int index, ParamT parameter)
	{
		m_itemList[index].SetupData(parameter);
	}
}

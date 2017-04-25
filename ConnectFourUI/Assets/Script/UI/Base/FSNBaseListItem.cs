using UnityEngine;
using System.Collections;


/// <summary>
/// WSBaseListUI 에 사용하는 컴포넌트
/// </summary>
public abstract class FSNBaseListItem<ParamT> : MonoBehaviour
{
	public abstract void SetupData(ParamT parameter);

	/// <summary>
	/// 이 아이템 삭제하기
	/// </summary>
	public void Remove()
	{
		Destroy(gameObject);
	}
}

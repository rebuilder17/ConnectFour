using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.IO;
#if UNITY_EDITOR
using UnityEditor;
#endif
using System.Text;
using System;

/// <summary>
/// 각종 유틸리티 함수 모음
/// </summary>
public static class FSNUtils
{
	/// <summary>
	/// ICollection의 원소를 모두 복사한 Array를 만들어낸다
	/// </summary>
	/// <param name="enumerable"></param>
	/// <returns></returns>
	public static T[] MakeArray<T>(ICollection<T> collection)
	{
		var array	= new T[collection.Count];
		collection.CopyTo(array, 0);
		return array;
	}

	/// <summary>
	/// 문자열을 Enum 값으로 변환
	/// </summary>
	/// <typeparam name="T"></typeparam>
	/// <param name="value"></param>
	/// <returns></returns>
	public static T ParseEnum<T>(string value)
		where T : struct, IConvertible, IComparable, IFormattable
	{
		return (T)Enum.Parse(typeof(T), value);
	}

	/// <summary>
	/// enum 타입에 해당하는 값들을 전부 리턴
	/// </summary>
	/// <typeparam name="T"></typeparam>
	/// <returns></returns>
	public static T[] GetAllEnumValues<T>()
		where T : struct, IConvertible, IComparable, IFormattable
	{
		return System.Enum.GetValues(typeof(T)) as T[];
	}

	public static string RemoveAllWhiteSpaces(string str)
	{
		return System.Text.RegularExpressions.Regex.Replace(str, "[ \t\n\r]", "");	// 공백 모두 제거
	}

	public static Color ConvertHexCodeToColor(string hexcode)
	{
		uint r = 0, g = 0, b = 0;
		uint a	= 255;

		if (hexcode[0] == '#')					// # 이 있을 경우 제거 (헥사코드 표시)
			hexcode	= hexcode.Substring(1);

		uint hexNumber	= uint.Parse(hexcode, System.Globalization.NumberStyles.HexNumber);

		switch(hexcode.Length)
		{
			case 3:								// * RGB
				r	= BitExtract(hexNumber, 0xf, 8) * 17;
				g	= BitExtract(hexNumber, 0xf, 4) * 17;
				b	= BitExtract(hexNumber, 0xf, 0) * 17;
				break;

			case 4:								// * RGBA
				r	= BitExtract(hexNumber, 0xf, 12) * 17;
				g	= BitExtract(hexNumber, 0xf, 8)  * 17;
				b	= BitExtract(hexNumber, 0xf, 4)  * 17;
				a	= BitExtract(hexNumber, 0xf, 0)  * 17;
				break;

			case 6:								// * RRGGBB
				r	= BitExtract(hexNumber, 0xff, 16);
				g	= BitExtract(hexNumber, 0xff, 8);
				b	= BitExtract(hexNumber, 0xff, 0);
				break;

			case 8:								// * RRGGBBAA
				r	= BitExtract(hexNumber, 0xff, 24);
				g	= BitExtract(hexNumber, 0xff, 16);
				b	= BitExtract(hexNumber, 0xff, 8);
				a	= BitExtract(hexNumber, 0xff, 0);
				break;

			default:
				Debug.LogError("[ConvertHexCodeToColor] wrong hexcode : " + hexcode);
				break;
		}

		return new Color((float)r / 255f, (float)g / 255f, (float)b / 255f, (float)a / 255f);
	}

	private static uint BitExtract(uint input, uint mask, byte shift)
	{
		return (input & (mask << shift)) >> shift;
	}


	/// <summary>
	/// persistent 경로에 해당 이름의 파일이 존재하는지
	/// </summary>
	/// <param name="filename"></param>
	/// <returns></returns>
	public static bool CheckTextFileExists(string filename)
	{
		return File.Exists(Application.persistentDataPath + "/" + filename);
	}

	/// <summary>
	/// persistent 경로에서 파일 삭제
	/// </summary>
	/// <param name="filename"></param>
	/// <returns></returns>
	public static void DeleteTextFile(string filename)
	{
		File.Delete(Application.persistentDataPath + "/" + filename);
	}

	/// <summary>
	/// persistent 경로의 특정 파일에 문자열 저장
	/// </summary>
	/// <param name="filename"></param>
	/// <param name="data"></param>
	public static void SaveTextData(string filename, string data)
	{
		var fs = File.Open(Application.persistentDataPath + "/" + filename, FileMode.Create);
		using(fs)
		{
			var writer = new StreamWriter(fs);
			using(writer)
			{
				writer.Write(data);
			}
		}
	}

	/// <summary>
	/// persistent 경로의 특정 파일에서 문자열 로드하기
	/// </summary>
	/// <param name="filename"></param>
	/// <returns></returns>
	public static string LoadTextData(string filename)
	{
		var fs = File.OpenText(Application.persistentDataPath + "/" + filename);
		string text;
		using(fs)										// 파일을 읽고 json으로 파싱
		{
			text = fs.ReadToEnd();
		}
		return text;
	}

	/// <summary>
	/// Persistent 경로에 있는 특정 파일이 존재하는지 여부 체크
	/// </summary>
	/// <param name="filename"></param>
	/// <returns></returns>
	public static bool CheckDataFileExists(string filename)
	{
		return File.Exists(Application.persistentDataPath + "/" + filename);
	}

	/// <summary>
	/// 파일을 바이너리로 읽는다
	/// </summary>
	/// <param name="filename"></param>
	/// <param name="readLength"></param>
	/// <returns></returns>
	public static byte[] LoadBinaryData(string filename, long readLength = -1)
	{
		var fs		= File.OpenRead(Application.persistentDataPath + "/" + filename);

		if (readLength == -1 || readLength > fs.Length)	// -1이거나 읽는 길이보 파일 길이가 짧으면, 파일 길이만큼 읽는다.
		{
			readLength  = fs.Length;
		}

		var buffer  = new byte[readLength];
		using (fs)
		{
			fs.Read(buffer, 0, (int)readLength);	// int...?
		}

		return buffer;
	}

	/// <summary>
	/// 바이너리 데이터를 파일로 저장
	/// </summary>
	/// <param name="filename"></param>
	/// <param name="data"></param>
	public static void SaveBinaryData(string filename, byte[] data)
	{
		var fs      = File.OpenWrite(filename);
		using (fs)
		{
			fs.Write(data, 0, data.Length);
		}
	}


	/// <summary>
	/// 앱 종료, 혹은 Play 종료하기
	/// </summary>
	public static void QuitApp()
	{
#if UNITY_EDITOR
		EditorApplication.isPlaying = false;
#else
		Application.Quit();
#endif
	}

	public static string GenerateCurrentDateAndTimeString()
	{
		var dateTime	= System.DateTime.Now;
		return dateTime.ToString();
	}

	
	/// <summary>
	/// WWW 에서 사용하기 위한 steamingAssetsPath
	/// </summary>
#if UNITY_EDITOR || UNITY_STANDALONE_WIN
	public static readonly string streamingAssetsPathWWW = "file://" + Application.streamingAssetsPath + "/";
#elif UNITY_ANDROID
	public static readonly string streamingAssetsPathWWW = Application.streamingAssetsPath + "/";
#elif UNITY_IOS
	public static readonly string streamingAssetsPathWWW = "file://" + Application.streamingAssetsPath + "/";
#endif


	/// <summary>
	/// 경로를 분리하여 디렉토리 부분과 파일 이름으로 나눈다
	/// </summary>
	/// <param name="origpath"></param>
	/// <param name="path"></param>
	/// <param name="name"></param>
	public static void StripPathAndName(string origpath, out string path, out string name)
	{
		var pathdel = origpath.LastIndexOf('/');
		if (pathdel != -1)
		{
			path    = origpath.Substring(0, pathdel);
			name    = origpath.Substring(pathdel + 1);
		}
		else
		{
			path    = "";
			name    = origpath;
		}
	}
	
	/// <summary>
	/// 파일 확장자 삭제
	/// </summary>
	/// <param name="origpath"></param>
	/// <returns></returns>
	public static string RemoveFileExt(string origpath)
	{
		var pos	= origpath.LastIndexOf('.');
		if (pos == -1)
			return origpath;
		else
		{
			return origpath.Substring(0, pos);
		}
	}
	


	/// <summary>
	/// 간단한 파라미터 파싱 함수. 컴포넌트 파라미터 등에 사용 가능하다.
	/// 문법 : "변수=값, 변수 = 값   , ...."
	/// </summary>
	/// <param name="param"></param>
	/// <returns></returns>
	public static Dictionary<string, string> ParseParameterSimple(string param)
	{
		var pairDict    = new Dictionary<string, string>();
		var entries		= param.Split(',');
		var paircount   = entries.Length;
		for (int i = 0; i < paircount; i++)
		{
			var entry   = entries[i].Trim();

			if (string.IsNullOrEmpty(entry))				// 빈 문자열은 통과할 수 있게
				continue;

			var pair    = entry.Split('=');
			pairDict[pair[0].Trim()]	= pair[1].Trim();
		}

		return pairDict;
	}
	
	/// <summary>
	/// 트랜지션 시의 T 곡선 함수. TransitionWith 에서 쓰기 위한 것.
	/// 기본형 TransitionWith 에 이미 적용되어있으며, 오버라이드해서 구현할 시에는 따로 적용해줘야한다.
	/// (파라미터로 들어오는 ratio에는 이 함수가 적용되어있지 않다.)
	/// </summary>
	/// <param name="t"></param>
	/// <returns></returns>
	public static float TimeRatioFunction(float t)
	{
		return (Mathf.Sin((t * 2 + 1) * (Mathf.PI / 6)) - 0.5f) * 2;
	}


	/// <summary>
	/// 일정 지속시간동안 매 프레임마다 진행시간에 비례하는 변화 처리를 하기 위한 코루틴 함수 패턴.
	/// </summary>
	/// <param name="duration">지속시간</param>
	/// <param name="funcDuringLerp">지속시간 끝나기 전까지 매 프레임 호출. 파라미터로는 지금까지 흐른 시간의 비율이 리턴된다.</param>
	/// <param name="funcFinalize">지속시간 끝난 후 호출.</param>
	/// <returns></returns>
	public static IEnumerator DoLerpingCoroutine(float duration, System.Action<float> funcDuringLerp, System.Action funcFinalize)
	{
		var startTime	= Time.time;
		var elapsed		= 0f;

		while ((elapsed = Time.time - startTime) < duration)
		{
			funcDuringLerp(elapsed / duration);
			yield return null;
		}
		if (funcFinalize != null)
			funcFinalize();
	}

	/// <summary>
	/// 일정 지속시간동안 매 프레임마다 진행시간에 비례하는 변화 처리를 하기 위한 코루틴 함수 패턴.
	/// </summary>
	/// <param name="duration"></param>
	/// <param name="funcDuringLerp"></param>
	/// <param name="funcFinalize"></param>
	/// <returns></returns>
	public static Coroutine StartLerpingCoroutine(this MonoBehaviour context, float duration, System.Action<float> funcDuringLerp, System.Action funcFinalize)
	{
		return context.StartCoroutine(DoLerpingCoroutine(duration, funcDuringLerp, funcFinalize));
	}

	/// <summary>
	/// 일정 지속시간(리얼타임)동안 매 프레임마다 진행시간에 비례하는 변화 처리를 하기 위한 코루틴 함수 패턴.
	/// </summary>
	/// <param name="duration">지속시간</param>
	/// <param name="funcDuringLerp">지속시간 끝나기 전까지 매 프레임 호출. 파라미터로는 지금까지 흐른 시간의 비율이 리턴된다.</param>
	/// <param name="funcFinalize">지속시간 끝난 후 호출.</param>
	/// <returns></returns>
	public static IEnumerator DoLerpingCoroutineRealtime(float duration, System.Action<float> funcDuringLerp, System.Action funcFinalize)
	{
		var startTime	= Time.realtimeSinceStartup;
		var elapsed		= 0f;

		while ((elapsed = Time.realtimeSinceStartup - startTime) < duration)
		{
			funcDuringLerp(elapsed / duration);
			yield return null;
		}
		if (funcFinalize != null)
			funcFinalize();
	}

	/// <summary>
	/// 일정 지속시간(리얼타임)동안 매 프레임마다 진행시간에 비례하는 변화 처리를 하기 위한 코루틴 함수 패턴.
	/// </summary>
	/// <param name="duration"></param>
	/// <param name="funcDuringLerp"></param>
	/// <param name="funcFinalize"></param>
	/// <returns></returns>
	public static Coroutine StartLerpingCoroutineRealtime(this MonoBehaviour context, float duration, System.Action<float> funcDuringLerp, System.Action funcFinalize)
	{
		return context.StartCoroutine(DoLerpingCoroutineRealtime(duration, funcDuringLerp, funcFinalize));
	}
	//

	/// <summary>
	/// 로딩/파싱 구현에서 메인 쓰레드에서 돌리면서도 약간 async한 느낌으로 처리할 수 있게 하기 위해 (Coroutine)
	/// 처리 시간 단위를 측정하고 단위 시간을 초과했는지 알려준다.
	/// </summary>
	public class SliceTimeLimiter
	{
		// Members

		float			m_startTime;
		float			m_timeThreshold;


		public SliceTimeLimiter()
		{
			var framerate	= Application.targetFrameRate;			// 초당 프레임 수를 가져온다.
			if (framerate <= 0)										// 초당 프레임 수가 따로 설정되지 않은 경우, 60프레임을 기준으로 한다.
				framerate	= 60;

			m_timeThreshold	= (1f / (float)framerate) * 0.9f;		// 프레임 당 시간에 약간 여유값을 준다.
			//Debug.Log("time threshold : " + m_timeThreshold);
		}

		/// <summary>
		/// 측정 시간 리셋. 맨 처음 측정을 시작할 때 필요.
		/// </summary>
		public void Reset()
		{
			m_startTime		= Time.realtimeSinceStartup;
		}

		/// <summary>
		/// 실행 시간 측정.
		/// </summary>
		/// <returns>제한 시간에 도달하면 true를 리턴한다. 이 때는 현재 처리를 잠시 중단하고 다음 프레임으로 넘겨야한다.</returns>
		public bool CheckTimeLimit()
		{
			var hitthelimit	= Time.realtimeSinceStartup > (m_startTime + m_timeThreshold);	// 측정 시작때보다 threshold 이상으로 시간이 지났으면 true
			if (hitthelimit)																// 한계 시간에 도달했으면 측정 시간을 현재값으로 리셋
			{
				//Debug.Log("time elapsed : " + (Time.realtimeSinceStartup - (m_startTime + m_timeThreshold)));
				Reset();
			}
			return hitthelimit;
		}
	}
}

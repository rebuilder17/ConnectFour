using UnityEngine;
using System.Collections;

public class DebugConsole : MonoBehaviour
{
	// Members

	bool            m_enableConsole = false;
	string			m_buffer		= "";

	private void Awake()
	{
		Application.logMessageReceived += ProcessLogMessage;
	}

	void Update()
	{
		if (Input.GetKeyDown(KeyCode.BackQuote))
		{
			m_enableConsole = !m_enableConsole;
		}
	}

	private void OnGUI()
	{
		if (m_enableConsole)
		{
			var tfstyle			= GUI.skin.GetStyle("TextField");
			tfstyle.alignment	= TextAnchor.LowerLeft;
			tfstyle.richText	= true;
			tfstyle.fontSize	= 16;
			GUI.TextArea(new Rect(5, 5, 600, 600), m_buffer, tfstyle);
		}
	}

	void ProcessLogMessage(string logString, string stackTrace, LogType type)
	{
		Color color;
		switch (type)
		{
			case LogType.Warning:
				color = Color.yellow;
				break;

			case LogType.Exception:
			case LogType.Assert:
			case LogType.Error:
				color = Color.red;
				break;

			case LogType.Log:
			default:
				color = Color.white;
				break;
		}

		PushMessage(logString, color);
	}

	void PushMessage(string message, Color color)
	{
		var formatstr   = (color == Color.white)? "\n{0}" : string.Format("\n<color={0}>{{0}}</color>", ColorToHex(color));
		m_buffer		+= string.Format(formatstr, message);
	}

	const string c_hexChars = "0123456789ABCDEF";
	string ColorToHex(Color color)
	{
		var r   = (int)(color.r * 255f);
		var g   = (int)(color.g * 255f);
		var b	= (int)(color.b * 255f);

		return string.Format("#{0}{1}{2}{3}{4}{5}",
			c_hexChars[r / 16], c_hexChars[r % 16],
			c_hexChars[g / 16], c_hexChars[g % 16],
			c_hexChars[b / 16], c_hexChars[b % 16]);
	}
}

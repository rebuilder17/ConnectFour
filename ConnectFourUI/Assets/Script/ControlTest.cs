using UnityEngine;
using System.Collections;

public class ControlTest : MonoBehaviour
{
	[SerializeField]
	GameStateController	m_controller;

	GameState m_gameState;
	string m_msgToSend	= "";

	// Use this for initialization
	void Start()
	{
		m_gameState	= new GameState();
		m_controller.MakeNewConnection(m_gameState);
	}

	// Update is called once per frame
	void Update()
	{

	}

	void SendInput(string msg)
	{
		var processed	= false;
		if (m_controller.waitingForInput)
		{
			switch(m_controller.requestedInput)
			{
				case GameStateController.InputType.SolverIndex:
					m_controller.InputSolverIndex(int.Parse(msg));
					processed	= true;
					break;

				case GameStateController.InputType.MovePosition:
					{
						var split	= msg.Split(',');
						m_controller.InputMovePosition(int.Parse(split[0]), int.Parse(split[1]));
						processed = true;
					}
					break;
			}
		}

		if (!processed)
		{
			Debug.LogWarning("Not processed input : " + msg);
		}
	}

	void OnGUI()
	{
		m_msgToSend			= GUI.TextField(new Rect(10, 570, 580, 20), m_msgToSend);

		// response to "enter key" press
		var ev              = Event.current;
		if (ev.type == EventType.KeyDown && ev.character == '\n')
		{
			SendInput(m_msgToSend);
			m_msgToSend		= "";
		}
	}
}

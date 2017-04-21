using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.ComponentModel;
using System.IO;
using System.Threading;

public class IPCConnection
{
	/// <summary>
	/// 프로세스가 보내는 메세지
	/// </summary>
	public class Message
	{
		public enum Header
		{
			None		= 0,

			Await,
			Terminate,
			Message,
		}

		public Header header;
		public string message;
	}


	// Constants

	const string	c_header_await		= "!AWAIT";
	const string	c_header_terminate	= "!TERMINATE";
	const string	c_header_message	= "!MESSAGE:";


	// Members

	Queue<string>	m_sendQueue;
	Queue<Message>	m_recvQueue;

	Queue<string>	m_stdoutQueue;
	Queue<string>	m_stderrQueue;

	Process			m_targetProcess;
	Thread			m_thread;

	volatile int	m_needProcessHalt;				// 프로세스 종료 플래그
	volatile int	m_processIsRunning;				// 프로세스 실행중인지 여부

#pragma warning disable 0420	// Interlocked API 때문에 발생하는 warning 죽이기

	bool needProcessHalt
	{
		get
		{
			return m_needProcessHalt != 0;
		}

		set
		{
			Interlocked.Exchange(ref m_needProcessHalt, value ? 1 : 0);
		}
	}

	/// <summary>
	/// 프로세스 실행중인지
	/// </summary>
	public bool processIsRunning
	{
		get
		{
			return m_processIsRunning != 0;
		}
		private set
		{
			Interlocked.Exchange(ref m_processIsRunning, value ? 1 : 0);
		}
	}

#pragma warning restore 0420

	public IPCConnection()
	{
		m_sendQueue		= new Queue<string>();
		m_recvQueue		= new Queue<Message>();
		m_stdoutQueue	= new Queue<string>();
		m_stderrQueue	= new Queue<string>();
	}


	/// <summary>
	/// 프로세스가 보낸 메세지 문자열 가져오기. 보낸 게 없거나 전부 읽었다면 null
	/// </summary>
	/// <returns></returns>
	public Message PollReceive()
	{
		lock (m_recvQueue)
		{
			if (m_recvQueue.Count > 0)
				return m_recvQueue.Dequeue();
			else
				return null;
		}
	}

	public string PollStdOut()
	{
		lock (m_stdoutQueue)
		{
			if (m_stdoutQueue.Count > 0)
				return m_stdoutQueue.Dequeue();
			else
				return null;
		}
	}

	public string PollStdErr()
	{
		lock (m_stderrQueue)
		{
			if (m_stderrQueue.Count > 0)
				return m_stderrQueue.Dequeue();
			else
				return null;
		}
	}

	/// <summary>
	/// 프로세스 센드 큐에 넣기
	/// </summary>
	/// <param name="message"></param>
	public void Send(string message)
	{
		lock (m_sendQueue)
		{
			m_sendQueue.Enqueue(message);
		}
	}

	public void Connect(string processPath)
	{
		m_targetProcess						= new Process();

		var startInfo						= m_targetProcess.StartInfo;
		startInfo.FileName					= processPath;
		startInfo.WorkingDirectory			= Path.GetDirectoryName(processPath);

		startInfo.UseShellExecute			= false;
		startInfo.RedirectStandardInput		= true;
		startInfo.RedirectStandardOutput	= true;
		startInfo.RedirectStandardError		= true;

		m_targetProcess.StartInfo			= startInfo;

		needProcessHalt						= false;
		m_thread							= new Thread(new ThreadStart(ThreadRun));	// 쓰레드 시작
		m_thread.Start();
	}

	public void Kill()
	{
		// 쓰레드가 알아서 프로세스를 죽이고 스스로 종료될 수 있도록 플래그만 올려둔다.

		needProcessHalt	= true;

		m_targetProcess	= null;
		m_thread		= null;
	}

	void ThreadRun()
	{
		StreamWriter	stdin		= null;
		//StreamReader	stdout		= null;
		//StreamReader	stderr		= null;

		try
		{
			processIsRunning		= true;

			m_targetProcess.OutputDataReceived	+= OnStdOutRead;
			m_targetProcess.ErrorDataReceived	+= OnStdErrRead;

			m_targetProcess.Start();								// 프로세스 시작
			stdin		= new StreamWriter(m_targetProcess.StandardInput.BaseStream, new System.Text.UTF8Encoding(false));	// BOM 추가하지 않도록
			//stdout	= m_targetProcess.StandardOutput;
			//stderr	= m_targetProcess.StandardError;

			m_targetProcess.BeginOutputReadLine();
			m_targetProcess.BeginErrorReadLine();
			
			var keepRunning	= true;
			while (keepRunning)
			{
				if (m_targetProcess.HasExited)						// 프로세스가 이미 종료된 경우, 나오기
				{
					UnityEngine.Debug.Log("processed exited!");
					break;
				}

				if (needProcessHalt)								// 프로세스 종료 플래그가 올라간 경우, 처리하고 루프 깨기
				{
					UnityEngine.Debug.Log("halt flag on!");
					try
					{
						m_targetProcess.Kill();
					}
					catch(System.InvalidOperationException e) { }	// 바로 직전에 프로세스가 죽어버린 경우가 있을 수 있다. Exception을 걸러낸다

					break;
				}

				lock (m_sendQueue)
				{
					while (m_sendQueue.Count > 0)					// 보낼 메세지가 있는 경우, 루프 시작
					{
						var send	= m_sendQueue.Dequeue();
						UnityEngine.Debug.Log("need send this : " + send);
						stdin.WriteLine(send);						// stdin에 보낸다
					}
					stdin.Flush();
				}

				Thread.Sleep(0);									// 루프 돌기 전에 쓰레드 잠깐 쉬기
			}
		}
		catch (System.ComponentModel.Win32Exception we)
		{
			lock (m_stderrQueue)										// 에러 큐에 exception 정보 넣기
			{
				m_stderrQueue.Enqueue(string.Format("Win32Exception occured! error code : {0}, {1}", System.Convert.ToString(we.ErrorCode, 16), we.Message));
			}
		}
		catch (System.Exception e)
		{
			lock (m_stderrQueue)										// 에러 큐에 exception 정보 넣기
			{
				m_stderrQueue.Enqueue(e.ToString());
			}
		}
		finally
		{
			UnityEngine.Debug.Log("Terminating...");

			processIsRunning	= false;

			if (stdin != null)		stdin.Close();
			//if (stdout != null)		stdout.Close();
			//if (stderr != null)		stderr.Close();

			m_targetProcess.WaitForExit();
			m_targetProcess.Close();
		}
	}

	void OnStdOutRead(object sender, DataReceivedEventArgs args)
	{
		var line	= args.Data;
		if (string.IsNullOrEmpty(line))					// 빈 줄 / null 은 무시
			return;

		line		= line.TrimEnd();

		UnityEngine.Debug.Log("received line : " + line);
		switch (line)
		{
			case c_header_await:						// 입력 기다리는 경우

				lock (m_recvQueue)						// await 메세지
					m_recvQueue.Enqueue(new Message() { header = Message.Header.Await });

				//while (true)
				//{
				//	if (needProcessHalt)	// NOTE : 입력 큐 기다리는 동안에 프로세스 종료 플래그가 서도 반응해야 한다.
				//		break;

				//	lock (m_sendQueue)
				//	{
				//		if (m_sendQueue.Count > 0)		// 보낼 메세지가 있는 경우, 루프 시작
				//		{
				//			var send	= m_sendQueue.Dequeue();
				//			stdin.WriteLine(send);		// stdin에 보낸다
				//			break;						// 전송 루프 나오기
				//		}
				//	}

				//	Thread.Sleep(0);					// 전송할 게 아직 없는 경우 쓰레드를 잠시 쉬고 다시 체크한다.
				//}
				break;

			case c_header_terminate:					// 프로세스 종료

				lock (m_recvQueue)						// await 메세지
					m_recvQueue.Enqueue(new Message() { header = Message.Header.Terminate });

				needProcessHalt	= true;
				break;

			default:
				if (line.StartsWith(c_header_message))	// 메세지 전송인 경우
				{
					var msg	= line.Substring(c_header_message.Length);
					lock (m_recvQueue)
					{
						m_recvQueue.Enqueue(new Message()
						{ header = Message.Header.Message, message = msg });		// 큐에 메세지를 넣는다.
					}
				}
				else
				{										// 일반 stdout
					lock (m_stdoutQueue)
					{
						m_stdoutQueue.Enqueue(line);
					}
				}
				break;
		}
	}

	void OnStdErrRead(object sender, DataReceivedEventArgs args)
	{
		lock (m_stderrQueue)
		{
			m_stderrQueue.Enqueue(args.Data);
		}
	}
}
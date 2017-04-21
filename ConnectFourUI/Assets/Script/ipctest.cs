using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Diagnostics;

public class ipctest : MonoBehaviour
{

	// Use this for initialization
	void Start ()
	{
		UnityEngine.Debug.Log(Application.streamingAssetsPath);
		//var startinfo						= new ProcessStartInfo("C:\\Windows\\System32\\cmd.exe");
		//var startinfo						= new ProcessStartInfo("E:\\exe.win-amd64-3.6\\main.exe");
		var startinfo						= new ProcessStartInfo("\"E:\\ReBsData\\GitHub\\ConnectFour\\ConnectFourAI\\build\\exe.win-amd64-3.6\\main.exe\"");
		startinfo.UseShellExecute			= false;
		startinfo.RedirectStandardInput		= true;
		startinfo.RedirectStandardOutput	= true;
		startinfo.CreateNoWindow	= true;

		//startinfo.Arguments			= "/C E:\\ReB's Data\\GitHub\\ConnectFour\\ConnectFourAI\\build\\exe.win-amd64-3.6\\main.exe";

		try
		{
			var p	= new Process();
			p.StartInfo	= startinfo;
			p.Start();
			p.WaitForInputIdle();

			var inputStream	= new System.IO.StreamWriter(p.StandardInput.BaseStream, System.Text.Encoding.ASCII);

			inputStream.WriteLine("dir");
			inputStream.WriteLine("exit");
			inputStream.Flush();

			var outputStream	= new System.IO.StreamReader(p.StandardOutput.BaseStream, System.Text.Encoding.Default);

			var output	= outputStream.ReadToEnd();
			UnityEngine.Debug.Log(output);
		}
		catch(System.ComponentModel.Win32Exception e)
		{
			UnityEngine.Debug.LogErrorFormat("win32 error code : {0}", System.Convert.ToString(e.ErrorCode, 16));
		}
	}
}

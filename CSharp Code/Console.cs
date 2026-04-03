using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32.SafeHandles;
using UnityEngine;

namespace BMSLib
{
	public static class ConsoleWindow
	{
		// Windows API 常量
		private const int STD_INPUT_HANDLE = -10;
		private const int STD_OUTPUT_HANDLE = -11;
		private const uint ENABLE_QUICK_EDIT_MODE = 0x0040;
		private const uint ENABLE_EXTENDED_FLAGS = 0x0080;

		// SetWindowPos 常量
		private static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
		private const uint SWP_NOSIZE = 0x0001;
		private const uint SWP_NOMOVE = 0x0002;
		private const uint SWP_SHOWWINDOW = 0x0040;

		private static TextWriter oldOutput;
		public static bool isInitialized = false;

		// 神级标签：让 Unity 引擎在加载场景前自动调用此方法，实现零侵入自启
		[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
		public static void Initialize()
		{
			if (ConsoleWindow.isInitialized)
			{
				return;
			}

			if (!ConsoleWindow.AttachConsole(4294967295U))
			{
				ConsoleWindow.AllocConsole();
			}

			ConsoleWindow.DisableQuickEditMode();

			ConsoleWindow.oldOutput = Console.Out;
			try
			{
				// 1. 重定向输出流
				Stream stream = new FileStream(new SafeFileHandle(ConsoleWindow.GetStdHandle(-11), true), FileAccess.Write);
				Encoding ascii = Encoding.ASCII;
				Console.SetOut(new StreamWriter(stream, ascii)
				{
					AutoFlush = true
				});

				// 2. 设置控制台 UI
				Console.Title = "MUSYNX Delay";
				Console.ForegroundColor = ConsoleColor.Red;
				Console.BackgroundColor = ConsoleColor.White;
				Console.SetWindowSize(30, 4);
				Console.Clear();

				// 3. 将控制台窗口置顶 (TopMost)
				IntPtr consoleWindowHandle = ConsoleWindow.GetConsoleWindow();
				if (consoleWindowHandle != IntPtr.Zero)
				{
					// 忽略移动和大小调整，仅修改 Z 轴层级使其置顶
					ConsoleWindow.SetWindowPos(consoleWindowHandle, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW);
				}
			}
			catch (Exception ex)
			{
				Debug.Log("Couldn't redirect output or set console UI: " + ex.Message);
			}

			ConsoleWindow.isInitialized = true;
		}

		private static void DisableQuickEditMode()
		{
			try
			{
				IntPtr consoleHandle = ConsoleWindow.GetStdHandle(STD_INPUT_HANDLE);
				uint consoleMode;
				if (ConsoleWindow.GetConsoleMode(consoleHandle, out consoleMode))
				{
					consoleMode &= ~ENABLE_QUICK_EDIT_MODE;
					consoleMode |= ENABLE_EXTENDED_FLAGS;
					ConsoleWindow.SetConsoleMode(consoleHandle, consoleMode);
				}
			}
			catch (Exception ex)
			{
				Debug.Log("Failed to disable QuickEdit mode: " + ex.Message);
			}
		}

		public static void Shutdown()
		{
			if (!ConsoleWindow.isInitialized)
			{
				return;
			}

			if (ConsoleWindow.oldOutput != null)
			{
				Console.SetOut(ConsoleWindow.oldOutput);
			}
			ConsoleWindow.FreeConsole();
			ConsoleWindow.isInitialized = false;
		}

		// --- 引入的 Windows API ---

		[DllImport("kernel32.dll", SetLastError = true)]
		private static extern bool AttachConsole(uint dwProcessId);

		[DllImport("kernel32.dll", SetLastError = true)]
		private static extern bool AllocConsole();

		[DllImport("kernel32.dll", SetLastError = true)]
		private static extern bool FreeConsole();

		[DllImport("kernel32.dll", CallingConvention = CallingConvention.StdCall, CharSet = CharSet.Auto, SetLastError = true)]
		private static extern IntPtr GetStdHandle(int nStdHandle);

		[DllImport("kernel32.dll")]
		private static extern bool GetConsoleMode(IntPtr hConsoleHandle, out uint lpMode);

		[DllImport("kernel32.dll")]
		private static extern bool SetConsoleMode(IntPtr hConsoleHandle, uint dwMode);

		// 获取控制台窗口句柄
		[DllImport("kernel32.dll", ExactSpelling = true)]
		private static extern IntPtr GetConsoleWindow();

		// 设置窗口位置和层级 (用于置顶)
		[DllImport("user32.dll", SetLastError = true)]
		[return: MarshalAs(UnmanagedType.Bool)]
		private static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
	}
}

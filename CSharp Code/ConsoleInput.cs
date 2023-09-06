using System;

namespace BMSLib
{
	public class ConsoleInput
	{
		public event Action<string> OnInputText;

		public void ClearLine()
		{
			Console.CursorLeft = 0;
			Console.Write(new string(' ', Console.BufferWidth));
			Console.CursorTop--;
			Console.CursorLeft = 0;
		}

		public void RedrawInputLine()
		{
			if (this.inputString.Length == 0)
			{
				return;
			}
			if (Console.CursorLeft > 0)
			{
				this.ClearLine();
			}
			Console.ForegroundColor = ConsoleColor.Green;
			Console.Write(this.inputString);
		}

		internal void OnBackspace()
		{
			if (this.inputString.Length < 1)
			{
				return;
			}
			this.inputString = this.inputString.Substring(0, this.inputString.Length - 1);
			this.RedrawInputLine();
		}

		internal void OnEscape()
		{
			this.ClearLine();
			this.inputString = "";
		}

		internal void OnEnter()
		{
			this.ClearLine();
			if (this.kD == 9999f)
			{
				this.inputString = "Game Start!";
			}
			else
			{
				this.inputString = string.Format("Hit Delay: {0}ms", this.kD);
			}
			float num = Math.Abs(this.kD);
			if (num < 5f)
			{
				Console.ForegroundColor = ConsoleColor.Cyan;
			}
			else if (num < 10f)
			{
				Console.ForegroundColor = ConsoleColor.DarkCyan;
			}
			else if (num < 45f)
			{
				Console.ForegroundColor = ConsoleColor.DarkBlue;
			}
			else if (num < 90f)
			{
				Console.ForegroundColor = ConsoleColor.DarkGreen;
			}
			else if (num < 150f)
			{
				Console.ForegroundColor = ConsoleColor.DarkMagenta;
			}
			else
			{
				Console.ForegroundColor = ConsoleColor.Red;
			}
			Console.WriteLine("> " + this.inputString);
			string obj = this.inputString;
			this.inputString = "";
			if (this.OnInputText != null)
			{
				this.OnInputText(obj);
			}
		}

		public void Update()
		{
			if (!Console.KeyAvailable)
			{
				return;
			}
			ConsoleKeyInfo consoleKeyInfo = Console.ReadKey();
			if (consoleKeyInfo.Key == ConsoleKey.Enter)
			{
				this.OnEnter();
				return;
			}
			if (consoleKeyInfo.Key == ConsoleKey.Backspace)
			{
				this.OnBackspace();
				return;
			}
			if (consoleKeyInfo.Key == ConsoleKey.Escape)
			{
				this.OnEscape();
				return;
			}
			if (consoleKeyInfo.KeyChar != '\0')
			{
				this.inputString += consoleKeyInfo.KeyChar.ToString();
				this.RedrawInputLine();
				return;
			}
		}

		public ConsoleInput()
		{
		}

		public string inputString;

		public float kD;
	}
}

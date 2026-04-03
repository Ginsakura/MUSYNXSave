using System;
using System.Collections.Generic;

namespace BMSLib
{
	// Token: 0x0200001F RID: 31
	public class JudgeGrade
	{
		public static void Reset()
		{
			/*
			 * and so on...
			 */
			//JudgeGrade.TotalCombo = 0;
			//JudgeGrade.uploadScore = new float[6];
			Console.Clear();
			Console.ForegroundColor = ConsoleColor.Red;
			Console.WriteLine("> SongStart!");
		}

		public static int GetJudgeGrade(long knockDistance)
		{
			if (knockDistance >= -1500000L)
			{
				long kd = Math.Abs(knockDistance);
				if (kd < 50000L)
					Console.ForegroundColor = ConsoleColor.Cyan;
				else if (kd < 100000L)
					Console.ForegroundColor = ConsoleColor.DarkCyan;
				else if (kd < 450000L)
					Console.ForegroundColor = ConsoleColor.DarkBlue;
				else if (kd < 900000L)
					Console.ForegroundColor = ConsoleColor.DarkGreen;
				else if (kd < 1500000L)
					Console.ForegroundColor = ConsoleColor.DarkMagenta;
				else
					Console.ForegroundColor = ConsoleColor.Red;
				Console.WriteLine("> Delay: {0}ms", knockDistance/10000.0f);
			}
			//int result = -1;
			//bool flag = knockDistance < 0L;
			//knockDistance = Math.Abs(knockDistance);
			//if (knockDistance < 450000L){
			/*
			 * and so on...
			 */
			return 0;
		}
	}
}

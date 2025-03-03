using System;

namespace BMSLib
{
	// Token: 0x0200001F RID: 31
	public class JudgeGrade
	{
		public static ConsoleInput ci = new ConsoleInput();
		public static void Reset()
		{
			//JudgeGrade.baseAccuracy = 0f;
			//JudgeGrade.exAccuracy = 0f;
			//JudgeGrade.exactAccuracy = 0f;
			//JudgeGrade.greatAccuracy = 0f;
			//JudgeGrade.rightAccuracy = 0f;
			//JudgeGrade.TotalEx = 0;
			//JudgeGrade.TotalExact = 0;
			//JudgeGrade.TotalGreat = 0;
			//JudgeGrade.TotalRight = 0;
			//JudgeGrade.TotalMiss = 0;
			//JudgeGrade.TotalCombo = 0;
			//JudgeGrade.uploadScore = new float[6];
			if (GloHasConsole.hasConsole == 0)
			{
				new ConsoleWindow().Initialize();
				Console.Title = "MUSYNX Delay";
				Console.ForegroundColor = ConsoleColor.Red;
				Console.BackgroundColor = ConsoleColor.White;
				Console.SetWindowSize(30, 4);
				GloHasConsole.hasConsole = 1;
			}
			Console.Clear();
			JudgeGrade.ci.kD = 9999f;
			JudgeGrade.ci.OnEnter();
		}

		public static int GetJudgeGrade(long knockDistance)
		{
			if (knockDistance >= -1500000L)
			{
				JudgeGrade.ci.kD = (float)knockDistance / 10000f;
				JudgeGrade.ci.OnEnter();
			}
			//int result = -1;
			//bool flag = knockDistance < 0L;
			//knockDistance = Math.Abs(knockDistance);
			//if (knockDistance < 450000L){}
		}
	}
}

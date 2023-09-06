using System;

namespace BMSLib
{
	// Token: 0x0200001F RID: 31
	public class JudgeGrade
	{
		public static void Reset()
		{
			JudgeGrade.baseAccuracy = 0f;
			JudgeGrade.exAccuracy = 0f;
			JudgeGrade.exactAccuracy = 0f;
			JudgeGrade.greatAccuracy = 0f;
			JudgeGrade.rightAccuracy = 0f;
			JudgeGrade.TotalEx = 0;
			JudgeGrade.TotalExact = 0;
			JudgeGrade.TotalGreat = 0;
			JudgeGrade.TotalRight = 0;
			JudgeGrade.TotalMiss = 0;
			JudgeGrade.TotalCombo = 0;
			JudgeGrade.uploadScore = new float[6];
			if (GloHasConsole.hasConsole == 1)
			{
				new ConsoleWindow().Initialize();
				Console.Title = "MUSYNX Delay";
				Console.ForegroundColor = ConsoleColor.Red;
				Console.BackgroundColor = ConsoleColor.White;
				Console.SetWindowSize(30, 4);
				GloHasConsole.hasConsole = 0;
			}
			Console.Clear();
			JudgeGrade.ci.kD = 9999f;
			JudgeGrade.ci.OnEnter();
		}

		public static int GetJudgeGrade(long knockDistance)
		{
			int result = -1;
			bool flag = knockDistance < 0L;
			float num = (float)knockDistance / 10000f;
			if (num >= -150f)
			{
				JudgeGrade.ci.kD = num;
				JudgeGrade.ci.OnEnter();
			}
			knockDistance = Math.Abs(knockDistance);
			if (knockDistance < 450000L)
			{
				result = 0;
				JudgeGrade.baseAccuracy += 1f;
				JudgeGrade.exAccuracy += 0.05f + 0.1f * (1f - (float)knockDistance / 450000f);
				JudgeGrade.exactAccuracy += 1f;
				JudgeGrade.TotalEx++;
				JudgeGrade.TotalExact++;
			}
			else if (knockDistance < 900000L)
			{
				result = 1;
				JudgeGrade.baseAccuracy += 1f;
				JudgeGrade.exactAccuracy += 1f;
				JudgeGrade.TotalExact++;
			}
			else if (knockDistance < 1500000L)
			{
				result = 2;
				JudgeGrade.baseAccuracy += 0.7f + 0.2f * (1f - (float)(knockDistance - 900000L) / 600000f);
				JudgeGrade.greatAccuracy += 0.7f + 0.2f * (1f - (float)(knockDistance - 900000L) / 600000f);
				JudgeGrade.TotalGreat++;
			}
			else if (knockDistance < 2500000L)
			{
				if (!flag)
				{
					result = 3;
					JudgeGrade.baseAccuracy += 0.1f + 0.5f * (1f - (float)(knockDistance - 900000L) / 1600000f);
					JudgeGrade.rightAccuracy += 0.1f + 0.5f * (1f - (float)(knockDistance - 900000L) / 1600000f);
					JudgeGrade.TotalRight++;
				}
			}
			else if (!flag)
			{
				result = 4;
				JudgeGrade.TotalMiss++;
			}
			return result;
		}
		public static ConsoleInput ci = new ConsoleInput();
	}
}

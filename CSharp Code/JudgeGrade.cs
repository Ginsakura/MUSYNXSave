using System;
using System.Collections.Generic;

namespace BMSLib
{
	// Token: 0x0200001F RID: 31
	public class JudgeGrade
	{
		public static List<long> hitMap = new List();
		
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
			OptimizedConsole.InitializeDefault();
			OptimizedConsole.WriteLine("> Game Start!");
			JudgeGrade.hitMap.Clear();
		}

		public static int GetJudgeGrade(long knockDistance)
		{
			if (knockDistance >= -1500000L)
			{
				JudgeGrade.hitMap.Add(knockDistance);
				OptimizedConsole.WriteHitDelay(knockDistance);
			}
			//int result = -1;
			//bool flag = knockDistance < 0L;
			//knockDistance = Math.Abs(knockDistance);
			//if (knockDistance < 450000L){}
		}
	}
}

using System;
using System.Collections.Generic;

namespace BMSLib
{
    // Token: 0x0200001F RID: 31
    public class JudgeGrade
    {
        public static List<long> hitMap = new List<long>();

        public static void Reset()
        {
            /*
             * and so on...
             */
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
            //if (knockDistance < 450000L){
            /*
             * and so on...
             */
            return 0;
        }
    }
}
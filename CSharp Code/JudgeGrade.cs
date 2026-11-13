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
            ConsoleWindow.Initialize();
            Console.Clear();
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine("> SongStart!");
        }

        public static int GetJudgeGrade(long knockDistance)
        {
            if (knockDistance >= -1500000L)
            {
                long kd = Math.Abs(knockDistance);
                bool kDsign = knockDistance < 0L;
                // -5 ~ +5
                if (kd < 50000L)
                    { Console.ForegroundColor = ConsoleColor.Cyan; }
                // +5 ~ +10 & -5 ~ -10
                else if (kd < 100000L)
                {
                    if (kDsign)
                        { Console.ForegroundColor = ConsoleColor.Yellow; }
                    else
                        { Console.ForegroundColor = ConsoleColor.DarkCyan; }
                }
                // +10 ~ +45 & -10 ~ -45
                else if (kd < 450000L)
                {
                    if (kDsign)
                        { Console.ForegroundColor = ConsoleColor.DarkYellow; }
                    else
                        { Console.ForegroundColor = ConsoleColor.Blue; }
                }
                // 45 ~ 90 & -45 ~ -90
                else if (kd < 900000L)
                {
                    if (kDsign)
                    { Console.ForegroundColor = ConsoleColor.Green; }
                    else
                    { Console.ForegroundColor = ConsoleColor.Magenta; }
                }
                // 90 ~ 150 & -90 ~ -150
                else if (kd < 1500000L)
                    { Console.ForegroundColor = ConsoleColor.DarkMagenta; }
                // 150 ~ 250
                else
                    { Console.ForegroundColor = ConsoleColor.Red; }
                Console.WriteLine("> Delay: {0}ms", knockDistance / 10000.0f);
            }
            //int result = -1;
            //bool flag = knockDistance < 0L;
            /*
			 * and so on...
			 */
            return 0;
        }
    }
}

public partial class SongInfoCore
{
	internal void UpdateSync(int maxCombo)
	{
		//this.MaxComboThis = maxCombo;
		//this.SyncNumberThis = JudgeGrade.GetSyncNumber(maxCombo);
		Console.ForegroundColor = ConsoleColor.Red;
		Console.WriteLine("> SongInfo::SID:{0},SN:{1},MC:{2},TC:{3}", new object[]
		{
			this.SongId,
			this.SyncNumberThis,
			this.MaxComboThis,
			JudgeGrade.TotalCombo
		});
		//UserMemory.AddPlayCount(this.SongId);
	}
}
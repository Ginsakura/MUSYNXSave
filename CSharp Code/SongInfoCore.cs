public partial class SongInfoCore
{
	// Token: 0x06000430 RID: 1072 RVA: 0x0003E128 File Offset: 0x0003C528
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
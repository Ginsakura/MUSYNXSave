using System;
using System.Collections.Generic;
using BMSLib;
using NPinyin;
using Steamworks;
using UnityEngine;

// Token: 0x020000D2 RID: 210
public class SongInfoCore
{
	// Token: 0x060006DC RID: 1756 RVA: 0x000504A8 File Offset: 0x0004E6A8
	internal void UpdateSync(int maxCombo)
	{
		//this.MaxComboThis = maxCombo;
		//this.SyncNumberThis = JudgeGrade.GetSyncNumber(maxCombo);
		LocalUdpClient.SendStructuredData(this.SongId, this.SyncNumberThis, this.MaxComboThis, JudgeGrade.TotalCombo, JudgeGrade.hitMap)
		//UserMemory.AddPlayCount(this.SongId);
		//if (this.SyncNumberThis > this.saveInfo.SyncNumber)
		//{
		//	this.saveInfo.SyncNumber = this.SyncNumberThis;
		//	this.NewRecordThis = true;
		//}
		//else
		//{
		//	this.NewRecordThis = (this.SongId == 0);
		//}
		//this.UploadScore();
	}
}
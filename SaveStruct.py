class SaveDataInfo(object):
	"""docstring for UserMemoryPy"""
	def __init__(self):
		super(SaveDataInfo, self).__init__()
		self.version:int = None;
		self.AppVersion:int = None;
		self.saveInfoList:list[MapDataInfo] = list();
		self.purchaseIds:list[str] = list();
		self.crc:int = None;
		# self.instance = None;
		self.saveDate:int = None;
		self.songIndex:int = 1;
		self.isHard:int = None;
		self.buttonNumber:int = 4;
		self.sortNum:int = None;
		self.missVibrate:bool = None;
		self.soundHelper:int = 3;
		self.displayAdjustment:int = None;
		self.judgeCompensate:int = None;
		self.advSceneSettringString:str = None;
		self.metronomeSquipment:str = None;
		self.playTimeUIA:int = None;
		self.playTimeUIB:int = None;
		self.playTimeUIC:int = None;
		self.playTimeUID:int = None;
		self.playTimeUIE:int = None;
		self.playTimeUIF:int = None;
		self.playTimeRankEX:int = None;
		self.playTimeKnockEX:int = None;
		self.playTimeKnockNote:int = None;
		self.playVsync:bool = True;
		self.buttonSetting4K:list[int] = list();
		self.buttonSetting6K:list[int] = list();
		self.hiddenUnlockSongs:bool = None;
		self.hideLeaderboardMini:bool = True;
		self.playingSceneName:str = None;
		self.selectSongName:str = "luobi";
		self.sceneName:str = "SelectSongScene";
		self.busVolume:float = None;
		self.advSceneSettingString:str = "\n";
		self.dropSpeed:int = 8;
		self.isUseUserMemoryDropSpeed:bool = True;
		self.dropSpeedFloat:float = None;
		self.isOpenVSync:bool = True;
		self.hadSaveFpsAndVSync:bool = None;
		self.fps:int = 60;

	def __str__(self)->str:
		return f"SongSaveInfoPy(\n"\
			f"\tversion:{self.version}\n"\
			f"\tAppVersion:{self.AppVersion}\n"\
			f"\tsaveInfoList: List[SongSaveInfoPy]\n"\
			f"\tpurchaseIds:{self.purchaseIds}\n"\
			f"\tcrc:{self.crc}\n"\
			f"\tsaveDate:{self.saveDate}\n"\
			f"\tsongIndex:{self.songIndex}\n"\
			f"\tisHard:{self.isHard}\n"\
			f"\tbuttonNumber:{self.buttonNumber}\n"\
			f"\tsortNum:{self.sortNum}\n"\
			f"\tmissVibrate:{self.missVibrate}\n"\
			f"\tsoundHelper:{self.soundHelper}\n"\
			f"\tdisplayAdjustment:{self.displayAdjustment}\n"\
			f"\tjudgeCompensate:{self.judgeCompensate}\n"\
			f"\tadvSceneSettringString:\"{self.advSceneSettringString}\"\n"\
			f"\tmetronomeSquipment:\"{self.metronomeSquipment}\"\n"\
			f"\tplayTimeUIA:{self.playTimeUIA}\n"\
			f"\tplayTimeUIB:{self.playTimeUIB}\n"\
			f"\tplayTimeUIC:{self.playTimeUIC}\n"\
			f"\tplayTimeUID:{self.playTimeUID}\n"\
			f"\tplayTimeUIE:{self.playTimeUIE}\n"\
			f"\tplayTimeUIF:{self.playTimeUIF}\n"\
			f"\tplayTimeRankEX:{self.playTimeRankEX}\n"\
			f"\tplayTimeKnockEX:{self.playTimeKnockEX}\n"\
			f"\tplayTimeKnockNote:{self.playTimeKnockNote}\n"\
			f"\tplayVsync:{self.playVsync}\n"\
			f"\tbuttonSetting4K:{self.buttonSetting4K}\n"\
			f"\tbuttonSetting6K:{self.buttonSetting6K}\n"\
			f"\thiddenUnlockSongs:{self.hiddenUnlockSongs}\n"\
			f"\thideLeaderboardMini:{self.hideLeaderboardMini}\n"\
			f"\tplayingSceneName:\"{self.playingSceneName}\"\n"\
			f"\tselectSongName:\"{self.selectSongName}\"\n"\
			f"\tsceneName:\"{self.sceneName}\"\n"\
			f"\tbusVolume:{self.busVolume}\n"\
			f"\tadvSceneSettingString:\"{self.advSceneSettingString}\"\n"\
			f"\tdropSpeed:{self.dropSpeed}\n"\
			f"\tisUseUserMemoryDropSpeed:{self.isUseUserMemoryDropSpeed}\n"\
			f"\tdropSpeedFloat:{self.dropSpeedFloat}\n"\
			f"\tisOpenVSync:{self.isOpenVSync}\n"\
			f"\thadSaveFpsAndVSync:{self.hadSaveFpsAndVSync}\n"\
			f"\tfps:{self.fps})";

	def ToDict(self)->dict[str,any]:
		return dict(
			Version = self.version,
			AppVersion = self.AppVersion,
			SaveInfoList = [saveInfo.ToDict() for saveInfo in self.saveInfoList],
			PurchaseIds = self.purchaseIds,
			Crc = self.crc,
			SongIndex = self.songIndex,
			IsHard = self.isHard,
			ButtonNumber = self.buttonNumber,
			SortNum = self.sortNum,
			MissVibrate = self.missVibrate,
			SoundHelper = self.soundHelper,
			DisplayAdjustment = self.displayAdjustment,
			JudgeCompensate = self.judgeCompensate,
			AdvSceneSettringString = self.advSceneSettringString,
			MetronomeSquipment = self.metronomeSquipment,
			PlayTimeUIA = self.playTimeUIA,
			PlayTimeUIB = self.playTimeUIB,
			PlayTimeUIC = self.playTimeUIC,
			PlayTimeUID = self.playTimeUID,
			PlayTimeUIE = self.playTimeUIE,
			PlayTimeUIF = self.playTimeUIF,
			PlayTimeRankEX = self.playTimeRankEX,
			PlayTimeKnockEX = self.playTimeKnockEX,
			PlayTimeKnockNote = self.playTimeKnockNote,
			PlayVsync = self.playVsync,
			ButtonSetting4K = self.buttonSetting4K,
			ButtonSetting6K = self.buttonSetting6K,
			HiddenUnlockSongs = self.hiddenUnlockSongs,
			HideLeaderboardMini = self.hideLeaderboardMini,
			PlayingSceneName = self.playingSceneName,
			SelectSongName = self.selectSongName,
			SceneName = self.sceneName,
			BusVolume = self.busVolume,
			AdvSceneSettingString = self.advSceneSettingString,
			DropSpeed = self.dropSpeed,
			IsUseUserMemoryDropSpeed = self.isUseUserMemoryDropSpeed,
			DropSpeedFloat = self.dropSpeedFloat,
			IsOpenVSync = self.isOpenVSync,
			HadSaveFpsAndVSync = self.hadSaveFpsAndVSync,
			Fps = self.fps,
			);


class MapDataInfo(object):
	def __init__(self,SongId:int=0, SpeedStall:int=0, SyncNumber:int=0,
			UploadScore:float=0.0, PlayCount:int=0, Isfav:bool=False,
			CrcInt:int=0) -> None:
		self.SongId:int = SongId;
		self.SongInfo:MapInfo = None;
		self.SpeedStall:int = SpeedStall;
		self.SyncNumber:int = SyncNumber;
		self.UploadScore:float = UploadScore;
		self.PlayCount:int = PlayCount;
		self.Isfav:bool = Isfav;
		self.CrcInt:int = CrcInt;
		self.state:str = "    ";

	def __str__(self):
		return f"SongSaveInfoPy("\
			f"SongId:{self.SongId:08X}, "\
			f"SongInfo:{self.SongInfo.ToDict}, "\
			f"SpeedStall:{self.SpeedStall:08X}, "\
			f"SyncNumber:{self.SyncNumber}, "\
			f"UploadScore:{self.UploadScore}, "\
			f"PlayCount:{self.PlayCount}, "\
			f"Isfav:{self.Isfav}, "\
			f"CrcInt:{self.CrcInt}, "\
			f"state:{self.state})";

	def ToDict(self)->dict[str,any]:
		return dict(
			SongId		= f"{self.SongId:08X}",
			SongInfo	= self.SongInfo.ToDict(),
			SpeedStall	= f"{self.SpeedStall:08X}",
			SyncNumber	= f"{self.SyncNumber / 100.0}%",
			UploadScore	= f"{self.UploadScore * 100.0}%",
			CrcInt		= self.CrcInt,
			State		= self.state
			);

class MapInfo(object):
	# def __init__(self, songName:str, songKeys:int, songDifficulty:int, songDifficultyNumber:int) -> None:
	# 	self.songName:str = songName;
	# 	self.songKeys:str = ("4Key" if songKeys==4 else "6Key")
	# 	self.songDifficulty:str = ["Easy","Hard","Inferno"][songDifficulty[2]];
	# 	self.songDifficultyNumber:str = f"{songDifficultyNumber:02d}";

	def __init__(self, info:list) -> None:
		self.name:str = info[0];
		self.keys:str = ("4Key" if info[1]==4 else "6Key")
		self.difficulty:str = ["Easy","Hard","Inferno"][info[2]];
		self.difficultyNumber:str = f"{info[3]:02d}";

	def ToDict(self)->dict[str,str]:
		return dict(
			Name = self.name,
			Keys = self.keys,
			Difficulty = self.difficulty,
			DifficultyNumber = self.difficultyNumber
			);

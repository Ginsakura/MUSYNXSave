import ctypes
from Difficulty_ScoreAnalyze import Analyze
from enum import Enum, unique
from HitDelay import HitDelayText
import json
import logging
from MusyncSavDecode import MUSYNCSavProcess
import os
# from PIL import Image as PILImage;
# from PIL import ImageTk;
import psutil
import requests
from Resources import Config, SaveDataInfo, SongName, Logger
import threading
import time
import tkinter
from tkinter import Label,Entry,Button,Scrollbar,Frame
from tkinter import font,messagebox,StringVar
from tkinter import Tk,ttk,Toplevel
from tkinter.filedialog import askopenfilename
from Toolkit import Toolkit
import Version
import webbrowser
#import win32api
#import win32con
#import win32gui_struct
#import win32gui


class MusyncSavDecodeGUI(object):
	"""docstring for MusyncSavDecodeGUI"""
	def __init__(self, root:Tk=None, isTKroot:bool=True):
	##Init##
		# super(MusyncSavDecodeGUI, self).__init__();
		self.logger:logging.Logger = Logger.GetLogger(name="MusyncSavDecodeGUI");
		self.version:str = Version.version;
		self.preVersion:str = Version.preVersion;
		self.isPreRelease:bool = Version.isPreRelease;
		self.isTKroot:bool = isTKroot;
		root.iconbitmap('./musync_data/Musync.ico');
		root.geometry(f'1000x670+500+300');
		root.title("同步音律喵赛克Steam端本地存档分析");
		root['background'] = '#efefef';
		self.root:Tk = root;
		self.root.minsize(500, 460);
		# def fixed_map(option):
		# 	return [elm for elm in style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]
		style:ttk.Style = ttk.Style();
		if 1 :# Config['SystemDPI'] == 100:
			style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',13));
			style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',15));
			# style.configure("Checkbutton", foreground=[]);
			style.configure("reload.TButton", font=('霞鹜文楷等宽',16));
			style.configure("F5.TButton", font=('霞鹜文楷等宽',16),
				image=[
					#photo=PhotoImage(file="./skin/F5.png").subsample(5, 4),
					style.map("F5.TButton",
					foreground=[('pressed', 'red'), ('active', 'blue')],
					background=[('pressed', '!disabled', 'black'), ('active', 'white')])
				]);
			style.configure("close.TButton", font=('霞鹜文楷等宽',16), bg="#EEBBBB");
			self.font:tuple = ('霞鹜文楷等宽',16);
		self.saveFilePathVar:StringVar = StringVar();
		self.saveFilePathVar.set('Input SaveFile or AnalyzeFile Path (savedata.sav)or(SavAnalyze.json)');
		self.windowInfo:list[int] = [root.winfo_x(), root.winfo_y(), root.winfo_width(), root.winfo_height()];
		self.oldWindowInfo:list[int] = [0, 0];
		self.saveCount:int = 0;
		self.totalSync:int = 0;
		self.excludeCount:int = 0;
		self.dataSortMethodsort:list[bool] = [None, True];
		self.dataSelectMethod:str = None;
		self.treeviewColumns:list[str] = ["SongId",'SongName',"Keys","Difficulty","DifficultyNumber","SyncNumber","Rank","UploadScore","PlayCount","Status"];
		self.difficute:DiffcuteEnum = DiffcuteEnum.All;
		self.keys:KeysEnum = KeysEnum.All;
		self.songSelect:SongSelectEnum = SongSelectEnum.All;
		self.checkGameStartEvent = threading.Event();
		self.UpdateEnum();

		self.root.protocol("WM_DELETE_WINDOW", self.Closing);

	##Controller##
		self.DecodeSaveFile = ttk.Button(self.root, text="解码并刷新",command=self.RefreshSave,style='F5.TButton')
		self.DecodeSaveFile.place(x=10,y=10,width=160,height=30)
		self.isGameRunning = Label(self.root, text="游戏未启动", font=self.font,bg='#FF8080')
		self.isGameRunning.place(x=30,y=85,width=110,height=30)

		self.countFrameLanel = Label(self.root,text="", relief="groove")
		self.countFrameLanel.place(x=8,y=48,width=164,height=34)
		self.countLabel = Label(self.countFrameLanel, text='显示计数: ', font=self.font, relief="flat")
		self.countLabel.place(x=0,y=0,width=100,height=30)
		self.saveCountLabel = Label(self.countFrameLanel, text=str(self.saveCount+self.excludeCount), font=self.font, relief="flat")
		self.saveCountLabel.place(x=100,y=0,width=60,height=30)

		self.saveFilePathEntry = Entry(self.root, textvariable=self.saveFilePathVar, font=self.font, relief="sunken")
		self.getSaveFilePath = Button(self.root, text='打开存档', command=self.SelectPath, font=self.font)

		self.saveData = ttk.Treeview(self.root, show="headings", columns = self.treeviewColumns)
		self.saveInfoScroll = Scrollbar(self.saveData, orient='vertical', command=self.saveData.yview)
		self.saveData.configure(yscrollcommand=self.saveInfoScroll.set)
		# self.saveData.tag_configure("BuiltinSong",background='#FF0000',foreground='blue')
		# self.saveData.tag_configure("DLCSong",background='#FDFFAE',foreground='blue')

		self.developer = Label(self.root, text=f'Version {self.preVersion if self.isPreRelease else self.version} | Develop By Ginsakura', font=self.font, relief="groove")
		self.gitHubLink = Button(self.root, text='点击打开GitHub仓库	点个Star吧，秋梨膏', command=lambda:webbrowser.open("https://github.com/Ginsakura/MUSYNXSave"), fg='#4BB1DA', anchor="center", font=self.font, relief="groove")

		self.initLabel = Label(self.root, text='启动中......', anchor="w", font=self.font, relief="groove")
		self.initLabel.place(x=250,y=300,width=500,height=30)

		# self.closeWindow = ttk.Button(self.root, text="关闭",command=lambda : self.root.destroy(),style='close.TButton')
		# self.closeWindow.place(x=100,y=88,width=90,height=30)
		self.difficuteScoreAnalyze = Button(self.root, text="成绩分布",command=lambda:Analyze(), font=self.font)
		self.difficuteScoreAnalyze.place(x=775,y=88,width=90,height=30)

		self.totalSyncFrameLabel = Label(self.root, text='', relief="groove")
		self.totalSyncFrameLabel.place(x=868,y=48,width=124,height=74)
		self.totalSyncTextLabel = Label(self.root, text='综合同步率', anchor="center", font=self.font, relief="flat")
		self.totalSyncTextLabel.place(x=870,y=50,width=120,height=30)
		self.avgSyncLabel = Label(self.root, text=f'{(self.totalSync / (1 if self.saveCount==0 else self.saveCount)):.6f}%', anchor="w", font=self.font, relief="flat")
		self.avgSyncLabel.place(x=870,y=90,width=120,height=30)

	#筛选控件
		self.selectFrame = Frame(self.root, relief="groove",bd=2)
		self.selectFrame.place(x=180,y=50,width=380,height=70)
		self.selectLabel0 = Label(self.selectFrame, text="筛选\n控件", anchor="w", font=self.font, relief="flat")
		self.selectLabel0.place(x=0,y=5,width=50,height=60)
		# self.selectPlayedButton = Checkbutton(self.selectFrame, text='已游玩', command=lambda:self.SelectMethod('Played'), anchor="w", font=self.font)
		self.selectPlayedButton = Button(self.selectFrame, text='已游玩', command=lambda:self.SelectMethod('Played'), anchor="w", font=self.font)
		self.selectPlayedButton.place(x=50,y=0,width=75,height=30)
		self.selectUnplayButton = Button(self.selectFrame, text='未游玩', command=lambda:self.SelectMethod('Unplay'), anchor="w", font=self.font)
		self.selectUnplayButton.place(x=50,y=35,width=75,height=30)
		self.selectIsFavButton = Button(self.selectFrame, text='已收藏', command=lambda:self.SelectMethod('IsFav'), anchor="w", font=self.font)
		self.selectIsFavButton.place(x=125,y=0,width=75,height=30)
		self.selectExRankButton = Button(self.selectFrame, text='RankEx', command=lambda:self.SelectMethod('RankEX'), anchor="w", font=self.font)
		self.selectExRankButton.place(x=125,y=35,width=75,height=30)
		self.selectSRankButton = Button(self.selectFrame, text='RankS', command=lambda:self.SelectMethod('RankS'), anchor="w", font=self.font)
		self.selectSRankButton.place(x=200,y=0,width=62,height=30)
		self.selectARankButton = Button(self.selectFrame, text='RankA', command=lambda:self.SelectMethod('RankA'), anchor="w", font=self.font)
		self.selectARankButton.place(x=200,y=35,width=62,height=30)
		self.selectBRankButton = Button(self.selectFrame, text='RankB', command=lambda:self.SelectMethod('RankB'), anchor="w", font=self.font)
		self.selectBRankButton.place(x=262,y=0,width=62,height=30)
		self.selectCRankButton = Button(self.selectFrame, text='RankC', command=lambda:self.SelectMethod('RankC'), anchor="w", font=self.font)
		self.selectCRankButton.place(x=262,y=35,width=62,height=30)
		self.select122Button = Button(self.selectFrame, text='黑Ex', command=lambda:self.SelectMethod('Sync122'), anchor="w", font=self.font)
		self.select122Button.place(x=324,y=0,width=50,height=30)
		self.select120Button = Button(self.selectFrame, text='红Ex', command=lambda:self.SelectMethod('Sync120'), anchor="w", font=self.font)
		self.select120Button.place(x=324,y=35,width=50,height=30)
	##额外筛选##
		self.selectExFrame = Frame(self.root, bd=2, relief="groove")
		self.selectExFrame.place(x=570,y=50,width=200,height=70)
		self.selectLabel1 = Label(self.selectExFrame, text="额外\n筛选", anchor="w", font=self.font, relief="flat")
		self.selectLabel1.place(x=0,y=5,width=50,height=60)
		self.selectDLCSong = Button(self.selectExFrame, text=self.songSelect.text, command=lambda:self.SelectDLCSong(), anchor='w', font=self.font)
		self.selectDLCSong.place(x=48,y=0,width=30,height=65)
		self.selectKeys = Button(self.selectExFrame, text=self.keys.text, command=lambda:self.SelectKeys(), anchor='center', font=self.font)
		self.selectKeys.place(x=80,y=0,width=92,height=30)
		self.selectDifficute = Button(self.selectExFrame, text=self.difficute.text, command=lambda:self.SelectDifficute(), anchor='w', font=self.font)
		self.selectDifficute.place(x=80,y=35,width=92,height=30)

	##AutoRun##
		self.InitLabel('初始化函数执行中......')
		self.UpdateWindowInfo()
		self.TreeviewWidthUptate()
		self.TreeviewColumnUpdate()

		def CheckGameRunning():
			logger:logging.Logger = Logger.GetLogger("MusyncSavDecodeGUI.CheckGameRunning")
			logger.info("Start Thread: CheckGameIsStart.");
			def Checking()->None:
				if not self.checkGameStartEvent.is_set(): return;
				startTime = time.perf_counter_ns()
				try:
						for ids in psutil.pids():
							if psutil.Process(pid=ids).name() == "MUSYNX.exe":
								# Config["MainExecPath"]
								self.isGameRunning["text"] = "游戏已启动";
								self.isGameRunning["bg"] = "#98E22B";
								logger.debug("Game is Running.");
								break;
						else:
							self.isGameRunning["text"] = "游戏未启动";
							self.isGameRunning["bg"] = "#FF8080";
							logger.debug("Game is not Running.");
				except RuntimeError:
						pass
				except Exception:
						# logger.exception("CheckGameRunning has Exception: ");
						pass
				logger.info("CheckGameIsStart Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000));
				self.root.after(5000, Checking);
			self.root.after(5000, Checking);
			logger.warning("Stop Thread: CheckGameIsStart.");

		self.checkGameStartEvent.set();
		CheckGameRunning();
		self.root.after(0, self.CheckJsonUpdate);

		if Config.CheckUpdate:
			self.logger.info("Check Updating...");
			self.root.after(0,self.CheckUpdate);
		else:
			self.gitHubLink.configure(text='更新已禁用	点击打开GitHub仓库页');
			self.logger.warning("Check update is Disable");
		self.InitLabel(text="正在读取存档路径……");
		if (not os.path.isfile(Config.MainExecPath+"SavesDir\\savedata.sav")):
			self.GetSaveFile();
		else:
			self.saveFilePathVar.set(Config.MainExecPath+"SavesDir\\savedata.sav");
		if Config.DLLInjection:
			self.logger.warning("DLL Injection is Enable.");
			self.hitDelay = Button(self.root, text="游玩结算",command=self.HitDelay, font=self.font,bg='#FF5959');
			self.hitDelay.place(x=775,y=50,width=90,height=30);
		MUSYNCSavProcess(savFile=self.saveFilePathVar.get()).Main();
		self.DataLoad();

# TK事件重载
	def Closing(self):
		self.root.destroy();
		Config.SaveConfig();
		SaveDataInfo.DumpToJson();

# select功能组
	def SelectKeys(self):
		self.keys = KeysEnum((self.keys.value+1)%3);
		self.selectKeys.configure(text=self.keys.text);
		self.DataLoad();
		self.root.update();
	def SelectDifficute(self):
		self.difficute = DiffcuteEnum((self.difficute.value+1)%4);
		self.selectDifficute.configure(text=self.difficute.text)
		self.DataLoad()
		self.root.update()
	def SelectDLCSong(self):
		self.songSelect = SongSelectEnum((self.songSelect.value+1)%3);
		self.selectDLCSong.configure(text=self.songSelect.text)
		self.selectDLCSong.configure(bg=self.songSelect.background)
		self.DataLoad()
		self.root.update()
	def SelectMethod(self,method):
		if self.dataSelectMethod == method:
			self.dataSelectMethod = None
			self.SelectButtonGrey(method)
		else:
			self.SelectButtonGrey(self.dataSelectMethod)
			self.dataSelectMethod = method
			self.SelectButtonGreen(self.dataSelectMethod)
		self.DataLoad()
		self.root.update()
	def SelectButtonGreen(self,method):
		if method == "Played":self.selectPlayedButton.configure(bg='#98E22B')
		elif method == "Unplay":self.selectUnplayButton.configure(bg='#98E22B')
		elif method == "IsFav":self.selectIsFavButton.configure(bg='#98E22B')
		elif method == "Sync122":self.select122Button.configure(bg='#98E22B')
		elif method == "Sync120":self.select120Button.configure(bg='#98E22B')
		elif method == "RankEX":self.selectExRankButton.configure(bg='#98E22B')
		elif method == "RankS":self.selectSRankButton.configure(bg='#98E22B')
		elif method == "RankA":self.selectARankButton.configure(bg='#98E22B')
		elif method == "RankB":self.selectBRankButton.configure(bg='#98E22B')
		elif method == "RankC":self.selectCRankButton.configure(bg='#98E22B')
	def SelectButtonGrey(self,method):
		if method == "Played":self.selectPlayedButton.configure(bg='#F0F0F0')
		elif method == "Unplay":self.selectUnplayButton.configure(bg='#F0F0F0')
		elif method == "IsFav":self.selectIsFavButton.configure(bg='#F0F0F0')
		elif method == "Sync122":self.select122Button.configure(bg='#F0F0F0')
		elif method == "Sync120":self.select120Button.configure(bg='#F0F0F0')
		elif method == "RankEX":self.selectExRankButton.configure(bg='#F0F0F0')
		elif method == "RankS":self.selectSRankButton.configure(bg='#F0F0F0')
		elif method == "RankA":self.selectARankButton.configure(bg='#F0F0F0')
		elif method == "RankB":self.selectBRankButton.configure(bg='#F0F0F0')
		elif method == "RankC":self.selectCRankButton.configure(bg='#F0F0F0')

	def SelectPath(self):
		# 使用askdirectory()方法返回文件夹的路径
		path_ = askopenfilename(title="打开存档文件", filetypes=(("Sav Files", "*.sav"),("All Files","*.*"),))
		if path_ == "":
			# 当打开文件路径选择框后点击"取消" 输入框会清空路径，所以使用get()方法再获取一次路径
			self.saveFilePathVar.get()
		else:
			# 实际在代码中执行的路径为“\“ 所以替换一下
			path_ = path_.replace("/", "\\")
			self.saveFilePathVar.set(path_)

# bind功能组
	def DoubleClick(self,event):
		e = event.widget									# 取得事件控件
		itemID = e.identify("item",event.x,event.y)			# 取得双击项目id
		# state = e.item(itemID,"text")						# 取得text参数
		songData = e.item(itemID,"values")					# 取得values参数
		self.logger.debug(songData)
		# nroot = Toplevel(self.root)
		# nroot.resizable(True, True)
		# newWindow = SubWindow(nroot, songData[0], songData[1], songData[2])

	def SortClick(self,event):
		def TreeviewSortColumn(col):
			startTime = time.perf_counter_ns()
			if self.dataSortMethodsort[0] == col:
				self.dataSortMethodsort[1] = not self.dataSortMethodsort[1]
			else:
				self.dataSortMethodsort[0] = col
				self.dataSortMethodsort[1] = True
			if col == 'SyncNumber' or col == 'UploadScore':
				l = [(float((self.saveData.set(k, col))[:-1]), k) for k in self.saveData.get_children('')]
			elif col == 'PlayCount':
				l = [(int(self.saveData.set(k, col)), k) for k in self.saveData.get_children('')]
			elif col == 'SongName':
				l = [((self.saveData.set(k, col)).lower(), k) for k in self.saveData.get_children('')]
			else:
				l = [(self.saveData.set(k, col), k) for k in self.saveData.get_children('')]
			l.sort(reverse=self.dataSortMethodsort[1])
			for index, (val, k) in enumerate(l):
				self.saveData.move(k, '', index)
			endTime = time.perf_counter_ns()
			print("SortClick Run Time: %f ms"%((endTime - startTime)/1000000))
			self.TreeviewColumnUpdate()
		if isinstance(event, list):
			self.dataSortMethodsort[1] = not self.dataSortMethodsort[1]
			TreeviewSortColumn(event[0])
		for col in self.treeviewColumns:
			self.saveData.heading(col, command=lambda _col=col:TreeviewSortColumn(_col))

	def StartGame(self,event):
		if self.isGameRunning["text"] == '游戏未启动':
			os.system('start steam://rungameid/952040')
		else:
			messagebox.showinfo("Info", '游戏已启动')

	def F5Key(self,event):
		self.DataLoad()

# update功能组
	def CheckJsonUpdate(self):
		startTime = time.perf_counter_ns()
		try:
			response:requests.Response = requests.get("https://raw.githubusercontent.com/Ginsakura/MUSYNCSave/main/musync_data/songname.update");
			localVersion:int = int(SongName.Version());
			self.logger.info(f"   Local Json Version: {localVersion}");
			if response.status_code == 200:
				githubVersion = int(response.content.decode('utf8'));
				self.logger.info(f"  Terget Json Version: {githubVersion}");
				if githubVersion>localVersion:
					response = requests.get("https://raw.githubusercontent.com/Ginsakura/MUSYNCSave/main/musync_data/songname.json")
					songNameJson = response.json()
					with open("./musync_data/SongName.json",'w',encoding='utf8') as snj:
						json.dump(songNameJson,snj,indent="",ensure_ascii=False)
					SongName.LoadFile();
			else:
				self.logger.error("Can't get \"songname.update\", HTTP status code: %d."%(response.status_code));
		except Exception as e:
			self.logger.exception("谱面信息更新发生错误: ");
			messagebox.showerror("Error", f'发生错误: {e}');
			if messagebox.askyesno("无法获取谱面信息更新", f'是否前往网页查看是否存在更新？\n(请比对 SongName.update 中的时间是否比本地文件中的时间更大)'):
				webbrowser.open("https://raw.githubusercontent.com/Ginsakura/MUSYNCSave/main/musync_data/songname.update")
		endTime = time.perf_counter_ns()
		self.logger.info("CheckJsonUpdate Run Time: %f ms"%((endTime - startTime)/1000000));

	def UpdateTip(self):
		if self.gitHubLink.cget('fg') == '#C4245C':
			self.gitHubLink.configure(fg='#4BB1DA')
		else:
			self.gitHubLink.configure(fg='#C4245C')
		self.root.after(500,self.UpdateTip)

	def CheckUpdate(self):
		def CheckVersion(local:str, target:str)->bool:
			localVer:list[str] = local.replace("pre" if self.isPreRelease else "rc",".").split(".");
			targetVer:list[str] =  target.replace("rc",".").split(".");
			if (targetVer[0] > localVer[0]): return True;
			if (targetVer[1] > localVer[1]): return True;
			if (targetVer[2] > localVer[2]): return True;
			if (targetVer[3] > localVer[3]): return True;
			else: return False;
		startTime:int = time.perf_counter_ns()
		try:
			response:requests.Response = requests.get("https://api.github.com/repos/ginsakura/MUSYNCSave/releases/latest")
			resJson = response.json()
			if "tag_name" in resJson:
				tergetVersion:str = response.json()["tag_name"].replace("rc",".")
			elif "message" in resJson:
				if resJson["message"][:23] == "API rate limit exceeded":
					if messagebox.askyesno("GitHub公共API访问速率已达上限", "是否前往发布页查看是否存在更新？"):
						webbrowser.open("https://github.com/Ginsakura/MUSYNCSave/releases/latest")
					return
		except Exception as e:
			self.logger.exception("更新信息发生错误: ");
			messagebox.showerror("Error", f'发生错误: {e}')
		# print(localVersion,tergetVersion)
		self.logger.info('  Terget Version : %s'%tergetVersion.replace("rc","."))
		self.logger.info('   Local Version : %s'%self.version.replace("rc","."))
		self.logger.info("Local PreVersion : %s"%self.preVersion.replace("pre","."))
		if (CheckVersion(self.preVersion if self.isPreRelease else self.version, tergetVersion)):
			self.gitHubLink.configure(text=f'有新版本啦——点此打开下载页面	NewVersion: {tergetVersion}', anchor="center")
			self.gitHubLink.configure(command=lambda:webbrowser.open(f"https://github.com/Ginsakura/MUSYNCSave/releases/tag/{tergetVersion}"))
			self.UpdateTip()
		else:
			self.gitHubLink.configure(text='点击打开GitHub仓库	点个Star吧，秋梨膏', anchor="center")
			self.gitHubLink.configure(command=lambda:webbrowser.open("https://github.com/Ginsakura/MUSYNCSave"))
		endTime = time.perf_counter_ns()
		self.logger.info("CheckUpdate Run Time: %f ms"%((endTime - startTime)/1000000))

# 初始化提示框
	def InitLabel(self,text,close=False):
		self.initLabel.place(x=250,y=300,width=500,height=30)
		self.initLabel.configure(text=text, anchor="w")
		self.root.update()
		if close:
			self.initLabel.place(x=-1,width=0)

# 数据分析功能组
	def RefreshSave(self)->None:
		"刷新存档"
		MUSYNCSavProcess(savFile=self.saveFilePathVar.get()).Main();
		self.DataLoad();

	def GetSaveFile(self)->None:
		"搜索预设存档目录"
		startTime:int = time.perf_counter_ns();
		self.InitLabel("正在搜索存档文件中……");
		self.logger.debug("正在搜索存档文件中……");
		saveFilePath:str = None;
		for ids in "DEFCGHIJKLMNOPQRSTUVWXYZAB":
			if os.path.isfile(f'{ids}:\\Program Files\\steam\\steamapps\\common\\MUSYNX\\SavesDir\\savedata.sav'):
				saveFilePath:str = f"{ids}:\\Program Files\\steam\\steamapps\\common\\MUSYNX\\"
				break
			elif os.path.isfile(f'{ids}:\\SteamLibrary\\steamapps\\common\\MUSYNX\\SavesDir\\savedata.sav'):
				saveFilePath:str = f"{ids}:\\SteamLibrary\\steamapps\\common\\MUSYNX\\"
				break
			elif os.path.isfile(f'{ids}:\\steam\\steamapps\\common\\MUSYNX\\SavesDir\\savedata.sav'):
				saveFilePath:str = f"{ids}:\\steam\\steamapps\\common\\MUSYNX\\"
				break
		else:
			self.InitLabel("搜索不到存档文件.");
			self.logger.error("搜索不到存档文件.");
			self.logger.info("GetSaveFile Run Time: %f ms"%((time.perf_counter_ns() - startTime)/1000000));
			return;
		self.logger.debug(f"SaveFilePath: {saveFilePath}");
		self.saveFilePathVar.set(saveFilePath+'SavesDir\\savedata.sav');
		Config.MainExecPath = saveFilePath;
		Config.SaveConfig();

	def HitDelay(self):
		"DLL注入功能"
		if Config.DLLInjection:
			result:int = Toolkit.GameLibCheck();
		if (result == 0):
			messagebox.showerror("Error", f'DLL注入失败：软件版本过低或者游戏有更新,\n请升级到最新版或等待开发者发布新的补丁');
			self.logger.error("DLL注入失败：软件版本过低或者游戏有更新,\n请升级到最新版或等待开发者发布新的补丁")
			return;
		else:
			self.logger.debug(f"return: {result}.");
			self.logger.info("DLL Injection Success.");
		nroot:Toplevel = Toplevel(self.root);
		nroot.resizable(True, True);
		HitDelayText(nroot);

	def DataLoad(self):
		"存档数据解析"
		self.logger.debug("DataLoad Start");
		startTime = time.perf_counter_ns();
		self.InitLabel(text="正在分析存档文件中……");
		self.logger.debug("正在分析存档文件中……");

		def Rank(sync:int):
			if	 (sync == 0)	: return "";
			if	 (sync < 7500)	: return "C";
			elif (sync < 9500)	: return "B";
			elif (sync < 11000)	: return "A";
			elif (sync < 11700)	: return "S";
			elif (sync < 12000)	: return "蓝Ex";
			elif (sync < 12200)	: return "红Ex";
			else				: return "黑Ex";

		# songNameJson = SongName.SongNameData();
		self.root.title(f'同步音律喵赛克Steam端本地存档分析   LastPlay: {SaveDataInfo.selectSongName}')
		[self.saveData.delete(ids) for ids in self.saveData.get_children()]
		self.saveCount = 0
		self.totalSync = 0
		for saveInfo in SaveDataInfo.saveInfoList:
			# 无名谱面筛选
			if saveInfo.SongName is None: continue;
			# 键数筛选
			if ((self.keys != KeysEnum.All) and (self.keys.text != saveInfo.SongKeys)): continue;
			# 难度筛选
			if (self.difficute != DiffcuteEnum.All) and (self.difficute.text != saveInfo.SongDifficulty): continue;
			# 内置曲目筛选
			if ((self.songSelect != SongSelectEnum.All) and (saveInfo.SongIsBuiltin != (self.songSelect == SongSelectEnum.Builtin))): continue;
			# 互斥筛选
			if (self.dataSelectMethod == "Played"):
				if ((saveInfo.PlayCount == 0) or (saveInfo.SyncNumber == 0)): continue;
			elif (self.dataSelectMethod == "Unplay"):
				if ((saveInfo.PlayCount != 0) or (saveInfo.SyncNumber != 0)): continue;
			elif (self.dataSelectMethod == "IsFav"):
				if (saveInfo.State != 'Favo'): continue;
			elif (self.dataSelectMethod == "Sync122"):
				if (saveInfo.SyncNumber//100 < 122): continue;
			elif (self.dataSelectMethod == "Sync120"):
				if ((saveInfo.SyncNumber//100 < 120) or (saveInfo.SyncNumber//100 >= 122)): continue;
			elif (self.dataSelectMethod == "RankEX"):
				if (saveInfo.SyncNumber//100 < 117): continue;
			elif (self.dataSelectMethod == "RankS"):
				if ((saveInfo.SyncNumber//100 < 110) or (saveInfo.SyncNumber//100 >= 117)): continue;
			elif (self.dataSelectMethod == "RankA"):
				if ((saveInfo.SyncNumber//100 < 95) or (saveInfo.SyncNumber//100 >= 110)): continue;
			elif (self.dataSelectMethod == "RankB"):
				if ((saveInfo.SyncNumber//100 < 75) or (saveInfo.SyncNumber//100 >= 95)): continue;
			elif (self.dataSelectMethod == "RankC"):
				if ((saveInfo.SyncNumber//100 == 0) or (saveInfo.SyncNumber//100 >= 75)): continue;
			if (saveInfo.State in ['    ', 'Favo']):
				self.saveCount += 1;
				self.totalSync += saveInfo.UploadScore;
			else:
				self.excludeCount += 1;
			self.saveData.insert('', tkinter.END, values=("%d"%saveInfo.SongId, #谱面号
				("" if (saveInfo.SongName is None) else saveInfo.SongName), #曲名
				("" if (saveInfo.SongKeys is None) else saveInfo.SongKeys), #键数
				("" if (saveInfo.SongDifficulty is None) else saveInfo.SongDifficulty), #难度
				("" if (saveInfo.SongDifficultyNumber is None) else saveInfo.SongDifficultyNumber), #难度等级
				f"{saveInfo.SyncNumber/10000:.2%}", #本地同步率
				(Rank(saveInfo.SyncNumber)), #Rank
				f"{saveInfo.UploadScore:.21%}", #云端同步率
				saveInfo.PlayCount, #游玩计数
				saveInfo.State #谱面状态
				))
		# print(songNameJson["NotDLCSong"])
		if not self.dataSortMethodsort[0] is None:
			self.SortClick(self.dataSortMethodsort)
		self.InitLabel('数据展示生成完成.',close=True)
		endTime = time.perf_counter_ns()
		print("DataLoad Run Time: %f ms"%((endTime - startTime)/1000000))
		self.UpdateWindowInfo()

# 控件更新功能组
	def TreeviewColumnUpdate(self):
		self.saveData.heading("SongId",anchor="center",text="谱面号"+(('⇓' if self.dataSortMethodsort[1] else '⇑') if self.dataSortMethodsort[0]=='SpeedStall' else ''))
		self.saveData.heading("SongName",anchor="center",text="曲名"+(('⇓' if self.dataSortMethodsort[1] else '⇑') if self.dataSortMethodsort[0]=='SongName' else ''))
		self.saveData.heading("Keys",anchor="center",text="键数"+(('⇓' if self.dataSortMethodsort[1] else '⇑') if self.dataSortMethodsort[0]=='Keys' else ''))
		self.saveData.heading("Difficulty",anchor="center",text="难度"+(('⇓' if self.dataSortMethodsort[1] else '⇑') if self.dataSortMethodsort[0]=='Difficulty' else ''))
		self.saveData.heading("DifficultyNumber",anchor="center",text="等级"+(('⇓' if self.dataSortMethodsort[1] else '⇑') if self.dataSortMethodsort[0]=='DifficultyNumber' else ''))
		self.saveData.heading("SyncNumber",anchor="center",text="同步率"+(('⇓' if self.dataSortMethodsort[1] else '⇑') if self.dataSortMethodsort[0]=='SyncNumber' else ''))
		self.saveData.heading("Rank",anchor="center",text="Rank"+(('⇓' if self.dataSortMethodsort[1] else '⇑') if self.dataSortMethodsort[0]=='Rank' else ''))
		self.saveData.heading("UploadScore",anchor="center",text="云端同步率"+(('⇓' if self.dataSortMethodsort[1] else '⇑') if self.dataSortMethodsort[0]=='UploadScore' else ''))
		self.saveData.heading("PlayCount",anchor="center",text="游玩计数"+(('⇓' if self.dataSortMethodsort[1] else '⇑') if self.dataSortMethodsort[0]=='PlayCount' else ''))
		self.saveData.heading("Status",anchor="center",text="Status"+(('⇓   ' if self.dataSortMethodsort[1] else '⇑   ') if self.dataSortMethodsort[0]=='Status' else '   '))
		self.root.update()

	def TreeviewWidthUptate(self):
		self.saveData.column("SongId",anchor="e",width=90)
		self.saveData.column("SongName",anchor="w",width=self.windowInfo[2]-771)
		self.saveData.column("Keys",anchor="center",width=60)
		self.saveData.column("Difficulty",anchor="w",width=65)
		self.saveData.column("DifficultyNumber",anchor="center",width=60)
		self.saveData.column("SyncNumber",anchor="e",width=80)
		self.saveData.column("Rank",anchor="center",width=55)
		self.saveData.column("UploadScore",anchor="e",width=160)
		self.saveData.column("PlayCount",anchor="e",width=90)
		self.saveData.column("Status",anchor="w",width=80)

	def UpdateWindowInfo(self,event=None):

		self.windowInfo = ['root.winfo_x()','root.winfo_y()',self.root.winfo_width(),self.root.winfo_height()]

		self.saveFilePathEntry.place(x=170,y=10,width=(self.windowInfo[2]-260),height=30)
		self.getSaveFilePath.place(x=(self.windowInfo[2]-90),y=10,width=90,height=30)
		self.saveData.place(x=0 ,y=130 ,width=(self.windowInfo[2]-1) ,height=(self.windowInfo[3]-160))
		if not self.oldWindowInfo == self.windowInfo[2:]:
			self.TreeviewWidthUptate()
			self.saveInfoScroll.place(x=self.windowInfo[2]-22, y=1, width=20, height=self.windowInfo[3]-162)
		# self.saveCountVar.set()
		self.saveCountLabel.configure(text=str(self.saveCount+self.excludeCount))
		self.avgSyncLabel.configure(text=f'{(self.totalSync / (1 if self.saveCount==0 else self.saveCount)):.6f}%')
		self.developer.place(x=0,y=self.windowInfo[3]-30,width=420,height=30)
		self.gitHubLink.place(x=420,y=self.windowInfo[3]-30,width=self.windowInfo[2]-420,height=30)

		self.isGameRunning.bind('<Button-1>', self.StartGame)
		self.saveData.bind("<Double-1>",self.DoubleClick)
		self.saveData.bind("<ButtonRelease-1>",self.SortClick)
		self.root.bind("<F5>", self.F5Key)
		self.oldWindowInfo = self.windowInfo[2:]
		self.root.update()
		# if self.after == False:
		# 	self.after = True
		# 	self.root.after(100,self.UpdateWindowInfo)

	def UpdateEnum(self)->None:
		DiffcuteEnum.Easy.text = "简单难度";
		DiffcuteEnum.Easy.stext = "EZ";
		DiffcuteEnum.Hard.text = "困难难度";
		DiffcuteEnum.Hard.stext = "HD";
		DiffcuteEnum.Inferno.text = "地狱难度";
		DiffcuteEnum.Inferno.stext = "IN";
		DiffcuteEnum.All.text = "所有难度";
		DiffcuteEnum.All.stext = "ALL";

		KeysEnum.Key4.text = "4 Key";
		KeysEnum.Key4.stext = "4K";
		KeysEnum.Key4.width = 72;
		KeysEnum.Key6.text = "6 Key";
		KeysEnum.Key6.stext = "6K";
		KeysEnum.All.text = "4&6 Key";
		KeysEnum.All.stext = "ALL";

		SongSelectEnum.Builtin.text = "本\n体";
		SongSelectEnum.DLC.text = "扩\n展";
		SongSelectEnum.All.text = "所\n有";
		SongSelectEnum.Builtin.background = '#FF9B9B';
		SongSelectEnum.DLC.background = '#98E22B';
		SongSelectEnum.All.background = '#F0F0F0';

class SubWindow(object):
	def __init__(self, nroot, songID, songName, songDifficute):
		##Init##
		nroot.iconbitmap('./musync_data/Musync.ico')
		# super(SubWindow, self).__init__()
		self.font=('霞鹜文楷等宽',16)
		nroot.geometry(f'1000x630+500+300')
		style = ttk.Style()
		style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',12))
		style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',12))
		nroot.title(f"{songID}:{songName}:{songDifficute} 全球排行")
		nroot['background'] = '#efefef'
		self.root = nroot
		self.songID = songID
		self.globalSync = ttk.Treeview(self.root, show="headings")
		self.globalSync.configure(columns = ['SongName',"Difficulty","Rank","SyncNumber"])
		self.VScroll = Scrollbar(self.globalSync, orient='vertical', command=self.globalSync.yview)

		self.TIPS = Label(self.root, text="这里还没有被实现鸭——", relief="groove", font=('霞鹜文楷等宽',15))
		self.TIPS.place(x=10,y=10,width=300,height=30)

		##AutoRun##
		self.UpdateWindow()

	def UpdateWindow(self):
		self.root.update()
		self.windowInfo = ['root.winfo_x()','root.winfo_y()',root.winfo_width(),root.winfo_height()]

		self.globalSync.place(x=10 ,y=10 ,width=(self.windowInfo[2]-20) ,height=(self.windowInfo[3]-20))
		self.globalSync.column("SongName",anchor="w",width=100)
		self.globalSync.heading("SongName",anchor="center",text="曲名")
		self.globalSync.column("Difficulty",anchor="w",width=90)
		self.globalSync.heading("Difficulty",anchor="center",text="难度")
		self.globalSync.column("Rank",anchor="e",width=90)
		self.globalSync.heading("Rank",anchor="center",text="Rank")
		self.globalSync.column("SyncNumber",anchor="e",width=70)
		self.globalSync.heading("SyncNumber",anchor="center",text="同步率")

		self.VScroll.place(x=self.windowInfo[2]-40, y=1, width=20, relheight=1)

@unique
class DiffcuteEnum(Enum):
	"难度枚举"
	Easy = 0;
	Hard = 1;
	Inferno = 2;
	All = 3;

@unique
class KeysEnum(Enum):
	"键数枚举"
	Key4 = 0;
	Key6 = 1;
	All = 2;

@unique
class SongSelectEnum(Enum):
	'曲目筛选枚举'
	Builtin = 0;
	DLC = 1;
	All = 2;


if __name__ == '__main__':
	from Version import *

	# Init
	Config();
	SongName();
	SaveDataInfo();
	Config.Version = preVersion.replace("pre",".") if (isPreRelease) else version.replace("rc",".");

	# Launcher
	root:Tk = Tk();
	ctypes.windll.shcore.SetProcessDpiAwareness(1);
	fontlist:list[str] = list(font.families());
	Toolkit.CheckResources(fonts=fontlist);
	# del fonts
	if Config.ChangeConsoleStyle:
		Toolkit.ChangeConsoleStyle();
	root.tk.call('tk', 'scaling', 1.25);
	root.resizable(False, True); #允许改变窗口高度，不允许改变窗口宽度
	# 强制仅旧版UI
	MusyncSavDecodeGUI(root=root);
	# if cfg['EnableFramelessWindow']:
	# 	root.overrideredirect(1)
	# 	window = NewStyle.MusyncSavDecodeGUI(root=root)
	# else:
	# 	window = OldStyle.MusyncSavDecodeGUI(root=root,version=version,preVersion=preVersion,isPreRelease=isPreRelease)
	root.update();
	root.mainloop();
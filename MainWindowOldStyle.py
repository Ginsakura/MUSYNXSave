import ctypes
import json
import os
import psutil
import requests
import threading
import time
import webbrowser
#import win32api
#import win32con
#import win32gui_struct
#import win32gui

from PIL import Image as PILImage
from PIL import ImageTk
#from threading import Thread
from tkinter import *
from tkinter import Tk,ttk,font,messagebox
from tkinter.filedialog import askopenfilename

import Difficulty_ScoreAnalyze as dsa
import Functions
import MusyncSavDecode
from HitDelay import HitDelayCheck,HitDelayText


class MusyncSavDecodeGUI(object):
	"""docstring for MusyncSavDecodeGUI"""
	def __init__(self, version, preVersion, isPreRelease=False, root=None, isTKroot=True):
	##Init##
		self.version = version
		self.preVersion = preVersion
		with open('./musync_data/ExtraFunction.cfg','r',encoding='utf8') as confFile:
			self.config = json.load(confFile)
		root.iconbitmap('./musync_data/Musync.ico')
		super(MusyncSavDecodeGUI, self).__init__()
		self.isTKroot = isTKroot
		root.geometry(f'1000x670+500+300')
		self.root = root
		self.root.minsize(500, 460)
		def fixed_map(option):
			return [elm for elm in style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]
		style = ttk.Style()
		if 1 :# self.config['SystemDPI'] == 100:
			style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',13))
			style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',15))
			style.configure("reload.TButton", font=('霞鹜文楷等宽',16))
			# , background='#EEBBBB', foreground='#00CCFF',relief='ridge')
			# photo = PhotoImage(file="./skin/F5.png").subsample(5, 4)
			style.configure("F5.TButton", font=('霞鹜文楷等宽',16),# background='#EEBBBB')
				# image=[photo,style.map("F5.TButton",
				image=[style.map("F5.TButton",
					foreground=[('pressed', 'red'), ('active', 'blue')],
					background=[('pressed', '!disabled', 'black'), ('active', 'white')])
				])
			style.configure("close.TButton", font=('霞鹜文楷等宽',16), bg="#EEBBBB")
			self.font=('霞鹜文楷等宽',16)
		# elif self.config['SystemDPI'] == 125:
		# else:
		# 	style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',11))
		# 	style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',15))
		# 	style.configure("reload.TButton", font=('霞鹜文楷等宽',13.5))
		# 	# , background='#EEBBBB', foreground='#00CCFF',relief='ridge')
		# 	style.configure("F5.TButton", font=('霞鹜文楷等宽',13.5), bg="#EEBBBB")
		# 	self.font=('霞鹜文楷等宽',13.5)
		# style.configure("Treeview", foreground=fixed_map("foreground"), background=fixed_map("background"))
		# style.configure("Treeview", background="#EFEFEF", foreground="#050505", fieldbackground="red")
		if isTKroot == True:
			root.title("同步音律喵赛克Steam端本地存档分析")
			root['background'] = '#efefef'
		self.saveFilePathVar = StringVar()
		self.saveFilePathVar.set('Input SaveFile or AnalyzeFile Path (savedata.sav)or(SavAnalyze.json)')
		self.analyzeFilePathVar = StringVar()
		self.analyzeFilePathVar.set('Input Analyze File Dir (or not)')
		self.windowInfo = [root.winfo_x(),root.winfo_y(),root.winfo_width(),root.winfo_height()]
		self.saveCount = 0
		self.totalSync = 0
		self.excludeCount = 0
		self.dataSortMethodsort = [None,True]
		self.dataSelectMethod = None
		self.treeviewColumns = ["SpeedStall",'SongName',"Keys","Difficulty","DifficultyNumber","SyncNumber","Rank","UploadScore","PlayCount","Status"]
		self.difficute = 3
		self.keys = 0
		self.isDLC = 0
		self.wh = [0,0]

	##Controller##
		self.deleteAnalyzeFile = ttk.Button(self.root, text="解码并刷新",command=self.DeleteAnalyzeFile,style='F5.TButton')
		self.deleteAnalyzeFile.place(x=10,y=10,width=160,height=30)
		self.isGameRunning = Label(self.root, text="游戏未启动", font=self.font,bg='#FF8080')
		self.isGameRunning.place(x=30,y=85,width=110,height=30)

		self.CountFrameLanel = Label(self.root,text="", relief="groove")
		self.CountFrameLanel.place(x=8,y=48,width=164,height=34)
		self.PrintLabel0 = Label(self.root, text='显示计数: ', font=self.font, relief="flat")
		self.PrintLabel0.place(x=10,y=50,width=100,height=30)
		self.saveCountLabel = Label(self.root, text=str(self.saveCount+self.excludeCount), font=self.font, relief="flat")
		self.saveCountLabel.place(x=110,y=50,width=60,height=30)

		self.saveFilePathEntry = Entry(self.root, textvariable=self.saveFilePathVar, font=self.font, relief="sunken")
		self.getSaveFilePath = Button(self.root, text='打开存档', command=self.SelectPath, font=self.font)

		self.saveData = ttk.Treeview(self.root, show="headings", columns = self.treeviewColumns)
		self.VScroll1 = Scrollbar(self.saveData, orient='vertical', command=self.saveData.yview)
		self.saveData.configure(yscrollcommand=self.VScroll1.set)
		# self.saveData.tag_configure("NotDLCSong",background='#BBDDFF')
		# self.saveData.tag_configure("NotDLCSong",background='#FF0000',foreground='blue')
		# self.saveData.tag_configure("IsDLCSong",background='#FDFFAE',foreground='blue')

		self.developer = Label(self.root, text=f'Version {self.preVersion if isPreRelease else self.version} | Develop By Ginsakura', font=self.font, relief="groove")
		self.gitHubLink = Button(self.root, text='点击打开GitHub仓库	点个Star吧，秋梨膏', command=lambda:webbrowser.open("https://github.com/Ginsakura/MUSYNCSave"), fg='#4BB1DA', anchor="center", font=self.font, relief="groove")

		self.initLabel = Label(self.root, text='启动中......', anchor="w", font=self.font, relief="groove")
		self.initLabel.place(x=250,y=300,width=500,height=30)

		# self.closeWindow = ttk.Button(self.root, text="关闭",command=lambda : self.root.destroy(),style='close.TButton')
		# self.closeWindow.place(x=100,y=88,width=90,height=30)
		self.difficuteScoreAnalyze = Button(self.root, text="成绩分布",command=lambda:dsa.Analyze(), font=self.font)
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
		self.selectDLCSong = Button(self.selectExFrame, text=['所\n有','本\n体','扩\n展'][self.isDLC], command=lambda:self.SelectDLCSong(), anchor='w', font=self.font)
		self.selectDLCSong.place(x=48,y=0,width=30,height=65)
		self.selectKeys = Button(self.selectExFrame, text=['4 & 6 Keys','4 Keys','6 Keys'][self.keys], command=lambda:self.SelectKeys(), anchor='w', font=self.font)
		self.selectKeys.place(x=80,y=0,width=[112,72,72][self.keys],height=30)
		self.selectDifficute = Button(self.selectExFrame, text=['Easy','Hard',"Inferno",'所有难度'][self.difficute], command=lambda:self.SelectDifficute(), anchor='w', font=self.font)
		self.selectDifficute.place(x=80,y=35,width=[52,52,82,92][self.difficute],height=30)

	##AutoRun##
		self.InitLabel('初始化函数执行中......')
		self.UpdateWindowInfo()
		self.TreeviewWidthUptate()
		self.TreeviewColumnUpdate()

		def CheckGameIsStart():
			while True:
				startTime = time.perf_counter_ns()
				# print("Checking Game Is Start?")
				for ids in psutil.pids():
					try:
						if psutil.Process(pid=ids).name() == "MUSYNX.exe":
							# self.config["MainExecPath"]
							self.isGameRunning["text"] = "游戏已启动"
							self.isGameRunning["bg"] = "#98E22B"
							break
					except Exception as e:
						print(repr(e))
					
				else:
					self.isGameRunning["text"] = "游戏未启动"
					self.isGameRunning["bg"] = "#FF8080"
				endTime = time.perf_counter_ns()
				print("CheckGameIsStart Run Time: %f ms"%((endTime - startTime)/1000000))
				time.sleep(5)
		threading.Thread(target=CheckGameIsStart).start()
		threading.Thread(target=self.CheckJsonUpdate).start()

		if self.config['DisableCheckUpdate']:
			self.gitHubLink.configure(text='更新已禁用	点击打开GitHub仓库页')
		else:
			threading.Thread(target=self.CheckUpdate).start()
		if not os.path.isfile('./musync_data/SaveFilePath.sfp'):
			self.GetSaveFile()
		else:
			self.InitLabel(text="正在读取存档路径……")
			with open('./musync_data/SaveFilePath.sfp','r+',encoding='utf8') as sfp:
				sfpr = sfp.read()
			if not sfpr:
				self.GetSaveFile()
			elif (not os.path.isfile(sfpr)):
				self.InitLabel(text="正在删除存档路径.")
				os.remove('./musync_data/SaveFilePath.sfp')
				self.GetSaveFile()
			else:
				self.saveFilePathVar.set(sfpr)
		if self.config['EnableAnalyzeWhenStarting']:
			self.DeleteAnalyzeFile()
		self.CheckFile()
		if self.config['EnableDLLInjection']:
			self.hitDelay = Button(self.root, text="游玩结算",command=self.HitDelay, font=self.font,bg='#FF5959')
			self.hitDelay.place(x=775,y=50,width=90,height=30)
		if os.path.isfile('./musync_data/SavAnalyze.json'):
			self.DataLoad()
		elif os.path.isfile('./musync_data/SavDecode.decode'):
			self.InitLabel('解码存档中......')
			MusyncSavDecode.MUSYNCSavProcess(decodeFile='./musync_data/SavDecode.decode').Main('decode')
			self.DataLoad()
		else:
			self.DataLoad()

# json文件检查
	def CheckFile(self):
		saveData=None
		if os.path.isfile('./musync_data/SavAnalyze.json'):
			try:
				with open(f'./musync_data/SavAnalyze.json','r+',encoding='utf8') as saveData:
					saveDataJson = json.load(saveData)
			except Exception as e:
				messagebox.showerror("Error", f'SavAnalyze.json文件打开失败\n错误的Json文件格式\n{e}')
				os.remove("./musync_data/SavAnalyze.json")
			else:
				if len(saveDataJson['SaveData']) == 0:
					os.remove("./musync_data/SavAnalyze.json")

# select功能组
	def SelectKeys(self):
		self.keys = (self.keys+1)%3
		self.selectKeys.configure(text=['4 & 6Keys','4 Keys','6 Keys'][self.keys])
		self.selectKeys.place(width=[102,72,72][self.keys])
		self.DataLoad()
		self.root.update()
	def SelectDifficute(self):
		self.difficute = (self.difficute+1)%4
		self.selectDifficute.configure(text=['Easy','Hard',"Inferno",'所有难度'][self.difficute])
		self.selectDifficute.place(width=[52,52,82,92][self.difficute])
		self.DataLoad()
		self.root.update()
	def SelectDLCSong(self):
		self.isDLC = (self.isDLC+1)%3
		self.selectDLCSong.configure(text=['所\n有','本\n体','扩\n展'][self.isDLC])
		self.selectDLCSong.configure(bg=['#F0F0F0','#FF9B9B','#98E22B'][self.isDLC])
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
		print(songData)
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
		self.DeleteAnalyzeFile()

# update功能组
	def CheckJsonUpdate(self):
		startTime = time.perf_counter_ns()
		try:
			response = requests.get("https://raw.githubusercontent.com/Ginsakura/MUSYNCSave/main/musync_data/songname.update")
			githubVersion = response.content.decode('utf8')
			with open("./musync_data/SongName.update",'r',encoding='utf8') as snju:
				localVersion = snju.read()
			print(f"   Local Json Version: {localVersion}")
			print(f"  Terget Json Version: {githubVersion}")
			if githubVersion>localVersion:
				response = requests.get("https://raw.githubusercontent.com/Ginsakura/MUSYNCSave/main/musync_data/songname.json")
				songNameJson = response.json()
				with open("./musync_data/SongName.json",'w',encoding='utf8') as snj:
					json.dump(songNameJson,snj,indent="",ensure_ascii=False)
				with open("./musync_data/SongName.update",'r',encoding='utf8') as snju:
					snju.write(githubVersion)
		except Exception as e:
			messagebox.showerror("Error", f'发生错误: {e}')
			messagebox.showerror("Error", f'若游戏本体已更新，请访问仓库更新songname.update和songname.json两个文件')
		endTime = time.perf_counter_ns()
		print("CheckJsonUpdate Run Time: %f ms"%((endTime - startTime)/1000000))

	def CheckUpdate(self):
		startTime = time.perf_counter_ns()
		localVersion = float(self.version.replace(".","").replace("rc","."))
		try:
			response = requests.get("https://api.github.com/repos/ginsakura/MUSYNCSave/releases/latest")
			tagVersion = response.json()["tag_name"]
			tergetVersion = float(tagVersion.replace(".","").replace("rc","."))
		except Exception as e:
			messagebox.showerror("Error", f'发生错误: {e}')
			tergetVersion = localVersion
		# print(localVersion,tergetVersion)
		print('  Terget Version : %s'%tagVersion.replace("rc","."))
		print('   Local Version : %s'%self.version.replace("rc","."))
		print("Local PreVersion : %s"%self.preVersion.replace("pre","."))
		if (tergetVersion > localVersion):
			self.gitHubLink.configure(text=f'有新版本啦——点此打开下载页面	NewVersion: {tagVersion}', anchor="center")
			self.gitHubLink.configure(command=lambda:webbrowser.open(f"https://github.com/Ginsakura/MUSYNCSave/releases/tag/{tagVersion}"))
			self.UpdateTip()
		else:
			self.gitHubLink.configure(text='点击打开GitHub仓库	点个Star吧，秋梨膏', anchor="center")
			self.gitHubLink.configure(command=lambda:webbrowser.open("https://github.com/Ginsakura/MUSYNCSave"))
		endTime = time.perf_counter_ns()
		print("CheckUpdate Run Time: %f ms"%((endTime - startTime)/1000000))

	def UpdateTip(self):
		if self.gitHubLink.cget('fg') == '#C4245C':
			self.gitHubLink.configure(fg='#4BB1DA')
		else:
			self.gitHubLink.configure(fg='#C4245C')
		self.root.after(500,self.UpdateTip)

# 初始化提示框
	def InitLabel(self,text,close=False):
		self.initLabel.place(x=250,y=300,width=500,height=30)
		self.initLabel.configure(text=text, anchor="w")
		self.root.update()
		if close:
			self.initLabel.place(x=-1,width=0)

# 数据分析功能组
	def GetSaveFile(self):
		startTime = time.perf_counter_ns()
		self.InitLabel("正在搜索存档文件中……")
		saveFilePath = None
		for ids in "DEFCGHIJKLMNOPQRSTUVWXYZAB":
			if os.path.isfile(f'{ids}:/Program Files/steam/steamapps/common/MUSYNX/SavesDir/savedata.sav'):
				saveFilePath = f"{ids}:/Program Files/steam/steamapps/common/MUSYNX/"
				break
			elif os.path.isfile(f'{ids}:/SteamLibrary/steamapps/common/MUSYNX/SavesDir/savedata.sav'):
				saveFilePath = f"{ids}:/SteamLibrary/steamapps/common/MUSYNX/"
				break
			elif os.path.isfile(f'{ids}:/steam/steamapps/common/MUSYNX/SavesDir/savedata.sav'):
				saveFilePath = f"{ids}:/steam/steamapps/common/MUSYNX/"
				break
		print("savefilepath:",saveFilePath)
		if not saveFilePath == None:
			with open('./musync_data/SaveFilePath.sfp','w',encoding="utf8") as sfp:
				sfp.write(saveFilePath+'SavesDir/savedata.sav')
			self.saveFilePathVar.set(saveFilePath+'SavesDir/savedata.sav')
			if self.config['MainExecPath'] != saveFilePath:
				self.config['MainExecPath'] = saveFilePath
				json.dump(self.config,open('./musync_data/ExtraFunction.cfg','w',encoding='utf8'),indent="",ensure_ascii=False)
		else:
			self.InitLabel("搜索不到存档文件.")
		endTime = time.perf_counter_ns()
		print("GetSaveFile Run Time: %f ms"%((endTime - startTime)/1000000))

	def DeleteAnalyzeFile(self):
		if os.path.isfile("./musync_data/SavAnalyze.json"):
			os.remove("./musync_data/SavAnalyze.json")
		if os.path.isfile("./musync_data/SavAnalyze.analyze"):
			os.remove("./musync_data/SavAnalyze.analyze")
		if os.path.isfile("./musync_data/SavDecode.decode"):
			os.remove("./musync_data/SavDecode.decode")
		self.DataLoad()
	def HitDelay(self):
		if not HitDelayCheck().DLLCheck():
			messagebox.showerror("Error", f'DLL注入失败：软件版本过低或者游戏有更新,\n请升级到最新版或等待开发者发布新的补丁')
		else:
			nroot = Toplevel(self.root)
			nroot.resizable(True, True)
			HitDelayText(nroot)
	def DataLoad(self):
		startTime = time.perf_counter_ns()
		self.InitLabel(text="正在分析存档文件中……")
		def Rank(sync):
			sync = float(sync[0:-1])
			if sync < 75:return "C"
			elif sync < 95:return "B"
			elif sync < 110:return "A"
			elif sync < 117:return "S"
			elif sync < 120:return "蓝Ex"
			elif sync < 122:return "红Ex"
			else:return "黑Ex"

		if os.path.isfile('./musync_data/SavAnalyze.json'):pass
		elif os.path.isfile('./musync_data/SavDecode.decode'):MusyncSavDecode.MUSYNCSavProcess(decodeFile='./musync_data/SavDecode.decode').Main('decode')
		else:
			if self.saveFilePathVar.get() == 'Input SaveFile or AnalyzeFile Path (savedata.sav)or(SavAnalyze.json)':
				self.SelectPath()
			MusyncSavDecode.MUSYNCSavProcess(self.saveFilePathVar.get()).Main()

		saveData = open(f'./musync_data/SavAnalyze.json','r+',encoding='utf8')
		saveDataJson = json.load(saveData)
		saveData.close()

		self.InitLabel('正在分析存档文件中……')
		with open(f'./musync_data/SavAnalyze.json','r',encoding='utf8') as saveData:
			saveDataJson = json.load(saveData)
			with open("./musync_data/SongName.json",'r',encoding='utf8') as snj:
				songNameJson = json.load(snj)
			self.root.title(f'同步音律喵赛克Steam端本地存档分析   LastPlay: {saveDataJson["LastPlay"]}')
			[self.saveData.delete(ids) for ids in self.saveData.get_children()]
			self.saveCount = 0
			self.totalSync = 0
			for saveLine in saveDataJson['SaveData']:
				if not saveLine['SongName'] is None:
					if (self.keys==1) and (saveLine['SongName'][1]=='6Key'):continue
					elif (self.keys==2) and (saveLine['SongName'][1]=='4Key'):continue
					if (self.difficute==0) and (not saveLine['SongName'][2]=='Easy'):continue
					elif (self.difficute==1) and (not saveLine['SongName'][2]=='Hard'):continue
					elif (self.difficute==2) and (not saveLine['SongName'][2]=='Inferno'):continue
					if (self.isDLC==1) and (not saveLine['SongName'][0] in songNameJson["NotDLCSong"]):continue
					elif (self.isDLC==2) and (saveLine['SongName'][0] in songNameJson["NotDLCSong"]):continue
				if self.dataSelectMethod == "Played":
					if (saveLine["PlayCount"] == 0) and (float(saveLine["SyncNumber"][0:-1]) == 0):continue
				elif self.dataSelectMethod == "Unplay":
					if not ((saveLine["PlayCount"] == 0) and (float(saveLine["SyncNumber"][0:-1]) == 0)):continue
				elif self.dataSelectMethod == "IsFav":
					if saveLine["Status"] != 'Favo':continue
				elif self.dataSelectMethod == "Sync122":
					if float(saveLine["SyncNumber"][0:-1]) < 122:continue
				elif self.dataSelectMethod == "Sync120":
					if (float(saveLine["SyncNumber"][0:-1]) < 120) or (float(saveLine["SyncNumber"][0:-1]) > 122):continue
				elif self.dataSelectMethod == "RankEX":
					if float(saveLine["SyncNumber"][0:-1]) < 117:continue
				elif self.dataSelectMethod == "RankS":
					if (float(saveLine["SyncNumber"][0:-1]) < 110) or (float(saveLine["SyncNumber"][0:-1]) >= 117):continue
				elif self.dataSelectMethod == "RankA":
					if (float(saveLine["SyncNumber"][0:-1]) < 95) or (float(saveLine["SyncNumber"][0:-1]) >= 110):continue
				elif self.dataSelectMethod == "RankB":
					if (float(saveLine["SyncNumber"][0:-1]) < 75) or (float(saveLine["SyncNumber"][0:-1]) >= 95):continue
				elif self.dataSelectMethod == "RankC":
					if (float(saveLine["SyncNumber"][0:-1]) == 0) or (float(saveLine["SyncNumber"][0:-1]) >= 75):continue
				if saveLine["Status"] in ['    ', 'Favo']:
					self.saveCount += 1
					self.totalSync += float(saveLine["UploadScore"][0:-1])
				else:
					self.excludeCount += 1
				self.saveData.insert('', END, values=(saveLine["SpeedStall"], #谱面号
					("" if saveLine["SongName"] is None else saveLine["SongName"][0]), #曲名
					("" if saveLine["SongName"] is None else saveLine["SongName"][1]), #键数
					("" if saveLine["SongName"] is None else saveLine["SongName"][2]), #难度
					("" if saveLine["SongName"] is None else ("" if saveLine["SongName"][3]=="00" else saveLine["SongName"][3])), #等级
					saveLine["SyncNumber"], #本地同步率
					("" if ((saveLine["PlayCount"] == 0) and (saveLine["UploadScore"] == "0.00000000000000%")) else Rank(saveLine["SyncNumber"])), #Rank
					saveLine["UploadScore"], saveLine["PlayCount"], saveLine["Status"]))
			# print(songNameJson["NotDLCSong"])
		if not self.dataSortMethodsort[0] is None:
			self.SortClick(self.dataSortMethodsort)
		self.InitLabel('数据展示生成完成.',close=True)
		endTime = time.perf_counter_ns()
		print("DataLoad Run Time: %f ms"%((endTime - startTime)/1000000))
		self.UpdateWindowInfo()

# 控件更新功能组
	def TreeviewColumnUpdate(self):
		self.saveData.heading("SpeedStall",anchor="center",text="谱面号"+(('⇓' if self.dataSortMethodsort[1] else '⇑') if self.dataSortMethodsort[0]=='SpeedStall' else ''))
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
		self.saveData.column("SpeedStall",anchor="e",width=90)
		self.saveData.column("SongName",anchor="w",width=self.windowInfo[2]-771)
		self.saveData.column("Keys",anchor="center",width=60)
		self.saveData.column("Difficulty",anchor="w",width=65)
		self.saveData.column("DifficultyNumber",anchor="center",width=60)
		self.saveData.column("SyncNumber",anchor="e",width=80)
		self.saveData.column("Rank",anchor="center",width=55)
		self.saveData.column("UploadScore",anchor="e",width=160)
		self.saveData.column("PlayCount",anchor="e",width=90)
		self.saveData.column("Status",anchor="w",width=80)

	def UpdateWindowInfo(self):

		self.windowInfo = ['root.winfo_x()','root.winfo_y()',self.root.winfo_width(),self.root.winfo_height()]

		self.saveFilePathEntry.place(x=170,y=10,width=(self.windowInfo[2]-260),height=30)
		self.getSaveFilePath.place(x=(self.windowInfo[2]-90),y=10,width=90,height=30)
		self.saveData.place(x=0 ,y=130 ,width=(self.windowInfo[2]-1) ,height=(self.windowInfo[3]-160))
		if not self.wh == self.windowInfo[2:]:
			self.TreeviewWidthUptate()
			self.VScroll1.place(x=self.windowInfo[2]-22, y=1, width=20, height=self.windowInfo[3]-162)
		# self.saveCountVar.set()
		self.saveCountLabel.configure(text=str(self.saveCount+self.excludeCount))
		self.avgSyncLabel.configure(text=f'{(self.totalSync / (1 if self.saveCount==0 else self.saveCount)):.6f}%')
		self.developer.place(x=0,y=self.windowInfo[3]-30,width=420,height=30)
		self.gitHubLink.place(x=420,y=self.windowInfo[3]-30,width=self.windowInfo[2]-420,height=30)

		self.isGameRunning.bind('<Button-1>', self.StartGame)
		self.saveData.bind("<Double-1>",self.DoubleClick)
		self.saveData.bind("<ButtonRelease-1>",self.SortClick)
		self.root.bind("<F5>", self.F5Key)
		self.wh = self.windowInfo[2:]
		self.root.update()
		# if self.after == False:
		# 	self.after = True
		# 	self.root.after(100,self.UpdateWindowInfo)

class SubWindow(object):
	def __init__(self, nroot, songID, songName, songDifficute):
		##Init##
		nroot.iconbitmap('./musync_data/Musync.ico')
		super(SubWindow, self).__init__()
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


if __name__ == '__main__':
	version = '1.2.6rc3'
	isPreRelease = True
	preVersion = "1.2.6pre7"

	root = Tk()
	ctypes.windll.shcore.SetProcessDpiAwareness(1)
	fonts = list(font.families())
	Functions.CheckFileBeforeStarting(fonts)
	del fonts
	Functions.CheckConfig()
	with open('./musync_data/ExtraFunction.cfg','r',encoding='utf8') as cfg:
		cfg = json.load(cfg)
	if cfg['ChangeConsoleStyle']:
		Functions.ChangeConsoleStyle()
	root.tk.call('tk', 'scaling', 1.25)
	root.resizable(False, True) #允许改变窗口高度，不允许改变窗口宽度
	window = MusyncSavDecodeGUI(root=root,version=version,preVersion=preVersion,isPreRelease=isPreRelease)
	root.update()
	root.mainloop()
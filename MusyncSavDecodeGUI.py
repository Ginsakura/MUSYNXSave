import os
import json
#import time
import MusyncSavDecode
import ctypes
import webbrowser
import requests
import threading
from PIL import Image as PILImage
from PIL import ImageTk
from tkinter import *
from tkinter import Tk,ttk,font
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from HitDelay import HitDelayCheck,HitDelayText
import Functions
#import win32api
#import win32con
#import win32gui_struct
#import win32gui
#from threading import Thread
version = '1.2.1rc4'

class MusyncSavDecodeGUI(object):
	"""docstring for MusyncSavDecodeGUI"""
	def __init__(self, root=None, isTKroot=True, dpi=100):
		##Init##
		self.version = version
		root.iconbitmap('./musync_data/Musync.ico')
		super(MusyncSavDecodeGUI, self).__init__()
		self.isTKroot = isTKroot
		root.geometry(f'1000x670+500+300')
		style = ttk.Style()
		if dpi == 100:
			style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',13))
			style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',15))
			style.configure("reload.TButton", font=('霞鹜文楷等宽',16))
			#, background='#EEBBBB', foreground='#00CCFF',relief='ridge')
			style.configure("F5.TButton", font=('霞鹜文楷等宽',16), bg="#EEBBBB")
			self.font=('霞鹜文楷等宽',16)
		# elif dpi == 125:
		else:
			style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',11))
			style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',15))
			style.configure("reload.TButton", font=('霞鹜文楷等宽',13.5))
			#, background='#EEBBBB', foreground='#00CCFF',relief='ridge')
			style.configure("F5.TButton", font=('霞鹜文楷等宽',13.5), bg="#EEBBBB")
			self.font=('霞鹜文楷等宽',13.5)
		if isTKroot == True:
			root.title("同步音律喵赛克 Steam端 本地存档分析")
			root['background'] = '#efefef'
		self.saveFilePathVar = StringVar()
		self.saveFilePathVar.set('Input SaveFile or AnalyzeFile Path (savedata.sav)or(SavAnalyze.json)')
		self.analyzeFilePathVar = StringVar()
		self.analyzeFilePathVar.set('Input Analyze File Dir (or not)')
		self.root = root
		self.root.minsize(500, 460)
		self.windowInfo = [root.winfo_x(),root.winfo_y(),root.winfo_width(),root.winfo_height()]
		self.saveCount = 0
		self.saveCountVar = StringVar()
		self.saveCountVar.set(str(self.saveCount))
		self.totalSync = 0
		self.avgSyncVar = StringVar()
		self.avgSyncVar.set(f'{(self.totalSync / (1 if self.saveCount==0 else self.saveCount))}')
		self.dataSortMethodsort = [None,False]
		self.dataSelectMethod = None
		self.keys = 0
		self.treeviewColumns = ["SpeedStall",'SongName',"Keys","Difficulty","DifficultyNumber","SyncNumber","Rank","UploadScore","PlayCount","IsFav"]
		self.difficute = 3
		self.wh = [0,0]
		self.vScrollpos = (0,1)

		##Controls##
		# self..place(x= ,y= ,width= ,height=)
		# self.saveFileDecodeButton = Button(self.root, text="存档解码及分析",command=self.DeleteAnalyzeFile, font=self.font)
		# self.saveFileDecodeButton = ttk.Button(self.root, text="存档解码及分析",command=self.DeleteAnalyzeFile, image=ImageTk.PhotoImage(PILImage.open("./skin/Decode.png")), style='reload.TButton')
		self.saveFileDecodeButton = ttk.Button(self.root, text="存档解码及分析", command=self.DeleteAnalyzeFile, image=self.LoadImage('./skin/Decode.png',(150,30)), style='reload.TButton')
		self.saveFileDecodeButton.place(x=10,y=10,width=150,height=30)

		self.CountFrameLanel = Label(self.root,text="", relief="groove")
		self.CountFrameLanel.place(x=8,y=48,width=164,height=34)
		self.PrintLabel0 = Label(self.root, text='显示计数: ', font=self.font, relief="flat")
		self.PrintLabel0.place(x=10,y=50,width=100,height=30)
		self.saveCountLabel = Label(self.root, text=self.saveCountVar.get(), font=self.font, relief="flat")
		self.saveCountLabel.place(x=110,y=50,width=60,height=30)

		self.saveFilePathEntry = Entry(self.root, textvariable=self.saveFilePathVar, font=self.font, relief="sunken")
		self.getSaveFilePath = Button(self.root, text='打开存档', command=self.SelectPath, font=self.font)

		self.saveData = ttk.Treeview(self.root, show="headings", columns = self.treeviewColumns)
		self.VScroll1 = Scrollbar(self.saveData, orient='vertical', command=self.saveData.yview)
		# self.VScroll1 = Scrollbar(self.saveData, orient='vertical', command=print)
		self.saveData.configure(yscrollcommand=self.VScroll1.set)

		self.developer = Label(self.root, text=f'Version {self.version} | Develop By Ginsakura', font=self.font, relief="groove")
		# self.gitHubLink = Button(self.root, text='https://github.com/Ginsakura/MUSYNCSave	点个Star吧，秋梨膏', command=lambda:webbrowser.open("https://github.com/Ginsakura/MUSYNCSave"), fg='#4BB1DA', anchor="center", font=self.font, relief="groove")
		self.gitHubLink = Button(self.root, text='点击打开下载链接	点个Star吧，秋梨膏', command=lambda:webbrowser.open("https://github.com/Ginsakura/MUSYNCSave"), fg='#4BB1DA', anchor="center", font=self.font, relief="groove")

		self.initLabel = Label(self.root, text='启动中......', anchor="w", font=self.font, relief="groove")
		self.initLabel.place(x=250,y=300,width=500,height=30)

		self.deleteAnalyzeFile = ttk.Button(self.root, text="刷新",command=self.DeleteAnalyzeFile,style='F5.TButton', image=self.LoadImage('./skin/F5.png',(90,30)))
		self.deleteAnalyzeFile.place(x=10,y=88,width=90,height=30)

		self.totalSyncFrameLabel = Label(self.root, text='', relief="groove")
		self.totalSyncFrameLabel.place(x=868,y=48,width=124,height=74)
		self.totalSyncTextLabel = Label(self.root, text='综合同步率', anchor="center", font=self.font, relief="flat")
		self.totalSyncTextLabel.place(x=870,y=50,width=120,height=30)
		self.avgSyncLabel = Label(self.root, text=self.avgSyncVar.get()+'%', anchor="w", font=self.font, relief="flat")
		self.avgSyncLabel.place(x=870,y=90,width=120,height=30)

		#筛选控件
		self.selectFrameLabel0 = Label(self.root, text="", relief="groove")
		self.selectFrameLabel0.place(x=178,y=48,width=383,height=74)
		self.selectLabel0 = Label(self.root, text="筛选\n控件", anchor="w", font=self.font, relief="flat")
		self.selectLabel0.place(x=180,y=55,width=50,height=60)
		self.selectPlayedButton = Button(self.root, text='已游玩', command=lambda:self.SelectMethod('Played'), anchor="w", font=self.font)
		self.selectPlayedButton.place(x=230,y=50,width=75,height=30)
		self.selectUnplayButton = Button(self.root, text='未游玩', command=lambda:self.SelectMethod('Unplay'), anchor="w", font=self.font)
		self.selectUnplayButton.place(x=230,y=88,width=75,height=30)
		self.selectIsFavButton = Button(self.root, text='已收藏', command=lambda:self.SelectMethod('IsFav'), anchor="w", font=self.font)
		self.selectIsFavButton.place(x=305,y=50,width=75,height=30)
		self.selectExRankButton = Button(self.root, text='RankEx', command=lambda:self.SelectMethod('RankEX'), anchor="w", font=self.font)
		self.selectExRankButton.place(x=305,y=88,width=75,height=30)
		self.selectSRankButton = Button(self.root, text='RankS', command=lambda:self.SelectMethod('RankS'), anchor="w", font=self.font)
		self.selectSRankButton.place(x=380,y=50,width=62,height=30)
		self.selectARankButton = Button(self.root, text='RankA', command=lambda:self.SelectMethod('RankA'), anchor="w", font=self.font)
		self.selectARankButton.place(x=380,y=88,width=62,height=30)
		self.selectBRankButton = Button(self.root, text='RankB', command=lambda:self.SelectMethod('RankB'), anchor="w", font=self.font)
		self.selectBRankButton.place(x=442,y=50,width=62,height=30)
		self.selectCRankButton = Button(self.root, text='RankC', command=lambda:self.SelectMethod('RankC'), anchor="w", font=self.font)
		self.selectCRankButton.place(x=442,y=88,width=62,height=30)
		self.select122Button = Button(self.root, text='黑Ex', command=lambda:self.SelectMethod('Sync122'), anchor="w", font=self.font)
		self.select122Button.place(x=504,y=50,width=52,height=30)
		self.select120Button = Button(self.root, text='红Ex', command=lambda:self.SelectMethod('Sync120'), anchor="w", font=self.font)
		self.select120Button.place(x=504,y=88,width=52,height=30)

		##额外筛选##
		self.selectFrameLabel1 = Label(self.root, text="", relief="groove")
		self.selectFrameLabel1.place(x=568,y=48,width=169,height=74)
		self.selectLabel1 = Label(self.root, text="额外\n筛选", anchor="w", font=self.font, relief="flat")
		self.selectLabel1.place(x=570,y=55,width=50,height=60)
		self.selectKeys = Button(self.root, text=['4 & 6 Keys','4 Keys','6 Keys'][self.keys], command=lambda:self.SelectKeys(), anchor='w', font=self.font)
		self.selectKeys.place(x=620,y=50,width=[112,72,72][self.keys],height=30)
		self.selectDifficute = Button(self.root, text=['Easy','Hard',"Inferno",'所有难度'][self.difficute], command=lambda:self.SelectDifficute(), anchor='w', font=self.font)
		self.selectDifficute.place(x=620,y=88,width=[52,52,82,92][self.difficute],height=30)

		##AutoRun##
		self.InitLabel('初始化函数执行中......')
		self.UpdateWindowInfo()
		self.TreeviewWidthUptate()
		self.TreeviewColumnUpdate()

		with open('./musync_data/ExtraFunction.cfg','r') as confFile:
			config = json.load(confFile)

		if config['DisableCheckUpdate']:
			self.gitHubLink.configure(text='更新已禁用	点击打开GitHub仓库页')
		else:
			threading.Thread(target=self.CheckUpdate).start()
			threading.Thread(target=self.CheckJsonUpdate).start()
		if config['EnableAnalyzeWhenStarting']:
			self.DeleteAnalyzeFile()
		self.CheckFile()
		if config['EnableDLLInjection']:
			self.hitDelay = Button(self.root, text="DLL注入\n分析\n游玩结果",command=self.HitDelay, font=self.font,bg='#FF5555')
			self.hitDelay.place(x=776,y=48,width=90,height=74)
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
				execPath = sfpr[:-21]
				# print(execPath)
				if config['MainExecPath'] != execPath:
					config['MainExecPath'] = execPath
					json.dump(config,open('./musync_data/ExtraFunction.cfg','w'),indent="",ensure_ascii=False)
				self.DataLoad()
		if os.path.isfile('./musync_data/SavAnalyze.json'):
			self.DataLoad()
		elif os.path.isfile('./musync_data/SavDecode.decode'):
			self.InitLabel('解码存档中......')
			MusyncSavDecode.MUSYNCSavProcess(decodeFile='./musync_data/SavDecode.decode').Main('decode')
			self.DataLoad()

	def LoadImage(self,imgPath,size):
		img = PILImage.open(imgPath)
		img = img.resize(size)
		return ImageTk.PhotoImage(img)

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
				# saveData = open(f'./musync_data/SavAnalyze.json','r+',encoding='utf8')
				# saveDataJson = json.load(saveData)
				# saveData.close()
				# print(len(saveDataJson['SaveData']))
				if len(saveDataJson['SaveData']) == 0:
					os.remove("./musync_data/SavAnalyze.json")

	def SelectKeys(self):
		self.keys = (self.keys+1)%3
		self.selectKeys.configure(text=['4 & 6Keys','4 Keys','6 Keys'][self.keys])
		self.selectKeys.place(width=[102,72,72][self.keys])
		self.root.update()
		self.DataLoad()
	def SelectDifficute(self):
		self.difficute = (self.difficute+1)%4
		self.selectDifficute.configure(text=['Easy','Hard',"Inferno",'所有难度'][self.difficute])
		self.selectDifficute.place(width=[52,52,82,92][self.difficute])
		self.root.update()
		self.DataLoad()
	def SelectMethod(self,method):
		if self.dataSelectMethod == method:
			self.dataSelectMethod = None
			self.SelectButtonGrey(method)
		else:
			self.SelectButtonGrey(self.dataSelectMethod)
			self.dataSelectMethod = method
			self.SelectButtonGreen(method)
		self.DataLoad()
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

	def CheckJsonUpdate(self):
		try:
			response = requests.get("https://raw.githubusercontent.com/Ginsakura/MUSYNCSave/main/musync_data/songname.update")
			githubVersion = response.content.decode('utf8')
			with open("./musync_data/SongName.update",'r',encoding='utf8') as snju:
				localVersion = snju.read()
			if githubVersion>localVersion:
				response = requests.get("https://raw.githubusercontent.com/Ginsakura/MUSYNCSave/main/musync_data/songname.json")
				songNameJson = response.json()
				with open("./musync_data/SongName.json",'w',encoding='utf8') as snj:
					json.dump(songNameJson,snj,indent="",ensure_ascii=False)
				with open("./musync_data/SongName.update",'r',encoding='utf8') as snju:
					snju.write(githubVersion)
		except Exception as e:
			messagebox.showerror("Error", f'发生错误: {e}')

	def CheckUpdate(self):
		oldVersion,oldRC = int(f'{self.version[0]}{self.version[2]}{self.version[4]}'),int(self.version[7:])
		try:
			response = requests.get("https://api.github.com/repos/ginsakura/MUSYNCSave/releases/latest")
			version = response.json()["tag_name"]
			# print(version)
			newVersion,newRC = int(f'{version[0]}{version[2]}{version[4]}'),int(version[7:])
		except Exception as e:
			messagebox.showerror("Error", f'发生错误: {e}')
			newVersion,newRC = oldVersion,oldRC
		# print(newVersion)
		print(f'terget: {newVersion}.{newRC}')
		print(f'local: {oldVersion}.{oldRC}')
		if (newVersion > oldVersion) or ((newVersion == oldVersion) and (newRC > oldRC)):
			self.gitHubLink.configure(text=f'有新版本啦——点此打开下载页面	NewVersion: {version}', anchor="center")
			self.gitHubLink.configure(command=lambda:webbrowser.open("https://github.com/Ginsakura/MUSYNCSave/releases"))
			self.UpdateTip()
		else:
			self.gitHubLink.configure(text='点击打开GitHub仓库	点个Star吧，秋梨膏', anchor="center")
			self.gitHubLink.configure(command=lambda:webbrowser.open("https://github.com/Ginsakura/MUSYNCSave"))

	def InitLabel(self,text,close=False):
		self.initLabel.place(x=250,y=300,width=500,height=30)
		self.initLabel.configure(text=text, anchor="w")
		self.root.update()
		if close:
			self.initLabel.place(x=-1,width=0)

	# def DoubleClick(self,event):
	# 	e = event.widget									# 取得事件控件
	# 	itemID = e.identify("item",event.x,event.y)			# 取得双击项目id
	# 	# state = e.item(itemID,"text")						# 取得text参数
	# 	songData = e.item(itemID,"values")					# 取得values参数
	# 	# print(e.item(itemID))
	# 	nroot = Toplevel(self.root)
	# 	nroot.resizable(True, True)
	# 	newWindow = SubWindow(nroot, songData[0], songData[1], songData[2])
	def SortClick(self,event):
		def TreeviewSortColumn(col):
			# print(self.dataSortMethodsort, end=' /// ')
			if self.dataSortMethodsort[0] == col:
				self.dataSortMethodsort[1] = not self.dataSortMethodsort[1]
			else:
				self.dataSortMethodsort[0] = col
				self.dataSortMethodsort[1] = False
			if col == 'SyncNumber' or col == 'UploadScore':
				l = [(float((self.saveData.set(k, col))[:-1]), k) for k in self.saveData.get_children('')]
			elif col == 'PlayCount':
				l = [(int(self.saveData.set(k, col)), k) for k in self.saveData.get_children('')]
			else:
				l = [(self.saveData.set(k, col), k) for k in self.saveData.get_children('')]
			# print(l)
			l.sort(reverse=self.dataSortMethodsort[1])
			for index, (val, k) in enumerate(l):
				self.saveData.move(k, '', index)
			# print(self.dataSortMethodsort)
			self.TreeviewColumnUpdate()
		if isinstance(event, list):
			self.dataSortMethodsort[1] = not self.dataSortMethodsort[1]
			TreeviewSortColumn(event[0])
		for col in self.treeviewColumns:
			self.saveData.heading(col, command=lambda _col=col:TreeviewSortColumn(_col))

	def UpdateTip(self):
		if self.gitHubLink.cget('fg') == '#C4245C':
			self.gitHubLink.configure(fg='#4BB1DA')
		else:
			self.gitHubLink.configure(fg='#C4245C')
		root.after(500,self.UpdateTip)

	def GetSaveFile(self):
		self.InitLabel("正在搜索存档文件中……")
		saveFilePath = None
		for ids in "DEFCGHIJKLMNOPQRSTUVWXYZAB":
			if os.path.isfile(f'{ids}:/Program Files/steam/steamapps/common/MUSYNX/SavesDir/savedata.sav'):
				saveFilePath = f"{ids}:/Program Files/steam/steamapps/common/MUSYNX/SavesDir/savedata.sav"
				break
			elif os.path.isfile(f'{ids}:/SteamLibrary/steamapps/common/MUSYNX/SavesDir/savedata.sav'):
				saveFilePath = f"{ids}:/SteamLibrary/steamapps/common/MUSYNX/SavesDir/savedata.sav"
				break
			elif os.path.isfile(f'{ids}:/steam/steamapps/common/MUSYNX/SavesDir/savedata.sav'):
				saveFilePath = f"{ids}:/steam/steamapps/common/MUSYNX/SavesDir/savedata.sav"
				break
		if not saveFilePath == None:
			with open('./musync_data/SaveFilePath.sfp','w',encoding="utf8") as sfp:
				sfp.write(saveFilePath)
				self.saveFilePathVar.set(saveFilePath)
			self.DataLoad()
		else:
			self.InitLabel("搜索不到存档文件.")

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
		self.InitLabel(text="正在分析存档文件中……")
		self.vScrollpos = self.VScroll1.get()
		def Rank(sync):
			sync = float(sync[0:-1])
			if sync < 75:return "C"
			elif sync < 95:return "B"
			elif sync < 110:return "A"
			elif sync < 117:return "S"
			elif sync < 120:return "蓝Ex"
			elif sync < 122:return "红Ex"
			else:return "黑Ex"

		for ids in self.saveData.get_children():
			self.saveData.delete(ids)
		self.saveCount = 0
		self.totalSync = 0
		if os.path.isfile('./musync_data/SavAnalyze.json'):pass
		elif os.path.isfile('./musync_data/SavDecode.decode'):MusyncSavDecode.MUSYNCSavProcess(decodeFile='./musync_data/SavDecode.decode').Main('decode')
		else:
			if self.saveFilePathEntry.get() == 'Input SaveFile or AnalyzeFile Path (savedata.sav)or(SavAnalyze.json)':
				self.SelectPath()
			MusyncSavDecode.MUSYNCSavProcess(self.saveFilePathVar.get()).Main()

		saveData = open(f'./musync_data/SavAnalyze.json','r+',encoding='utf8')
		saveDataJson = json.load(saveData)
		saveData.close()

		self.InitLabel('正在分析存档文件中……')
		with open(f'./musync_data/SavAnalyze.json','r+',encoding='utf8') as saveData:
			saveDataJson = json.load(saveData)
			self.root.title(f'同步音律喵赛克 Steam端 本地存档分析	LastPlay: {saveDataJson["LastPlay"]}')
			for saveLine in saveDataJson['SaveData']:
				if not saveLine['SongName'] is None:
					if (self.keys==1) and (saveLine['SongName'][1]=='6Key'):continue
					elif (self.keys==2) and (saveLine['SongName'][1]=='4Key'):continue
					if (self.difficute==0) and (not saveLine['SongName'][2]=='Easy'):continue
					elif (self.difficute==1) and (not saveLine['SongName'][2]=='Hard'):continue
					elif (self.difficute==2) and (not saveLine['SongName'][2]=='Inferno'):continue
				if self.dataSelectMethod == "Played":
					if (saveLine["PlayCount"] == 0) and (float(saveLine["SyncNumber"][0:-1]) == 0):continue
				elif self.dataSelectMethod == "Unplay":
					if not ((saveLine["PlayCount"] == 0) and (float(saveLine["SyncNumber"][0:-1]) == 0)):continue
				elif self.dataSelectMethod == "IsFav":
					if saveLine["IsFav"] == '0x00':continue
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
					if float(saveLine["SyncNumber"][0:-1]) >= 75:continue
				self.saveCount += 1
				self.totalSync += float(saveLine["UploadScore"][0:-1])
				self.saveData.insert('', END, values=(saveLine["SpeedStall"],
					("" if saveLine["SongName"] is None else saveLine["SongName"][0]), 
					("" if saveLine["SongName"] is None else saveLine["SongName"][1]), 
					("" if saveLine["SongName"] is None else saveLine["SongName"][2]), 
					("" if saveLine["SongName"] is None else ("" if saveLine["SongName"][3]=="00" else saveLine["SongName"][3])), 
					 saveLine["SyncNumber"], 
					("" if ((saveLine["PlayCount"] == 0) and (saveLine["UploadScore"] == "0.00000000000000%")) else Rank(saveLine["SyncNumber"])), 
					saveLine["UploadScore"], saveLine["PlayCount"], saveLine["IsFav"]))
		if not self.dataSortMethodsort[0] is None:
			self.SortClick(self.dataSortMethodsort)
		self.InitLabel('存档分析完成.',close=True)
		if not (self.vScrollpos[0]==0 and self.vScrollpos[1]==1):
			self.VScroll1.set(self.vScrollpos[0],self.vScrollpos[1])
			self.saveData.yview_moveto(self.vScrollpos[0])

	def SelectPath(self):
		path_ = askopenfilename(title="打开存档文件", filetypes=(("Sav Files", "*.sav"),("All Files","*.*"),)) #使用askdirectory()方法返回文件夹的路径
		if path_ == "":
			self.saveFilePathVar.get() #当打开文件路径选择框后点击"取消" 输入框会清空路径，所以使用get()方法再获取一次路径
		else:
			path_ = path_.replace("/", "\\")  # 实际在代码中执行的路径为“\“ 所以替换一下
			self.saveFilePathVar.set(path_)
		
	def TreeviewColumnUpdate(self):
		self.saveData.heading("SpeedStall",anchor="center",text="谱面号"+(('▼' if self.dataSortMethodsort[1] else '▲') if self.dataSortMethodsort[0]=='SpeedStall' else ''))
		self.saveData.heading("SongName",anchor="center",text="曲名"+(('▼' if self.dataSortMethodsort[1] else '▲') if self.dataSortMethodsort[0]=='SongName' else ''))
		self.saveData.heading("Keys",anchor="center",text="键数"+(('▼' if self.dataSortMethodsort[1] else '▲') if self.dataSortMethodsort[0]=='Keys' else ''))
		self.saveData.heading("Difficulty",anchor="center",text="难度"+(('▼' if self.dataSortMethodsort[1] else '▲') if self.dataSortMethodsort[0]=='Difficulty' else ''))
		self.saveData.heading("DifficultyNumber",anchor="center",text="等级"+(('▼' if self.dataSortMethodsort[1] else '▲') if self.dataSortMethodsort[0]=='DifficultyNumber' else ''))
		self.saveData.heading("SyncNumber",anchor="center",text="同步率"+(('▼' if self.dataSortMethodsort[1] else '▲') if self.dataSortMethodsort[0]=='SyncNumber' else ''))
		self.saveData.heading("Rank",anchor="center",text="Rank"+(('▼' if self.dataSortMethodsort[1] else '▲') if self.dataSortMethodsort[0]=='Rank' else ''))
		self.saveData.heading("UploadScore",anchor="center",text="云端同步率"+(('▼' if self.dataSortMethodsort[1] else '▲') if self.dataSortMethodsort[0]=='UploadScore' else ''))
		self.saveData.heading("PlayCount",anchor="center",text="游玩计数"+(('▼' if self.dataSortMethodsort[1] else '▲') if self.dataSortMethodsort[0]=='PlayCount' else ''))
		self.saveData.heading("IsFav",anchor="center",text="IsFav"+(('▼' if self.dataSortMethodsort[1] else '▲') if self.dataSortMethodsort[0]=='IsFav' else ''))
		self.VScroll1.set(self.vScrollpos[0],self.vScrollpos[1])
		self.saveData.yview_moveto(self.vScrollpos[0])
		self.root.update()

	def TreeviewWidthUptate(self):
		self.saveData.column("SpeedStall",anchor="e",width=90)
		self.saveData.column("SongName",anchor="w",width=self.windowInfo[2]-761)
		self.saveData.column("Keys",anchor="center",width=60)
		self.saveData.column("Difficulty",anchor="w",width=65)
		self.saveData.column("DifficultyNumber",anchor="center",width=60)
		self.saveData.column("SyncNumber",anchor="e",width=80)
		self.saveData.column("Rank",anchor="center",width=70)
		self.saveData.column("UploadScore",anchor="e",width=160)
		self.saveData.column("PlayCount",anchor="e",width=90)
		self.saveData.column("IsFav",anchor="center",width=70)
		self.root.update()

	def UpdateWindowInfo(self):
		self.windowInfo = ['root.winfo_x()','root.winfo_y()',root.winfo_width(),root.winfo_height()]

		self.saveFilePathEntry.place(x=170,y=10,width=(self.windowInfo[2]-260),height=30)
		self.getSaveFilePath.place(x=(self.windowInfo[2]-90),y=10,width=90,height=30)
		self.saveData.place(x=0 ,y=130 ,width=(self.windowInfo[2]-1) ,height=(self.windowInfo[3]-160))
		if not self.wh == self.windowInfo[2:]:
			self.TreeviewWidthUptate()
			self.VScroll1.place(x=self.windowInfo[2]-22, y=1, width=20, height=self.windowInfo[3]-162)
		# self.saveData.yview_moveto(self.VScroll1.get()[0])
		self.saveCountVar.set(self.saveCount)
		self.saveCountLabel.configure(text=self.saveCountVar.get())
		self.avgSyncVar.set(f'{(self.totalSync / (1 if self.saveCount==0 else self.saveCount))}')
		self.avgSyncLabel.configure(text=self.avgSyncVar.get()[0:10]+"%")
		self.developer.place(x=0,y=self.windowInfo[3]-30,width=420,height=30)
		self.gitHubLink.place(x=420,y=self.windowInfo[3]-30,width=self.windowInfo[2]-420,height=30)

		# self.saveData.bind("<Double-1>",self.DoubleClick)
		self.saveData.bind("<ButtonRelease-1>",self.SortClick)

		self.wh = self.windowInfo[2:]
		self.root.update()
		root.after(1000,self.UpdateWindowInfo)

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
	def is_admin():
		try:
			return ctypes.windll.shell32.IsUserAnAdmin()
		except:
			return False
	ctypes.windll.shcore.SetProcessDpiAwareness(1)
	root = Tk()
	fonts = list(font.families())
	Functions.CheckFileBeforeStarting(fonts)
	del fonts
	Functions.CheckConfig()
	with open('./musync_data/ExtraFunction.cfg','r') as cfg:
		cfg = json.load(cfg)
	if cfg['ChangeConsoleStyle']:
		Functions.ChangeConsoleStyle()
		# if is_admin():
		# 	try:
		# 		Functions.ChangeConsoleStyle()
		# 	except Exception as e:
		# 		print(e)
		# 		os.system('pause')
		# else:
		# 	ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
	del cfg
	#root.state('zoomed') #隐藏最小化、最大化按钮
	#设置程序缩放
	# root.tk.call('tk', 'scaling', (ctypes.windll.shcore.GetScaleFactorForDevice(0))/75)
	root.resizable(False, True) #允许改变窗口高度，不允许改变窗口宽度
	window = MusyncSavDecodeGUI(root=root, dpi=Functions.GetDpi())
	root.update()
	root.mainloop()

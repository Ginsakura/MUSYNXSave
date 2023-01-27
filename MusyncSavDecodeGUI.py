import sys
import os
import json
import time
import MusyncSavDecode
import FileExport
import webbrowser
import requests
import pyglet
from tkinter import *
from tkinter import Tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
#import win32api
#import win32con
#import win32gui_struct
#import win32gui
#from threading import Thread

class MusyncSavDecodeGUI(object):
	"""docstring for MusyncSavDecodeGUI"""
	def __init__(self, root, isTKroot=True):
		##Init##
		root.iconbitmap('./Musync.ico')
		super(MusyncSavDecodeGUI, self).__init__()
		self.isTKroot = isTKroot
		self.font=('霞鹜文楷等宽',16)
		root.geometry(f'1000x670+500+300')
		style = ttk.Style()
		style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',12))
		style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',12))
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
		self.dataSortMethod = None
		self.dataSortMethodsort = True
		self.dataSelectMethod = None
		self.version = '1.0.6'

		##Controls##
		#self..place(x= ,y= ,width= ,height=)
		self.saveFileDecodeButton = Button(self.root, text="存档解码及分析", font=self.font)
		self.saveFileDecodeButton.configure(command=self.DataLoad)
		self.saveFileDecodeButton.place(x=10,y=10,width=150,height=30)

		self.CountFrameLanel = Label(self.root,text="", relief="groove")
		self.CountFrameLanel.place(x=8,y=48,width=164,height=34)
		self.PrintLabel0 = Label(self.root, text='显示计数: ', font=self.font, relief="flat")
		self.PrintLabel0.place(x=10,y=50,width=100,height=30)
		self.saveCountLabel = Label(self.root, text=self.saveCountVar.get(), font=self.font, relief="flat")
		self.saveCountLabel.place(x=110,y=50,width=60,height=30)

		self.saveFilePathEntry = Entry(self.root, textvariable=self.saveFilePathVar, font=self.font, relief="sunken")
		self.getSaveFilePath = Button(self.root, text='打开存档', command=self.SelectPath, font=self.font)

		self.saveData = ttk.Treeview(self.root, show="headings")
		self.saveData.configure(columns = ["SongID",'SongName',"Keys","Difficulty","DifficultyNumber","SpeedStall","SyncNumber","Rank","UploadScore","PlayCount","IsFav"])
		self.VScroll1 = Scrollbar(self.saveData, orient='vertical', command=self.saveData.yview)
		self.saveData.configure(yscrollcommand=self.VScroll1.set)

		self.developer = Label(self.root, text=f'Version {self.version} | Develop By Ginsakura', font=self.font, relief="groove")
		self.gitHubLink = Button(self.root, text='https://github.com/Ginsakura/MUSYNCSave    点个Star吧，秋梨膏', command=lambda:webbrowser.open("https://github.com/Ginsakura/MUSYNCSave"), fg='#4BB1DA', anchor="center", font=self.font, relief="groove")

		self.initLabel = Label(self.root, text='启动中', anchor="center", font=self.font, relief="groove")
		self.initLabel.place(x=300,y=300,width=400,height=30)

		self.deleteAnalyzeFile = Button(self.root, text="重新分析",command=self.DeleteAnalyzeFile, font=self.font, bg="#EE0000")
		self.deleteAnalyzeFile.place(x=10,y=88,width=100,height=30)

		self.totalSyncFrameLabel = Label(self.root, text='', relief="groove")
		self.totalSyncFrameLabel.place(x=868,y=48,width=124,height=74)
		self.totalSyncTextLabel = Label(self.root, text='综合同步率', anchor="center", font=self.font, relief="flat")
		self.totalSyncTextLabel.place(x=870,y=50,width=120,height=30)
		self.avgSyncLabel = Label(self.root, text=self.avgSyncVar.get()+'%', anchor="w", font=self.font, relief="flat")
		self.avgSyncLabel.place(x=870,y=90,width=120,height=30)

		#筛选控件
		self.selectFrameLabel = Label(self.root, text="", relief="groove")
		self.selectFrameLabel.place(x=178,y=48,width=426,height=74)
		self.selectLabel = Label(self.root, text="筛选\n控件", anchor="w", font=self.font, relief="flat")
		self.selectLabel.place(x=180,y=55,width=50,height=60)
		self.selectPlayedButton = Button(self.root, text='已游玩', command=lambda:self.SelectMethod('Played'), anchor="w", font=self.font)
		self.selectPlayedButton.place(x=230,y=50,width=70,height=30)
		self.selectUnplayButton = Button(self.root, text='未游玩', command=lambda:self.SelectMethod('Unplay'), anchor="w", font=self.font)
		self.selectUnplayButton.place(x=230,y=88,width=70,height=30)
		self.selectIsFavButton = Button(self.root, text='已收藏', command=lambda:self.SelectMethod('IsFav'), anchor="w", font=self.font)
		self.selectIsFavButton.place(x=300,y=50,width=70,height=30)
		self.selectExRankButton = Button(self.root, text='RankEx', command=lambda:self.SelectMethod('RankEX'), anchor="w", font=self.font)
		self.selectExRankButton.place(x=300,y=88,width=70,height=30)
		self.selectSRankButton = Button(self.root, text='RankS', command=lambda:self.SelectMethod('RankS'), anchor="w", font=self.font)
		self.selectSRankButton.place(x=370,y=50,width=60,height=30)
		self.selectARankButton = Button(self.root, text='RankA', command=lambda:self.SelectMethod('RankA'), anchor="w", font=self.font)
		self.selectARankButton.place(x=370,y=88,width=60,height=30)
		self.selectBRankButton = Button(self.root, text='RankB', command=lambda:self.SelectMethod('RankB'), anchor="w", font=self.font)
		self.selectBRankButton.place(x=430,y=50,width=60,height=30)
		self.selectCRankButton = Button(self.root, text='RankC', command=lambda:self.SelectMethod('RankC'), anchor="w", font=self.font)
		self.selectCRankButton.place(x=430,y=88,width=60,height=30)
		self.select122Button = Button(self.root, text='Score>122%', command=lambda:self.SelectMethod('Sync122'), anchor="w", font=self.font)
		self.select122Button.place(x=490,y=50,width=110,height=30)
		self.select120Button = Button(self.root, text='Score>120%', command=lambda:self.SelectMethod('Sync120'), anchor="w", font=self.font)
		self.select120Button.place(x=490,y=88,width=110,height=30)

		##排序控件##
		self.sortFrameLabel = Label(self.root, text="", relief="groove")
		self.sortFrameLabel.place(x=608,y=48,width=256,height=74)
		self.sortLabel = Label(self.root,text="排序\n控件", anchor="nw", font=self.font, relief="flat")
		self.sortLabel.place(x=610,y=55,width=50,height=60)
		self.sortPlayCountButton = Button(self.root, text="游玩次数", command=lambda:self.SortMethod('PC'), anchor="w", font=self.font)
		self.sortPlayCountButton.place(x=660,y=50,width=90,height=30)
		self.sortDiffNumButton = Button(self.root, text="难度等级", command=lambda:self.SortMethod('DiffNum'), anchor="w", font=self.font)
		self.sortDiffNumButton.place(x=660,y=88,width=90,height=30)
		self.sortSyncButton = Button(self.root, text="本地同步率", command=lambda:self.SortMethod('Sync'), anchor="w", font=self.font)
		self.sortSyncButton.place(x=750,y=50,width=110,height=30)
		self.sortSongNameButton = Button(self.root, text="歌曲名称", command=lambda:self.SortMethod('SongName'), anchor="w", font=self.font)
		self.sortSongNameButton.place(x=750,y=88,width=90,height=30)

		##AutoRun##
		self.UpdateWindowInfo()
		self.CheckUpdate()
		if not os.path.isfile('./SongName.json'):
			Error = list()
			successDown = False
			self.initLabel.configure(text="正在从GitHub Repo下载SongName文件中……", anchor="w")
			try:
				jsonData = requests.get("https://raw.githubusercontent.com/Ginsakura/MUSYNCSave/main/SongName.json")
				try:
					with open("./SongName.json",'wb+') as downData:
						downData.write(jsonData.content)
					successDown = True
				except Exception as e:
					Error.append(f"无法打开SongName.json文件,\n请检查文件是否被占用或读写需要管理员权限.\n{e}\n")
			except Exception as e:
				Error.append(f"无法从GitHub Repo下载SongName.json文件.\n请检查网路连接或者开启代理(VPN)服务.\n{e}\n")
			
			if not successDown:
				pass
			if not len(Error) == 0:
				messagebox.showerror("Error", ''.join(Error))
		if not os.path.isfile('./SaveFilePath.sfp'):
			self.GetSaveFile()
		else:
			self.initLabel.configure(text="正在读取存档路径……", anchor="w")
			sfp = open('./SaveFilePath.sfp','r+')
			sfpr = sfp.read()
			sfp.close()
			if (not sfpr == ""):
				self.GetSaveFile()
			elif (not os.path.isfile(sfpr)):
				self.initLabel.configure(text="正在删除存档路径.", anchor="w")
				os.remove('./SaveFilePath.sfp')
				self.GetSaveFile()
			else:
				self.saveFilePathVar.set(sfpr)
				self.DataLoad()
		if os.path.isfile('./SavAnalyze.json'):
			self.DataLoad()
		elif os.path.isfile('./SavDecode.decode'):
			MusyncSavDecode.MUSYNCSavProcess(decodeFile='./SavDecode.decode').Main('decode')
			self.DataLoad()

	def SortMethod(self,method):
		if self.dataSortMethod == method:
			if self.dataSortMethodsort:
				self.dataSortMethodsort = False
				self.SortButtonGreenRed(method)
			else:
				self.dataSortMethod = None
				self.dataSortMethodsort = True
				self.SortButtonGreenGrey(method)
		else:
			self.dataSortMethodsort = True
			self.SortButtonGreenGrey(self.dataSortMethod)
			self.dataSortMethod = method
			self.SortButtonGreen(method)
		self.DataLoad()
	def SelectMethod(self,method):
		if self.dataSelectMethod == method:
			self.dataSelectMethod = None
			self.SelectButtonGreenGrey(method)
		else:
			self.SelectButtonGreenGrey(self.dataSelectMethod)
			self.dataSelectMethod = method
			self.SelectButtonGreen(method)
		self.DataLoad()
	def SortButtonGreenRed(self,method):
		if method == "PC":self.sortPlayCountButton.configure(bg='#FF7B7B')
		elif method == "Sync":self.sortSyncButton.configure(bg='#FF7B7B')
		elif method == "DiffNum":self.sortDiffNumButton.configure(bg='#FF7B7B')
		elif method == "SongName":self.sortSongNameButton.configure(bg='#FF7B7B')
	def SortButtonGreen(self,method):
		if method == "PC":self.sortPlayCountButton.configure(bg='#98E22B')
		elif method == "Sync":self.sortSyncButton.configure(bg='#98E22B')
		elif method == "DiffNum":self.sortDiffNumButton.configure(bg='#98E22B')
		elif method == "SongName":self.sortSongNameButton.configure(bg='#98E22B')
	def SortButtonGreenGrey(self,method):
		if method == "PC":self.sortPlayCountButton.configure(bg='#F0F0F0')
		elif method == "Sync":self.sortSyncButton.configure(bg='#F0F0F0')
		elif method == "DiffNum":self.sortDiffNumButton.configure(bg='#F0F0F0')
		elif method == "SongName":self.sortSongNameButton.configure(bg='#F0F0F0')
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
	def SelectButtonGreenGrey(self,method):
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

	def CheckUpdate(self):
		self.initLabel.configure(text="正在拉取更新信息……", anchor="w")
		oldVersion = int(f'{self.version[0]}{self.version[2]}{self.version[4]}')
		try:
			response = requests.get("https://api.github.com/repos/ginsakura/MUSYNCSave/releases/latest")
			version = response.json()["tag_name"]
			newVersion = int(f'{version[0]}{version[2]}{version[4]}')
		except Exception as e:
			messagebox.showerror("Error", f'发生错误: {e}')
			newVersion = oldVersion
		if (newVersion > oldVersion):
			self.gitHubLink.configure(text=f'有新版本啦——    NewVersion: {version}', anchor="center")
			self.UpdateTip()
		else:
			self.gitHubLink.configure(text='https://github.com/Ginsakura/MUSYNCSave    点个Star吧，秋梨膏', anchor="center")

	def DoubleClick(self,event):
		e = event.widget									# 取得事件控件
		itemID = e.identify("item",event.x,event.y)			# 取得双击项目id
		# state = e.item(itemID,"text")						# 取得text参数
		songData = e.item(itemID,"values")					# 取得values参数
		print(e.item(itemID))
		nroot = Toplevel(self.root)
		nroot.resizable(True, True)
		newWindow = SubWindow(nroot, songData[0], songData[1], songData[2])

	def UpdateTip(self):
		if self.gitHubLink.cget('fg') == '#C4245C':
			self.gitHubLink.configure(fg='#4BB1DA')
		else:
			self.gitHubLink.configure(fg='#C4245C')
		root.after(500,self.UpdateTip)

	def GetSaveFile(self):
		self.initLabel.configure(text="正在搜索存档文件中……", anchor="w")
		saveFilePath = None
		for ids in "CDEFGHIJKLMNOPQRSTUVWXYZAB":
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
			with open('./SaveFilePath.sfp','w+') as sfp:
				sfp.write(saveFilePath)
				self.saveFilePathVar.set(saveFilePath)
			self.DataLoad()
		else:
			self.initLabel.configure(text="搜索不到存档文件.", anchor="w")

	def DeleteAnalyzeFile(self):
		if os.path.isfile("./SavAnalyze.json"):
			os.remove("./SavAnalyze.json")
		if os.path.isfile("./SavAnalyze.analyze"):
			os.remove("./SavAnalyze.analyze")
		if os.path.isfile("./SavDecode.decode"):
			os.remove("./SavDecode.decode")
		self.DataLoad()

	def DataSort(self,_dict):
		if self.dataSortMethod == None:
			return _dict
		elif self.dataSortMethod == "PC":
			return sorted(_dict, reverse=self.dataSortMethodsort, key=(lambda _dict:_dict["PlayCount"]))
		elif self.dataSortMethod == "Sync":
			return sorted(_dict, reverse=self.dataSortMethodsort, key=(lambda _dict:float(_dict["SyncNumber"][0:-1])))
		elif self.dataSortMethod == "DiffNum":
			return sorted(_dict, reverse=self.dataSortMethodsort, key=(lambda _dict:(_dict["SongName"][3]) if (not _dict["SongName"] == None) else "00"))
		elif self.dataSortMethod == "SongName":
			return sorted(_dict, reverse=(not self.dataSortMethodsort), key=(lambda _dict:(_dict["SongName"][0]) if (not _dict["SongName"] == None) else ""))
		else:
			return _dict

	def DataLoad(self):
		self.initLabel.configure(text="正在分析存档文件中……", anchor="w")
		def Rank(sync):
			sync = float(sync[0:-1])
			if sync < 75:return "C"
			elif sync < 95:return "B"
			elif sync < 110:return "A"
			elif sync < 117:return "S"
			elif sync < 120:return "蓝Ex"
			elif sync < 122:return "红Ex"
			else:return "黑Ex"
		ids = self.saveData.get_children()
		if not len(ids) == 0:
			for idx in ids:
				self.saveData.delete(idx)
			self.saveCount = 0
			self.totalSync = 0
		else:saveFilePath = self.saveFilePathEntry.get()
		if os.path.isfile('./SavAnalyze.json'):pass
		#elif os.path.isfile('./SavAnalyze.analyze'):MusyncSavDecode.MUSYNCSavProcess(analyzeFile='./SavAnalyze.analyze').Main('analyze')
		elif os.path.isfile('./SavDecode.decode'):MusyncSavDecode.MUSYNCSavProcess(decodeFile='./SavDecode.decode').Main('decode')
		else:
			if self.saveFilePathEntry.get() == 'Input SaveFile or AnalyzeFile Path (savedata.sav)or(SavAnalyze.json)':
				self.SelectPath()
			path = MusyncSavDecode.MUSYNCSavProcess(self.saveFilePathVar.get()).Main()
			with open('./SaveFilePath.sfp','w+') as sfp:
				sfp.write("" if path is None else path)

		saveData = open(f'./SavAnalyze.json','r+')
		saveDataJson = json.load(saveData)
		saveData.close()

		if (saveDataJson['SaveData'][0]["SongName"] is None):
			saveData = open(f'./SavAnalyze.json','w+')
			for ids in range(len(saveDataJson['SaveData'])):
				saveDataJson['SaveData'][ids]["SongName"] = MusyncSavDecode.GetSongName(saveDataJson['SaveData'][ids]["SongID"])
			json.dump(saveDataJson,saveData,indent="")
			saveData.close()
			
		with open(f'./SavAnalyze.json','r+') as saveData:
			saveDataJson = json.load(saveData)
			self.root.title(f'同步音律喵赛克 Steam端 本地存档分析    LastPlay: {saveDataJson["LastPlay"]}')
			saveDataJson = self.DataSort(saveDataJson['SaveData'])
			for saveLine in saveDataJson:
				if self.dataSelectMethod == "Played":
					if saveLine["PlayCount"] == 0:continue
				elif self.dataSelectMethod == "Unplay":
					if not saveLine["PlayCount"] == 0:continue
				elif self.dataSelectMethod == "IsFav":
					if saveLine["IsFav"] == '0x00':continue
				elif self.dataSelectMethod == "Sync122":
					if float(saveLine["SyncNumber"][0:-1]) < 122:continue
				elif self.dataSelectMethod == "Sync120":
					if float(saveLine["SyncNumber"][0:-1]) < 120:continue
				elif self.dataSelectMethod == "RankEX":
					if float(saveLine["SyncNumber"][0:-1]) < 117:continue
				elif self.dataSelectMethod == "RankS":
					if (float(saveLine["SyncNumber"][0:-1]) < 110) or (float(saveLine["SyncNumber"][0:-1]) >= 117):continue
				elif self.dataSelectMethod == "RankA":
					if (float(saveLine["SyncNumber"][0:-1]) < 95) or (float(saveLine["SyncNumber"][0:-1]) >= 110):continue
				elif self.dataSelectMethod == "RankB":
					if (float(saveLine["SyncNumber"][0:-1]) < 75) or (float(saveLine["SyncNumber"][0:-1]) >= 95):continue
				elif self.dataSelectMethod == "RankC":
					if (float(saveLine["SyncNumber"][0:-1]) >= 75) or (saveLine["PlayCount"] == 0):continue
				self.saveCount += 1
				self.totalSync += float(saveLine["UploadScore"][0:-1])
				self.saveData.insert('', END, values=(saveLine["SongID"], 
					("" if saveLine["SongName"] is None else saveLine["SongName"][0]), 
					("" if saveLine["SongName"] is None else saveLine["SongName"][1]), 
					("" if saveLine["SongName"] is None else saveLine["SongName"][2]), 
					("" if saveLine["SongName"] is None else ("" if saveLine["SongName"][3]=="00" else saveLine["SongName"][3])), 
					saveLine["SpeedStall"], saveLine["SyncNumber"], 
					("" if ((saveLine["PlayCount"] == 0) and (saveLine["UploadScore"] == "0.00000000000000%")) else Rank(saveLine["SyncNumber"])), 
					saveLine["UploadScore"], saveLine["PlayCount"], saveLine["IsFav"]))
		self.initLabel.place(x=0,width=0)

	def SelectPath(self):
		path_ = askopenfilename() #使用askdirectory()方法返回文件夹的路径
		if path_ == "":
			self.saveFilePathVar.get() #当打开文件路径选择框后点击"取消" 输入框会清空路径，所以使用get()方法再获取一次路径
		else:
			path_ = path_.replace("/", "\\")  # 实际在代码中执行的路径为“\“ 所以替换一下
			self.saveFilePathVar.set(path_)

	def UpdateWindowInfo(self):
		self.root.update()
		self.windowInfo = ['root.winfo_x()','root.winfo_y()',root.winfo_width(),root.winfo_height()]

		self.saveFilePathEntry.place(x=170,y=10,width=(self.windowInfo[2]-260),height=30)
		self.getSaveFilePath.place(x=(self.windowInfo[2]-90),y=10,width=90,height=30)
		self.saveData.place(x=10 ,y=130 ,width=(self.windowInfo[2]-10) ,height=(self.windowInfo[3]-160))
 
		self.saveData.column("SongID",anchor="e",width=60)
		self.saveData.heading("SongID",anchor="center",text="谱面号")
		self.saveData.column("SongName",anchor="w",width=(self.windowInfo[2]-740 if self.windowInfo[2]-740 > 100 else 100))
		self.saveData.heading("SongName",anchor="center",text="曲名")
		self.saveData.column("Keys",anchor="center",width=40)
		self.saveData.heading("Keys",anchor="center",text="键数")
		self.saveData.column("Difficulty",anchor="w",width=70)
		self.saveData.heading("Difficulty",anchor="center",text="难度")
		self.saveData.column("DifficultyNumber",anchor="center",width=40)
		self.saveData.heading("DifficultyNumber",anchor="center",text="等级")
		self.saveData.column("SpeedStall",anchor="e",width=90)
		self.saveData.heading("SpeedStall",anchor="center",text="SpeedStall")
		self.saveData.column("SyncNumber",anchor="e",width=70)
		self.saveData.heading("SyncNumber",anchor="center",text="同步率")
		self.saveData.column("Rank",anchor="center",width=50)
		self.saveData.heading("Rank",anchor="center",text="Rank")
		self.saveData.column("UploadScore",anchor="e",width=160)
		self.saveData.heading("UploadScore",anchor="center",text="云端同步率")
		self.saveData.column("PlayCount",anchor="e",width=80)
		self.saveData.heading("PlayCount",anchor="center",text="游玩计数")
		self.saveData.column("IsFav",anchor="center",width=50)
		self.saveData.heading("IsFav",anchor="center",text="IsFav")

		self.VScroll1.place(x=self.windowInfo[2]-30, y=1, width=20, relheight=1)
		self.saveCountVar.set(self.saveCount)
		self.saveCountLabel.configure(text=self.saveCountVar.get())
		self.avgSyncVar.set(f'{(self.totalSync / (1 if self.saveCount==0 else self.saveCount))}')
		self.avgSyncLabel.configure(text=self.avgSyncVar.get()[0:10]+"%")
		self.developer.place(x=10,y=self.windowInfo[3]-30,width=370,height=30)
		self.gitHubLink.place(x=380,y=self.windowInfo[3]-30,width=self.windowInfo[2]-380,height=30)

		self.saveData.bind("<Double-1>",self.DoubleClick)

		root.after(200,self.UpdateWindowInfo)

class SubWindow(object):
	def __init__(self, nroot, songID, songName, songDifficute):
		##Init##
		nroot.iconbitmap('./Musync.ico')
		super(SubWindow, self).__init__()
		self.font=('霞鹜文楷等宽',16)
		nroot.geometry(f'1000x630+500+300')
		style = ttk.Style()
		style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',12))
		style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',12))
		nroot.title(f"同步音律喵赛克 Steam端 {songID}:{songName}:{songDifficute}全球排行")
		nroot['background'] = '#efefef'
		self.root = nroot
		self.songID = songID
		self.globalSync = ttk.Treeview(self.root, show="headings")
		self.globalSync.configure(columns = ['SongName',"Difficulty","Rank","SyncNumber"])
		self.VScroll = Scrollbar(self.globalSync, orient='vertical', command=self.globalSync.yview)
		
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
	if not os.path.isfile('./MUSYNC.ico'):
		FileExport.WriteIcon()
	if not os.path.isfile('./LXGW.ttf'):
		FileExport.WriteTTF()
	try:
		pyglet.font.add_file('./LXGW.ttf')
		pyglet.font.load('霞鹜文楷等宽')
	except Exception as e:
		messagebox.showerror("Error", f'{e}\n无法加载字体文件')
	root = Tk()
	root.resizable(True, True) #允许改变窗口大小
	window = MusyncSavDecodeGUI(root=root)
	root.update()
	root.mainloop()

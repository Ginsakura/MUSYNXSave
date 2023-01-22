#Version 1.0.1#
import sys
import os
import json
import MusyncSavDecode
import WriteIcon
import webbrowser
import requests
from tkinter import *
from tkinter import Tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import win32api
import win32con
import win32gui_struct
import win32gui
from threading import Thread

class MusyncSavDecodeGUI(object):
	"""docstring for MusyncSavDecodeGUI"""
	def __init__(self, root, isTKroot=True):
		##Init##
		root.iconbitmap('./MUSYNC.ico')
		super(MusyncSavDecodeGUI, self).__init__()
		self.isTKroot = isTKroot
		self.font=('霞鹜文楷等宽',16)
		root.geometry(f'1000x630+500+300')
		style = ttk.Style()
		style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',12))
		style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',12))
		if isTKroot == True:
			root.title("同步音律喵赛克SteamPC存档分析")
			root['background'] = '#efefef'
		self.saveFilePathVar = StringVar()
		self.saveFilePathVar.set('Input SaveFile or AnalyzeFile Path (savedata.sav)or(SavAnalyze.json)')
		self.analyzeFilePathVar = StringVar()
		self.analyzeFilePathVar.set('Input Analyze File Dir (or not)')
		self.root = root
		self.root.minsize(500, 430)
		self.windowInfo = [root.winfo_x(),root.winfo_y(),root.winfo_width(),root.winfo_height()]
		self.saveCount = 0
		self.saveCountVar = StringVar()
		self.saveCountVar.set(str(self.saveCount))
		self.version = '1.0.1'

		##Controls##
		#self..place(x= ,y= ,width= ,height=)
		self.saveFileDecodeButton = Button(self.root, text="存档解码及分析", font=self.font)
		self.saveFileDecodeButton.configure(command=self.DataLoad)
		self.saveFileDecodeButton.place(x=10,y=10,width=150,height=30)

		self.PrintLabel0 = Label(self.root, text='显示计数: ', font=self.font, relief="groove")
		self.PrintLabel0.place(x=10,y=50,width=100,height=30)

		self.saveCountLabel = Label(self.root, text=self.saveCountVar.get(), font=self.font, relief="groove")
		self.saveCountLabel.place(x=110,y=50,width=60,height=30)

		self.saveFilePathEntry = Entry(self.root, textvariable=self.saveFilePathVar, font=self.font, relief="sunken")
		self.getSaveFilePath = Button(self.root, text='打开存档', command=self.SelectPath, font=self.font)

		self.saveData = ttk.Treeview(self.root, show="headings")
		self.saveData.configure(columns = ["SongID",'SongName',"Difficulty","SpeedStall","SyncNumber","Rank","UploadScore","PlayCount","IsFav"])
		self.VScroll1 = Scrollbar(self.saveData, orient='vertical', command=self.saveData.yview)
		self.saveData.configure(yscrollcommand=self.VScroll1.set)
		self.developer = Label(self.root, text=f'Version {self.version} | Develop By Ginsakura', font=self.font, relief="groove")
		self.gitHubLink = Button(self.root, text='https://github.com/Ginsakura/MUSYNCSave    点个Star吧，秋梨膏', command=lambda:webbrowser.open("https://github.com/Ginsakura/MUSYNCSave"), fg='#4BB1DA', anchor="center", font=self.font, relief="groove")

		#筛选控件
		self.selectPlayedButton = Button(self.root, text='已游玩', command=lambda:self.DataLoad('Played'), anchor="w", font=self.font)
		self.selectPlayedButton.place(x=180,y=50,width=70,height=30)
		self.selectUnplayButton = Button(self.root, text='未游玩', command=lambda:self.DataLoad('Unplay'), anchor="w", font=self.font)
		self.selectUnplayButton.place(x=250,y=50,width=70,height=30)
		self.selectIsFavButton = Button(self.root, text='收藏', command=lambda:self.DataLoad('IsFav'), anchor="w", font=self.font)
		self.selectIsFavButton.place(x=320,y=50,width=50,height=30)
		self.select122Button = Button(self.root, text='Score>122%', command=lambda:self.DataLoad('Sync122'), anchor="w", font=self.font)
		self.select122Button.place(x=370,y=50,width=110,height=30)
		self.select120Button = Button(self.root, text='Score>120%', command=lambda:self.DataLoad('Sync120'), anchor="w", font=self.font)
		self.select120Button.place(x=480,y=50,width=110,height=30)
		self.selectExRankButton = Button(self.root, text='RankEX', command=lambda:self.DataLoad('RankEX'), anchor="w", font=self.font)
		self.selectExRankButton.place(x=590,y=50,width=70,height=30)
		self.selectSRankButton = Button(self.root, text='RankS', command=lambda:self.DataLoad('RankS'), anchor="w", font=self.font)
		self.selectSRankButton.place(x=660,y=50,width=60,height=30)
		self.selectARankButton = Button(self.root, text='RankA', command=lambda:self.DataLoad('RankA'), anchor="w", font=self.font)
		self.selectARankButton.place(x=720,y=50,width=60,height=30)
		self.selectBRankButton = Button(self.root, text='RankB', command=lambda:self.DataLoad('RankB'), anchor="w", font=self.font)
		self.selectBRankButton.place(x=780,y=50,width=60,height=30)
		self.selectCRankButton = Button(self.root, text='RankC', command=lambda:self.DataLoad('RankC'), anchor="w", font=self.font)
		self.selectCRankButton.place(x=840,y=50,width=60,height=30)
		self.deleteAnalyzeFile = Button(self.root, text="重新分析",command=self.DeleteAnalyzeFile, font=self.font, bg="#EE0000")
		self.deleteAnalyzeFile.place(x=900,y=50,width=100,height=30)

		##AutoRun##
		self.UpdateWindowInfo()
		self.CheckUpdate()
		if not os.path.isfile('./SaveFilePath.sfp'):
			self.GetSaveFile()
		else:
			with open('./SaveFilePath.sfp','r+') as sfp:
				sfpr = sfp.read()
				if not os.path.isfile(sfpr):
					os.remove('./SaveFilePath.sfp')
					self.GetSaveFile()
				else:self.saveFilePathVar.set(sfpr)
		if os.path.isfile('./SavAnalyze.json'):
			self.DataLoad()

	def CheckUpdate(self):
		oldVersion = int(f'{self.version[0]}{self.version[2]}{self.version[4]}')
		try:
			response = requests.get("https://api.github.com/repos/ginsakura/MUSYNCSave/releases/latest")
			newVersion = response.json()["tag_name"]
			version = int(f'{newVersion[0]}.{newVersion[2]}.{newVersion[4]}')
		except:
			version = oldVersion
		if (version > oldVersion):
			self.gitHubLink.configure(text=f'有新版本啦——    NewVersion: {newVersion}', anchor="center")
		else:
			self.gitHubLink.configure(text='https://github.com/Ginsakura/MUSYNCSave    点个Star吧，秋梨膏', anchor="center")

	def UpdateTip(self,newVersion):
		self.gitHubLink.configure(fg='#4BB1DA')
		time.sleep(0.5)
		self.gitHubLink.configure(fg='#C4245C')
		root.after(1000,self.UpdateTip)

	def GetSaveFile(self):
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

	def DeleteAnalyzeFile(self):
		if os.path.isfile("./SavAnalyze.json"):
			os.remove("./SavAnalyze.json")
		if os.path.isfile("./SavAnalyze.analyze"):
			os.remove("./SavAnalyze.analyze")
		if os.path.isfile("./SavAnalyze.decode"):
			os.remove("./SavAnalyze.decode")
		self.DataLoad()

	def DataLoad(self,command=None):
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
		else:saveFilePath = self.saveFilePathEntry.get()
		if os.path.isfile('./SavAnalyze.json'):pass
		#elif os.path.isfile('./SavAnalyze.analyze'):MusyncSavDecode.MUSYNCSavProcess(analyzeFile='./SavAnalyze.analyze').Main('analyze')
		elif os.path.isfile('./SavAnalyze.decode'):MusyncSavDecode.MUSYNCSavProcess(decodeFile='./SavAnalyze.decode').Main('decode')
		else:
			if self.saveFilePathEntry.get() == 'Input SaveFile or AnalyzeFile Path (savedata.sav)or(SavAnalyze.json)':
				self.SelectPath()
			path = MusyncSavDecode.MUSYNCSavProcess(self.saveFilePathVar.get()).Main()
			with open('./SaveFilePath.sfp','w+') as sfp:
				sfp.write(path)
		with open(f'./SavAnalyze.json','r+') as saveData:
			saveDataJson = json.load(saveData)
			self.root.title(f'同步音律喵赛克SteamPC存档分析    LastPlay: {saveDataJson["LastPlay"]}')
			for saveLine in saveDataJson['SaveData']:
				if command == "Played":
					if saveLine["PlayCount"] == 0:continue
				elif command == "Unplay":
					if not saveLine["PlayCount"] == 0:continue
				elif command == "IsFav":
					if saveLine["IsFav"] == '0x00':continue
				elif command == "Sync122":
					if float(saveLine["SyncNumber"][0:-1]) < 122:continue
				elif command == "Sync120":
					if float(saveLine["SyncNumber"][0:-1]) < 120:continue
				elif command == "RankEX":
					if float(saveLine["SyncNumber"][0:-1]) < 117:continue
				elif command == "RankS":
					if (float(saveLine["SyncNumber"][0:-1]) < 110) or (float(saveLine["SyncNumber"][0:-1]) >= 117):continue
				elif command == "RankA":
					if (float(saveLine["SyncNumber"][0:-1]) < 95) or (float(saveLine["SyncNumber"][0:-1]) >= 110):continue
				elif command == "RankB":
					if (float(saveLine["SyncNumber"][0:-1]) < 75) or (float(saveLine["SyncNumber"][0:-1]) >= 95):continue
				elif command == "RankC":
					if (float(saveLine["SyncNumber"][0:-1]) >= 75) or (saveLine["PlayCount"] == 0):continue
				self.saveCount += 1
				self.saveData.insert('', END, values=(saveLine["SongID"], saveLine["SongName"][0], saveLine["SongName"][1], saveLine["SpeedStall"], saveLine["SyncNumber"], ("" if ((saveLine["PlayCount"] == 0) and (saveLine["UploadScore"] == "0.00000000000000%")) else Rank(saveLine["SyncNumber"])), saveLine["UploadScore"], saveLine["PlayCount"], saveLine["IsFav"]))

	def SelectPath(self):
		path_ = askopenfilename() #使用askdirectory()方法返回文件夹的路径
		if path_ == "":
			self.saveFilePathVar.get() #当打开文件路径选择框后点击"取消" 输入框会清空路径，所以使用get()方法再获取一次路径
		else:
			path_ = path_.replace("/", "\\")  # 实际在代码中执行的路径为“\“ 所以替换一下
			self.saveFilePathVar.set(path_)

	def UpdateWindowInfo(self):
		self.root.update()
		self.windowInfo = [root.winfo_x(),root.winfo_y(),root.winfo_width(),root.winfo_height()]

		self.saveFilePathEntry.place(x=170,y=10,width=(self.windowInfo[2]-260),height=30)
		self.getSaveFilePath.place(x=(self.windowInfo[2]-90),y=10,width=90,height=30)
		self.saveData.place(x=10 ,y=90 ,width=(self.windowInfo[2]-10) ,height=(self.windowInfo[3]-120))
 
		self.saveData.column("SongID",anchor="e",width=70)
		self.saveData.heading("SongID",anchor="center",text="谱面编号")
		self.saveData.column("SongName",anchor="e",width=(self.windowInfo[2]-680 if self.windowInfo[2]-680 > 100 else 100))
		self.saveData.heading("SongName",anchor="center",text="曲名")
		self.saveData.column("Difficulty",anchor="e",width=80)
		self.saveData.heading("Difficulty",anchor="center",text="难度")
		self.saveData.column("SpeedStall",anchor="e",width=90)
		self.saveData.heading("SpeedStall",anchor="center",text="SpeedStall")
		self.saveData.column("SyncNumber",anchor="e",width=70)
		self.saveData.heading("SyncNumber",anchor="center",text="同步率")
		self.saveData.column("Rank",anchor="center",width=50)
		self.saveData.heading("Rank",anchor="center",text="Rank")
		self.saveData.column("UploadScore",anchor="e",width=160)
		self.saveData.heading("UploadScore",anchor="center",text="上传分数")
		self.saveData.column("PlayCount",anchor="e",width=80)
		self.saveData.heading("PlayCount",anchor="center",text="游玩计数")
		self.saveData.column("IsFav",anchor="center",width=50)
		self.saveData.heading("IsFav",anchor="center",text="IsFav")

		self.VScroll1.place(x=self.windowInfo[2]-30, y=1, width=20, relheight=1)
		self.saveCountVar.set(self.saveCount)
		self.saveCountLabel.configure(text=self.saveCountVar.get())
		self.deleteAnalyzeFile.place(x=self.windowInfo[2]-100,y=50,width=100,height=30)
		self.developer.place(x=10,y=self.windowInfo[3]-30,width=370,height=30)
		self.gitHubLink.place(x=380,y=self.windowInfo[3]-30,width=self.windowInfo[2]-380,height=30)

		root.after(100,self.UpdateWindowInfo)

if __name__ == '__main__':
	if not os.path.isfile('./MUSYNC.ico'):
		WriteIcon()
	root = Tk()
	root.resizable(True, True) #允许改变窗口大小
	window = MusyncSavDecodeGUI(root=root)
	root.update()
	root.mainloop()
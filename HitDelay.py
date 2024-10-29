import json
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import os
import pyperclip
import sqlite3 as sql
import uiautomation as uiauto

from tkinter import *
from tkinter import Tk,ttk,font,Text,messagebox
from matplotlib.pyplot import MultipleLocator
from datetime import datetime as dt
from hashlib import md5

import FileExport
from AllHitAnalyze import AllHitAnalyze
# from AllHitAnalyze_New import AllHitAnalyze

uiauto.SetGlobalSearchTimeout(1)

class HitDelayCheck(object):
	"""docstring for HitDelayWindow"""
	def __init__(self):
		self.md5l = FileExport.ChangedDLL # Changed Assembly-CSharp.dll
		self.md5o = FileExport.SourceDLL # Source  Assembly-CSharp.dll

		with open('./musync_data/ExtraFunction.cfg','r',encoding='utf8') as confFile:
			config = json.load(confFile)
		self.spfr = config['MainExecPath']+'MUSYNX_Data/Managed/Assembly-CSharp.dll'
		del config
		self.DLLCheck()

	def DLLCheck(self):
		# 'D41D8CD98F00B204E9800998ECF8427E' is a Null file
		with open(self.spfr,'rb') as spfrb:
			md5o = md5(spfrb.read()).hexdigest().upper()
		if (md5o != "D41D8CD98F00B204E9800998ECF8427E") and (md5o == self.md5o) and (not md5o == self.md5l):
			self.DLLInjection()
			return 1
		elif (md5o == self.md5l):
			return 1
		elif (md5o == "D41D8CD98F00B204E9800998ECF8427E"):
			self.DLLInjection()
			return 1
		else:
			return 0

	def DLLInjection(self):
		if os.path.isfile(self.spfr+'.old'):
			os.remove(self.spfr+'.old')
		os.rename(self.spfr,self.spfr+'.old')
		FileExport.WriteHitDelayFix(self.spfr)

class HitDelayText(object):
	"""docstring for DrawHDLine"""
	def __init__(self,subroot):
		if os.path.isfile('./musync_data/HitDelayHistory_v2.db'):
			self.db = sql.connect('./musync_data/HitDelayHistory_v2.db')
			self.cur = self.db.cursor()
		else:
			self.db = sql.connect('./musync_data/HitDelayHistory_v2.db')
			self.cur = self.db.cursor()
			self.cur.execute("""CREATE table HitDelayHistory (
				SongMapName text Not Null,
				RecordTime text Not Null,
				AvgDelay float,
				AllKeys int,
				AvgAcc float,
				HitMap text,
				PRIMARY KEY ("SongMapName", "RecordTime"))""")
		self.subroot = subroot
		self.font=('霞鹜文楷等宽',16)
		self.subroot.iconbitmap('./musync_data/Musync.ico')
		self.subroot.geometry(f'1000x600+600+400')
		self.subroot.title("高精度延迟分析")
		self.subroot['background'] = '#efefef'
		self.tipLabel = Label(self.subroot,font=self.font, relief="groove",text='↓将您用来辨识谱面的方式填入右侧文本框，然后点击右侧红色按钮进行结果分析↓',fg='#F9245E')
		self.tipLabel.place(x=0,y=0,height=40,relwidth=1)
		self.style = ttk.Style()
		self.cursorHistory = ''

		with open('./musync_data/ExtraFunction.cfg', 'r',encoding='utf8') as confFile:
			config = json.load(confFile)

		self.hitAnalyzeButton = Button(self.subroot,text='All\nHit',command=lambda :AllHitAnalyze().Show(),font=self.font, relief="groove")
		self.hitAnalyzeButton.place(x=0,y=40,height=90,relwidth=0.05)
		self.nameDelayLabel = Label(self.subroot,font=self.font, relief="groove",text='↓请在下面输入曲名与谱面难度↓这只是用来标记你玩的哪个谱面而已，\n没有任何要求                    ↓右侧水绿色按钮选择难度和键数↓')
		self.nameDelayLabel.place(relx=0.05,y=40,height=60,relwidth=0.65)
		self.nameDelayEntry = Entry(self.subroot,font=self.font, relief="sunken",validate='focus',validatecommand=self.TestEntryString)
		self.nameDelayEntry.insert(0, "→→在这里输入谱面标识←←")
		self.nameDelayEntry.place(relx=0.05,y=100,height=30,relwidth=0.449)
		self.delayHistory = ttk.Treeview(self.subroot, show="headings", columns = ['Name','RecordTime','AllKeys','AvgDelay','AvgAcc'])
		self.VScroll1 = Scrollbar(self.subroot, orient='vertical', command=self.delayHistory.yview)
		self.delayHistory.configure(yscrollcommand=self.VScroll1.set)
		
		self.logButton = Button(self.subroot,text='点击生成图表',command=self.Draw,font=self.font,bg='#FFCCCC')
		if config['EnableAcc-Sync']:
			self.logButton.place(relx=0.7,y=70,height=60,relwidth=0.3)
			self.txtButton = Button(self.subroot,text='生成Acc-Sync图表',command=self.OpenTxt,font=self.font)
			self.txtButton.place(relx=0.7,y=40,height=30,relwidth=0.3)
		else:
			self.logButton.place(relx=0.7,y=40,height=90,relwidth=0.3)
		self.keys = config['DefaultKeys'] # F=4, T=6
		self.keysButton = Button(self.subroot,font=self.font, text=("6Key" if self.keys else "4Key"), command=self.ChangeKeys, bg="#4AA4C9")
		self.keysButton.place(relx=0.5,y=100,height=30,relwidth=0.1)
		self.diffcute = config['DefaultDiffcute']
		self.diffcuteButton = Button(self.subroot,font=self.font, text=["Easy","Hard","Inferno"][self.diffcute], command=self.ChangeDiffcute, bg="#4AA4C9")
		self.diffcuteButton.place(relx=0.6,y=100,height=30,relwidth=0.1)

		self.historyFrame = Frame(self.subroot,relief="groove",bd=2)
		self.historyFrame.place(relx=0.701,y=198,height=244,relwidth=0.298)
		self.historyNameLabel = Label(self.historyFrame, text='谱面游玩标识',font=self.font, relief="groove")
		self.historyNameLabel.place(x=0,y=0,height=30,relwidth=1)
		self.historyNameEntry = Entry(self.historyFrame,font=self.font, relief="sunken")
		self.historyNameEntry.place(x=0,y=30,height=30,relwidth=1)
		self.historyRecordTimeLabel = Label(self.historyFrame, text='记录时间',font=self.font, relief="groove")
		self.historyRecordTimeLabel.place(x=0,y=60,height=30,relwidth=1)
		self.historyRecordTimeValueLabel = Label(self.historyFrame, text=dt.now(),font=self.font, relief="groove")
		self.historyRecordTimeValueLabel.place(x=0,y=90,height=30,relwidth=1)
		self.historyKeysLabel = Label(self.historyFrame, text=f'按键数量: ',font=self.font, relief="groove", anchor="e")
		self.historyKeysLabel.place(x=0,y=120,height=30,relwidth=0.4)
		self.historyKeysValueLabel = Label(self.historyFrame, text="0    ",font=self.font, relief="groove", anchor="e")
		self.historyKeysValueLabel.place(relx=0.4,y=120,height=30,relwidth=0.6)
		self.historyDelayLabel = Label(self.historyFrame, text='Delay: ',font=self.font, relief="groove", anchor="e")
		self.historyDelayLabel.place(x=0,y=150,height=30,relwidth=0.4)
		self.historyDelayValueLabel = Label(self.historyFrame, text="000.000000ms  ",font=self.font, relief="groove", anchor="e")
		self.historyDelayValueLabel.place(relx=0.4,y=150,height=30,relwidth=0.6)
		self.historyAccLabel = Label(self.historyFrame, text='AvgAcc: ',font=self.font, relief="groove", anchor="e")
		self.historyAccLabel.place(x=0,y=180,height=30,relwidth=0.4)
		self.historyAccValueLabel = Label(self.historyFrame, text='000.000000ms  ',font=self.font, relief="groove", anchor="e")
		self.historyAccValueLabel.place(relx=0.4,y=180,height=30,relwidth=0.6)
		self.style.configure("update.TButton",font=self.font, relief="raised", background='#A6E22B')
		self.historyUpdateButton = ttk.Button(self.historyFrame, text='更新记录', style="update.TButton",command=self.UpdateCursorHistory)
		self.historyUpdateButton.place(x=0,y=210,height=30,relwidth=0.5)
		self.style.configure("delete.TButton",font=self.font, relief="raised", foreground='#FF4040', background='#FF2020')
		self.historyDeleteButton = ttk.Button(self.historyFrame, text='删除记录', style="delete.TButton",command=self.DeleteCursorHistory)
		self.historyDeleteButton.place(relx=0.5,y=210,height=30,relwidth=0.5)

		self.delayInterval = 90
		if config['EnableNarrowDelayInterval']:
			self.delayInterval = 45
		del config

		self.history = list()
		self.HistoryUpdate()
		self.UpdateWindowInfo()

	def ChangeKeys(self):
		self.keys = not self.keys
		self.keysButton.configure(text=("6Key" if self.keys else "4Key"))
	def ChangeDiffcute(self):
		self.diffcute = (self.diffcute+1)%3
		self.diffcuteButton.configure(text=["Easy","Hard","Inferno"][self.diffcute])
	def ChangeConfig(self):
		with open('./musync_data/ExtraFunction.cfg', 'r',encoding='utf8') as confFile:
			config = json.load(confFile)
		isChange = False
		if config["DefaultKeys"] != self.keys:
			config["DefaultKeys"] = self.keys
			isChange = True
		if config["DefaultDiffcute"] != self.diffcute:
			config["DefaultDiffcute"] = self.diffcute
			isChange = True
		if isChange:
			json.dump(config,open('./musync_data/ExtraFunction.cfg','w',encoding='utf8'),indent="",ensure_ascii=False)

	def TestEntryString(self):
		string = self.nameDelayEntry.get()
		# print(type(string),string,reason)
		if string == '':
			self.nameDelayEntry.insert(0, "→→在这里输入谱面标识←←")
		elif string == '→→在这里输入谱面标识←←':
			self.nameDelayEntry.delete(0,'end')
		return True

	def HistoryUpdate(self):
		for ids in self.delayHistory.get_children():
			self.delayHistory.delete(ids)
		data = self.cur.execute("SELECT SongMapName,RecordTime,AvgDelay,AllKeys,AvgAcc from HitDelayHistory")
		data = data.fetchall()
		self.history = list()
		for ids in data:
			self.history.append(ids[0])
			self.delayHistory.insert('', END, values=(ids[0],ids[1],ids[3],'%.6f ms'%ids[2],'%.6f ms'%ids[4]))
		del data
		self.UpdateWindowInfo()

	def Draw(self):
		self.ChangeConfig()
		consoleFind = False
		try:
			win = uiauto.WindowControl(searchDepth=1,Name='MUSYNX Delay',searchInterval=1).DocumentControl(serchDepth=1,Name='Text Area',searchInterval=1)
			win.SendKeys('{Ctrl}A',waitTime=0.1)
			win.SendKeys('{Ctrl}C',waitTime=0.1)
			consoleFind = True
		except Exception as e:
			try:
				win = uiauto.WindowControl(searchDepth=1,Name='选择 MUSYNX Delay',searchInterval=1).DocumentControl(serchDepth=1,Name='Text Area',searchInterval=1)
				win.SendKeys('{Ctrl}A',waitTime=0.1)
				win.SendKeys('{Ctrl}C',waitTime=0.1)
				consoleFind = True
			except Exception as e:
				messagebox.showerror("Error", f'控制台窗口未找到\n请确认控制台窗口已开启\n{e}')
		if consoleFind:
			data = pyperclip.paste().split('\n')
			dataList=list()
			n = self.nameDelayEntry.get().replace("\'","’")
			k = "6K" if self.keys else "4K"
			d = ["EZ","HD","IN"][self.diffcute]
			name = f"{n} {k}{d}"
			time = f"{dt.now()}"
			if data[-1] == "": #如果最后一行是空行，则去除
				data.pop(-1)
			for ids in range(1,len(data)): # 去除第一行
				dataList.append(float(data[ids][13:-3]))
			allKeys = len(dataList)
			sumNums,sumKeys = 0,0
			for ids in dataList:
				if (ids < self.delayInterval) and (ids > -self.delayInterval):
					sumNums += ids
					sumKeys += 1
			avgDelay = sumNums/sumKeys
			avgAcc = sum([abs(i) for i in dataList])/allKeys
			self.delayHistory.insert('', END, values=(name,allKeys,'%.6f ms'%avgDelay,'%.6f ms'%avgAcc))
			dataListStr = ""
			for i in dataList:
				dataListStr += f'{i}|'
			self.cur.execute("INSERT into HitDelayHistory values(?,?,?,?,?,?)",(name,time,avgDelay,allKeys,avgAcc,dataListStr[:-1]))
			self.db.commit()
			self.HistoryUpdate()
			dataList = [name,time,avgDelay,allKeys,avgAcc,dataList]
			HitDelayDraw(dataList,isHistory=False)

	def OpenTxt(self):
		os.system('start notepad ./musync_data/Acc-Sync.json')
		# print(os.getcwd())
		# os.system(f'start explorer {os.getcwd()}')
		import AvgAcc_SynxAnalyze
		AvgAcc_SynxAnalyze.Analyze()

	def ShowHistoryInfo(self,event):
		e = event.widget									# 取得事件控件
		itemID = e.identify("item",event.x,event.y)			# 取得双击项目id
		# state = e.item(itemID,"text")						# 取得text参数
		historyItem = e.item(itemID,"values")				# 取得values参数
		if not self.history == []:
			isChange = False
			historyName = historyItem[0].replace("\'",'’')
			recordTime = historyItem[1]
			print("ShowHistoryInfo:",historyItem)
			data = self.cur.execute(f"select * from HitDelayHistory where SongMapName=\'{historyName}\'  and RecordTime=\'{recordTime}\'")
			data = data.fetchone()
			# print(data[:4])
			self.cursorHistory = data[0]
			self.historyNameEntry.delete(0, 'end')
			self.historyNameEntry.insert(0, data[0])
			self.historyRecordTimeValueLabel['text'] = data[1]
			self.historyKeysValueLabel['text'] = '% 5s    '%data[3]
			self.historyDelayValueLabel['text'] = '%.6fms  '%float(data[2])
			self.historyAccValueLabel['text'] = '%.6fms  '%float(data[4])
			del data

	def DeleteCursorHistory(self):
		print(f"delete history {self.cursorHistory}")
		if self.cursorHistory == '':
			messagebox.showerror('Error','请输入谱面标识')
		else:
			result = messagebox.askyesno('提示', f'是否删除该谱面游玩记录?\n{self.cursorHistory}')
			if result:
				self.cur.execute(f'delete from HitDelayHistory where SongMapName=\'{self.cursorHistory}\' and RecordTime=\'{self.historyRecordTimeValueLabel["text"]}\'')
				self.db.commit()
				self.HistoryUpdate()

	def UpdateCursorHistory(self):
		nowHistoryName = self.historyNameEntry.get().replace("\'","’")
		if self.cursorHistory != nowHistoryName:
			print(f"change history name \nfrom {self.cursorHistory} \nto {nowHistoryName} \nwhen time is {self.historyRecordTimeValueLabel['text']}")
			self.cur.execute(f'update HitDelayHistory set SongMapName=\'{nowHistoryName}\' where SongMapName=\'{self.cursorHistory}\' and RecordTime=\'{self.historyRecordTimeValueLabel["text"]}\'')
			self.db.commit()
			self.HistoryUpdate()

	def HistoryDraw(self,event):
		e = event.widget									# 取得事件控件
		itemID = e.identify("item",event.x,event.y)			# 取得双击项目id
		# state = e.item(itemID,"text")						# 取得text参数
		historyItem = e.item(itemID,"values")				# 取得values参数
		# print(e.item(itemID))
		if not self.history == []:
			data = self.cur.execute(f'select * from HitDelayHistory where SongMapName=\'{historyItem[0]}\' and RecordTime=\'{historyItem[1]}\'')
			data = data.fetchone()
			HitDelayDraw(data,isHistory=True)
			# print(self.history[historyItem[0]])

	def UpdateWindowInfo(self):
		self.delayHistory.heading("Name",anchor="center",text="曲名")
		self.delayHistory.heading("RecordTime",anchor="center",text="记录时间")
		self.delayHistory.heading("AllKeys",anchor="center",text="Keys")
		self.delayHistory.heading("AvgDelay",anchor="center",text="Delay")
		self.delayHistory.heading("AvgAcc",anchor="center",text="AvgAcc")
		self.delayHistory.column("Name",anchor="w",width=180)
		self.delayHistory.column("RecordTime",anchor="w",width=200)
		self.delayHistory.column("AllKeys",anchor="e",width=60)
		self.delayHistory.column("AvgDelay",anchor="e",width=120)
		self.delayHistory.column("AvgAcc",anchor="e",width=120)
		self.delayHistory.bind("<Double-1>",self.HistoryDraw)
		self.delayHistory.bind("<ButtonPress-1>",self.ShowHistoryInfo)
		self.historyRecordTimeValueLabel['text'] = dt.now()

		print("VScroll1.get",self.VScroll1.get())
		self.delayHistory.place(x=0,y=130,height=self.subroot.winfo_height()-130,relwidth=0.684)
		self.VScroll1.place(relx=0.684,y=132,height=self.subroot.winfo_height()-133,relwidth=0.015)
		self.subroot.update()
		self.delayHistory.yview_moveto(1.0)
		# self.subroot.after(500,self.UpdateWindowInfo)

class HitDelayDraw(object):
	"""docstring for ClassName"""
	def __init__(self, dataList,isHistory=False):
		print('Name:%s\nRecordTime:%s'%(dataList[0],dataList[1]))
		self.avgDelay = dataList[2]
		self.allKeys = dataList[3]
		self.avgAcc = dataList[4]
		if isHistory:
			self.dataList = [float(i) for i in dataList[5].split("|")]
		else:
			self.dataList = dataList[5]

		self.dataListLenth = len(self.dataList)
		self.x_axis = [i for i in range(self.dataListLenth)]
		self.y_axis = [int(i) for i in self.dataList]

		self.sum = [0,0,0,0,0]
		self.exCount = [0,0,0,0]
		for ids in self.dataList:
			ids = abs(ids)
			if ids < 45: 
				if ids < 5:self.exCount[0] += 1
				elif ids < 10:self.exCount[1] += 1
				elif ids < 20:self.exCount[2] += 1
				else:self.exCount[3] += 1
			elif ids < 90: self.sum[1] += 1
			elif ids < 150: self.sum[2] += 1
			elif ids < 250: self.sum[3] += 1
			else: self.sum[4] += 1
		self.sum[0] = sum(self.exCount)
		self.exCount = self.exCount + self.sum[1:]
		print("HitDelayDraw:",self.sum,self.exCount)

		self.DrawLine()
		with open('./musync_data/ExtraFunction.cfg', 'r',encoding='utf8') as confFile:
			config = json.load(confFile)
		if config['EnableDonutChartinHitDelay']:
			self.DrawBarPie()
		plt.show()

	def DrawLine(self):
		fig = plt.figure(f'AvgDelay: {"%.4fms"%self.avgDelay}    ' \
			f'AllKeys: {self.allKeys}    AvgAcc: {"%.4fms"%self.avgAcc}',figsize=(9, 4))
		fig.clear()
		fig.subplots_adjust(**{"left":0.045,"bottom":0.055,"right":1,"top":1})
		ax = fig.add_subplot()
		plt.rcParams['font.serif'] = ["LXGW WenKai Mono"]
		plt.rcParams["font.sans-serif"] = ["LXGW WenKai Mono"]
		print(f'AvgDelay: {self.avgDelay}\tAllKeys: {self.allKeys}\tAvgAcc: {self.avgAcc}')
		ax.text(0,5,"Slower→", ha='right',color='#c22472',rotation=90, fontdict={'size':15})
		ax.text(0,-5,"←Faster", ha='right',va='top',color='#288328',rotation=90, fontdict={'size':15})

		maxAbsYAxis = max(max(self.y_axis),abs(min(self.y_axis)))
		if maxAbsYAxis >= 150:
			ax.plot(self.x_axis,[250]*self.dataListLenth,linestyle='--',alpha=0.7,linewidth=1,color='red',
				label='Right(+250ms)         --%d'%self.sum[3])
		if maxAbsYAxis >= 90:
			ax.plot(self.x_axis,[150]*self.dataListLenth,linestyle='--',alpha=0.7,linewidth=1,color='green',
				label='Great(±150ms)        --%d'%self.sum[2])
			ax.plot(self.x_axis,[-150]*self.dataListLenth,linestyle='--',alpha=0.7,linewidth=1,color='green')
		if maxAbsYAxis >= 45:
			ax.plot(self.x_axis,[90]*self.dataListLenth,linestyle='--',alpha=0.7,linewidth=1,color='blue',
				label='Blue Exact(±90ms)    --%d'%self.sum[1])
			ax.plot(self.x_axis,[-90]*self.dataListLenth,linestyle='--',alpha=0.7,linewidth=1,color='blue')

		ax.plot(self.x_axis,[45]*self.dataListLenth,linestyle='--',alpha=0.7,linewidth=1,color='cyan',
			label='Cyan Exact(±45ms)    --%d'%self.sum[0])
		ax.plot(self.x_axis,[-45]*self.dataListLenth,linestyle='--',alpha=0.7,linewidth=1,color='cyan')
		ax.plot(self.x_axis,[0]*self.dataListLenth,linestyle='-',alpha=1,linewidth=1,color='red',label='0ms')
		ax.plot(self.x_axis,[self.avgDelay]*self.dataListLenth,linestyle='--',alpha=1,linewidth=1,color='red',label="AvgDelay")
		ax.plot(self.x_axis,self.y_axis,linestyle='-',alpha=0.7,linewidth=1,color='#8a68d0',
			label='HitDelay(ms)      miss--%d'%self.sum[4],marker='.',markeredgecolor='#c4245c',markersize='3')

		for x,y in zip(self.x_axis,self.y_axis):
			if y<0:
				ax.text(x,y-3,'%dms'%y,ha='center',va='top',fontsize=7.5,alpha=0.7, )
			else:
				ax.text(x,y+3,'%dms'%y,ha='center',va='bottom',fontsize=7.5,alpha=0.7, )

		ax.legend(prop={'size':12},framealpha=0.5)  #显示上面的label
		ax.set_xlabel('HitCount', fontsize=15) #x_label
		ax.set_ylabel('Delay', fontsize=15) #y_label
		ax.yaxis.set_major_locator(MultipleLocator(20))
		ax.set_xlim(-15,len(self.x_axis)+15)
		# plt.show()

	def DrawBarPie(self):
		def Percentage(num, summ):
			per = num/summ*100
			return ' '*(3-len(str(int((per)))))+'%.3f%%'%(per)
		def Count(num):
			cou = str(num)
			return ' '*(6-len(cou))+cou
		def PercentageLabel(num, summ):
			per = num/summ*100
			return '%.1f%%'%(per)
		# import random
		# fig = plt.figure(f'Pie&Bar AvgDelay: {"%.4fms"%self.avgDelay}  ' \
		# 	f'AllKeys: {self.allKeys}  AvgAcc: {"%.4fms"%self.avgAcc}', figsize=(5.5, 6.5))
		fig = plt.figure(f'Pie&Bar', figsize=(5.5, 6.5))
		fig.clear()
		grid = gridspec.GridSpec(4, 1, left=0, right=1, top=1, bottom=0.035, wspace=0, hspace=0)
		ax1 = fig.add_subplot(grid[0:3,0])
		wedgeprops = {'width':0.15, 'edgecolor':'black', 'linewidth':0.2}
		if self.sum[0]/sum(self.sum) > 0.6:
			exCountSum = sum(self.exCount)
			pieRtn = ax1.pie(self.exCount, wedgeprops=wedgeprops, startangle=90, autopct='%1.1f%%', pctdistance = 0.95, labeldistance = 1.05, 
				colors=['#9dfff0',    '#69f1f1',     '#25d8d8',     '#32a9c7',     '#2F97FF', 'green', 'orange', 'red', ], 
				labels=["EXACT±5ms", "EXACT±10ms", "EXACT±20ms", "EXACT±45ms", "Exact",   "Great", "Right",  "Miss", ],
				textprops={'size':10})
			ax1.legend(prop={'size':9},loc='center', handles=pieRtn[0], 
				labels=[
					f"EXACT± 5ms  {Count(self.exCount[0])}  {Percentage(self.exCount[0], exCountSum)}", 
					f"EXACT±10ms  {Count(self.exCount[1])}  {Percentage(self.exCount[1], exCountSum)}", 
					f"EXACT±20ms  {Count(self.exCount[2])}  {Percentage(self.exCount[2], exCountSum)}", 
					f"EXACT±45ms  {Count(self.exCount[3])}  {Percentage(self.exCount[3], exCountSum)}", 
					f"Exact±90ms  {Count(self.exCount[4])}  {Percentage(self.exCount[4], exCountSum)}", 
					f"Great±150ms {Count(self.exCount[5])}  {Percentage(self.exCount[5], exCountSum)}", 
					f"Right＋250ms {Count(self.exCount[6])}  {Percentage(self.exCount[6], exCountSum)}", 
					f"Miss >=251ms {Count(self.exCount[7])}  {Percentage(self.exCount[7], exCountSum)}", ],
				)
			ax1.text(-0.41,0.48,f"EXACT        {Count(sum(self.exCount[0:4]))}  " \
				f"{Percentage(sum(self.exCount[0:4]), exCountSum)}", 
				ha='left',va='top',fontsize=9,color='#00B5B5', )
		else:
			summ = sum(self.sum)
			ax1.pie(self.sum, wedgeprops=wedgeprops, startangle=90, autopct='%1.1f%%', pctdistance = 0.9, labeldistance = 1.05, 
				colors=['cyan', '#2F97FF', 'green', 'orange', 'red'],
				# autopct=lambda x:'%.3f%%'%(x*sum(self.exCount)/100+0.5),
				labels=["EXACT", "Exact", "Great", "Right", "Miss"],
				textprops={'size':9})
			ax1.legend(prop={'size':9},loc='center',
				labels=[
					f"EXACT±45ms  {Count(self.sum[0])}  {Percentage(self.sum[0], summ)}", 
					f"Exact±90ms  {Count(self.sum[1])}  {Percentage(self.sum[1], summ)}", 
					f"Great±150ms {Count(self.sum[2])}  {Percentage(self.sum[2], summ)}", 
					f"Right＋250ms {Count(self.sum[3])}  {Percentage(self.sum[3], summ)}", 
					f"Miss > 250ms {Count(self.sum[4])}  {Percentage(self.sum[4], summ)}"],
				)

		ax2 = fig.add_subplot(grid[3,0])
		hitMapA = [0]*150 # -149~-0
		hitMapB = [0]*251 # +0~+250
		for idx in self.dataList:
			if idx < 0:
				idx = int(idx)-1
			else:
				idx = int(idx)
			if (idx >= 0) and (idx < 250):
				hitMapB[idx] += 1
			elif (idx >= 250):
				hitMapB[250] += 1
			else:
				hitMapA[idx] += 1
		leftBorder,rightBorder = 0,0
		while (hitMapA[0] == 0):
			hitMapA.pop(0)
			leftBorder += 1
		while (hitMapB[-1] == 0):
			hitMapB.pop(-1)
			rightBorder += 1
		self.xAxis = [i for i in range(-len(hitMapA),251-rightBorder)]
		self.yAxis = hitMapA + hitMapB
		for i in range(len(self.xAxis)):
			ax2.bar(self.xAxis[i],self.yAxis[i])
		ax2.xaxis.set_major_locator(MultipleLocator(15))
		# plt.show()


if __name__ == '__main__':
	# HitDelayCheck()
	root = Tk()
	window = HitDelayText(subroot=root)
	root.update()
	root.mainloop()
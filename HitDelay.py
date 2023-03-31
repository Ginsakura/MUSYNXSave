from tkinter import *
from tkinter import Tk,ttk,font,Text
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
import json
from datetime import datetime as dt
from os.path import isfile
from hashlib import md5
from os import rename,remove
from FileExport import WriteHitDelayFix
import sqlite3 as sql
from AllHitAnalyze import HitAnalyze

class HitDelayCheck(object):
	"""docstring for HitDelayWindow"""
	def __init__(self):
		self.md5l = '6771D7829013707B491104DCC1D8902A' # HitDelayFix.dll
		self.md5o = 'EDA085BDD1136D6739BCB31C4247EAA3' # Assembly-CSharp.dll

		with open('./musync_data/SaveFilePath.sfp','r+',encoding='utf8') as sfp:
			self.spfr = sfp.read()[:-21]+'MUSYNX_Data/Managed/Assembly-CSharp.dll'
		self.DLLCheck()

	def DLLCheck(self):
		with open(self.spfr,'rb') as dllO:
			md5o = md5(dllO.read()).hexdigest().upper()
		if (md5o == self.md5o) and (not md5o == self.md5l):
			self.DLLInjection()
			return True
		elif (md5o == self.md5l):
			return True
		else:
			return False

	def DLLInjection(self):
		if isfile(self.spfr+'.old'):
			remove(self.spfr+'.old')
		rename(self.spfr,self.spfr+'.old')
		WriteHitDelayFix(self.spfr)

class HitDelayText(object):
	"""docstring for DrawHDLine"""
	def __init__(self,subroot):
		if isfile('./musync_data/HitDelayHistory.db'):
			self.db = sql.connect('./musync_data/HitDelayHistory.db')
			self.cur = self.db.cursor()

		else:
			self.db = sql.connect('./musync_data/HitDelayHistory.db')
			self.cur = self.db.cursor()
			self.cur.execute('''create table HitDelayHistory (
				SongMapName text Primary Key,
				AvgDelay float,
				AllKeys int,
				AvgAcc float,
				HitMap text);''')
		self.subroot = subroot
		self.font=('霞鹜文楷等宽',16)
		self.subroot.iconbitmap('./musync_data/Musync.ico')
		self.subroot.geometry(f'1000x600+600+400')
		self.subroot.title("高精度延迟分析")
		self.subroot['background'] = '#efefef'
		self.tipLabel = Label(self.subroot,font=self.font, relief="groove",text='↓将您用来辨识谱面的方式填入右侧文本框      请将控制台中的内容粘贴进右面的文本框，然后点击按钮↓')
		self.tipLabel.place(x=0,y=0,height=40,relwidth=1)
		self.logText = Text(self.subroot,font=self.font)
		self.logText.place(relx=0.7,y=70,relheight=0.88,relwidth=0.3)
		self.logButton = Button(self.subroot,text='点击生成图表',command=self.Draw,font=self.font,bg='#FFCCCC')
		self.logButton.place(relx=0.7,y=40,height=30,relwidth=0.3)
		self.hitAnalyzeButton = Button(self.subroot,text='All\nHit',command=lambda:HitAnalyze().Analyze(),font=self.font, relief="groove")
		self.hitAnalyzeButton.place(x=0,y=40,height=60,relwidth=0.05)
		self.nameDelayLabel = Label(self.subroot,font=self.font, relief="groove",text='↓请在下面输入曲名与谱面难度↓这只是用来标记你玩的哪个谱面而已，\n只要你能分辨就行，没有格式要求。如"ニニ 4KEZ"、"二重4H"等')
		self.nameDelayLabel.place(relx=0.05,y=40,height=60,relwidth=0.65)
		self.nameDelayEntry = Entry(self.subroot,font=self.font, relief="sunken")
		self.nameDelayEntry.place(relx=0.01,y=100,height=30,relwidth=0.68)
		self.delayHistory = ttk.Treeview(self.subroot, show="headings", columns = ['name','AllKeys','AvgDelay','AvgAcc'])
		self.delayHistory.place(x=0,y=130,relheight=0.78,relwidth=0.68)
		self.VScroll1 = Scrollbar(self.subroot, orient='vertical', command=self.delayHistory.yview)
		self.delayHistory.configure(yscrollcommand=self.VScroll1.set)
		self.VScroll1.place(relx=0.68,y=130,relheight=0.78,relwidth=0.02)

		self.history = list()
		self.HistoryUpdate()
		self.UpdateWindowInfo()

	def HistoryUpdate(self):
		ids = self.delayHistory.get_children()
		for idx in ids:
			self.delayHistory.delete(idx)
		data = self.cur.execute("select * from HitDelayHistory")
		data = data.fetchall()
		for ids in data:
			self.history = list()
			self.history.append(ids[0])
			self.delayHistory.insert('', END, values=(ids[0],ids[2],'%.6f ms'%ids[1],'%.6f ms'%ids[3]))
		del data

	def Draw(self):
		data = self.logText.get("0.0", "end").split('\n')
		dataIndex = self.GetIndex(data)
		dataList=list()
		name = self.nameDelayEntry.get()+f"-{dt.now()}"
		if data[-1] == "":
			data.pop(-1)
		for ids in range(dataIndex,len(data)-1):
			dataList.append(float(data[ids][13:-2]))
		allKeys = len(dataList)
		avgDelay = sum(dataList)/allKeys
		avgAcc = sum([abs(i) for i in dataList])/allKeys
		self.delayHistory.insert('', END, values=(name,allKeys,'%.6f ms'%avgDelay,'%.6f ms'%avgAcc))
		dataListStr = ""
		for i in dataList:
			dataListStr += f'{i}|'
		self.cur.execute("insert into HitDelayHistory values(?,?,?,?,?)",(name,avgDelay,allKeys,avgAcc,dataListStr[:-1]))
		self.db.commit()
		self.HistoryUpdate()
		dataList = [name,avgDelay,allKeys,avgAcc,dataList]
		HitDelayDraw(dataList,isHistory=False)


	def GetIndex(self,data):
		b=list()
		for index, value in enumerate(data):
			if value == '> Game Start!':
				b.append(index)
		if len(b)==0:
			return 0
		else:
			return (b[-1]+1)

	def HistoryDraw(self,event):
		e = event.widget									# 取得事件控件
		itemID = e.identify("item",event.x,event.y)			# 取得双击项目id
		# state = e.item(itemID,"text")						# 取得text参数
		historyItem = e.item(itemID,"values")				# 取得values参数
		# print(e.item(itemID))
		if not self.history == []:
			data = self.cur.execute(f'select * from HitDelayHistory where SongMapName=\'{historyItem[0]}\'')
			data = data.fetchone()
			HitDelayDraw(data,isHistory=True)
			# print(self.history[historyItem[0]])

	def UpdateWindowInfo(self):
		self.delayHistory.heading("name",anchor="center",text="曲名/时间")
		self.delayHistory.heading("AllKeys",anchor="center",text="Keys")
		self.delayHistory.heading("AvgDelay",anchor="center",text="Delay")
		self.delayHistory.heading("AvgAcc",anchor="center",text="AvgAcc")
		self.delayHistory.column("name",anchor="w",width=300)
		self.delayHistory.column("AllKeys",anchor="e",width=60)
		self.delayHistory.column("AvgDelay",anchor="e",width=150)
		self.delayHistory.column("AvgAcc",anchor="e",width=150)
		self.delayHistory.bind("<Double-1>",self.HistoryDraw)

		self.subroot.update()
		# self.subroot.after(500,self.UpdateWindowInfo)

class HitDelayDraw(object):
	"""docstring for ClassName"""
	def __init__(self, dataList,isHistory=False):
		self.avgDelay = dataList[1]
		self.allKeys = dataList[2]
		self.avgAcc = dataList[3]
		if isHistory:
			dataList = [float(i) for i in dataList[4].split("|")]
		else:
			dataList = dataList[4]

		self.x_axis = [i for i in range(0,len(dataList))]
		self.zero_axis = [0 for i in range(0,len(dataList))]
		self.EXTRAa = [45 for i in range(0,len(dataList))]
		self.EXTRAb = [-45 for i in range(0,len(dataList))]
		self.Extraa = [90 for i in range(0,len(dataList))]
		self.Extrab = [-90 for i in range(0,len(dataList))]
		self.Greata = [150 for i in range(0,len(dataList))]
		self.Greatb = [-150 for i in range(0,len(dataList))]
		self.Right = [250 for i in range(0,len(dataList))]
		self.y_axis = dataList

		# print(self.x_axis,self.y_axis)
		self.fig = plt.figure(f'AvgDelay: {"%.4fms"%self.avgDelay}    AllKeys: {self.allKeys}    AvgAcc: {"%.4fms"%self.avgAcc}',figsize=(9, 4))
		print(f'AvgDelay: {self.avgDelay}',end='\t')
		print(f'AllKeys: {self.allKeys}',end='\t')
		print(f'AvgAcc: {self.avgAcc}')
		
		plt.text(0,70,"Slower→", ha='right',fontsize=10,color='#c22472',rotation=90)
		plt.text(0,-70,"←Faster", ha='right',va='top',fontsize=10,color='#288328',rotation=90)
		
		self.Label()
		self.Draw()
		plt.show()


	def Label(self):
		for x,y in zip(self.x_axis,self.y_axis):
			if y<0:
				plt.text(x,y-3,'%.0fms'%y,ha='center',va='top',fontsize=7.5,alpha=0.7)
			else:
				plt.text(x,y+3,'%.0fms'%y,ha='center',va='bottom',fontsize=7.5,alpha=0.7)


	def Draw(self):
		self.fig.subplots_adjust(**{"left":0.04,"bottom":0.05,"right":1,"top":1})
		plt.plot(self.x_axis,self.zero_axis,linestyle='-',alpha=1,linewidth=1,color='red',label='0ms')
		plt.plot(self.x_axis,self.EXTRAa,linestyle='--',alpha=0.7,linewidth=1,color='cyan',label='Cyan Extra(±45ms)')
		plt.plot(self.x_axis,self.EXTRAb,linestyle='--',alpha=0.7,linewidth=1,color='cyan')
		plt.plot(self.x_axis,self.Extraa,linestyle='--',alpha=0.7,linewidth=1,color='blue',label='Blue Extra(±90ms)')
		plt.plot(self.x_axis,self.Extrab,linestyle='--',alpha=0.7,linewidth=1,color='blue')
		plt.plot(self.x_axis,self.Greata,linestyle='--',alpha=0.7,linewidth=1,color='green',label='Great(±150ms)')
		plt.plot(self.x_axis,self.Greatb,linestyle='--',alpha=0.7,linewidth=1,color='green')
		plt.plot(self.x_axis,self.Right,linestyle='--',alpha=0.7,linewidth=1,color='red',label='Right(+250ms)')
		plt.plot(self.x_axis,self.y_axis,linestyle='-',alpha=0.7,linewidth=1,color='#8a68d0',label='HitDelay(ms)',marker='.'
         ,markeredgecolor='#c4245c',markersize='3')
		plt.legend()  #显示上面的label
		plt.xlabel('HitCount') #x_label
		plt.ylabel('Delay')#y_label
		plt.gca().yaxis.set_major_locator(MultipleLocator(20))
		plt.xlim(-15,len(self.x_axis)+15)

if __name__ == '__main__':
	# HitDelayCheck()
	root = Tk()
	window = HitDelayText(subroot=root)
	root.update()
	root.mainloop()
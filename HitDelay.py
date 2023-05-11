from tkinter import *
from tkinter import Tk,ttk,font,Text
from matplotlib import pyplot as plt
from matplotlib.pyplot import MultipleLocator
from datetime import datetime as dt
from hashlib import md5
import os
import json
import FileExport
import sqlite3 as sql
from AllHitAnalyze import HitAnalyze

class HitDelayCheck(object):
	"""docstring for HitDelayWindow"""
	def __init__(self):
		self.md5l = '03CF2A2DCFE6572B26D08D94D3B581FE' # HitDelayFix.dll
		self.md5o = '0722724F7D0AC74AD42F6FC648D81359' # Assembly-CSharp.dll

		with open('./musync_data/SaveFilePath.sfp','r+',encoding='utf8') as sfp:
			self.spfr = sfp.read()[:-21]+'MUSYNX_Data/Managed/Assembly-CSharp.dll'
		self.DLLCheck()

	def DLLCheck(self):
		with open(self.spfr,'rb') as spfrb:
			md5o = md5(spfrb.read()).hexdigest().upper()
		if (md5o == self.md5o) and (not md5o == self.md5l):
			self.DLLInjection()
			return True
		elif (md5o == self.md5l):
			return True
		else:
			return False

	def DLLInjection(self):
		if os.path.isfile(self.spfr+'.old'):
			os.remove(self.spfr+'.old')
		os.rename(self.spfr,self.spfr+'.old')
		FileExport.WriteHitDelayFix(self.spfr)

class HitDelayText(object):
	"""docstring for DrawHDLine"""
	def __init__(self,subroot):
		if os.path.isfile('./musync_data/HitDelayHistory.db'):
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

		with open('./musync_data/ExtraFunction.cfg', 'r') as confFile:
			config = json.load(confFile)

		self.hitAnalyzeButton = Button(self.subroot,text='All\nHit',command=lambda : HitAnalyze(),font=self.font, relief="groove")
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
		
		if ('EnableAcc-Sync' in config) and (config['EnableAcc-Sync']):
			self.logButton = Button(self.subroot,text='点击生成图表',command=self.Draw,font=self.font,bg='#FFCCCC')
			self.logButton.place(relx=0.7,y=40,height=30,relwidth=0.2)
			self.txtButton = Button(self.subroot,text='Acc-Sync',command=self.OpenTxt,font=self.font)
			self.txtButton.place(relx=0.9,y=40,height=30,relwidth=0.1)
		else:
			self.logButton = Button(self.subroot,text='点击生成图表',command=self.Draw,font=self.font,bg='#FFCCCC')
			self.logButton.place(relx=0.7,y=40,height=30,relwidth=0.3)

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
		sumNums,sumKeys = 0,0
		for ids in dataList:
			if (ids < 90) and (ids > -90):
				sumNums += ids
				sumKeys += 1
		avgDelay = sumNums/sumKeys
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

	def OpenTxt(self):
		os.system('start notepad ./musync_data/Acc-Sync.json')
		# print(os.getcwd())
		# os.system(f'start explorer {os.getcwd()}')
		import AvgAcc_SynxAnalyze
		AvgAcc_SynxAnalyze.main()

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
		self.y_axis = [int(i) for i in dataList]

		self.sum = [0,0,0,0,0]
		self.exCount = [0,0,0]
		for ids in dataList:
			ids = abs(ids)
			if ids < 5:self.exCount[0] += 1
			elif ids < 10:self.exCount[1] += 1
			elif ids < 20:self.exCount[2] += 1
			if ids < 45: self.sum[0] += 1
			elif ids < 90: self.sum[1] += 1
			elif ids < 150: self.sum[2] += 1
			elif ids < 250: self.sum[3] += 1
			else: self.sum[4] += 1
		self.exCount = self.exCount + self.sum
		print(self.sum,self.exCount)
		fig = plt.figure(f'AvgDelay: {"%.4fms"%self.avgDelay}    AllKeys: {self.allKeys}    AvgAcc: {"%.4fms"%self.avgAcc}',figsize=(9, 4))
		fig.subplots_adjust(**{"left":0.04,"bottom":0.05,"right":1,"top":1})
		# print(self.x_axis,self.y_axis)
		print(f'AvgDelay: {self.avgDelay}\tAllKeys: {self.allKeys}\tAvgAcc: {self.avgAcc}')
		plt.text(0,70,"Slower→", ha='right',fontsize=10,color='#c22472',rotation=90, 
			fontdict={'family':'LXGW WenKai Mono','weight':'normal','size':15})
		plt.text(0,-70,"←Faster", ha='right',va='top',fontsize=10,color='#288328',rotation=90, 
			fontdict={'family':'LXGW WenKai Mono','weight':'normal','size':15})
		
		self.Label()
		self.Draw()
		with open('./musync_data/ExtraFunction.cfg', 'r') as confFile:
			config = json.load(confFile)
		if ('EnableDonutChartinHitDelay' in config) and (config['EnableDonutChartinHitDelay']):
			self.Pie()
		plt.show()


	def Label(self):
		for x,y in zip(self.x_axis,self.y_axis):
			if y<0:
				plt.text(x,y-3,'%dms'%y,ha='center',va='top',fontsize=7.5,alpha=0.7, 
					fontdict={'family':'LXGW WenKai Mono','weight':'normal'})
			else:
				plt.text(x,y+3,'%dms'%y,ha='center',va='bottom',fontsize=7.5,alpha=0.7, 
					fontdict={'family':'LXGW WenKai Mono','weight':'normal'})


	def Draw(self):
		plt.plot(self.x_axis,self.zero_axis,linestyle='-',alpha=1,linewidth=1,color='red',label='0ms')
		plt.plot(self.x_axis,self.EXTRAa,linestyle='--',alpha=0.7,linewidth=1,color='cyan',
			label='Cyan Extra(±45ms)    --%d'%self.sum[0])
		plt.plot(self.x_axis,self.EXTRAb,linestyle='--',alpha=0.7,linewidth=1,color='cyan')
		plt.plot(self.x_axis,self.Extraa,linestyle='--',alpha=0.7,linewidth=1,color='blue',
			label='Blue Extra(±90ms)    --%d'%self.sum[1])
		plt.plot(self.x_axis,self.Extrab,linestyle='--',alpha=0.7,linewidth=1,color='blue')
		plt.plot(self.x_axis,self.Greata,linestyle='--',alpha=0.7,linewidth=1,color='green',
			label='Great(±150ms)        --%d'%self.sum[2])
		plt.plot(self.x_axis,self.Greatb,linestyle='--',alpha=0.7,linewidth=1,color='green')
		plt.plot(self.x_axis,self.Right,linestyle='--',alpha=0.7,linewidth=1,color='red',
			label='Right(+250ms)         --%d'%self.sum[3])
		plt.plot(self.x_axis,self.y_axis,linestyle='-',alpha=0.7,linewidth=1,color='#8a68d0',
			label='HitDelay(ms)      miss--%d'%self.sum[4],marker='.',markeredgecolor='#c4245c',markersize='3')
		plt.legend(prop={'family':'LXGW WenKai Mono','weight':'normal','size':12},framealpha=0.5)  #显示上面的label
		plt.xlabel('HitCount') #x_label
		plt.ylabel('Delay')#y_label
		plt.gca().yaxis.set_major_locator(MultipleLocator(20))
		plt.xlim(-15,len(self.x_axis)+15)

	def Pie(self):
		def Percentage(num, summ):
			per = num/summ*100
			return ' '*(3-len(str(int((per)))))+'%.3f%%'%(per)
		def Count(num):
			cou = str(num)
			return ' '*(6-len(cou))+cou
		def PercentageLabel(num, summ):
			per = num/summ*100
			return '%.1f%%'%(per)
		fig = plt.figure(f'Pie', figsize=(5.5, 4.5))
		fig.subplots_adjust(**{"left":0,"bottom":0,"right":1,"top":1})
		wedgeprops = {'width':0.15, 'edgecolor':'black', 'linewidth':0.2}
		if self.sum[0]/sum(self.sum) > 0.6:
			exCountSum = sum(self.exCount)
			plt.pie(self.exCount, wedgeprops=wedgeprops, startangle=90,
				colors=['#AAFFFF','#00B5B5','#78BEFF','cyan', 'blue', 'green', 'orange', 'red'],
				# autopct=lambda x:'%.3f%%'%(x*sum(self.exCount)/100+0.5),
				labels=[
					f"EXTRA±5ms {PercentageLabel(self.exCount[0], exCountSum)}", 
					f"EXTRA±10ms {PercentageLabel(self.exCount[1], exCountSum)}", 
					f"EXTRA±20ms {PercentageLabel(self.exCount[2], exCountSum)}", 
					f"EXTRA±45ms {PercentageLabel(self.exCount[3], exCountSum)}", 
					f"Extra {PercentageLabel(self.exCount[4], exCountSum)}", 
					f"Great {PercentageLabel(self.exCount[5], exCountSum)}", 
					f"Right {PercentageLabel(self.exCount[6], exCountSum)}", 
					f"Miss {PercentageLabel(self.exCount[7], exCountSum)}"],
				textprops={'family':'LXGW WenKai Mono','weight':'normal','size':9})
			plt.legend(prop={'family':'LXGW WenKai Mono','weight':'normal','size':9},loc='center',
				labels=[
					f"EXTRA± 5ms  {Count(self.exCount[0])}  {Percentage(self.exCount[0], exCountSum)}", 
					f"EXTRA±10ms  {Count(self.exCount[1])}  {Percentage(self.exCount[1], exCountSum)}", 
					f"EXTRA±20ms  {Count(self.exCount[2])}  {Percentage(self.exCount[2], exCountSum)}", 
					f"EXTRA±45ms  {Count(self.exCount[3])}  {Percentage(self.exCount[3], exCountSum)}", 
					f"Extra±90ms  {Count(self.exCount[4])}  {Percentage(self.exCount[4], exCountSum)}", 
					f"Great±150ms {Count(self.exCount[5])}  {Percentage(self.exCount[5], exCountSum)}", 
					f"Right＋250ms {Count(self.exCount[6])}  {Percentage(self.exCount[6], exCountSum)}", 
					f"Miss > 250ms {Count(self.exCount[7])}  {Percentage(self.exCount[7], exCountSum)}"],
				)
			plt.text(-0.41,0.48,f"EXTRA        {Count(sum(self.exCount[0:4]))}  {Percentage(sum(self.exCount[0:4]), exCountSum)}", 
				ha='left',va='top',fontsize=9,color='#00B5B5', 
				fontdict={'family':'LXGW WenKai Mono','weight':'normal'})
		else:
			summ = sum(self.sum)
			plt.pie(self.sum, wedgeprops=wedgeprops, startangle=90,
				colors=['cyan', 'blue', 'green', 'orange', 'red'],
				# autopct=lambda x:'%.3f%%'%(x*sum(self.exCount)/100+0.5),
				labels=[
					f"EXTRA {PercentageLabel(self.sum[0], summ)}", 
					f"Extra {PercentageLabel(self.sum[1], summ)}", 
					f"Great {PercentageLabel(self.sum[2], summ)}", 
					f"Right {PercentageLabel(self.sum[3], summ)}", 
					f"Miss  {PercentageLabel(self.sum[4], summ)}"],
				textprops={'family':'LXGW WenKai Mono','weight':'normal','size':9})
			plt.legend(prop={'family':'LXGW WenKai Mono','weight':'normal','size':9},loc='center',
				labels=[
					f"EXTRA±45ms  {Count(self.sum[0], summ)}  {Percentage(self.sum[0], summ)}", 
					f"Extra±90ms  {Count(self.sum[1], summ)}  {Percentage(self.sum[1], summ)}", 
					f"Great±150ms {Count(self.sum[2], summ)}  {Percentage(self.sum[2], summ)}", 
					f"Right＋250ms {Count(self.sum[3], summ)}  {Percentage(self.sum[3], summ)}", 
					f"Miss > 250ms {Count(self.sum[4], summ)}  {Percentage(self.sum[4], summ)}"],
				)


if __name__ == '__main__':
	# HitDelayCheck()
	root = Tk()
	window = HitDelayText(subroot=root)
	root.update()
	root.mainloop()
import logging
import tkinter
import os
import pyperclip
import sqlite3
import uiautomation as uiauto
from datetime import datetime as dt
from matplotlib import axes, pyplot as plot, gridspec, figure
from matplotlib.pyplot import MultipleLocator
# from tkinter import *
from tkinter import Tk, ttk, messagebox
from tkinter import Button, Label, Entry, Frame, Scrollbar

from AllHitAnalyze import AllHitAnalyze
# from AllHitAnalyze_New import AllHitAnalyze
from Resources import Config, Logger

uiauto.SetGlobalSearchTimeout(1)

class HitDelayText(object):
	"""docstring for DrawHDLine"""
	def __init__(self,subroot):
		self.__logger:logging.Logger = Logger.GetLogger("HitDelay.HitDelayText")
		db_path:str = './musync_data/HitDelayHistory.db'
		db_exists:bool = os.path.isfile(db_path)
		self.db:sqlite3.Connection = sqlite3.connect(db_path)
		self.cur:sqlite3.Cursor = self.db.cursor()
		if not db_exists:
			self.cur.execute("""CREATE TABLE HitDelayHistory (
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
		self.subroot.geometry('1000x600+600+400')
		self.subroot.title("高精度延迟分析")
		self.subroot['background'] = '#efefef'
		self.tipLabel = Label(self.subroot,font=self.font, relief="groove",text='↓将您用来辨识谱面的方式填入右侧文本框，然后点击右侧红色按钮进行结果分析↓',fg='#F9245E')
		self.tipLabel.place(x=0,y=0,height=40,relwidth=1)
		self.style = ttk.Style()
		self.cursorHistory = ''
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
		if Config.Acc_Sync:
			self.logButton.place(relx=0.7,y=70,height=60,relwidth=0.3)
			self.txtButton = Button(self.subroot,text='生成Acc-Sync图表',command=self.OpenTxt,font=self.font)
			self.txtButton.place(relx=0.7,y=40,height=30,relwidth=0.3)
		else:
			self.logButton.place(relx=0.7,y=40,height=90,relwidth=0.3)
		self.keysButton = Button(self.subroot,font=self.font, text=("4Key" if Config.Default4Keys else "6Key"), command=self.ChangeKeys, bg="#4AA4C9")
		self.keysButton.place(relx=0.5,y=100,height=30,relwidth=0.1)
		self.diffcute = Config.DefaultDiffcute
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
		self.historyKeysLabel = Label(self.historyFrame, text='按键数量: ',font=self.font, relief="groove", anchor="e")
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

		self.delayInterval:int = 45 if Config.NarrowDelayInterval else 90
		self.history:list = list()
		self.HistoryUpdate()
		self.UpdateWindowInfo()

	def ChangeKeys(self):
		""" 切换按键数 """
		Config.Default4Keys = not Config.Default4Keys
		self.keysButton.configure(text=("4Key" if Config.Default4Keys else "6Key"))
	def ChangeDiffcute(self):
		""" 切换难度 """
		self.diffcute = (self.diffcute + 1) % 3
		Config.DefaultDiffcute = self.diffcute
		self.diffcuteButton.configure(text=["Easy","Hard","Inferno"][self.diffcute])

	def TestEntryString(self):
		""" 测试输入框内容 """
		string = self.nameDelayEntry.get()
		if string == '':
			self.nameDelayEntry.insert(0, "→→在这里输入谱面标识←←")
		elif string == '→→在这里输入谱面标识←←':
			self.nameDelayEntry.delete(0,'end')
		return True

	def HistoryUpdate(self):
		""" 更新历史记录 """
		for ids in self.delayHistory.get_children():
			self.delayHistory.delete(ids)
		data = self.cur.execute("SELECT SongMapName,RecordTime,AvgDelay,AllKeys,AvgAcc from HitDelayHistory")
		data = data.fetchall()
		self.history = list()
		for ids in data:
			self.history.append(ids[0])
			self.delayHistory.insert('', tkinter.END, values=(ids[0],ids[1],ids[3],'%.6f ms'%ids[2],'%.6f ms'%ids[4]))
		del data
		self.UpdateWindowInfo()

	def Draw(self):
		""" 绘制 HitDelay 图表 """
		consoleFind = False
		try:
			win = uiauto.WindowControl(searchDepth=1,Name='MUSYNX Delay',searchInterval=1).DocumentControl(searchDepth=1,Name='Text Area',searchInterval=1)
			win.SendKeys('{Ctrl}A',waitTime=0.1)
			win.SendKeys('{Ctrl}C',waitTime=0.1)
			consoleFind = True
		except Exception:
			self.__logger.exception("控制台窗口未找到,请确认控制台窗口已开启")
			try:
				win = uiauto.WindowControl(searchDepth=1,Name='选择 MUSYNX Delay',searchInterval=1).DocumentControl(searchDepth=1,Name='Text Area',searchInterval=1)
				win.SendKeys('{Ctrl}A',waitTime=0.1)
				win.SendKeys('{Ctrl}C',waitTime=0.1)
				consoleFind = True
			except Exception:
				self.__logger.exception("控制台窗口未找到,请确认控制台窗口已开启")
				messagebox.showerror("Error", '控制台窗口未找到\n请确认控制台窗口已开启')
		if consoleFind:
			data = pyperclip.paste().split('\n')
			dataList=list()
			n = self.nameDelayEntry.get().replace("\'","’")
			k = "4K" if Config.Default4Keys else "6K"
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
			avgDelay = (sumNums / sumKeys) if sumKeys > 0 else 0
			avgAcc = (sum(abs(i) for i in dataList) / allKeys) if allKeys > 0 else 0
			self.delayHistory.insert('', tkinter.END, values=(name, time, allKeys, '%.6f ms'%avgDelay, '%.6f ms'%avgAcc))
			dataListStr = ""
			for i in dataList:
				dataListStr += f'{i}|'
			self.cur.execute("INSERT into HitDelayHistory values(?,?,?,?,?,?)",(name,time,avgDelay,allKeys,avgAcc,dataListStr[:-1]))
			self.db.commit()
			self.HistoryUpdate()
			dataList = [name,time,avgDelay,allKeys,avgAcc,dataList]
			if allKeys == 0:
				messagebox.showwarning("Warning", "未检测到任何有效的 HitDelay 数据，已跳过绘图。")
				return
			HitDelayDraw(dataList,isHistory=False)

	def OpenTxt(self):
		""" 打开 Acc-Sync 文本文件 """
		import subprocess
		subprocess.Popen(['notepad', './musync_data/Acc-Sync.json'])
		# os.system(f'start explorer {os.getcwd()}')
		import AvgAcc_SynxAnalyze
		AvgAcc_SynxAnalyze.Analyze()

	def ShowHistoryInfo(self,event):
		""" 显示历史记录信息 """
		e = event.widget									# 取得事件控件
		itemID = e.identify("item",event.x,event.y)			# 取得双击项目id
		# state = e.item(itemID,"text")						# 取得text参数
		historyItem = e.item(itemID,"values")				# 取得values参数
		if not itemID or not historyItem:
			return
		if not self.history == []:
			# isChange = False
			historyName = historyItem[0].replace("\'",'’')
			recordTime = historyItem[1]
			self.__logger.debug(f"ShowHistoryInfo: {historyItem}")
			data = self.cur.execute("SELECT * FROM HitDelayHistory WHERE SongMapName=? AND RecordTime=?", (historyName, recordTime))
			data = data.fetchone()
			self.__logger.debug(data[:4])
			self.cursorHistory = data[0]
			self.historyNameEntry.delete(0, 'end')
			self.historyNameEntry.insert(0, data[0])
			self.historyRecordTimeValueLabel['text'] = data[1]
			self.historyKeysValueLabel['text'] = '% 5s    '%data[3]
			self.historyDelayValueLabel['text'] = '%.6fms  '%float(data[2])
			self.historyAccValueLabel['text'] = '%.6fms  '%float(data[4])
			del data

	def DeleteCursorHistory(self):
		""" 删除历史记录 """
		self.__logger.info(f"delete history {self.cursorHistory}")
		if self.cursorHistory == '':
			messagebox.showerror('Error','请输入谱面标识')
		else:
			result = messagebox.askyesno('提示', f'是否删除该谱面游玩记录?\n{self.cursorHistory}')
			if result:
				self.cur.execute(
					"DELETE FROM HitDelayHistory WHERE SongMapName=? AND RecordTime=?",
					(self.cursorHistory, self.historyRecordTimeValueLabel["text"])
				)
				self.db.commit()
				self.HistoryUpdate()

	def UpdateCursorHistory(self):
		""" 更新历史记录 """
		nowHistoryName = self.historyNameEntry.get().replace("\'","’")
		if self.cursorHistory != nowHistoryName:
			self.__logger.debug(f"change history name \nfrom {self.cursorHistory} \nto {nowHistoryName} \nwhen time is {self.historyRecordTimeValueLabel['text']}")
			self.cur.execute(
				"UPDATE HitDelayHistory SET SongMapName=? WHERE SongMapName=? AND RecordTime=?",
				(nowHistoryName, self.cursorHistory, self.historyRecordTimeValueLabel["text"]),
			)
			self.db.commit()
			self.HistoryUpdate()

	def HistoryDraw(self,event):
		""" 绘制历史记录图表 """
		e = event.widget									# 取得事件控件
		itemID = e.identify("item",event.x,event.y)			# 取得双击项目id
		# state = e.item(itemID,"text")						# 取得text参数
		historyItem = e.item(itemID,"values")				# 取得values参数
		self.__logger.debug(e.item(itemID))
		if not itemID or not historyItem:
			return
		if not self.history == []:
			data = self.cur.execute(
			 	"SELECT * FROM HitDelayHistory WHERE SongMapName=? AND RecordTime=?",
			 	(historyItem[0], historyItem[1]),
			)
			data = data.fetchone()
			HitDelayDraw(data,isHistory=True)

	def UpdateWindowInfo(self):
		""" 更新窗口信息 """
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

		self.__logger.debug(f"VScroll1.get:{self.VScroll1.get()}")
		self.delayHistory.place(x=0,y=130,height=self.subroot.winfo_height()-130,relwidth=0.684)
		self.VScroll1.place(relx=0.684,y=132,height=self.subroot.winfo_height()-133,relwidth=0.015)
		self.subroot.update()
		self.delayHistory.yview_moveto(1.0)
		# self.subroot.after(500,self.UpdateWindowInfo)

class HitDelayDraw(object):
	""" docstring for DrawHDLine """
	def __init__(self, dataList,isHistory=False):
		self.__logger:logging.Logger = Logger.GetLogger("HitDelay.HitDelayDraw")
		self.__logger.info(f'Name:{dataList[0]}\nRecordTime:{dataList[1]}')
		self.avgDelay = dataList[2]
		self.allKeys = dataList[3]
		self.avgAcc = dataList[4]
		if isHistory:
			self.dataList = [float(i) for i in dataList[5].split("|")]
		else:
			self.dataList = dataList[5]

		self.dataListLenth = len(self.dataList)
		if self.dataListLenth == 0:
			self.__logger.warning("HitDelayDraw: empty data list, skipping plots")
			return
		self.x_axis = [i for i in range(self.dataListLenth)]
		self.y_axis = [int(i) for i in self.dataList]

		self.sum = [0,0,0,0,0]
		self.exCount = [0,0,0,0]
		for ids in self.dataList:
			ids = abs(ids)
			if ids < 45:
				if ids < 5:
					self.exCount[0] += 1
				elif ids < 10:
					self.exCount[1] += 1
				elif ids < 20:
					self.exCount[2] += 1
				else:
					self.exCount[3] += 1
			elif ids < 90:
				self.sum[1] += 1
			elif ids < 150:
				self.sum[2] += 1
			elif ids < 250:
				self.sum[3] += 1
			else:
				self.sum[4] += 1
		self.sum[0] = sum(self.exCount)
		self.exCount = self.exCount + self.sum[1:]
		self.__logger.debug(f"HitDelayDraw: {self.sum}, {self.exCount}")

		self.DrawLine()
		if Config.DonutChartinHitDelay: self.DrawBarPie()
		plot.show()

	def DrawLine(self):
		""" 绘制 HitDelay 折线图 """
		fig = plot.figure(f'AvgDelay: {self.avgDelay:.4f}ms    AllKeys: {self.allKeys}    AvgAcc: {self.avgAcc:.4f}ms',figsize=(9, 4))
		fig.clear()
		fig.subplots_adjust(**{"left":0.045,"bottom":0.055,"right":1,"top":1})
		ax = fig.add_subplot()
		plot.rcParams['font.serif'] = ["LXGW WenKai Mono"]
		plot.rcParams["font.sans-serif"] = ["LXGW WenKai Mono"]
		self.__logger.info(f'AvgDelay: {self.avgDelay}\tAllKeys: {self.allKeys}\tAvgAcc: {self.avgAcc}')
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

		for x,y in zip(self.x_axis, self.y_axis, strict=True):
			if y<0:
				ax.text(x,y-3,'%dms'%y,ha='center',va='top',fontsize=7.5,alpha=0.7)
			else:
				ax.text(x,y+3,'%dms'%y,ha='center',va='bottom',fontsize=7.5,alpha=0.7)

		ax.legend(prop={'size':12},framealpha=0.5)  #显示上面的label
		ax.set_xlabel('HitCount', fontsize=15) #x_label
		ax.set_ylabel('Delay', fontsize=15) #y_label
		ax.yaxis.set_major_locator(MultipleLocator(20))
		ax.set_xlim(-15,len(self.x_axis)+15)
		# plt.show()

	def DrawBarPie(self):
		""" 绘制 HitDelay 饼图与柱状图 """
		def Percentage(num, summ, decimals=3)->str:
			"""
			百分比标签，补齐3位整数，保留三位小数
			param:
				num: 部分值
				summ: 总值
			return:
				str 百分比标签
			"""
			if summ == 0:
				return f"{0:.{decimals}f}%"
			return f"{num / summ * 100:.{decimals}f}%"
		def CountStr(num, width=6)->str:
			"""
			数量标签，补齐width位整数
			param:
				num: 数量值
				width: 补齐宽度
			return:
				str 数量标签
			"""
			return str(num).rjust(width)

		# import random
		# fig = plt.figure(f'Pie&Bar AvgDelay: {"%.4fms"%self.avgDelay}  ' \
		# 	f'AllKeys: {self.allKeys}  AvgAcc: {"%.4fms"%self.avgAcc}', figsize=(5.5, 6.5))
		fig:figure.Figure = plot.figure('Pie&Bar', figsize=(5.5, 6.5))
		fig.clear()
		grid:gridspec.GridSpec = gridspec.GridSpec(4, 1, left=0, right=1, top=1, bottom=0.035, wspace=0, hspace=0)
		ax1:axes.Axes = fig.add_subplot(grid[0:3,0])

		# 保护：计算总量并在为空时提前返回
		total_sum = sum(self.sum)
		ex_total = sum(self.exCount) if hasattr(self, "exCount") else 0
		if total_sum == 0 and ex_total == 0:
			self.__logger.warning("DrawBarPie: no data to plot")
			return

		wedgeprops = {'width': 0.15, 'edgecolor': 'black', 'linewidth': 0.2}

		# 当 EXACT 部分占比大时，显示更细的分段（exCount 包含 4 个 EXACT 子段，后面接其他段）
		if ex_total and (ex_total / (total_sum if total_sum > 0 else ex_total) > 0.6):
			labels = ["EXACT±5ms", "EXACT±10ms", "EXACT±20ms", "EXACT±45ms",
					  "Exact", "Great", "Right", "Miss"]
			colors = ['#9dfff0', '#69f1f1', '#25d8d8', '#32a9c7',
					  '#2F97FF', 'green', 'orange', 'red']
			# 确保 exCount 长度为 8（原逻辑中 exCount 已扩展），否则填 0
			data = list(self.exCount) if len(self.exCount) >= 8 else (list(self.exCount) + [0] * (8 - len(self.exCount)))
			pie_rtn = ax1.pie(data, wedgeprops=wedgeprops, startangle=90, autopct='%1.1f%%',
							  pctdistance=0.95, labeldistance=1.05, colors=colors, labels=labels,
							  textprops={'size': 10})
			# 构建 legend 文本
			legend_labels = [
				f"EXACT± 5ms  {CountStr(data[0])}  {Percentage(data[0], ex_total, 3)}",
				f"EXACT±10ms  {CountStr(data[1])}  {Percentage(data[1], ex_total, 3)}",
				f"EXACT±20ms  {CountStr(data[2])}  {Percentage(data[2], ex_total, 3)}",
				f"EXACT±45ms  {CountStr(data[3])}  {Percentage(data[3], ex_total, 3)}",
				f"Exact±90ms  {CountStr(data[4])}  {Percentage(data[4], ex_total, 3)}",
				f"Great±150ms {CountStr(data[5])}  {Percentage(data[5], ex_total, 3)}",
				f"Right＋250ms {CountStr(data[6])}  {Percentage(data[6], ex_total, 3)}",
				f"Miss >=251ms {CountStr(data[7])}  {Percentage(data[7], ex_total, 3)}",
			]
			ax1.legend(prop={'size': 9}, loc='center', handles=pie_rtn[0], labels=legend_labels)
			ax1.text(-0.41, 0.48,
					 f"EXACT        {CountStr(sum(data[0:4]))}  {Percentage(sum(data[0:4]), ex_total, 3)}",
					 ha='left', va='top', fontsize=9, color='#00B5B5')
		else:
			# 使用 self.sum 的五段显示
			summ = total_sum if total_sum > 0 else 1
			labels = ["EXACT", "Exact", "Great", "Right", "Miss"]
			colors = ['cyan', '#2F97FF', 'green', 'orange', 'red']
			data = list(self.sum)
			ax1.pie(data, wedgeprops=wedgeprops, startangle=90, autopct='%1.1f%%',
					pctdistance=0.9, labeldistance=1.05, colors=colors,
					labels=labels, textprops={'size': 9})
			ax1.legend(prop={'size': 9}, loc='center',
					   labels=[
						   f"EXACT±45ms  {CountStr(data[0])}  {Percentage(data[0], summ, 3)}",
						   f"Exact±90ms  {CountStr(data[1])}  {Percentage(data[1], summ, 3)}",
						   f"Great±150ms {CountStr(data[2])}  {Percentage(data[2], summ, 3)}",
						   f"Right＋250ms {CountStr(data[3])}  {Percentage(data[3], summ, 3)}",
						   f"Miss > 250ms {CountStr(data[4])}  {Percentage(data[4], summ, 3)}",
					   ])

		# ---- 构建命中分布直方图数据（保留原有 bin 范围） ----
		hitMapA = [0] * 150  # -149 ... -1, index 0 表示 -149
		hitMapB = [0] * 251  # 0 ... 250, 250 为 250+
		for v in self.dataList:
			# 原代码对负数向下取整的处理：负数 -1.2 -> int(-1.2)-1 -> -2
			if v < 0:
				idx = int(v) - 1
			else:
				idx = int(v)
			if 0 <= idx < 250:
				hitMapB[idx] += 1
			elif idx >= 250:
				hitMapB[250] += 1
			else:
				# 索引为负时，hitMapA 使用 idx 直接索引（保持原行为）
				# 这里若 idx < -149 仍会抛出 IndexError；为稳健，采用扩展处理
				neg_idx = idx
				# 若超出左界，扩展左侧列表以保证索引有效
				need = abs(neg_idx) - len(hitMapA) + 1
				if need > 0:
					hitMapA = [0] * need + hitMapA
				hitMapA[neg_idx] += 1

		# 删除左右无用空白
		leftBorder, rightBorder = 0, 0
		while hitMapA and (hitMapA[0] == 0):
			hitMapA.pop(0)
			leftBorder += 1
		while hitMapB and (hitMapB[-1] == 0):
			hitMapB.pop(-1)
			rightBorder += 1

		xAxis = [i for i in range(-len(hitMapA), 251 - rightBorder)]
		yAxis = hitMapA + hitMapB

		ax2 = fig.add_subplot(grid[3, 0])
		# 一次性绘制 bar（避免在 Python 中循环单个绘制）
		if yAxis:
			ax2.bar(xAxis, yAxis, align='center')
		ax2.xaxis.set_major_locator(MultipleLocator(15))

		fig.tight_layout()


if __name__ == '__main__':
	# HitDelayCheck()
	root = Tk()
	window = HitDelayText(subroot=root)
	root.update()
	root.mainloop()
from tkinter import *
from tkinter import Tk,ttk,font,Text
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
import json
from datetime import datetime as dt
from os.path import isfile
from hashlib import md5
from os import rename
from FileExport import WriteHitDelayFix

class HitDelayCheck(object):
	"""docstring for HitDelayWindow"""
	def __init__(self):
		self.md5l = '9C7A7CE7C2C69DEF7C56316394D193D3' # HitDelayFix.dll
		self.md5o = 'B6852581AA60C7E2EDC7EF44DF3ACC96' # Assembly-CSharp.dll
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
		rename(self.spfr,self.spfr+'.old')
		WriteHitDelayFix(self.spfr)

class HitDelayText(object):
	"""docstring for DrawHDLine"""
	def __init__(self,subroot):
		self.subroot = subroot
		self.font=('霞鹜文楷等宽',16)
		self.subroot.iconbitmap('./musync_data/Musync.ico')
		self.subroot.geometry(f'1000x600+600+400')
		style = ttk.Style()
		style.configure("Treeview", rowheight=20, font=('霞鹜文楷等宽',14))
		style.configure("Treeview.Heading", rowheight=20, font=('霞鹜文楷等宽',16))
		self.subroot.title("高精度延迟分析")
		self.subroot['background'] = '#efefef'
		self.tipLabel = Label(self.subroot,font=self.font, relief="groove",text='请将控制台中的内容粘贴进右面的文本框，然后点击按钮↘')
		self.tipLabel.place(x=0,y=0,height=40,relwidth=1)
		self.logText = Text(self.subroot,font=self.font)
		self.logText.place(relx=0.7,y=70,relheight=0.88,relwidth=0.3)
		self.logButton = Button(self.subroot,text='点击生成图表',command=self.Draw,font=self.font,bg='#FFCCCC')
		self.logButton.place(relx=0.7,y=40,height=30,relwidth=0.3)
		self.nameDelayLabel = Label(self.subroot,font=self.font, relief="groove",text='↓请在下面输入曲名与谱面难度↓这只是用来标记你玩的哪个谱面而已，\n只要你能分辨就行，没有格式要求。如"ニニ 4KEZ"、"二重4H"等')
		self.nameDelayLabel.place(x=0,y=40,height=60,relwidth=0.7)
		self.nameDelayEntry = Entry(self.subroot,font=self.font, relief="sunken")
		self.nameDelayEntry.place(relx=0.01,y=100,height=30,relwidth=0.68)
		self.delayHistory = ttk.Treeview(self.subroot, show="headings", columns = ['name','AllKeys','AvgDelay','AvgAcc'])
		self.delayHistory.place(x=0,y=130,relheight=0.78,relwidth=0.7)
		self.VScroll1 = Scrollbar(self.delayHistory, orient='vertical', command=self.delayHistory.yview)
		self.delayHistory.configure(yscrollcommand=self.VScroll1.set)
		self.VScroll1.place(relx=0.97,rely=0.005,relheight=0.99,width=20)

		self.History()
		self.UpdateWindowInfo()

	def Draw(self):
		data = self.logText.get("0.0", "end")
		HitDelayDraw(data,self.nameDelayEntry.get())
		self.History()

	def History(self):
		if isfile('./musync_data/HitDelayHistory.json'):
			with open('./musync_data/HitDelayHistory.json','r',encoding='utf8') as f:
				history = json.load(f)
			del f
			# print(history.keys())
			for ids in history:
				self.delayHistory.insert('', END, values=(ids,history[ids][1],'%.6f ms'%history[ids][0],'%.6f ms'%history[ids][2]))


	def HistoryDraw(self,*args):
		print(args)
		pass

	def UpdateWindowInfo(self):
		self.delayHistory.heading("name",anchor="center",text="曲名/时间")
		self.delayHistory.heading("AllKeys",anchor="center",text="Keys")
		self.delayHistory.heading("AvgDelay",anchor="center",text="Delay")
		self.delayHistory.heading("AvgAcc",anchor="center",text="AvgAcc")
		self.delayHistory.column("name",anchor="w",width=320)
		self.delayHistory.column("AllKeys",anchor="e",width=60)
		self.delayHistory.column("AvgDelay",anchor="e",width=150)
		self.delayHistory.column("AvgAcc",anchor="e",width=150)
		self.subroot.update()
		self.delayHistory.bind("<Double-1>",self.HistoryDraw)

		self.subroot.update()
		self.subroot.after(500,self.UpdateWindowInfo)

class HitDelayDraw(object):
	"""docstring for ClassName"""
	def __init__(self, data,name):
		self.data = data.split('\n')
		self.name = name + f"{dt.now()}"
		p = self.GetIndex()
		self.x_axis = [i for i in range(1,len(self.data)-p-1)]
		self.zero_axis = [0 for i in range(p,len(self.data)-2)]
		self.EXTRAa = [45 for i in range(p,len(self.data)-2)]
		self.EXTRAb = [-45 for i in range(p,len(self.data)-2)]
		self.Extraa = [90 for i in range(p,len(self.data)-2)]
		self.Extrab = [-90 for i in range(p,len(self.data)-2)]
		self.Greata = [150 for i in range(p,len(self.data)-2)]
		self.Greatb = [-150 for i in range(p,len(self.data)-2)]
		self.Right = [250 for i in range(p,len(self.data)-2)]
		self.pos = p
		self.y_axis = list()
		for i in range(p,len(self.data)-2):
			# print(self.data[i])
			print(i,self.data[i])
			self.y_axis.append(float(self.data[i][13:-2]))
		# print(self.x_axis,self.y_axis)
		self.allKeys = len(self.y_axis)
		self.avgDelay = sum(self.y_axis)/self.allKeys
		self.avgAcc = sum([abs(i) for i in self.y_axis])/self.allKeys
		self.fig = plt.figure(f'AvgDelay: {"%.4fms"%self.avgDelay}    AllKeys: {self.allKeys}    AvgAcc: {"%.4fms"%self.avgAcc}',figsize=(9, 4))
		print(f'AvgDelay: {self.avgDelay}')
		print(f'AllKeys: {self.allKeys}')
		print(f'AvgAcc: {self.avgAcc}')

		self.Write()
		
		plt.text(0,70,"Slower→", ha='right',fontsize=10,color='#c22472',rotation=90)
		plt.text(0,-70,"←Faster", ha='right',va='top',fontsize=10,color='#288328',rotation=90)
		
		self.Label()
		self.Draw()
		plt.show()

	def GetIndex(self):
		b=list()
		for index, value in enumerate(self.data):
			if value == '> Game Start!':
				b.append(index)
		if len(b)==0:
			return 0
		else:
			return (b[-1]+1)

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

	def Write(self):
		if isfile('./musync_data/HitDelayHistory.json'):
			with open('./musync_data/HitDelayHistory.json','r',encoding='utf8') as f:
				pre = json.load(f)
			pre[self.name] = [self.avgDelay,self.allKeys,self.avgAcc,self.y_axis]
			with open('./musync_data/HitDelayHistory.json','w',encoding='utf8') as f:
				json.dump(pre,f,ensure_ascii=False)
		else:
			with open('./musync_data/HitDelayHistory.json','w',encoding='utf8') as nf:
				json.dump({self.name:[self.avgDelay,self.allKeys,self.avgAcc,self.y_axis]},nf,ensure_ascii=False)

if __name__ == '__main__':
	# HitDelayCheck()
	root = Tk()
	window = HitDelayText(subroot=root)
	root.update()
	root.mainloop()
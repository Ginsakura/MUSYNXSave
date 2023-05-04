#-*- coding: utf-8 -*-
from matplotlib import pyplot as plt
from matplotlib.pyplot import MultipleLocator
# import numpy as np
import sqlite3 as sql

class HitAnalyze(object):
	"""docstring for HitAnalyze"""
	def __init__(self):
		super(HitAnalyze, self).__init__()
		db = sql.connect('./musync_data/HitDelayHistory.db')
		cur = db.cursor()
		res = cur.execute('select HitMap from HitDelayHistory')
		res = res.fetchall()
		hitMapA = [0]*150 # -149~-0
		hitMapB = [0]*251 # +0~+250
		self.sumYnum = 0 # with miss
		self.rate=[0,0,0,0,0]
		for ids in res:
			for idx in ids[0].split("|"):
				idx = float(idx)
				self.sumYnum += 1

				idxAbs = abs(idx)
				if idxAbs<45:self.rate[0] += 1
				elif idxAbs<90:self.rate[1] += 1
				elif idxAbs<150:self.rate[2] += 1
				elif idxAbs<250:self.rate[3] += 1
				else :self.rate[4] += 1

				if idx < 0:
					idx = int(idx)-1
				else:
					idx = int(idx)

				if (idx >= 0) and (idx < 250):
					hitMapB[idx] += 1
				elif idx >= 250:
					hitMapB[250] += 1
				else:
					hitMapA[idx] += 1

		self.xAxis = [i for i in range(-150,251)]
		self.yAxis = hitMapA + hitMapB
		self.avg = sum([ids[0]*ids[1]/self.sumYnum for ids in zip(self.xAxis,self.yAxis)])
		self.var = sum([(ids[1]/self.sumYnum)*((ids[0] - self.avg) ** 2) for ids in zip(self.xAxis,self.yAxis)])
		self.std = self.var**0.5

		self.sumYnumEx = sum(self.yAxis[60:240])
		self.avgEx = sum([ids[0]*ids[1]/self.sumYnumEx for ids in zip(self.xAxis[60:240],self.yAxis[60:240])])
		self.varEx = sum([(ids[1]/self.sumYnumEx)*((ids[0] - self.avg) ** 2) for ids in zip(self.xAxis[60:240],self.yAxis[60:240])])
		self.stdEx = self.varEx**0.5
		# del db,cur,hitMapA,hitMapB,res,idxAbs
		print(self.avg,self.var,self.std,self.sumYnum)
		print(self.avgEx,self.varEx,self.stdEx,self.sumYnumEx)
		self.Analyze()
		self.Pie()
		plt.show()

	def Analyze(self):
		def PDFx(x):
			# pdf = np.exp((x-self.avg)**2/(-2*self.var))/(np.sqrt(2*np.pi)*self.std)
			e = 2.718281828459045
			p = 3.141592653589793
			pdf = (e**(-1*(((x-self.avg)**2))/(2*self.var))) / (((2*p)**0.5)*self.std)
			return pdf*self.sumYnum
		def PDFxEx(x):
			# pdf = np.exp((x-self.avg)**2/(-2*self.var))/(np.sqrt(2*np.pi)*self.std)
			e = 2.718281828459045
			p = 3.141592653589793
			pdf = (e**(-1*(((x-self.avgEx)**2))/(2*self.varEx))) / (((2*p)**0.5)*self.stdEx)
			return pdf*self.sumYnumEx

		##正态分布函数曲线
		pdfAxis = [PDFx(i) for i in self.xAxis]
		pdfExAxis = [PDFxEx(i) for i in self.xAxis]

		colors = ['red','orange','yellow','green','cyan','blue','purple']
		yLine = []
		maxY = max(self.yAxis)
		strMaxY = str(maxY)
		maxLen = 10**len(strMaxY)
		maxLenSub2 = maxLen//100

		if maxY < maxLen*0.2:
			for ids in range(maxLen//400,maxLenSub2,maxLen//400):
				yLine.append([ids for i in range(-150,251)])
			for ids in range(maxLenSub2,maxLenSub2*(int(strMaxY[0:2])+2),maxLenSub2):
				yLine.append([ids for i in range(-150,251)])
		elif maxY < maxLen*0.3:
			for ids in range(maxLenSub2,maxLenSub2*(int(strMaxY[0:2])+2),maxLenSub2):
				yLine.append([ids for i in range(-150,251)])
		elif maxY < maxLen*0.6:
			for ids in range(maxLenSub2*2,maxLenSub2*(int(strMaxY[0:2])+2),maxLenSub2*2):
				yLine.append([ids for i in range(-150,251)])
		else:
			for ids in range(maxLen//40,maxLen//10,maxLen//40):
				yLine.append([ids for i in range(-150,251)])
			for ids in range(maxLen//10,maxY+maxLen//10,maxLen//10):
				yLine.append([ids for i in range(-150,251)])

		fig = plt.figure(f"HitAnalyze (total:{self.sumYnum},  CyanEx:{self.rate[0]},  BlueEx:{self.rate[1]},  Great:{self.rate[2]},  Right:{self.rate[3]},  Miss:{self.rate[4]})", figsize=(16, 8))
		fig.subplots_adjust(**{"left":0.045,"bottom":0.06,"right":1,"top":1})
		plt.xlabel("Delay(ms)",fontproperties='LXGW WenKai Mono',fontsize=15)
		plt.ylabel("HitNumber",fontproperties='LXGW WenKai Mono',fontsize=15)
		plt.xlim(-155,255)

		plt.gca().xaxis.set_major_locator(MultipleLocator(10))
		if maxY < 100:
			plt.gca().yaxis.set_major_locator(MultipleLocator(5))
		elif maxY < 1000:
			plt.gca().yaxis.set_major_locator(MultipleLocator(25))
		elif maxY < 2000:
			plt.gca().yaxis.set_major_locator(MultipleLocator(50))
		elif maxY < 4000:
			plt.gca().yaxis.set_major_locator(MultipleLocator(75))
		elif maxY < 8000:
			plt.gca().yaxis.set_major_locator(MultipleLocator(150))
		elif maxY < 16000:
			plt.gca().yaxis.set_major_locator(MultipleLocator(300))
		elif maxY < 32000:
			plt.gca().yaxis.set_major_locator(MultipleLocator(600))

		x=0
		for ids in yLine:
			plt.plot(self.xAxis,ids,linestyle='--',alpha=1,linewidth=1,color=colors[x])
			x = (x+1)%7
			# print(ids[0],end=',')
		# print()
		plt.plot(self.xAxis,pdfAxis,linestyle=':',alpha=1,linewidth=1,color='black',label=f'Fitting all data\n(μ={self.avg}\n σ={self.std})')
		plt.plot(self.xAxis,pdfExAxis,linestyle='-',alpha=1,linewidth=1,color='black',label=f'Fitting only on Extra rate\n(μ={self.avgEx}\n σ={self.stdEx})')

		for i in range(len(self.xAxis)):
			plt.bar(self.xAxis[i],self.yAxis[i])

		plt.legend(prop={'family':'LXGW WenKai Mono','weight':'normal','size':15})  #显示上面的label

	def Pie(self):
		def Percentage(num):
			per = self.rate[num]/sum(self.rate)*100
			return ' '*(3-len(str(int((per)))))+'%.3f%%'%(per)
		def Count(num):
			cou = str(self.rate[num])
			return ' '*(6-len(cou))+cou
		fig = plt.figure(f'Pie')
		fig.subplots_adjust(**{"left":0,"bottom":0,"right":1,"top":1})
		wedgeprops = {'width':0.2, 'edgecolor':'black', 'linewidth':0.2}
		plt.pie(self.rate, wedgeprops=wedgeprops, startangle=90,
			colors=['cyan', 'blue', 'green', 'orange', 'red'],
			# autopct=lambda x:'%d'%(x*sum(self.rate)/100+0.5),
			labels=["EXTRA", "Extra", "Great", "Right", "Miss"],
			textprops={'family':'LXGW WenKai Mono','weight':'normal','size':12})
		plt.legend(prop={'family':'LXGW WenKai Mono','weight':'normal','size':12},loc='center',
			labels=[f"EXTRA  {Count(0)}  {Percentage(0)}", 
				f"Extra  {Count(1)}  {Percentage(1)}", 
				f"Great  {Count(2)}  {Percentage(2)}", 
				f"Right  {Count(3)}  {Percentage(3)}", 
				f"Miss   {Count(4)}  {Percentage(4)}"],
			)
# 		plt.text(-0.65, -0.35, 
# f'''
# EXTRA  {self.rate[0]}{' '*(6-len(str(self.rate[0])))}  {' '*(3-len(str(int((self.rate[0]/sum(self.rate)*100)))))}{'%.3f%%'%(self.rate[0]/sum(self.rate)*100)}
# Extra  {self.rate[1]}{' '*(6-len(str(self.rate[1])))}  {' '*(3-len(str(int((self.rate[1]/sum(self.rate)*100)))))}{'%.3f%%'%(self.rate[1]/sum(self.rate)*100)}
# Great  {self.rate[2]}{' '*(6-len(str(self.rate[2])))}  {' '*(3-len(str(int((self.rate[2]/sum(self.rate)*100)))))}{'%.3f%%'%(self.rate[2]/sum(self.rate)*100)}
# Right  {self.rate[3]}{' '*(6-len(str(self.rate[3])))}  {' '*(3-len(str(int((self.rate[3]/sum(self.rate)*100)))))}{'%.3f%%'%(self.rate[3]/sum(self.rate)*100)}
# Miss   {self.rate[4]}{' '*(6-len(str(self.rate[4])))}  {' '*(3-len(str(int((self.rate[4]/sum(self.rate)*100)))))}{'%.3f%%'%(self.rate[4]/sum(self.rate)*100)}
# ''', fontdict={'family':'LXGW WenKai Mono','weight':'normal','size':15})

if __name__ == '__main__':
	HitAnalyze()
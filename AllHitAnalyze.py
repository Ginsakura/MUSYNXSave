#-*- coding: utf-8 -*-
from matplotlib import pyplot as plt
from matplotlib.pyplot import MultipleLocator
# import numpy as np
import sqlite3 as sql
import json

class HitAnalyze(object):
	"""docstring for HitAnalyze"""
	def __init__(self,isOpen=False):
		super(HitAnalyze, self).__init__()
		self.isOpen = isOpen
		db = sql.connect('./musync_data/HitDelayHistory.db')
		cur = db.cursor()
		res = cur.execute('select HitMap from HitDelayHistory')
		res = res.fetchall()
		hitMapA = [0]*150 # -149~-0
		hitMapB = [0]*251 # +0~+250
		self.sumYnum = 0 # with miss
		self.sumYnumEx = 0 # only extra
		self.sumYnumEX = 0 # only cyan extra
		self.rate=[0,0,0,0,0] # EXTRA,Extra,Great,Right,Miss
		self.accurateRate=[0,0,0,0,0,0,0,0] # ±5ms,±10ms,±20ms,±45ms,Extra,Great,Right,Miss
		for ids in res:
			for idx in ids[0].split("|"):
				idx = float(idx)
				self.sumYnum += 1

				idxAbs = abs(idx)
				if idxAbs<5:
					self.accurateRate[0] += 1
				elif idxAbs<10:
					self.accurateRate[1] += 1
				elif idxAbs<20:
					self.accurateRate[2] += 1
				elif idxAbs<45:
					self.rate[0] += 1
					self.accurateRate[3] += 1
				elif idxAbs<90:
					self.rate[1] += 1
					self.accurateRate[4] += 1
				elif idxAbs<150:
					self.rate[2] += 1
					self.accurateRate[5] += 1
				elif idxAbs<250:
					self.rate[3] += 1
					self.accurateRate[6] += 1
				else :
					self.rate[4] += 1
					self.accurateRate[7] += 1

				if idxAbs<45:
					self.sumYnumEX += 1
					self.sumYnumEx += 1
				elif idxAbs<90:
					self.sumYnumEx += 1

				if idx < 0:
					idx = int(idx)-1
				else:
					idx = int(idx)

				if (idx >= 0) and (idx < 250):hitMapB[idx] += 1
				elif (idx >= 250):hitMapB[250] += 1
				else:hitMapA[idx] += 1

		self.xAxis = [i for i in range(-150,251)]
		self.yAxis = hitMapA + hitMapB
		self.avg = sum([ids[0]*ids[1]/self.sumYnum for ids in zip(self.xAxis,self.yAxis)])
		self.var = sum([(ids[1]/self.sumYnum)*((ids[0] - self.avg) ** 2) for ids in zip(self.xAxis,self.yAxis)])
		self.std = self.var**0.5

		self.avgEx = sum([ids[0]*ids[1]/self.sumYnumEx for ids in zip(self.xAxis[61:240],self.yAxis[61:240])])
		self.varEx = sum([(ids[1]/self.sumYnumEx)*((ids[0] - self.avgEx) ** 2) for ids in zip(self.xAxis[61:240],self.yAxis[61:240])])
		self.stdEx = self.varEx**0.5
		# del db,cur,hitMapA,hitMapB,res,idxAbs
		print('all data:  ',self.avg,self.var,self.std,self.sumYnum)
		print('extra rate:',self.avgEx,self.varEx,self.stdEx,self.sumYnumEx)

	def Show(self):
		with open('./musync_data/ExtraFunction.cfg', 'r',encoding='utf8') as confFile:
			config = json.load(confFile)
		if config['EnablePDFofCyanExtra']:
			self.avgEX = sum([ids[0]*ids[1]/self.sumYnumEX for ids in zip(self.xAxis[106:195],self.yAxis[106:195])])
			self.varEX = sum([(ids[1]/self.sumYnumEX)*((ids[0] - self.avgEX) ** 2) for ids in zip(self.xAxis[106:195],self.yAxis[106:195])])
			self.stdEX = self.varEX**0.5
			self.enablePDFofCyanExtra = True
			print('cyan extra:',self.avgEX,self.varEX,self.stdEX,self.sumYnumEX)
		else:
			self.enablePDFofCyanExtra = False
		self.Analyze()
		if config['EnableDonutChartinAllHitAnalyze']:
			self.Pie()
		plt.show()

	def Analyze(self):
		e = 2.718281828459045
		p = 3.141592653589793
		def PDFx(x):
			# pdf = np.exp((x-self.avg)**2/(-2*self.var))/(np.sqrt(2*np.pi)*self.std)
			pdf = (e**(-1*(((x-self.avg)**2))/(2*self.var))) / (((2*p)**0.5)*self.std)
			return pdf*self.sumYnum
		def PDFxEx(x):
			# pdf = np.exp((x-self.avg)**2/(-2*self.var))/(np.sqrt(2*np.pi)*self.std)
			pdf = (e**(-1*(((x-self.avgEx)**2))/(2*self.varEx))) / (((2*p)**0.5)*self.stdEx)
			return pdf*self.sumYnumEx
		def PDFxEX(x):
			# pdf = np.exp((x-self.avg)**2/(-2*self.var))/(np.sqrt(2*np.pi)*self.std)
			pdf = (e**(-1*(((x-self.avgEX)**2))/(2*self.varEX))) / (((2*p)**0.5)*self.stdEX)
			return pdf*self.sumYnumEX

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

		fig = plt.figure(f"HitAnalyze (Total:{self.sumYnum},  CyanEx:{self.rate[0]},  BlueEx:{self.rate[1]},  Great:{self.rate[2]},  Right:{self.rate[3]},  Miss:{self.rate[4]})", figsize=(16, 8))
		fig.subplots_adjust(**{"left":0.045,"bottom":0.06,"right":1,"top":1})
		if self.isOpen: fig.clear()
		plt.xlabel("Delay(ms)",fontproperties='LXGW WenKai Mono',fontsize=15)
		plt.ylabel("HitCount",fontproperties='LXGW WenKai Mono',fontsize=15)
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

		##正态分布函数曲线
		pdfAxis = [PDFx(i) for i in self.xAxis]
		plt.plot(self.xAxis,pdfAxis,linestyle='-',alpha=1,linewidth=1,color='grey',
			label=f'Fitting all data\n(μ={self.avg}\n σ={self.std})')

		pdfExAxis = [PDFxEx(i) for i in self.xAxis]
		plt.plot(self.xAxis,pdfExAxis,linestyle='-',alpha=1,linewidth=1,color='black',
			label=f'Fitting only on Extra rate\n(μ={self.avgEx}\n σ={self.stdEx})')

		if self.enablePDFofCyanExtra:
			pdfEXAxis = [PDFxEX(i) for i in self.xAxis]
			plt.plot(self.xAxis,pdfEXAxis,linestyle='-',alpha=1,linewidth=1,color='blue',
				label=f'Fitting only on Cyan Extra rate\n(μ={self.avgEX}\n σ={self.stdEX})')


		for i in range(len(self.xAxis)):
			plt.bar(self.xAxis[i],self.yAxis[i])

		plt.legend(prop={'family':'LXGW WenKai Mono','weight':'normal','size':15})  #显示上面的label

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
		accurateRateSum = sum(self.accurateRate)
		fig = plt.figure(f'Pie', figsize=(7, 6))
		fig.subplots_adjust(**{"left":0,"bottom":0,"right":1,"top":1})
		if self.isOpen: fig.clear()
		wedgeprops = {'width':0.15, 'edgecolor':'black', 'linewidth':0.2}
		plt.pie(self.accurateRate, wedgeprops=wedgeprops, startangle=90,
			colors=['#AAFFFF','#00B5B5','#78BEFF','cyan', 'blue', 'green', 'orange', 'red'],
			# autopct=lambda x:'%.3f%%'%(x*sum(self.accurateRate)/100+0.5),
			labels=[
				f"EXTRA±5ms {PercentageLabel(self.accurateRate[0], accurateRateSum)}", 
				f"EXTRA±10ms {PercentageLabel(self.accurateRate[1], accurateRateSum)}", 
				f"EXTRA±20ms {PercentageLabel(self.accurateRate[2], accurateRateSum)}", 
				f"EXTRA±45ms {PercentageLabel(self.accurateRate[3], accurateRateSum)}", 
				f"Extra {PercentageLabel(self.accurateRate[4], accurateRateSum)}", 
				f"Great {PercentageLabel(self.accurateRate[5], accurateRateSum)}", 
				f"Right {PercentageLabel(self.accurateRate[6], accurateRateSum)}", 
				f"Miss {PercentageLabel(self.accurateRate[7], accurateRateSum)}"],
			textprops={'family':'LXGW WenKai Mono','weight':'normal','size':12})
		plt.legend(prop={'family':'LXGW WenKai Mono','weight':'normal','size':12},loc='center',
			labels=[
				f"EXTRA± 5ms  {Count(self.accurateRate[0])}  {Percentage(self.accurateRate[0], accurateRateSum)}", 
				f"EXTRA±10ms  {Count(self.accurateRate[1])}  {Percentage(self.accurateRate[1], accurateRateSum)}", 
				f"EXTRA±20ms  {Count(self.accurateRate[2])}  {Percentage(self.accurateRate[2], accurateRateSum)}", 
				f"EXTRA±45ms  {Count(self.accurateRate[3])}  {Percentage(self.accurateRate[3], accurateRateSum)}", 
				f"Extra±90ms  {Count(self.accurateRate[4])}  {Percentage(self.accurateRate[4], accurateRateSum)}", 
				f"Great±150ms {Count(self.accurateRate[5])}  {Percentage(self.accurateRate[5], accurateRateSum)}", 
				f"Right＋250ms {Count(self.accurateRate[6])}  {Percentage(self.accurateRate[6], accurateRateSum)}", 
				f"Miss > 250ms {Count(self.accurateRate[7])}  {Percentage(self.accurateRate[7], accurateRateSum)}"],
			)
		plt.text(-0.41,0.48,f"EXTRA        {Count(sum(self.accurateRate[0:4]))}  {Percentage(sum(self.accurateRate[0:4]), accurateRateSum)}", 
			ha='left',va='top',fontsize=12,color='#00B5B5', 
			fontdict={'family':'LXGW WenKai Mono','weight':'normal'})

if __name__ == '__main__':
	HitAnalyze().Show()
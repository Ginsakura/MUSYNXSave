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
		self.hitMapA = [0]*150 # -149~-0
		self.hitMapB = [0]*251 # +0~+250
		self.avg = 0
		self.var = 0
		self.std = 0
		self.sumy = 0
		for ids in res:
			for idx in ids[0].split("|"):
				idx = float(idx)
				if idx < 0:
					idx = int(idx)-1
				else:
					idx = int(idx)
				if (idx >= 0) and (idx < 250):
					self.hitMapB[idx] += 1
				elif idx >= 250:
					self.hitMapB[250] += 1
				else:
					self.hitMapA[idx] += 1

	def Analyze(self):
		def PDF(x,y):
			# self.avg = sum([i[0]*i[1]/self.sumy for i in zip(x,y)])
			# self.var = sum([(i[1]*((i[0]-self.avg)**2)/self.sumy) for i in zip(x,y)]) #numpy.var(y)
			s=0
			for ids in zip(x,y):
				s += ids[0]*ids[1]/self.sumy
			self.avg = s
			s=0
			for ids in zip(x,y):
				s += (ids[1] / self.sumy) * ((ids[0] - self.avg) ** 2)
			self.var = s
			self.std = self.var**0.5 #numpy.std(y)
			print(self.avg,self.var,self.std,self.sumy)
		def PDFx(x):
			# pdf = np.exp((x-self.avg)**2/(-2*self.var))/(np.sqrt(2*np.pi)*self.std)
			e=2.718281828459045
			p=3.141592653589793
			pdf = (e**(-1*(((x-self.avg)**2))/(2*self.var))) / (((2*p)**0.5)*self.std)
			return pdf*self.sumy

		xAxis = [i for i in range(-150,251)]
		yAxis = self.hitMapA + self.hitMapB

		self.sumy = sum(yAxis)
		##正态分布函数
		PDF(xAxis,yAxis)
		pdfAxis = [PDFx(i) for i in xAxis]

		colors = ['red','orange','yellow','green','cyan','blue','purple']
		yLine = []
		maxLen = 10**len(str(max(yAxis)))
		maxLenSub2 = maxLen//100
		# print(max(yAxis), maxLen*0.2,maxLenSub2,(int(str(max(yAxis))[0:2])+2))

		if max(yAxis) < maxLen*0.2:
			for ids in range(maxLen//400,maxLenSub2,maxLen//400):
				yLine.append([ids for i in range(-150,251)])
			for ids in range(maxLenSub2,maxLenSub2*(int(str(max(yAxis))[0:2])+2),maxLenSub2):
				yLine.append([ids for i in range(-150,251)])
		elif max(yAxis) < maxLen*0.3:
			for ids in range(maxLenSub2,maxLenSub2*(int(str(max(yAxis))[0:2])+2),maxLenSub2):
				yLine.append([ids for i in range(-150,251)])
		elif max(yAxis) < maxLen*0.6:
			for ids in range(maxLenSub2*2,maxLenSub2*(int(str(max(yAxis))[0:2])+2),maxLenSub2*2):
				yLine.append([ids for i in range(-150,251)])
		else:
			for ids in range(maxLen//40,maxLen//10,maxLen//40):
				yLine.append([ids for i in range(-150,251)])
			for ids in range(maxLen//10,max(yAxis)+maxLen//10,maxLen//10):
				yLine.append([ids for i in range(-150,251)])

		fig = plt.figure(f"HitAnalyze (total:{sum(yAxis)})", figsize=(16, 8))
		fig.subplots_adjust(**{"left":0.04,"bottom":0.06,"right":1,"top":1})
		plt.xlabel("Delay(ms)")
		plt.ylabel("HitNumber")
		plt.xlim(-155,255)

		plt.gca().xaxis.set_major_locator(MultipleLocator(10))
		if max(yAxis) < 100:
			plt.gca().yaxis.set_major_locator(MultipleLocator(5))
		elif max(yAxis) < 1000:
			plt.gca().yaxis.set_major_locator(MultipleLocator(25))
		elif max(yAxis) < 2000:
			plt.gca().yaxis.set_major_locator(MultipleLocator(50))
		elif max(yAxis) < 4000:
			plt.gca().yaxis.set_major_locator(MultipleLocator(75))
		elif max(yAxis) < 8000:
			plt.gca().yaxis.set_major_locator(MultipleLocator(150))
		elif max(yAxis) < 16000:
			plt.gca().yaxis.set_major_locator(MultipleLocator(300))
		elif max(yAxis) < 32000:
			plt.gca().yaxis.set_major_locator(MultipleLocator(600))

		x=0
		for ids in yLine:
			plt.plot(xAxis,ids,linestyle='--',alpha=1,linewidth=1,color=colors[x])
			x = (x+1)%7
			# print(ids[0],end=',')
		# print()
		plt.plot(xAxis,pdfAxis,linestyle='-',alpha=1,linewidth=1,color='black')

		for i in range(len(xAxis)):
			plt.bar(xAxis[i],yAxis[i])

		plt.show()
	

if __name__ == '__main__':
	obj = HitAnalyze()
	obj.Analyze()
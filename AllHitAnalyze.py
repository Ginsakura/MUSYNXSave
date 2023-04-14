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
		sumY = 0
		self.sumYnum = 0 # with miss
		for ids in res:
			for idx in ids[0].split("|"):
				idx = float(idx)
				self.sumYnum += 1

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
		print(self.avg,self.var,self.std,self.sumYnum)

	def Analyze(self):
		def PDFx(x):
			# pdf = np.exp((x-self.avg)**2/(-2*self.var))/(np.sqrt(2*np.pi)*self.std)
			e = 2.718281828459045
			p = 3.141592653589793
			pdf = (e**(-1*(((x-self.avg)**2))/(2*self.var))) / (((2*p)**0.5)*self.std)
			return pdf*self.sumYnum

		##正态分布函数曲线
		pdfAxis = [PDFx(i) for i in self.xAxis]

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

		fig = plt.figure(f"HitAnalyze (total:{self.sumYnum})", figsize=(16, 8))
		fig.subplots_adjust(**{"left":0.04,"bottom":0.06,"right":1,"top":1})
		plt.xlabel("Delay(ms)")
		plt.ylabel("HitNumber")
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
		plt.plot(self.xAxis,pdfAxis,linestyle='-',alpha=1,linewidth=1,color='black')

		for i in range(len(self.xAxis)):
			plt.bar(self.xAxis[i],self.yAxis[i])

		plt.show()
	

if __name__ == '__main__':
	obj = HitAnalyze()
	obj.Analyze()
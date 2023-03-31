import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
import sqlite3 as sql

class HitAnalyze(object):
	"""docstring for HitAnalyze"""
	def __init__(self):
		super(HitAnalyze, self).__init__()
		db = sql.connect('./musync_data/HitDelayHistory.db')
		cur = db.cursor()
		res = cur.execute('select HitMap from HitDelayHistory')
		res = res.fetchall()
		self.hitMapA = [0]*150 # -150~-1
		self.hitMapB = [0]*251 # 0~250
		for ids in res:
			for idx in ids[0].split("|"):
				idx = int(float(idx))
				if (idx >= 0) and (idx < 250):
					self.hitMapB[idx] += 1
				elif idx >= 250:
					self.hitMapB[250] += 1
				else:
					self.hitMapA[idx] += 1

	def Analyze(self):
		xAxis = [i for i in range(-150,0)] + [i for i in range(0,251)]
		yAxis = self.hitMapA + self.hitMapB
		y5 = [5 for i in range(-150,251)]
		y10 = [10 for i in range(-150,251)]
		y15 = [15 for i in range(-150,251)]
		y25 = [25 for i in range(-150,251)]
		y50 = [50 for i in range(-150,251)]
		y75 = [75 for i in range(-150,251)]
		y100 = [100 for i in range(-150,251)]
		y200 = [200 for i in range(-150,251)]
		y300 = [300 for i in range(-150,251)]
		y400 = [400 for i in range(-150,251)]
		y500 = [500 for i in range(-150,251)]
		y600 = [600 for i in range(-150,251)]
		y700 = [700 for i in range(-150,251)]
		y800 = [800 for i in range(-150,251)]

		# print(len(xAxis),len(yAxis))
		# print(xAxis)
		# print(yAxis)

		fig = plt.figure(f"HitAnalyze (total:{sum(yAxis)})", figsize=(16, 8))
		fig.subplots_adjust(**{"left":0.04,"bottom":0.06,"right":1,"top":1})
		plt.xlabel("Delay(ms)")
		plt.ylabel("HitNumber")
		plt.xlim(-155,255)
		plt.gca().xaxis.set_major_locator(MultipleLocator(10))
		plt.gca().yaxis.set_major_locator(MultipleLocator(50))

		plt.plot(xAxis,y5,linestyle='--',alpha=1,linewidth=1,color='red')
		plt.plot(xAxis,y10,linestyle='--',alpha=1,linewidth=1,color='orange')
		plt.plot(xAxis,y15,linestyle='--',alpha=1,linewidth=1,color='yellow')
		plt.plot(xAxis,y25,linestyle='--',alpha=1,linewidth=1,color='green')
		plt.plot(xAxis,y50,linestyle='--',alpha=1,linewidth=1,color='cyan')
		plt.plot(xAxis,y75,linestyle='--',alpha=1,linewidth=1,color='blue')
		plt.plot(xAxis,y100,linestyle='--',alpha=1,linewidth=1,color='purple')

		plt.plot(xAxis,y200,linestyle='--',alpha=1,linewidth=1,color='red')
		plt.plot(xAxis,y300,linestyle='--',alpha=1,linewidth=1,color='orange')
		plt.plot(xAxis,y400,linestyle='--',alpha=1,linewidth=1,color='yellow')
		plt.plot(xAxis,y500,linestyle='--',alpha=1,linewidth=1,color='green')
		plt.plot(xAxis,y600,linestyle='--',alpha=1,linewidth=1,color='cyan')
		plt.plot(xAxis,y700,linestyle='--',alpha=1,linewidth=1,color='blue')
		plt.plot(xAxis,y800,linestyle='--',alpha=1,linewidth=1,color='purple')

		for i in range(len(xAxis)):
			plt.bar(xAxis[i],yAxis[i])

		plt.show()
	

if __name__ == '__main__':
	obj = HitAnalyze()
	obj.Analyze()
import json
# import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import sqlite3 as sql

from matplotlib.pyplot import MultipleLocator

from Resources import Config

class AllHitAnalyze(object):
	"""docstring for HitAnalyze"""
	def __init__(self):
		# super(AllHitAnalyze, self).__init__()
		db = sql.connect('./musync_data/HitDelayHistory.db');
		cur = db.cursor();
		res = cur.execute('select HitMap from HitDelayHistory');
		res = res.fetchall();
		hitMapA = [0]*150; # -149~-0
		hitMapB = [0]*251; # +0~+250
		self.sumYnum = 0; # with miss
		self.sumYnumEx = 0; # only Exact
		self.sumYnumEX = 0; # only cyan Exact
		self.rate=[0,0,0,0,0]; # EXACT,Exact,Great,Right,Miss
		self.accurateRate=[0,0,0,0,0,0,0,0]; # ±5ms,±10ms,±20ms,±45ms,Exact,Great,Right,Miss
		for ids in res:
			for idx in ids[0].split("|"):
				idx = float(idx);
				self.sumYnum += 1;

				idxAbs = abs(idx);
				if idxAbs<5:
					self.rate[0] += 1;
					self.accurateRate[0] += 1;
				elif idxAbs<10:
					self.rate[0] += 1;
					self.accurateRate[1] += 1;
				elif idxAbs<20:
					self.rate[0] += 1;
					self.accurateRate[2] += 1;
				elif idxAbs<45:
					self.rate[0] += 1;
					self.accurateRate[3] += 1;
				elif idxAbs<90:
					self.rate[1] += 1;
					self.accurateRate[4] += 1;
				elif idxAbs<150:
					self.rate[2] += 1;
					self.accurateRate[5] += 1;
				elif idxAbs<250:
					self.rate[3] += 1;
					self.accurateRate[6] += 1;
				else :
					self.rate[4] += 1;
					self.accurateRate[7] += 1;

				if idxAbs<45:
					self.sumYnumEX += 1;
					self.sumYnumEx += 1;
				elif idxAbs<90:
					self.sumYnumEx += 1;

				if idx < 0:
					idx = int(idx)-1;
				else:
					idx = int(idx);

				if (idx >= 0) and (idx < 250):hitMapB[idx] += 1;
				elif (idx >= 250):hitMapB[250] += 1;
				else:hitMapA[idx] += 1;

		self.xAxis = [i for i in range(-150,251)];
		self.yAxis = hitMapA + hitMapB;
		self.avg = sum([ids[0]*ids[1]/self.sumYnum for ids in zip(self.xAxis,self.yAxis)]) if self.sumYnum > 0 else 0;
		self.var = sum([(ids[1]/self.sumYnum)*((ids[0] - self.avg) ** 2) for ids in zip(self.xAxis,self.yAxis)]) if self.sumYnum > 0 else 0;
		self.std = self.var**0.5;

		self.avgEx = sum([ids[0]*ids[1]/self.sumYnumEx for ids in zip(self.xAxis[61:240],self.yAxis[61:240])]) if self.sumYnumEx > 0 else 0;
		self.varEx = sum([(ids[1]/self.sumYnumEx)*((ids[0] - self.avgEx) ** 2) for ids in zip(self.xAxis[61:240],self.yAxis[61:240])]) if self.sumYnumEx > 0 else 0;
		self.stdEx = self.varEx**0.5;

		self.avgEX = sum([ids[0]*ids[1]/self.sumYnumEX for ids in zip(self.xAxis[106:195],self.yAxis[106:195])]) if self.sumYnumEX > 0 else 0;
		self.varEX = sum([(ids[1]/self.sumYnumEX)*((ids[0] - self.avgEX) ** 2) for ids in zip(self.xAxis[106:195],self.yAxis[106:195])]) if self.sumYnumEX > 0 else 0;
		self.stdEX = self.varEX**0.5;
		# del db,cur,hitMapA,hitMapB,res,idxAbs
		print('All data:  ',self.avg,self.var,self.std,self.sumYnum);
		print('Exact rate:',self.avgEx,self.varEx,self.stdEx,self.sumYnumEx);
		print('cyan Exact:',self.avgEX,self.varEX,self.stdEX,self.sumYnumEX);

	def Show(self):
		fig = plt.figure(f"HitAnalyze (Total:{self.sumYnum},  CyanEx:{self.rate[0]},  BlueEx:{self.rate[1]},  Great:{self.rate[2]},  Right:{self.rate[3]},  Miss:{self.rate[4]})", figsize=(16, 9));
		fig.clear();
		# fig.subplots_adjust(**{"left":0,"bottom":0,"right":1,"top":1});
		plt.rcParams['font.serif'] = ["LXGW WenKai Mono"];
		plt.rcParams["font.sans-serif"] = ["LXGW WenKai Mono"];
		# plt.rcParams["figure.subplot.bottom"] = 0;
		# plt.rcParams["figure.subplot.hspace"] = 0;
		# plt.rcParams["figure.subplot.left"] = 0;
		# plt.rcParams["figure.subplot.right"] = 0;
		# plt.rcParams["figure.subplot.top"] = 0;
		# plt.rcParams["figure.subplot.wspace"] = 0;
		grid = gridspec.GridSpec(3, 5, left=0.045, right=1, top=1, bottom=0.06, wspace=0, hspace=0);

		# print(plt.rcParams);

		ax1 = fig.add_subplot(grid[:,:]);
		self.Line(ax1);
		if Config.DonutChartinAllHitAnalyze:
			ax2 = fig.add_subplot(grid[0:2,3:]);
			ax2.add_patch(patches.Rectangle((-1.5, -1.5), 3, 3, color="white"));
			# print(ax2.get_subplotspec());
			self.Pie(ax2);
		plt.show();

	def Line(self,ax1):
		e = 2.718281828459045;
		p = 3.141592653589793;
		def PDFx(x):
			# pdf = np.exp((x-self.avg)**2/(-2*self.var))/(np.sqrt(2*np.pi)*self.std);
			pdf = (e**(-1*(((x-self.avg)**2))/(2*self.var))) / (((2*p)**0.5)*self.std);
			return pdf*self.sumYnum;
		def PDFxEx(x):
			# pdf = np.exp((x-self.avg)**2/(-2*self.var))/(np.sqrt(2*np.pi)*self.std);
			pdf = (e**(-1*(((x-self.avgEx)**2))/(2*self.varEx))) / (((2*p)**0.5)*self.stdEx);
			return pdf*self.sumYnumEx;
		def PDFxEX(x):
			# pdf = np.exp((x-self.avg)**2/(-2*self.var))/(np.sqrt(2*np.pi)*self.std);
			pdf = (e**(-1*(((x-self.avgEX)**2))/(2*self.varEX))) / (((2*p)**0.5)*self.stdEX);
			return pdf*self.sumYnumEX;

		colors = ['red','orange','yellow','green','cyan','blue','purple'];
		yLine = [];
		maxY = max(self.yAxis);
		strMaxY = str(maxY);
		maxLen = 10**len(strMaxY);
		maxLenSub2 = maxLen//100;

		if maxY < maxLen*0.2:
			for ids in range(maxLen//400,maxLenSub2,maxLen//400):
				yLine.append([ids for i in range(-150,251)]);
			for ids in range(maxLenSub2,maxLenSub2*(int(strMaxY[0:2])+2),maxLenSub2):
				yLine.append([ids for i in range(-150,251)]);
		elif maxY < maxLen*0.3:
			for ids in range(maxLenSub2,maxLenSub2*(int(strMaxY[0:2])+2),maxLenSub2):
				yLine.append([ids for i in range(-150,251)]);
		elif maxY < maxLen*0.6:
			for ids in range(maxLenSub2*2,maxLenSub2*(int(strMaxY[0:2])+2),maxLenSub2*2):
				yLine.append([ids for i in range(-150,251)]);
		else:
			for ids in range(maxLen//40,maxLen//10,maxLen//40):
				yLine.append([ids for i in range(-150,251)]);
			for ids in range(maxLen//10,maxY+maxLen//10,maxLen//10):
				yLine.append([ids for i in range(-150,251)]);

		ax1.set_xlabel("Delay(ms)", fontsize=15);
		ax1.set_ylabel("HitCount", fontsize=15);
		ax1.set_xlim(-155,255);

		ax1.xaxis.set_major_locator(MultipleLocator(10));
		if maxY < 100:
			ax1.yaxis.set_major_locator(MultipleLocator(5));
		elif maxY < 1000:
			ax1.yaxis.set_major_locator(MultipleLocator(25));
		elif maxY < 2000:
			ax1.yaxis.set_major_locator(MultipleLocator(50));
		elif maxY < 4000:
			ax1.yaxis.set_major_locator(MultipleLocator(75));
		elif maxY < 8000:
			ax1.yaxis.set_major_locator(MultipleLocator(150));
		elif maxY < 16000:
			ax1.yaxis.set_major_locator(MultipleLocator(300));
		elif maxY < 32000:
			ax1.yaxis.set_major_locator(MultipleLocator(600));

		x=0;
		for ids in yLine:
			ax1.plot(self.xAxis,ids,linestyle='--',alpha=1,linewidth=1,color=colors[x]);
			x = (x+1)%7;

		##正态分布函数曲线
		pdfAxis = [PDFx(i) for i in self.xAxis]
		ax1.plot(self.xAxis,pdfAxis,linestyle='-',alpha=1,linewidth=1,color='grey',
			label=f'Fitting all data\n(μ={self.avg}\n σ={self.std})');

		pdfExAxis = [PDFxEx(i) for i in self.xAxis]
		ax1.plot(self.xAxis,pdfExAxis,linestyle='-',alpha=1,linewidth=1,color='black',
			label=f'Fitting only on Exact rate\n(μ={self.avgEx}\n σ={self.stdEx})');

		pdfEXAxis = [PDFxEX(i) for i in self.xAxis]
		ax1.plot(self.xAxis,pdfEXAxis,linestyle='-',alpha=1,linewidth=1,color='blue',
			label=f'Fitting only on Cyan Exact rate\n(μ={self.avgEX}\n σ={self.stdEX})');


		for i in range(len(self.xAxis)):
			ax1.bar(self.xAxis[i],self.yAxis[i]);

		ax1.legend(loc='upper left',prop={'size':15}); #显示上面的label

	def Pie(self,ax2):
		def Percentage(num, summ):
			per = num/summ*100;
			return ' '*(3-len(str(int((per)))))+'%.3f%%'%(per);
		def Count(num):
			cou = str(num);
			return ' '*(6-len(cou))+cou;
		def PercentageLabel(num, summ):
			per = num/summ*100;
			return '%.1f%%'%(per);
		accurateRateSum = sum(self.accurateRate);

		wedgeprops = {'width':0.15, 'edgecolor':'black', 'linewidth':0.2};
		pieRtn = ax2.pie(self.accurateRate, wedgeprops=wedgeprops, startangle=90, autopct='%1.1f%%', pctdistance = 0.95, labeldistance = 1.05, 
			colors=['#9dfff0',    '#69f1f1',     '#25d8d8',     '#32a9c7',     '#2F97FF', 'green', 'orange', 'red', ], 
			labels=["EXACT±5ms", "EXACT±10ms", "EXACT±20ms", "EXACT±45ms", "Exact",   "Great", "Right",  "Miss", ], 
			textprops={'size':12});
		ax2.legend(prop={'size':12},loc='center', handles=pieRtn[0], 
			# labelcolor=['#9dfff0', '#69f1f1', '#25d8d8', '#32a9c7', '#2F97FF', 'green', 'orange', 'red', ], 
			labels=[
				f"EXACT± 5ms  {Count(self.accurateRate[0])}  {Percentage(self.accurateRate[0], accurateRateSum)}", 
				f"EXACT±10ms  {Count(self.accurateRate[1])}  {Percentage(self.accurateRate[1], accurateRateSum)}", 
				f"EXACT±20ms  {Count(self.accurateRate[2])}  {Percentage(self.accurateRate[2], accurateRateSum)}", 
				f"EXACT±45ms  {Count(self.accurateRate[3])}  {Percentage(self.accurateRate[3], accurateRateSum)}", 
				f"Exact±90ms  {Count(self.accurateRate[4])}  {Percentage(self.accurateRate[4], accurateRateSum)}", 
				f"Great±150ms {Count(self.accurateRate[5])}  {Percentage(self.accurateRate[5], accurateRateSum)}", 
				f"Right＋250ms {Count(self.accurateRate[6])}  {Percentage(self.accurateRate[6], accurateRateSum)}", 
				f"Miss > 250ms {Count(self.accurateRate[7])}  {Percentage(self.accurateRate[7], accurateRateSum)}", ],
			);
		ax2.text(0.1,0.5,f"EXACT        {Count(sum(self.accurateRate[0:4]))}  " \
			f"{Percentage(sum(self.accurateRate[0:4]), accurateRateSum)}", 
			ha='center',va='top',fontsize=12,color='#00B5B5', );

if __name__ == '__main__':
	AllHitAnalyze().Show();
from matplotlib.axes import Axes;
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.pyplot import MultipleLocator
from matplotlib.widgets import Button, Slider
import numpy
import matplotlib.patches
import matplotlib.pyplot
#import matplotlib.widgets as widgets
import json;
import sqlite3

# init Natural Constant: π & The base *e* of the natural logarithm
E:float = 2.718281828459045;
PI:float = 3.141592653589793;

class AllHitAnalyze(object):
	def __init__(self) -> None:
		super(AllHitAnalyze,self).__init__();
		# sqlite3 init and select data
		db:sqlite3.Connection = sqlite3.connect("./musync_data/HitDelayHistory_v2.db");
		cur:sqlite3.Cursor = db.cursor();
		self.sqlData:list[list[str]] = cur.execute("SELECT HitMap FROM HitDelayHistory").fetchall();
		# load config
		with open('./musync_data/ExtraFunction.cfg', 'r',encoding='utf8') as confFile:
			self.config:dict = json.load(confFile);
		# init PDF(Probability Density Function)
		self.summation:int = 0; # All Hit
		self.summationEx:int = 0; # Blue Exact & Cyan Exact
		self.summationEX:int = 0; # Only Cyan Exact
		# summation SYNC.Rate: [Cyan Exact, Blue Exact, Great, Right, Miss]
		# self.SYNC_Rate:list[int] = [0] * 5;
		# summation Accurate SYNC.Rate:
		#   [±5ms, ±10ms, ±20ms, ±45ms, Blue Exact, Great, Right, Miss]
		self.Accurate_Sync_Rate:list[int] = [0] * 8;
		# init hit map: [-149, -0], [+0, +250]
		# self.hitMapPositive:list[int] = [0]*150;
		# self.hitMapNegative:list[int] = [0]*251;
		# init chart axis
		self.xAxis:list[int] = [i for i in range(-150, 251, 1)];
		self.yAxis:list[int] = [0] * 401 # self.hitMapPositive + self.hitMapNegative;
		self.LoadHitMap(0);
		# All Hit PDF: Normal Distribution
		# avg:Average , var:Variance ,std: Standard Deviation
		self.avg:float = sum([num[0] * num[1] / self.summation for num in zip(self.xAxis, self.yAxis)]);
		self.var:float = sum([(num[1] / self.summation) * ((num[0] - self.avg) ** 2) for num in zip(self.xAxis, self.yAxis)]);
		self.std:float = self.var ** 0.5;
		print(f'All: avg:{self.avg:.4}, var:{self.var:.4}, std:{self.std:.4} sum:{self.summation}');
		# Exact Hit PDF: Normal Distribution
		# avg:Average , var:Variance ,std: Standard Deviation
		self.avgEx:float = sum([num[0]*num[1]/self.summationEx for num in zip(self.xAxis[61:240],self.yAxis[61:240])]);
		self.varEx:float = sum([(num[1] / self.summationEx) * ((num[0] - self.avgEx) ** 2) for num in zip(self.xAxis[61:240], self.yAxis[61:240])]);
		self.stdEx:float = self.varEx ** 0.5;
		print(f'All Exact: avg:{self.avgEx:.4}, var:{self.varEx:.4}, std:{self.stdEx:.4} sum:{self.summationEx}');
		# Only Cyan Exact Hit PDF: Normal Distribution
		# avg:Average , var:Variance ,std: Standard Deviation
		self.avgEX:float = sum([num[0]*num[1]/self.summationEX for num in zip(self.xAxis[106:195], self.yAxis[106:195])]);
		self.varEX:float = sum([(num[1] / self.summationEX) * ((num[0] - self.avgEX) ** 2) for num in zip(self.xAxis[106:195], self.yAxis[106:195])]);
		self.stdEX:float = self.varEX ** 0.5;
		print(f'cyan Exact: avg:{self.avgEX:.4}, var:{self.varEX:.4}, std:{self.stdEX:.4} sum:{self.summationEX}');

	def LoadHitMap(self,limit:int) -> None:
		for record in (self.sqlData if limit == 0 else self.sqlData[0:limit]):
			for hitS in record[0].split("|"):
				# init
				hitF:float = float(hitS);
				hitFAbs:float = abs(hitF);
				hitI:int = int(hitF) - 1 if hitF < 0 else int(hitF);
				# add Summations
				if hitFAbs < 45:
					self.summationEX += 1;
				if hitFAbs < 90:
					self.summationEx += 1;
				self.summation += 1;
				# Add SYNC.Rate list
				# CyanExact, (-5, +5) ms
				if hitFAbs < 5:
					self.Accurate_Sync_Rate[0] += 1;
				# CyanExact, (-10, -5] & [+5, +10) ms
				elif hitFAbs < 10:
					self.Accurate_Sync_Rate[1] += 1;
				# CyanExact, (-20, -10] & [+10, +20) ms
				elif hitFAbs < 20:
					self.Accurate_Sync_Rate[2] += 1;
				# CyanExact, (-45, -20] & [+20, +45) ms
				elif hitFAbs < 45:
					self.Accurate_Sync_Rate[3] += 1;
				# BlueExact, (-90, -45] & [+45, +90) ms
				elif hitFAbs < 90:
					self.Accurate_Sync_Rate[4] += 1;
				# Great, (-150, -90] & [+90, +150) ms
				elif hitFAbs < 150:
					self.Accurate_Sync_Rate[5] += 1;
				# Right, [+150, +250) ms
				elif hitFAbs < 250:
					self.Accurate_Sync_Rate[6] += 1;
				# Miss, [+250, +∞) ms
				else:
					self.Accurate_Sync_Rate[7] += 1;
				# add yAxis list
				if hitI < 250:
					self.yAxis[150 + hitI] += 1;
				else:
					self.yAxis[400] += 1;

	def Show(self) -> None:
		# init Figure
		fig:Figure = matplotlib.pyplot.figure(f"HitAnalyze (Total:{self.summation},"\
			f"  CyanEx:{sum(self.Accurate_Sync_Rate[0:4])},"\
			f"  BlueEx:{self.Accurate_Sync_Rate[5]},"\
			f"  Great:{self.Accurate_Sync_Rate[6]},"\
			f"  Right:{self.Accurate_Sync_Rate[7]},"\
			f"  Miss:{self.Accurate_Sync_Rate[8]})",
				  figsize=(16.0, 9.0));
		fig.clear();
		# init plot config
		matplotlib.pyplot.rcParams["font.serif"] = ["LXGW WenKai Mono"];
		matplotlib.pyplot.rcParams["font.sans-serif"] = ["LXGW WenKai Mono"]
		grid:GridSpec = GridSpec(3, 5, left=0.045, right=1, top=1, bottom=0.06, wspace=0, hspace=0);
		# create Bar Chart Axes
		BarAxes:Axes = fig.add_subplot(grid[:,:]);
		self.BarChart(BarAxes);
		if self.config['EnableDonutChartinAllHitAnalyze']:
			# create Ring Chart Axes
			RingAxes:Axes = fig.add_subplot(grid[0:2,3:]);
			RingAxes.add_patch(matplotlib.patches.Rectangle((-1.5, -1.5), 3, 3, color="white"));
			self.RingChart(RingAxes);
		# Show Plots
		matplotlib.plt.show();

	def BarChart(self, axes:Axes) -> None:
		# f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}
		# define PDF functions
		def PDF(x:int) -> float:
			return (E ** (((x - self.avg) ** 2) / (-2 * self.std ** 2))) / (((2 * PI) ** 0.5) * self.std) * self.summation;
		def PDFEx(x:int) -> float:
			return (E ** (((x - self.avgEx) ** 2) / (-2 * self.stdEx ** 2))) / (((2 * PI) ** 0.5) * self.stdEx) * self.summationEx;
		def PDFEX(x:int) -> float:
			return (E ** (((x - self.avgEX) ** 2) / (-2 * self.stdEX ** 2))) / (((2 * PI) ** 0.5) * self.stdEX) * self.summationEX;
		# init chart argument
		colors:list[str] = ['red','orange','yellow','green','cyan','blue','purple'];
		horizontalLines:list[list[int]] = list(list(int));
		yAxisMax:int = max(self.yAxis);
		yAxisMaxS:str = "%d"%yAxisMax;
		yAxisUpperLimit:int = 10 ** len(yAxisMaxS);
		yAxisLowerLimit:int = yAxisUpperLimit // 100;

		# yAxisMax = 190, yAxisUpperLimit = 1000, yAxisLowerLimit = 10
		# HorizontalLines = [2.5, 5, 7.5]
		# HorizontalLines = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
		if yAxisMax < yAxisUpperLimit / 5: # 20% UpperLimit
			for y in range(yAxisUpperLimit // 400, yAxisLowerLimit, yAxisUpperLimit // 400):
				horizontalLines.append([y] * 401);
			for y in range(yAxisLowerLimit, yAxisLowerLimit * (int(yAxisMaxS[0:2]) + 2), yAxisLowerLimit):
				horizontalLines.append([y] * 401);


	def RingChart(self, axes:Axes) -> None:
		pass

if __name__ == '__main__':
	AllHitAnalyze().Show()
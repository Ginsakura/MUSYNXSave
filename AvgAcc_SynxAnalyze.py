import logging

from matplotlib import pyplot as plot
from matplotlib.pyplot import MultipleLocator
from Resources import Logger

def Analyze() -> None:
	__logger:logging.Logger = Logger.GetLogger("AvgAcc_SynxAnalyze.Analyze")
	acc=list()
	sync=list()
	try:
		with open('./musync_data/Acc-Sync.json') as f:
			rows = [line.strip().split(',') for line in f]
	except FileNotFoundError:
		__logger.error("Acc-Sync.json not found")
		return
	for row in rows:
		try:
			acc.append(float(row[0]))
			sync.append(float(row[1]))
		except (ValueError, IndexError):
			__logger.exception("Failed to parse row")
			continue

	if not acc or not sync:
		__logger.error("No valid data found in Acc-Sync.json")
		return

	fig = plot.figure('AvgAcc与SYNC.Rate散点图', figsize=(10, 10))
	fig.clear()
	# print(acc,sync)

	fig.subplots_adjust(**{"left":0.06,"bottom":0.05,"right":0.998,"top":0.994})
	ax = fig.add_subplot()

	y_step = max(int((max(sync) - min(sync)) // 15), 1)
	x_step = max(int((max(acc) - min(acc)) // 10), 1)
	ax.yaxis.set_major_locator(MultipleLocator(y_step))
	ax.xaxis.set_major_locator(MultipleLocator(x_step))

	ax.set_xlim(int(min(acc))-1,int(max(acc))+1)
	ax.set_ylim(int(min(sync))-1,125)

	# 画线和标注
	xLineDict: dict[str, tuple[float, str]] = {
		'Max'		: (125,	'red'),
		'BlackEx'	: (122,	'black'),
		'RedEx'		: (120,	'red'),
		'CyanEx'	: (117,	'cyan'),
		'S'			: (110,	'blue'),
		'A'			: (95,	'green'),
		'B'			: (75,	'orange'),
	}
	for label, (syncLine, color) in xLineDict.items():
		if syncLine == 125:
			ax.plot([0, int(max(acc))+3], [syncLine] * 2, linestyle="-", alpha=1, linewidth=1.5, color=color)
		else:
			ax.plot([0, int(max(acc))+3], [syncLine] * 2, linestyle='--', alpha=0.7, linewidth=1.2, color=color)
		ax.text(int(max(acc)) - 5, syncLine - 0.4, label, ha='center', va='top', fontsize=8, alpha=0.7)

	# 每5ms画一条竖线
	for accLine in range(0, int(max(acc)), 5):
		if accLine == 0:
			ax.plot([accLine] * 2, [int(min(sync))-3, 125], linestyle='-', alpha=1, linewidth=1.5)
		else:
			ax.plot([accLine] * 2, [int(min(sync))-3, 125], linestyle='--', alpha=0.6, linewidth=1)


	# ax.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[122]*((int(max(acc))+3)-(int(min(acc))-3)),linestyle='--',alpha=0.7,linewidth=1,color='black')
	# ax.text(int(max(acc))-5,122.5,'BlackEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	# ax.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[120]*((int(max(acc))+3)-(int(min(acc))-3)),linestyle='--',alpha=0.7,linewidth=1,color='red')
	# ax.text(int(max(acc))-5,120.5,'RedEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	# ax.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[117]*((int(max(acc))+3)-(int(min(acc))-3)),linestyle='--',alpha=0.7,linewidth=1,color='cyan')
	# ax.text(int(max(acc))-5,117.5,'CyanEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	# ax.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[110]*((int(max(acc))+3)-(int(min(acc))-3)),linestyle='--',alpha=0.7,linewidth=1,color='blue')
	# ax.text(int(max(acc))-5,110.5,'S',ha='center',va='top',fontsize=7.5,alpha=0.7)
	# ax.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[95]*((int(max(acc))+3)-(int(min(acc))-3)),linestyle='--',alpha=0.7,linewidth=1,color='green')
	# ax.text(int(max(acc))-5,95.5,'A',ha='center',va='top',fontsize=7.5,alpha=0.7)
	# ax.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[75]*((int(max(acc))+3)-(int(min(acc))-3)),linestyle='--',alpha=0.7,linewidth=1,color='orange')
	# ax.text(int(max(acc))-5,75.5,'B',ha='center',va='top',fontsize=7.5,alpha=0.7)



	ax.scatter(acc,sync,alpha=0.7,color='#8a68d0',s=5)
	# plt.plot(acc,sync,'o')
	ax.set_xlabel('AvgAcc (ms)')  # x_label
	ax.set_ylabel('SYNC.Rate (%)')  # y_label

	plot.show()

if __name__ == '__main__':
	Analyze()

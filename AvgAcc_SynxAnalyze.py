from matplotlib import pyplot as plt
from matplotlib.pyplot import MultipleLocator

def Analyze() -> None:
	acc=list()
	sync=list()
	with open('./musync_data/Acc-Sync.json') as f:
		rows = [line.strip().split(',') for line in f]
	for row in rows:
		try:
			acc.append(float(row[0]))
			sync.append(float(row[1]))
		except Exception as e:
			continue
	
	fig = plt.figure('AvgAcc与SYNC.Rate散点图', figsize=(10, 10))
	fig.clear()
	# print(acc,sync)
	
	fig.subplots_adjust(**{"left":0.06,"bottom":0.05,"right":0.998,"top":0.994})
	ax = fig.add_subplot()

	y_step = max((max(sync) - min(sync)) // 15, 1)
	x_step = max((max(acc) - min(acc)) // 10, 1)
	ax.yaxis.set_major_locator(MultipleLocator(y_step))
	ax.xaxis.set_major_locator(MultipleLocator(x_step))
	
	ax.set_xlim(int(min(acc))-1,int(max(acc))+1)
	ax.set_ylim(int(min(sync))-1,int(max(sync))+1)
	
	ax.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[122 for i in range(int(min(acc))-3,int(max(acc))+3)],linestyle='--',alpha=0.7,linewidth=1,color='black')
	ax.text(int(max(acc))-5,122.5,'BlackEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	ax.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[120 for i in range(int(min(acc))-3,int(max(acc))+3)],linestyle='--',alpha=0.7,linewidth=1,color='red')
	ax.text(int(max(acc))-5,120.5,'RedEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	ax.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[117 for i in range(int(min(acc))-3,int(max(acc))+3)],linestyle='--',alpha=0.7,linewidth=1,color='cyan')
	ax.text(int(max(acc))-5,117.5,'CyanEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	ax.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[110 for i in range(int(min(acc))-3,int(max(acc))+3)],linestyle='--',alpha=0.7,linewidth=1,color='blue')
	ax.text(int(max(acc))-5,110.5,'S',ha='center',va='top',fontsize=7.5,alpha=0.7)
	ax.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[95 for i in range(int(min(acc))-3,int(max(acc))+3)],linestyle='--',alpha=0.7,linewidth=1,color='green')
	ax.text(int(max(acc))-5,95.5,'A',ha='center',va='top',fontsize=7.5,alpha=0.7)
	ax.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[75 for i in range(int(min(acc))-3,int(max(acc))+3)],linestyle='--',alpha=0.7,linewidth=1,color='orange')
	ax.text(int(max(acc))-5,75.5,'B',ha='center',va='top',fontsize=7.5,alpha=0.7)
	
	ax.scatter(acc,sync,alpha=0.7,color='#8a68d0',s=5)
	# plt.plot(acc,sync,'o')
	ax.set_xlabel('AvgAcc (ms)'); #x_label
	ax.set_ylabel('SYNC.Rate (%)'); #y_label
	
	plt.show()

if __name__ == '__main__':
	Analyze();
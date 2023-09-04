from matplotlib import pyplot as plt
from matplotlib.pyplot import MultipleLocator

def Analyze():
	acc=list()
	sync=list()
	with open('./musync_data/Acc-Sync.json') as f:
		data=f.readlines()
	for ids in range(len(data)):
		data.append(data.pop(0).split(','))
	for ids in data:
		acc.append(float(ids[0]))
		sync.append(float(ids[1]))
	
	fig = plt.figure('AvgAcc与SYNC.Rate散点图', figsize=(10, 10))
	# print(acc,sync)
	
	fig.subplots_adjust(**{"left":0.06,"bottom":0.05,"right":0.998,"top":0.994})
	plt.gca().yaxis.set_major_locator(MultipleLocator((max(sync)-min(sync))//15))
	plt.gca().xaxis.set_major_locator(MultipleLocator((max(acc)-min(acc))//10))
	plt.xlim(int(min(acc))-1,int(max(acc))+1)
	plt.ylim(int(min(sync))-1,int(max(sync))+1)
	
	plt.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[122 for i in range(int(min(acc))-3,int(max(acc))+3)],linestyle='--',alpha=0.7,linewidth=1,color='black')
	plt.text(int(max(acc))-5,122.5,'BlackEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	plt.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[120 for i in range(int(min(acc))-3,int(max(acc))+3)],linestyle='--',alpha=0.7,linewidth=1,color='red')
	plt.text(int(max(acc))-5,120.5,'RedEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	plt.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[117 for i in range(int(min(acc))-3,int(max(acc))+3)],linestyle='--',alpha=0.7,linewidth=1,color='cyan')
	plt.text(int(max(acc))-5,117.5,'CyanEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	plt.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[110 for i in range(int(min(acc))-3,int(max(acc))+3)],linestyle='--',alpha=0.7,linewidth=1,color='blue')
	plt.text(int(max(acc))-5,110.5,'S',ha='center',va='top',fontsize=7.5,alpha=0.7)
	plt.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[95 for i in range(int(min(acc))-3,int(max(acc))+3)],linestyle='--',alpha=0.7,linewidth=1,color='green')
	plt.text(int(max(acc))-5,95.5,'A',ha='center',va='top',fontsize=7.5,alpha=0.7)
	plt.plot([i for i in range(int(min(acc))-3,int(max(acc))+3)],[75 for i in range(int(min(acc))-3,int(max(acc))+3)],linestyle='--',alpha=0.7,linewidth=1,color='orange')
	plt.text(int(max(acc))-5,75.5,'B',ha='center',va='top',fontsize=7.5,alpha=0.7)
	
	plt.scatter(acc,sync,alpha=0.7,color='#8a68d0',s=5)
	# plt.plot(acc,sync,'o')
	plt.xlabel('AvgAcc') #x_label
	plt.ylabel('SYNC.Rate')#y_label
	
	plt.show()

if __name__ == '__main__':
	Analyze()
import json
import matplotlib.pyplot as plt

from matplotlib.pyplot import MultipleLocator

def Analyze():
	diff = [[],[]]
	score = [[],[]]
	diffSocre = [dict(),dict()]
	for ids in range(1,16):
		diffSocre[0]['%02d'%ids] = []
		diffSocre[1]['%02d'%ids] = []
	# print(diffSocre)

	with open('./musync_data/SavAnalyze.json','r',encoding='utf8') as file:
		data = json.load(file)
	for ids in data["SaveData"]:
		if float(ids["SyncNumber"][:-1]) != 0:
			diffcute = int(ids["SongName"][3])
			if ids["SongName"][1]=="4Key":
				diff[0].append(diffcute-0.15)
				score[0].append(float(ids["SyncNumber"][:-1]))
				diffSocre[0]['%02d'%diffcute] += [float(ids["SyncNumber"][:-1])]
			else: # 6Key Mode
				diff[1].append(diffcute+0.15)
				score[1].append(float(ids["SyncNumber"][:-1]))
				diffSocre[1]['%02d'%diffcute] += [float(ids["SyncNumber"][:-1])]
	# print(diffSocre)

	diffSocreTrim = [dict(),dict()]
	for ids in range(0,2):
		for idx in diffSocre[ids].keys():
			if len(diffSocre[ids][idx]) != 0:
				diffSocreTrim[ids][idx] = [round(sum(diffSocre[ids][idx])/len(diffSocre[ids][idx]),3),len(diffSocre[ids][idx])]
			# else:
			# 	diffSocre.pop(ids, None)
	# print(diffSocreTrim)
	
	fig = plt.figure('难度与分数散点图', figsize=(7, 8))
	fig.clear()
	fig.subplots_adjust(**{"left":0.083,"bottom":0.07,"right":0.60,"top":0.994})
	ax = fig.add_subplot()
	axR = ax.twinx()
	ax.yaxis.set_major_locator(MultipleLocator(1))
	axR.yaxis.set_major_locator(MultipleLocator(1))
	ax.xaxis.set_major_locator(MultipleLocator(1))
	ax.set_xlim(0,16)
	min0 = 125 if len(score[0]) == 0 else min(score[0])
	min1 = 125 if len(score[1]) == 0 else min(score[1])
	minScore = int(min([min0,min1]))
	ax.set_ylim(minScore-1,125)
	axR.set_ylim(minScore-1,125)

	labels = []
	for ids in diffSocreTrim[0].keys():
		labels.append(f"难度: 4K {ids} Avg:{'%.3f'%diffSocreTrim[0][ids][0]:0>7s}% 计数:{diffSocreTrim[0][ids][1]:0=2d}")
	labels.append("")
	for ids in diffSocreTrim[1].keys():
		labels.append(f"难度: 6K {ids} Avg:{'%.3f'%diffSocreTrim[1][ids][0]:0>7s}% 计数:{diffSocreTrim[1][ids][1]:0=2d}")
	print("\n".join(labels))

	for ids in range(1,16):
		ax.plot([ids]*(125-minScore+2),[ids for ids in range(minScore-1,126)],linestyle='--',alpha=0.6,linewidth=1)
	# diffSocreTrim:[{'diff':[avg,count]}, {'diff':[avg,count]}]
	# [4K, 6K]
	for ids in range(0,2): #ids <= [4K, 6K]
		for idx in diffSocreTrim[ids].keys(): #idx <= diff
			ax.plot([i for i in range(int(idx)+1)] if ids else [i for i in range(int(idx),17)], # '6k=>' if ids else '<=4K'
				[diffSocreTrim[ids][idx][0]]*(int(idx)+1) if ids else [diffSocreTrim[ids][idx][0]]*(17-int(idx)), # '6k=>' if ids else '<=4K'
				linestyle='--',alpha=1,linewidth=1)

	if minScore < 122:
		ax.plot([i for i in range(17)],[122]*17,linestyle='-',alpha=0.7,linewidth=1,color='black')
		ax.text(14.5,122.5,'BlackEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	if minScore < 120:
		ax.plot([i for i in range(17)],[120]*17,linestyle='-',alpha=0.7,linewidth=1,color='red')
		ax.text(14.5,120.5,'RedEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	if minScore < 117:
		ax.plot([i for i in range(17)],[117]*17,linestyle='-',alpha=0.7,linewidth=1,color='cyan')
		ax.text(14.5,117.5,'CyanEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	if minScore < 110:
		ax.plot([i for i in range(17)],[110]*17,linestyle='-',alpha=0.7,linewidth=1,color='blue')
		ax.text(14.5,110.5,'S',ha='center',va='top',fontsize=7.5,alpha=0.7)
	if minScore < 95:
		ax.plot([i for i in range(17)],[95]*17,linestyle='-',alpha=0.7,linewidth=1,color='green')
		ax.text(14.5,95.5,'A',ha='center',va='top',fontsize=7.5,alpha=0.7)
	if minScore < 75:
		ax.plot([i for i in range(17)],[75]*17,linestyle='-',alpha=0.7,linewidth=1,color='orange')
		ax.text(14.5,75.5,'B',ha='center',va='top',fontsize=7.5,alpha=0.7)

	# supported values are '-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted'
	ax.plot([int(i) for i in diffSocreTrim[0].keys()],[diffSocreTrim[0][ids][0] for ids in diffSocreTrim[0].keys()],
		linestyle='-',color='orange',marker="D",markerfacecolor="Blue",alpha=0.7,linewidth=2, 
		label="4Key Mode")
	ax.plot([int(i) for i in diffSocreTrim[1].keys()],[diffSocreTrim[1][ids][0] for ids in diffSocreTrim[1].keys()],
		linestyle='-',color='orange',marker="D",markerfacecolor="Red",alpha=0.7,linewidth=2, 
		label="6Key Mode")

	ax.scatter(diff[0],score[0],alpha=0.7,color='#8A68D0',s=5)
	ax.scatter(diff[1],score[1],alpha=0.7,color='#F83535',s=5)
	ax.text(18,123,"\n".join(labels),ha="left",va="top",alpha=1,
		fontdict={'family':'LXGW WenKai Mono','weight':'normal','size':10})
	ax.legend(prop={'family':'LXGW WenKai Mono','weight':'normal','size':10},framealpha=0.4)  #show label
	ax.set_xlabel('Difficulty') #x_label
	ax.set_ylabel('SYNC.Rate')#y_label
	
	plt.show()

if __name__ == '__main__':
	Analyze()
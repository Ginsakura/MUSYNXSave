import json

from matplotlib import pyplot as plt
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
				diff[0].append(diffcute)
				score[0].append(float(ids["SyncNumber"][:-1]))
				diffSocre[0]['%02d'%diffcute] += [float(ids["SyncNumber"][:-1])]
			else: # 6Key Mode
				diff[1].append(diffcute+0.3)
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
	
	fig = plt.figure('难度与分数散点图', figsize=(6, 8))
	fig.subplots_adjust(**{"left":0.071,"bottom":0.07,"right":0.59,"top":0.994})
	plt.gca().yaxis.set_major_locator(MultipleLocator(1))
	plt.gca().xaxis.set_major_locator(MultipleLocator(1))
	plt.xlim(0,16)
	minScore = int(min([min(score[0]),min(score[1])]))
	plt.ylim(minScore-1,125)
	# print(minScore)

	# colors = ['#880000','#008800','#000088','#888800','#880088','#008888','#888888',
	# 	'#FF8888','#88FF88','#8888FF','#CCCC44','#FF88FF','#88FFFF','#000000','#444444']
	# for ids in diffSocreTrim:
	# 	plt.plot([i for i in range(17)],[diffSocre[ids][0]]*17,linestyle='--',alpha=0.7,linewidth=1,color=colors[(float(ids)*2)-1],
	# 		label='难度%s 均值:%.3f%%'%(ids,diffSocre[ids][0]))
	labels = []
	# hards = sorted(list(set(list(diffSocreTrim[0].keys())+list(diffSocreTrim[1].keys()))))
	# print(hards)
	for ids in diffSocreTrim[0].keys():
		# labels.append("4K %s Avg:%03.3f%% %03d"%(ids, diffSocreTrim[0][ids][0], diffSocreTrim[0][ids][1]))
		labels.append(f"难度: 4K {ids} Avg:{'%.3f'%diffSocreTrim[0][ids][0]:0>7s}% 计数:{diffSocreTrim[0][ids][1]:0=2d}")
	labels.append("")
	for ids in diffSocreTrim[1].keys():
		labels.append(f"难度: 6K {ids} Avg:{'%.3f'%diffSocreTrim[1][ids][0]:0>7s}% 计数:{diffSocreTrim[1][ids][1]:0=2d}")
	print("\n".join(labels))

	# for ids in range(0,2):
	# 	for idx in diffSocreTrim[ids].keys():
	# 		print('难度: %s %s\t平均值:%.3f%%\t计数:%d' % (("4K" if ids==0 else "6K"),
	# 			idx,diffSocreTrim[ids][idx][0],diffSocreTrim[ids][idx][1]))

	for ids in range(1,16):
		plt.plot([ids+0.15]*(125-minScore),[ids for ids in range(minScore,125)],linestyle='--',alpha=0.6,linewidth=1)
	for ids in range(0,2):
		for idx in diffSocreTrim[ids].keys():
			plt.plot([i for i in range(int(idx)+1)],[diffSocreTrim[ids][idx][0]]*(int(idx)+1),linestyle='--',alpha=1,linewidth=1)

	if minScore < 122:
		plt.plot([i for i in range(17)],[122]*17,linestyle='-',alpha=0.7,linewidth=1,color='black')
		plt.text(14.5,122.5,'BlackEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	if minScore < 120:
		plt.plot([i for i in range(17)],[120]*17,linestyle='-',alpha=0.7,linewidth=1,color='red')
		plt.text(14.5,120.5,'RedEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	if minScore < 117:
		plt.plot([i for i in range(17)],[117]*17,linestyle='-',alpha=0.7,linewidth=1,color='cyan')
		plt.text(14.5,117.5,'CyanEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	if minScore < 110:
		plt.plot([i for i in range(17)],[110]*17,linestyle='-',alpha=0.7,linewidth=1,color='blue')
		plt.text(14.5,110.5,'S',ha='center',va='top',fontsize=7.5,alpha=0.7)
	if minScore < 95:
		plt.plot([i for i in range(17)],[95]*17,linestyle='-',alpha=0.7,linewidth=1,color='green')
		plt.text(14.5,95.5,'A',ha='center',va='top',fontsize=7.5,alpha=0.7)
	if minScore < 75:
		plt.plot([i for i in range(17)],[75]*17,linestyle='-',alpha=0.7,linewidth=1,color='orange')
		plt.text(14.5,75.5,'B',ha='center',va='top',fontsize=7.5,alpha=0.7)

	# supported values are '-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted'
	plt.plot([int(i) for i in diffSocreTrim[0].keys()],[diffSocreTrim[0][ids][0] for ids in diffSocreTrim[0].keys()],
		linestyle='-',color='orange',marker="D",markerfacecolor="Blue",alpha=0.7,linewidth=2, 
		label="4Key Mode")
	plt.plot([int(i)+0.3 for i in diffSocreTrim[1].keys()],[diffSocreTrim[1][ids][0] for ids in diffSocreTrim[1].keys()],
		linestyle='-',color='orange',marker="D",markerfacecolor="Red",alpha=0.7,linewidth=2, 
		label="6Key Mode")

	plt.scatter(diff[0],score[0],alpha=0.7,color='#8A68D0',s=5)
	plt.scatter(diff[1],score[1],alpha=0.7,color='#F83535',s=5)
	plt.text(16.5,123,"\n".join(labels),ha="left",va="top",alpha=1,
		fontdict={'family':'LXGW WenKai Mono','weight':'normal','size':10})
	plt.legend(prop={'family':'LXGW WenKai Mono','weight':'normal','size':10},framealpha=0.4)  #显示上面的label
	plt.xlabel('Difficulty') #x_label
	plt.ylabel('SYNC.Rate')#y_label
	
	plt.show()

if __name__ == '__main__':
	Analyze()
from matplotlib import pyplot as plt
from matplotlib.pyplot import MultipleLocator
import json

def Analyze():
	diff=list()
	score=list()
	diff_score = dict()
	for ids in range(1,16):
		diff_score['%02d'%ids] = []
	with open('./musync_data/SavAnalyze.json','r',encoding='utf8') as file:
		data = json.load(file)
	for ids in data["SaveData"]:
		if float(ids["SyncNumber"][:-1]) != 0:
			diff.append(int(ids["SongName"][3]))
			score.append(float(ids["SyncNumber"][:-1]))
			diff_score[ids["SongName"][3]] += [float(ids["SyncNumber"][:-1])]
	
	for ids in range(1,16):
		data = diff_score['%02d'%ids]
		if len(data) != 0:
			diff_score['%02d'%ids] = [round(sum(data)/len(data),3),len(data)]
		else:
			diff_score.pop('%02d'%ids, None)
	
	fig = plt.figure('难度与分数散点图', figsize=(5, 7))
	fig.subplots_adjust(**{"left":0.12,"bottom":0.07,"right":0.998,"top":0.994})
	plt.gca().yaxis.set_major_locator(MultipleLocator(1))
	plt.gca().xaxis.set_major_locator(MultipleLocator(1))
	plt.xlim(0,16)
	plt.ylim(int(min(score))-1,125)

	colors = ['#880000','#008800','#000088','#888800','#880088','#008888','#888888',
		'#FF8888','#88FF88','#8888FF','#CCCC44','#FF88FF','#88FFFF','#000000','#444444']
	for ids in diff_score:
		plt.plot([i for i in range(17)],[diff_score[ids][0]]*17,linestyle='--',alpha=0.7,linewidth=1,color=colors[int(ids)-1],
			label='难度%s 均值:%.3f%%'%(ids,diff_score[ids][0]))

	for ids in diff_score:
		print('难度: %s\t平均值:%.3f%%\t计数:%d'%(ids,diff_score[ids][0],diff_score[ids][1]))


	plt.plot([i for i in range(17)],[122]*17,linestyle='-',alpha=0.7,linewidth=1,color='black')
	plt.text(14.5,122.5,'BlackEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	plt.plot([i for i in range(17)],[120]*17,linestyle='-',alpha=0.7,linewidth=1,color='red')
	plt.text(14.5,120.5,'RedEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	plt.plot([i for i in range(17)],[117]*17,linestyle='-',alpha=0.7,linewidth=1,color='cyan')
	plt.text(14.5,117.5,'CyanEx',ha='center',va='top',fontsize=7.5,alpha=0.7)
	plt.plot([i for i in range(17)],[110]*17,linestyle='-',alpha=0.7,linewidth=1,color='blue')
	plt.text(14.5,110.5,'S',ha='center',va='top',fontsize=7.5,alpha=0.7)
	plt.plot([i for i in range(17)],[95]*17,linestyle='-',alpha=0.7,linewidth=1,color='green')
	plt.text(14.5,95.5,'A',ha='center',va='top',fontsize=7.5,alpha=0.7)
	plt.plot([i for i in range(17)],[75]*17,linestyle='-',alpha=0.7,linewidth=1,color='orange')
	plt.text(14.5,75.5,'B',ha='center',va='top',fontsize=7.5,alpha=0.7)

	plt.scatter(diff,score,alpha=0.7,color='#8a68d0',s=5)
	# plt.plot(diff,score,'o')
	plt.legend(prop={'family':'LXGW WenKai Mono','weight':'normal','size':10},framealpha=0.4)  #显示上面的label
	plt.xlabel('Difficulty') #x_label
	plt.ylabel('SYNC.Rate')#y_label
	
	plt.show()

if __name__ == '__main__':
	Analyze()
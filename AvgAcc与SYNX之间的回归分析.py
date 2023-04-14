from matplotlib import pyplot as plt
from matplotlib.pyplot import MultipleLocator

acc=list()
sync=list()
with open('./musync_data/Acc-Sync.json') as f:
	data=f.readlines()
for ids in range(len(data)):
	data.append(data.pop(0).split(','))
for ids in data:
	acc.append(float(ids[0]))
	sync.append(float(ids[1]))

fig = plt.figure('AvgAcc与SYNC.Rate之间的回归分析')
# print(acc,sync)

plt.gca().yaxis.set_major_locator(MultipleLocator((max(sync)-min(sync))/15))
plt.gca().xaxis.set_major_locator(MultipleLocator((max(acc)-min(acc))/10))
plt.xlim(min(acc)-2,max(acc)+2)
plt.ylim(min(sync)-2,max(sync)+2)

plt.scatter(acc,sync,alpha=0.7,color='#8a68d0')
# plt.plot(acc,sync,'o')
plt.show()

import matplotlib.pyplot as plt
import re

class DrawHDLine(object):
	"""docstring for DrawHDLine"""
	def __init__(self):
		super(DrawHDLine, self).__init__()
		self.filePath = './musync_data/HitDelay.log'
		with open(self.filePath,'r',encoding='utf8') as f:
			self.data = f.read().split('\n')
		p = self.GetIndex()
		self.x_axis = [i for i in range(1,len(self.data)-p)]
		self.zero_axis = [0 for i in range(p,len(self.data)-1)]
		self.EXTRAa = [45 for i in range(p,len(self.data)-1)]
		self.EXTRAb = [-45 for i in range(p,len(self.data)-1)]
		self.Extraa = [90 for i in range(p,len(self.data)-1)]
		self.Extrab = [-90 for i in range(p,len(self.data)-1)]
		self.Greata = [150 for i in range(p,len(self.data)-1)]
		self.Greatb = [-150 for i in range(p,len(self.data)-1)]
		self.pos = p
		self.y_axis = list()
		for i in range(p,len(self.data)-1):
			# print(self.data[i])
			self.y_axis.append(float(self.data[i][13:-2]))
		# print(self.x_axis,self.y_axis)
		self.allKeys = len(self.y_axis)
		self.avgDelay = sum(self.y_axis)/self.allKeys
		self.avgAcc = sum([abs(i) for i in self.y_axis])/self.allKeys
		self.fig = plt.figure(f'AvgDelay: {"%.4fms"%self.avgDelay}    AllKeys: {self.allKeys}    AvgAcc: {"%.4fms"%self.avgAcc}',figsize=(9, 4))
		print(f'AvgDelay: {self.avgDelay}')
		print(f'AllKeys: {self.allKeys}')
		print(f'AvgAcc: {self.avgAcc}')
		self.Label()
		self.Draw()
		plt.show()

	def GetIndex(self):
		b=list()
		for index, value in enumerate(self.data):
		    if value == '> Game Start!':
		        b.append(index)
		return (b[-1]+1)

	def Label(self):
		plt.text(0,70,"Slower↑", ha='right',fontsize=10,color='#c22472')
		plt.text(0,-70,"Faster↓", ha='right',fontsize=10,color='#288328')
		for x,y in zip(self.x_axis,self.y_axis):
			if y<0:
				plt.text(x,y-3,'%.0fms'%y,ha='center',va='top',fontsize=7.5,alpha=0.7)
			else:
				plt.text(x,y+3,'%.0fms'%y,ha='center',va='bottom',fontsize=7.5,alpha=0.7)


	def Draw(self):
		self.fig.subplots_adjust(**{"left":0.04,"bottom":0.05,"right":1,"top":1})
		plt.plot(self.x_axis,self.zero_axis,linestyle='-',alpha=1,linewidth=1,color='red',label='0ms')
		plt.plot(self.x_axis,self.EXTRAa,linestyle='--',alpha=0.7,linewidth=1,color='cyan',label='Cyan Extra(±45ms)')
		plt.plot(self.x_axis,self.EXTRAb,linestyle='--',alpha=0.7,linewidth=1,color='cyan')
		plt.plot(self.x_axis,self.Extraa,linestyle='--',alpha=0.7,linewidth=1,color='blue',label='Blue Extra(±90ms)')
		plt.plot(self.x_axis,self.Extrab,linestyle='--',alpha=0.7,linewidth=1,color='blue')
		plt.plot(self.x_axis,self.Greata,linestyle='--',alpha=0.7,linewidth=1,color='green',label='Great(±150ms)')
		plt.plot(self.x_axis,self.Greatb,linestyle='--',alpha=0.7,linewidth=1,color='green')
		plt.plot(self.x_axis,self.y_axis,linestyle='-',alpha=0.7,linewidth=1,color='#8a68d0',label='HitDelay(ms)',marker='.'
         ,markeredgecolor='#c4245c',markersize='3')
		plt.legend()  #显示上面的label
		plt.xlabel('HitCount') #x_label
		plt.ylabel('Delay')#y_label

if __name__ == '__main__':
	DrawHDLine()
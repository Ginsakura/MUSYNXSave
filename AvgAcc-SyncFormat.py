import os
import sqlite3 as sql

## Global Argument ##
acc_sync = dict() #{acc:[sync,EX,Ex,Gt,Rt,Ms]}
db = sql.connect('./musync_data/HitDelayHistory.db')
cur = db.cursor()

def ReadData():
	with open('./musync_data/Acc-Sync.json','r') as f:
		data=f.readlines()
	for ids in range(len(data)):
		data.append(data.pop(0).split(',')) #[acc,sync]
	for ids in data:
		acc_sync[float(ids[0])] = [float(ids[1])] #{acc:sync}

def SQLSelect():
	data = cur.execute("select * from HitDelayHistory")
	data = data.fetchall()
	for ids in data:
		DataFormat(ids)


def DataFormat(data):
	acc = round(data[3],4)
	if acc in acc_sync:
		dataList = [float(i) for i in data[4].split("|")]
		sumn = [0,0,0,0,0]
		for ids in dataList:
			ids = abs(ids)
			if ids < 45: sumn[0] += 1
			elif ids < 90: sumn[1] += 1
			elif ids < 150: sumn[2] += 1
			elif ids < 250: sumn[3] += 1
			else: sumn[4] += 1
		acc_sync[acc] = acc_sync[acc] + sumn

def WriteData():
	with open('./musync_data/Acc-SyncFormat.txt','w') as f:
		for ids in acc_sync:
			if len(acc_sync[ids]) == 6:
				dataStr = f"{ids},{acc_sync[ids][0]},{acc_sync[ids][1]},{acc_sync[ids][2]},{acc_sync[ids][3]},{acc_sync[ids][4]},{acc_sync[ids][5]}"
			else:
				dataStr = f"{ids},{acc_sync[ids]}"
			print(dataStr)
			f.write(dataStr+"\n")

if __name__ == '__main__':
	ReadData()
	SQLSelect()
	WriteData()
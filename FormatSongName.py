import json
import os

def Format():
	if not os.path.isfile('./musync_data/songname.json'):
		f = open('./musync_data/songname.json','w',encoding='utf8')
		f.write('{}')
		f.close()
	with open('./musync_data/songname.json','r',encoding='utf8') as f:
		d = json.load(f)
	for ids in range(15,1344):
		if not f'{ids}' in d:
			d[f'{ids}'] = None
	with open('./musync_data/songname.json','w',encoding='utf8') as f:
		json.dump(d,f,ensure_ascii=False)

def Sort():
	with open('./musync_data/songname.json','r',encoding='utf8') as f:
		songJson = json.load(f)
	songListSorted = sorted(songJson.items(), key=lambda item:item[0])
	songJsonSorted = dict(songListSorted)
	print(songJsonSorted)
	with open('./musync_data/songname.json','w',encoding='utf8') as f:
		json.dump(songJsonSorted,f,ensure_ascii=False)

def SwichLittle2Big():
	with open('./musync_data/songname.json','r',encoding='utf8') as f:
		d = json.load(f)
	k = list(d.keys())
	for ids in k:
		idx = ids[6:]+ids[4:6]+ids[2:4]+ids[0:2]
		d[idx] = d.pop(ids)
	with open('./musync_data/songname.json','w',encoding='utf8') as f:
		json.dump(d,f,indent="",ensure_ascii=False)

def main():
	jsonFile = open("./musync_data/SongName.json",'r',encoding='utf8')
	songName = json.load(jsonFile)
	jsonFile.close()
	with open("./musync_data/SavAnalyze.analyze",'r') as analyze:
		while True:
			line = analyze.readline()
			if not line:break
			songid = line[4:8].strip()
			speedStall = line[23:31]
			# print(songid,speedStall)
			if songid in songName:
				dictVue = songName[songid]
				songName[speedStall] = songName.pop(songid)
	with open("./musync_data/SongName.json",'w',encoding='utf8') as jsonFile:
		json.dump(songName,jsonFile,ensure_ascii=False)

def FormatSongName20230626(): #2023年6月26日
	with open("./musync_data/songname.json",'r',encoding='utf8') as f:
		data = json.load(f)
	for ids in data:
		data[ids] = data[ids]+[0]
	with open("./musync_data/SongName.json",'w',encoding='utf8') as f:
		json.dump(data, f, ensure_ascii=False)
		
if __name__ == '__main__':
	# Sort()
	# FormatSongName20230626()
	pass

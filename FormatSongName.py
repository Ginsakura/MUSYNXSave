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

if __name__ == '__main__':
	# Sort()
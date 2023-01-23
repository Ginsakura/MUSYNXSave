import json
import os

if not os.path.isfile('./songname.json'):
	f = open('./songname.json','w',encoding='utf8')
	f.write('{}')
	f.close()
with open('./songname.json','r',encoding='utf8') as f:
	d = json.load(f)
for ids in range(15,1344):
	if not f'{ids}' in d:
		d[f'{ids}'] = None
with open('./songname.json','w',encoding='utf8') as f:
	json.dump(d,f,indent="")
import json
import os

def GetSongName(SpeedStall):
	diffcute = ["Easy","Hard","Inferno"]
	if os.path.isfile("./SongName.json"):
		songNameFile = open("./SongName.json",'r',encoding='utf8')
		songNameJson = json.load(songNameFile)
		if f'{SpeedStall}' in songNameJson:
			data = songNameJson[f'{SpeedStall}']
			if data is None:return None
			songName = data[0]
			songKeys = ("4Key" if data[1]==4 else "6Key")
			songDifficulty = diffcute[int(data[2])]
			songDifficultyNumber = "%02d"%data[3]
			return [songName,songKeys,songDifficulty,songDifficultyNumber]
		else:
			return None
	else:
		return None

def main():
	jsonFile = open("./SongName.json",'r',encoding='utf8')
	songName = json.load(jsonFile)
	jsonFile.close()
	with open("./SavAnalyze.analyze",'r') as analyze:
		while True:
			line = analyze.readline()
			if not line:break
			songid = line[4:8].strip()
			speedStall = line[23:31]
			# print(songid,speedStall)
			if songid in songName:
				dictVue = songName[songid]
				songName[speedStall] = songName.pop(songid)
	with open("./SongName.json",'w',encoding='utf8') as jsonFile:
		json.dump(songName,jsonFile,indent="")

if __name__ == '__main__':
	main()
import ctypes
import json
import os
import sqlite3 as sql
import winreg

from win32 import win32gui, win32print
from win32.lib import win32con
from win32.win32api import GetSystemMetrics

import FileExport

def GetDpi():
	hDC = win32gui.GetDC(0)
	relw = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
	relh = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
	w = GetSystemMetrics (0)
	h = GetSystemMetrics (1)
	real_resolution = [relw,relh]
	screen_size = [w,h]
	return int(round(real_resolution[0] / screen_size[0], 2) * 100)

def ChangeConsoleStyle():
	# print('Changing Console Style...')
	with open('./musync_data/ExtraFunction.cfg','r',encoding='utf8') as cfg:
		cfg = json.load(cfg)
	execPath = cfg['MainExecPath']
	execPath = execPath.replace('/','_')+'musynx.exe'
	# print(execPath)
	regkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Console',reserved=0, access=winreg.KEY_WRITE)
	winreg.CreateKey(regkey,execPath)
	regkey.Close()
	regkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f'Console\\{execPath}',reserved=0, access=winreg.KEY_WRITE)
	winreg.SetValueEx(regkey,'CodePage',0,winreg.REG_DWORD,65001)
	winreg.SetValueEx(regkey,'WindowSize',0,winreg.REG_DWORD,262174)
	winreg.SetValueEx(regkey,'WindowAlpha',0,winreg.REG_DWORD,(cfg['ConsoleAlpha']*255//100))
	winreg.SetValueEx(regkey,'FaceName',0,winreg.REG_SZ,'霞鹜文楷等宽')
	winreg.SetValueEx(regkey,'FontSize',0,winreg.REG_DWORD,(cfg['ConsoleFontSize'] << 16))
	regkey.Close()

def CheckFileBeforeStarting(fonts):
	if os.path.exists('./musync/'):
		os.rename('./musync/','./musync_data/')
	if not os.path.exists('./musync_data/'):
		os.makedirs('./musync_data/')
	if not os.path.isfile('./musync_data/MUSYNC.ico'):
		FileExport.WriteIcon()
	if not os.path.isfile('./musync_data/ExtraFunction.cfg'):
		cfgData = "{\n\"EnableAcc-Sync\": true,\n\"DisableCheckUpdate\": false,\n\"EnableAnalyzeWhenStarting\": false,\n\"EnableDLLInjection\": true,\n\"SystemDPI\": 100,\n\"EnableDonutChartinHitDelay\": true,\n\"EnableDonutChartinAllHitAnalyze\": true,\n\"EnablePDFofCyanExact\": true,\n\"EnableNarrowDelayInterval\": true,\n\"ConsoleAlpha\": 75,\n\"ConsoleFont\": \"霞鹜文楷等宽\",\n\"ConsoleFontSize\": 36,\n\"MainExecPath\": \"\",\n\"ChangeConsoleStyle\": true,\n\"EnableFramelessWindow\": false,\n\"TransparentColor\": \"#FFFFFF\"\n}"
		with open('./musync_data/ExtraFunction.cfg','w',encoding='utf8') as cfg:
			cfg.write(cfgData)
		del cfgData
	if (not os.path.isfile('./musync_data/SongName.json')) or (not os.path.isfile('./musync_data/SongName.update')) or (FileExport.snjU > int(open('./musync_data/songname.update','r').read())):
		FileExport.WriteSongNameJson()
	if not os.path.isfile('./musync_data/ExtraFunction.cfg'):
		json.dump({"DisableCheckUpdate": False,"EnableDLLInjection": False},
			open('./musync_data/ExtraFunction.cfg','w'),indent="",ensure_ascii=False)
	if not '霞鹜文楷等宽' in fonts:
		if os.path.isfile('./musync_data/LXGW.ttf'):
			os.system(f'{os.getcwd()}/musync_data/LXGW.ttf')
		else:
			FileExport.WriteTTF()
			os.system(f'{os.getcwd()}/musync_data/LXGW.ttf')
	if not os.path.exists("./skin/"):
		os.makedirs('./skin/')
	if (not os.path.isfile('./musync_data/HitDelayHistory_v2.db')) and os.path.isfile('./musync_data/HitDelayHistory.db'):
		db = sql.connect('./musync_data/HitDelayHistory.db')
		cur = db.cursor()
		testData = cur.execute("SELECT * from HitDelayHistory limit 1")
		testData = testData.fetchone()
		# print(len(testData))
		if len(testData) != 6:
			print("记录数据迁移中...")
			ndb = sql.connect('./musync_data/HitDelayHistorytemp.db')
			ncur = ndb.cursor()
			ncur.execute("""CREATE table HitDelayHistory (
				SongMapName text Not Null,
				RecordTime text Not Null,
				AvgDelay float,
				AllKeys int,
				AvgAcc float,
				HitMap text,
				PRIMARY KEY ("SongMapName", "RecordTime"))""")
			for ids in cur.execute("SELECT * from HitDelayHistory").fetchall():
				nameAndTime = ids[0].split("-202")
				name = nameAndTime[0]
				recordTime = "202%s"%nameAndTime[1]
				avgDelay = ids[1]
				allKeys = ids[2]
				avgAcc = ids[3]
				dataList = ids[4]
				print("正在迁移%s  %s"%(name,recordTime))
				ncur.execute("INSERT into HitDelayHistory values(?,?,?,?,?,?)",(name,recordTime,avgDelay,allKeys,avgAcc,dataList))
			ndb.commit()
			ndb.close()
			db.close()
			# os.chdir()
			os.remove("./musync_data/HitDelayHistory.db")
			os.rename("./musync_data/HitDelayHistorytemp.db", "./musync_data/HitDelayHistory_v2.db")
		else:
			db.close()
			os.rename("./musync_data/HitDelayHistory.db", "./musync_data/HitDelayHistory_v2.db")
			print("记录数据无需迁移.")
			

def CheckConfig():
	try:
		with open('./musync_data/ExtraFunction.cfg','r',encoding='utf8') as cfg:
			cfg = json.load(cfg)
	except UnicodeDecodeError:
		with open('./musync_data/ExtraFunction.cfg','r',encoding='gbk') as cfg:
			cfg = json.load(cfg)
		json.dump(cfg,open('./musync_data/ExtraFunction.cfg','w',encoding='utf8'),indent="",ensure_ascii=False)
	except Exception as e:
		raise e
	with open('./musync_data/ExtraFunction.cfg','r',encoding='utf8') as cfg:
		cfg = json.load(cfg)
		isChange = False
	if 'EnableAcc-Sync' not in cfg:
		cfg['EnableAcc-Sync'] = False
		isChange = True
	if 'DisableCheckUpdate' not in cfg:
		cfg['DisableCheckUpdate'] = False
		isChange = True
	if 'EnableAnalyzeWhenStarting' not in cfg:
		cfg['EnableAnalyzeWhenStarting'] = False
		isChange = True
	if 'EnableDLLInjection' not in cfg:
		cfg['EnableDLLInjection'] = False
		isChange = True
	if 'EnableDonutChartinHitDelay' not in cfg:
		cfg['DonutChartinHitDelay'] = False
		isChange = True
	if 'EnableDonutChartinAllHitAnalyze' not in cfg:
		cfg['EnableDonutChartinAllHitAnalyze'] = False
		isChange = True
	if 'EnablePDFofCyanExact' not in cfg:
		cfg['EnablePDFofCyanExact'] = True
		isChange = True
	if 'EnableNarrowDelayInterval' not in cfg:
		cfg['EnableNarrowDelayInterval'] = True
		isChange = True
	if 'ConsoleAlpha' not in cfg:
		cfg['ConsoleAlpha'] = 75
		isChange = True
	if 'ConsoleFont' not in cfg:
		cfg['ConsoleFont'] = '霞鹜文楷等宽'
		isChange = True
	if 'ConsoleFontSize' not in cfg:
		cfg['ConsoleFontSize'] = 36
		isChange = True
	if 'MainExecPath' not in cfg:
		cfg['MainExecPath'] = ''
		isChange = True
	if 'ChangeConsoleStyle' not in cfg:
		cfg['ChangeConsoleStyle'] = False
		isChange = True
	if 'EnableFramelessWindow' not in cfg:
		cfg['EnableFramelessWindow'] = False
		isChange = True
	if 'TransparentColor' not in cfg:
		cfg['TransparentColor'] = "#FFFFFF"
		isChange = True
	dpi = ctypes.windll.shcore.GetScaleFactorForDevice(0) # GetDpi()
	if 'SystemDPI' not in cfg:
		cfg['SystemDPI'] = dpi
		isChange = True
	elif dpi != cfg['SystemDPI']:
		cfg['SystemDPI'] = dpi
		isChange = True
	if isChange:
		json.dump(cfg,open('./musync_data/ExtraFunction.cfg','w',encoding='utf8'),indent="",ensure_ascii=False)

if __name__ == '__main__':
	print(GetDpi())
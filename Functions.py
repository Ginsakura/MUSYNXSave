from win32 import win32gui, win32print
from win32.lib import win32con
from win32.win32api import GetSystemMetrics
import os
import json
import FileExport
import winreg

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
		cfg = json.load(cfg,encoding='utf8')
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
	if (not os.path.isfile('./musync_data/SongName.json')) or (FileExport.snjU != open('./musync_data/songname.update','r').read()):
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

def CheckConfig():
	try:
		with open('./musync_data/ExtraFunction.cfg','r',encoding='utf8') as cfg:
			cfg = json.load(cfg)
	except Exception as e:
		if type(e).__name__ == 'UnicodeDecodeError':
			with open('./musync_data/ExtraFunction.cfg','r',encoding='gbk') as cfg:
				cfg = json.load(cfg)
			json.dump(cfg,open('./musync_data/ExtraFunction.cfg','w',encoding='utf8'),indent="",ensure_ascii=False)
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
	if 'SystemDPI' not in cfg:
		cfg['SystemDPI'] = GetDpi()
		isChange = True
	if 'EnableDonutChartinHitDelay' not in cfg:
		cfg['DonutChartinHitDelay'] = False
		isChange = True
	if 'EnableDonutChartinAllHitAnalyze' not in cfg:
		cfg['EnableDonutChartinAllHitAnalyze'] = False
		isChange = True
	if 'EnablePDFofCyanExtra' not in cfg:
		cfg['EnablePDFofCyanExtra'] = False
		isChange = True
	if 'EnableNarrowDelayInterval' not in cfg:
		cfg['EnableNarrowDelayInterval'] = False
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
	if isChange:
		json.dump(cfg,open('./musync_data/ExtraFunction.cfg','w',encoding='utf8'),indent="",ensure_ascii=False)

if __name__ == '__main__':
	print(GetDpi())
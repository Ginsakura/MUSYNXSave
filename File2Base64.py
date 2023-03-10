from base64 import *
from os import path
import pyperclip

def EncodeIcon():
	with open("./musync_data/MUSYNC.ico", 'rb+') as icon:
		with open("./musync_data/icon.b64", 'wb+') as iconEncode:
			iconData = icon.read()
			iconEncode.write(b64encode(iconData))

def EncodeTTF():
	with open("./musync_data/LXGW.ttf", 'rb+') as ttf:
		with open("./musync_data/ttf.b64", 'wb+') as ttfEncode:
			ttfData = ttf.read()
			ttfEncode.write(b64encode(ttfData))

def EncodeJson():
	with open("./musync_data/songname.json", 'rb+') as snj:
		with open("./musync_data/songname.b64", 'wb+') as snjEncode:
			snjData = snj.read()
			b64e = b64encode(snjData)
			snjEncode.write(b64e)
			pyperclip.copy(b64e.decode('utf8'))

if __name__ == '__main__':
	if not path.isfile("./musync_data/ttf.b64"):
		EncodeTTF()
	if not path.isfile('./musync_data/icon.b64'):
		EncodeIcon()
	EncodeJson()
from base64 import *

def EncodeIcon():
	with open("./musync/MUSYNC.ico", 'rb+') as icon:
		with open("./musync/icon.b64", 'wb+') as iconEncode:
			iconData = icon.read()
			iconEncode.write(b64encode(iconData))

def EncodeTTF():
	with open("./musync/LXGW.ttf", 'rb+') as ttf:
		with open("./musync/ttf.b64", 'wb+') as ttfEncode:
			ttfData = ttf.read()
			ttfEncode.write(b64encode(ttfData))

def EncodeJson():
	with open("./musync/songname.json", 'rb+') as snj:
		with open("./musync/songname.b64", 'wb+') as snjEncode:
			snjData = snj.read()
			snjEncode.write(b64encode(snjData))

if __name__ == '__main__':
	# EncodeTTF()
	# EncodeIcon()
	EncodeJson()
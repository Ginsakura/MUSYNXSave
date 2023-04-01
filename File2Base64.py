from base64 import b64encode,b64decode
import os
# import pyperclip

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

def EncodeDLL():
	with open('./HitDelayFix.dll','rb') as hdf:
		with open('./musync_data/HitDelayFix.b64','wb') as hdfE:
			hdfD = hdf.read()
			b64e = b64encode(hdfD)
			hdfE.write(b64e)

if __name__ == '__main__':
	if not os.path.isfile("./musync_data/ttf.b64"):
		EncodeTTF()
	if not os.path.isfile('./musync_data/icon.b64'):
		EncodeIcon()
	EncodeJson()
	if not os.path.isfile('./musync_data/HitDelayFix.b64'):
		EncodeDLL()
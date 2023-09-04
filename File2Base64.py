from base64 import b64encode,b64decode
import os
import pyperclip

def EncodeIcon():
	with open("./musync_data/MUSYNC.ico", 'rb+') as icon:
		with open("./musync_data/icon.b64", 'wb+') as iconEncode:
			iconEncode.write(b64encode(icon.read()))

def EncodeTTF():
	with open("./musync_data/LXGW.ttf", 'rb+') as ttf:
		with open("./musync_data/ttf.b64", 'wb+') as ttfEncode:
			ttfEncode.write(b64encode(ttf.read()))

def EncodeJson():
	with open("./musync_data/songname.json", 'rb+') as snj:
		with open("./musync_data/songname.b64", 'wb+') as snjEncode:
			b64e = b64encode(snj.read())
			snjEncode.write(b64e)
			pyperclip.copy(b64e.decode('utf8'))

def EncodeDLL():
	with open('./musync_data/Assembly-CSharp.dll','rb') as hdf:
		with open('./musync_data/HitDelayFix.b64','wb') as hdfE:
			hdfE.write(b64encode(hdf.read()))

def EncodeLicense():
	with open('./LICENSE', 'rb') as license:
		with open('./musync_data/LICENSE.b64','wb') as licenseE:
			licenseE.write(b64encode(license.read()))
			
if __name__ == '__main__':
	if not os.path.isfile("./musync_data/ttf.b64"):
		EncodeTTF()
	if not os.path.isfile('./musync_data/icon.b64'):
		EncodeIcon()
	EncodeJson()
	if not os.path.isfile('./musync_data/HitDelayFix.b64'):
		EncodeDLL()
	if not os.path.isfile('./musync_data/LICENSE.b64'):
		EncodeLicense()
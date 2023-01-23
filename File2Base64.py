from base64 import *

def EncodeIcon():
	with open("./MUSYNC.ico", 'rb+') as icon:
		with open("./icon.b64", 'wb+') as iconEncode:
			iconData = icon.read()
			iconEncode.write(b64encode(iconData))

def EncodeTTF():
	with open("./LXGW.ttf", 'rb+') as ttf:
		with open("./ttf.b64", 'wb+') as ttfEncode:
			ttfData = ttf.read()
			ttfEncode.write(b64encode(ttfData))

if __name__ == '__main__':
	EncodeTTF()
	EncodeIcon()
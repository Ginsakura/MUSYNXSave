import os
import pyperclip

from base64 import b64encode,b64decode

def EncodeIcon():
	with open("./musync_data/MUSYNC.ico", 'rb+') as icon:
		with open("./musync_data/icon.b64", 'w') as iconEncode:
			data:str = b64encode(icon.read()).decode("ascii")
			iconEncode.write("[")
			for i in range(len(data)//128+1):
				iconEncode.write(f"\t\"{data[i*128:i*128+128]}\",\n")
			iconEncode.write("];")

def EncodeTTF():
	with open("./musync_data/LXGW.ttf", 'rb+') as ttf:
		with open("./musync_data/ttf.b64", 'w') as ttfEncode:
			data = b64encode(ttf.read()).decode("ascii")
			ttfEncode.write("[")
			for i in range(len(data)//128+1):
				ttfEncode.write(f"\t\"{data[i*128:i*128+128]}\",\n")
			ttfEncode.write("];")

def EncodeJson():
	with open("./musync_data/songname.json", 'rb+') as snj:
		with open("./musync_data/songname.b64", 'w') as snjEncode:
			data = b64encode(snj.read()).decode("ascii")
			snjEncode.write("[")
			for i in range(len(data)//128+1):
				snjEncode.write(f"\t\"{data[i*128:i*128+128]}\",\n")
			snjEncode.write("];")

def EncodeDLL():
	with open('./musync_data/Assembly-CSharp.dll','rb') as hdf:
		with open('./musync_data/Assembly-CSharp.b64','w') as hdfE:
			data = b64encode(hdf.read()).decode("ascii")
			hdfE.write("[")
			for i in range(len(data)//128+1):
				hdfE.write(f"\t\"{data[i*128:i*128+128]}\",\n")
			hdfE.write("];")

def EncodeLicense():
	with open('./LICENSE', 'rb') as license:
		with open('./musync_data/LICENSE.b64','w') as licenseE:
			data:str = b64encode(license.read()).decode("ascii")
			licenseE.write("[")
			for i in range(len(data)//128+1):
				licenseE.write(f"\t\"{data[i*128:i*128+128]}\",\n")
			licenseE.write("];")
			
if __name__ == '__main__':
	if not os.path.isfile("./musync_data/ttf.b64"):
		EncodeTTF()
	if not os.path.isfile('./musync_data/icon.b64'):
		EncodeIcon()
	EncodeJson()
	if not os.path.isfile('./musync_data/Assembly-CSharp.b64'):
		EncodeDLL()
	if not os.path.isfile('./musync_data/LICENSE.b64'):
		EncodeLicense()
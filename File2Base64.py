import gzip
from hashlib import md5
import io
import json
import os
import struct
# from base64 import b64encode

FillSize:int = 512;
FixDLL:str = "F39E7D866C2EF4F6A40E573EF5B0D2A8";
# Source Assembly-CSharp.dll
SourceDLL:str = '6968CEE6E5F671B9DDB3F6AB0769396E';
SongNameVersion:int = 20250303;

def GetHash(filePath:str=None)->str:
	if (filePath is None): return "";
	with open(filePath,'rb') as fileBytes:
		return md5(fileBytes.read()).hexdigest().upper();

def CompressAndEncode(filePath: str) -> bytes:
	"""
	压缩一个二进制文件。
	参数:
		filePath (str): 要压缩的文件路径。
	返回:
		bytes: 压缩后的二进制数据。
	"""
	# 打开文件并读取二进制内容
	with open(filePath, 'rb') as file:
		fileData:bytes = file.read();

	# 使用 gzip 压缩数据
	compressedData:io.BytesIO = io.BytesIO();
	with gzip.GzipFile(fileobj=compressedData, mode='wb') as gzipFile:
		gzipFile.write(fileData);

	# 获取压缩后的数据
	compressedData:bytes = compressedData.getvalue();
	return compressedData;
	# 将压缩后的数据转换为 Base64 字符串
	# return b64encode(compressedData).decode('utf-8');

def CompressAndEncodeToFile(readFilePath:str, writeFilePath:str)->(bytes|None):
	"""
	编码文件
	参数:
		readFilePath (str): 读文件路径;
		writeFilePath (str): 写文件路径;
	返回:
		(bytes | None): 压缩后的二进制数据。
	"""
	if (os.path.isfile(readFilePath)):
		with open(writeFilePath, 'wb') as iconEncode:
			data:bytes = CompressAndEncode(readFilePath);
			iconEncode.write(data);
		return data;
	return None;

if __name__ == '__main__':
	fileList:list[dict[str,str]] = [
		{
			"Source": "./musync_data/MUSYNC.ico",
			"Target": "./musync_data/Icon.bin",
			"Tag": "Icon",
		},
		{
			"Source": "./musync_data/LXGW.ttf",
			"Target": "./musync_data/Font.bin",
			"Tag": "Font",
		},
		{
			"Source": "./musync_data/songname.json",
			"Target": "./musync_data/SongName.bin",
			"Tag": "SongName",
		},
		{
			"Source": "./musync_data/Assembly-CSharp.dll",
			"Target": "./musync_data/Assembly-CSharp.bin",
			"Tag": "GameLib",
		},
		{
			"Source": "./mscorlib.dll",
			"Target": "./musync_data/mscorlib.bin",
			"Tag": "CoreLib",
		},
		{
			"Source": "./LICENSE",
			"Target": "./musync_data/LICENSE.bin",
			"Tag": "License",
		},
		];

	binaryInfo:dict[str,dict[str,any]] = dict();
	binaryFile:io.TextIOWrapper = open("./musync_data/Resources.bin",'wb');
	binaryOffset:int = FillSize;
	binaryData:bytes = b'';

	for file in fileList:
		# 编码
		print(f"Encoding: {file['Source']} -> {file['Target']}");
		# if (os.path.isfile(file['Target'])): continue;
		encodeString:str = CompressAndEncodeToFile(file['Source'], file['Target']);
		if (encodeString is None): continue;
		# 整合
		binaryInfo[file["Tag"]] = dict(
			offset = binaryOffset,
			lenth = len(encodeString),
			hash = GetHash(file['Source']),
			);
		binaryOffset += len(encodeString);
		with open(file['Target'],"rb") as fileContext:
			binaryData += encodeString;

	# 修复文件结构
	binaryInfo["GameLib"]["SourceHash"] = SourceDLL;
	binaryInfo["SongName"]["Version"] = SongNameVersion;
	print(json.dumps(binaryInfo, ensure_ascii=False, indent=4));
	# 封装文件
	# 创建一个BytesIO对象，用于存储压缩后的数据
	# 使用gzip.GzipFile进行压缩
	buffer:io.BytesIO = io.BytesIO();
	with gzip.GzipFile(fileobj=buffer, mode='wb') as gzFile:
		gzFile.write(json.dumps(binaryInfo).encode("ASCII"));
	# 获取压缩后的字节数据
	compressData = buffer.getvalue()
	# 写入文件结构大小, 4 Bytes
	binaryFile.write(struct.pack('I', len(compressData)));
	# 写入文件结构
	binaryFile.write(compressData.ljust(FillSize-4, b'\x00'));
	# 写入文件数据
	binaryFile.write(binaryData);

	print("success encode resources");
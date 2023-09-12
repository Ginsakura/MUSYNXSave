import <iostream>;
import <fstream>;
import <vector>;
import <string>;
import <utility>;
import <cstddef>;
import <Python.h>;
import <format>;
#include "json/json.h"
using namespace std;

class SongInfo
{
public:
	SongInfo(int mSMID,string mSS,string mSN,string mK,string mD,string mDN,string mSNb,double mUS,int mPC,byte mIF)
	:mSongMapID {mSMID},mSpeedStall {mSS},mSongName {mSN},mKeys {mK},mDiffcute {mD},mDiffcuteNumber {mDN},
	mSyncNumber {mSNb},mUploadScore {mUS},mPlayCount {mPC},mIsFav {mIF}
	{}
	~SongInfo()
	{}
	void setSongMapID(int mSMID) { this->mSongMapID = mSMID;}
	int getSongMapID() {return this->mSongMapID;}
	void setSpeedStall(string mSS) { this->mSpeedStall = mSS;}
	string getSpeedStall() {return this->mSpeedStall;}
	void setSongName(string mSN) { this->mSongName = mSN;}
	string getSongName() {return this->mSongName;}
	void setKeys(string mK) { this->mKeys = mK;}
	string getKeys() {return this->mKeys;}
	void setDiffcute(string mD) { this->mDiffcute = mD;}
	string getDiffcute() {return this->mDiffcute;}
	void setDiffcuteNumber(string mDN) { this->mDiffcuteNumber = mDN;}
	string getDiffcuteNumber() {return this->mDiffcuteNumber;}
	void setSyncNumber(string mSNb) { this->mSyncNumber = mSNb;}
	string getSyncNumber() {return this->mSyncNumber;}
	void setUploadScore(double mUS) { this->mUploadScore = mUS;}
	double getUploadScore() {return this->mUploadScore;}
	void setPlayCount(int mPC) { this->mPlayCount = mPC;}
	int getPlayCount() {return this->mPlayCount;}
	void setIsFav(byte mIF) { this->mIsFav = mIF;}
	byte getIsFav() {return this->mIsFav;}
private:
	int mSongMapID;
	string mSpeedStall;
	string mSongName;
	string mKeys;
	string mDiffcute;
	string mDiffcuteNumber;
	string mSyncNumber;
	double mUploadScore;
	int mPlayCount;
	byte mIsFav;
};

class SaveData
{
public:
	SaveData(string mLP,SongInfo mSD)
	:mLastPlay {mLP},mSaveData {mSD}
	{}
	~SaveData()
	{}
	void setLastPlay(string mLP) { this->mLastPlay = mLP;}
	string getLastPlay() {return this->mLastPlay;}
	//void setSaveData(vector<SongInfo> mSD) {mSaveData = mSD;}
	void addSaveData(SongInfo mSD) {this->mSaveData.push_back(mSD);}
	vector<SongInfo> getSaveData() { return mSaveData; }
	SongInfo* getSaveData2Array() {
		SongInfo* saveDataArray = mSaveData.data();
		return saveDataArray;
	}
private:
	string mLastPlay {};
	vector<SongInfo> mSaveData {};
};

// extern "C" __declspec(dllexport) SaveData* SavDecode(string& filePath) {
static SaveData SavDecode(string filePath) {
	cout << filePath << endl;

	string mSS = {"00018AED"};
	string mSN = {"test"};
	string mK {"4Key"};
	string mD {"Easy"};
	string mDN {"02"};
	string mSNb {"12009"};
	byte mIF {0x01};
	SongInfo songInfo {10,mSS,mSN,mK,mD,mDN,mSNb,120.09730339050293,12,mIF};

	string lastPlay {"Last Play"};
	SaveData saveData {lastPlay,songInfo};
	cout << saveData.getLastPlay() << endl;
	for (SongInfo ids : saveData.getSaveData()) {
		cout << format("songName:{}\nsongUploadScore:{}",ids.getSongName(), ids.getUploadScore()) << endl;
	}
	cout << "====== End ======" << endl;
	return saveData;
}
struct SavDataStruct {
	string lastPlay{};
	SongInfo* saveData{};
};

static PyObject * _SavDecode(PyObject *self, PyObject *args)
{
	SaveData SavDecode(string);
	char* filePath;
	int opt;

	if (!PyArg_ParseTuple(args, "si", &filePath, &opt))
		return NULL;
	cout << format("test args 1: {}",filePath) << endl;
	SaveData res = SavDecode((string)filePath);
	SavDataStruct sds;
	sds.lastPlay = res.getLastPlay();
	sds.saveData = res.getSaveData2Array();
	cout << sds.saveData[0].getDiffcute() << endl;
	//return obj;
	if (opt == 0) {
		return (PyObject*)(Py_BuildValue(""));
	}
	else {
		//return (PyObject*)(Py_BuildValue("O&", res));
		return (PyObject*)(Py_BuildValue("O", sds));
		// PyObject_CallMethod(pClass, “class_method”, “O”, pInstance)
		// 参数分别为 PyObject（类），string（类方法），string（O表示参数为PyObject） ，PyObject（类实例）
	}
}

static PyMethodDef ModuleMethods[] = {
	{
		"SavDecode", // function name
		(PyCFunction)(_SavDecode), // function address
		METH_VARARGS, // ?
		"??????" // function doc
	},
	{NULL, NULL, 0, NULL} //函数导出结束
};
static struct PyModuleDef SavDecodeModule = 
{
	PyModuleDef_HEAD_INIT,
	"SavDecode",  //name of module
	"Fast Decode Save File by C++ (std:20)", //module documentation, may be NULL
	-1, //size of per-interpreter state of the module, or -1 if the module keeps state in global variables.
	ModuleMethods // methods
};

//函数名必须为这样的格式： PyInit_模块名 
PyMODINIT_FUNC PyInit_SavDecode();
PyObject* PyInit_SavDecode() {
	PyObject* module = PyModule_Create(&SavDecodeModule);
	return module;
}
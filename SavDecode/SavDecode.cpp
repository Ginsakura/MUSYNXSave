//#include "SavDecode.h"
import <iostream>
import <fstream>
import <vector>
import <string>
import <utility>
import <cstddef>
import "json/json.h"
using namespace std;

class SongInfo
{
public:
	SongInfo(int mSMID,string mSS,string mSN,string mK,string mD,string mDN,string mSNb,float mUS,int mPC,byte mIF)
	:mSongMapID {mSMID},mSpeedStall {mSS},mSongName {mSN},mKeys {mK},mDiffcute {mD},mDiffcuteNumber {mDN},
	mSyncNumber {mSNb},mUploadScore {mUS},mPlayCount {mPC},mIsFav {mIF}
	{}
	~SongInfo()
	{}
	void setSongMapID(int mSMID) {mSongMapID = mSMID;}
	int getSongMapID() {return mSongMapID;}
	void setSpeedStall(string mSS) {mSpeedStall = mSS;}
	string getSpeedStall() {return mSpeedStall;}
	void setSongName(string mSN) {mSongName = mSN;}
	string getSongName() {return mSongName;}
	void setKeys(string mK) {mKeys = mK;}
	string getKeys() {return mKeys;}
	void setDiffcute(string mD) {mDiffcute = mD;}
	string getDiffcute() {return mDiffcute;}
	void setDiffcuteNumber(string mDN) {mDiffcuteNumber = mDN;}
	string getDiffcuteNumber() {return mDiffcuteNumber;}
	void setSyncNumber(string mSNb) {mSyncNumber = mSNb;}
	string getSyncNumber() {return mSyncNumber;}
	void setUploadScore(float mUS) {mUploadScore = mUS;}
	float getUploadScore() {return mUploadScore;}
	void setPlayCount(int mPC) {mPlayCount = mPC;}
	int getPlayCount() {return mPlayCount;}
	void setIsFav(byte mIF) {mIsFav = mIF;}
	byte getIsFav() {return mIsFav;}
private:
	int mSongMapID;
	string mSpeedStall;
	string mSongName;
	string mKeys;
	string mDiffcute;
	string mDiffcuteNumber;
	string mSyncNumber;
	float mUploadScore;
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
	void setLastPlay(string mLP) {mLastPlay = mLP;}
	string getLastPlay() {return mLastPlay;}
	void setSaveData(vector<SongInfo> mSD) {mSaveData = mSD;}
	void addSaveData(SongInfo mSD) {mSaveData.push_back(mSD);}
	vector<SongInfo> getSaveData() {return mSaveData;}
private:
	string mLastPlay{};
	vector<SongInfo> mSaveData{};
};

extern "C" __declspec(dllexport) int SavDecode(string& filePath) {

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
		cout << ids.getSongName() << endl;
	}
	cout << ">>>> End <<<<" << endl;
	return 0;
}
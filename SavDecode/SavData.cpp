#include <vector>
#include <string>
#include <utility>
#include <array>
#include "SavData.h"

namespace SavData {
	class SavData::SaveData
	{
	public:
		SaveData();
		~SaveData();
		void setLastPlay(std::string& mLP) {
			mLastPlay = mLP;
		}
		std::string getLastPlay() {
			return mLastPlay;
		}
		void setSaveData(std::vector<SavData::SongInfo>& mSD) {
			mSaveData = mSD;
		}
		void addSaveData(SavData::SongInfo& mSD) {
			mSaveData.push_back(mSD);
		}
		std::vector<SavData::SongInfo> getSaveData() {
			return mSaveData;
		}
	private:
		std::string mLastPlay{};
		std::vector<SavData::SongInfo> mSaveData{};
	};

	class SavData::SongInfo
	{
	public:
		SongInfo();
		~SongInfo();
		void setSongMapID(int& mSMID) {
			mSongMapID = mSMID;
		}
		int getSongMapID() {
			return mSongMapID;
		}
		void setUnknownData0(std::byte& mUD0) {
			*mUnknownData0 = mUD0;
		}
		std::byte* getUnknownData0() {
			return mUnknownData0;
		}
		void setSpeedStall(std::string& mSS) {
			mSpeedStall = mSS;
		}
		std::string getSpeedStall() {
			return mSpeedStall;
		}
		void setSongName(std::string& mSN) {
			mSongName = mSN;
		}
		std::string getSongName() {
			return mSongName;
		}
		void setKeys(std::string& mK) {
			mKeys = mK;
		}
		std::string getKeys() {
			return mKeys;
		}
		void setDiffcute(std::string& mD) {
			mDiffcute = mD;
		}
		std::string getDiffcute() {
			return mDiffcute;
		}
		void setDiffcuteNumber(std::string& mDN) {
			mDiffcuteNumber = mDN;
		}
		std::string getDiffcuteNumber() {
			return mDiffcuteNumber;
		}
		void setUnknownData1(std::byte& mUD1) {
			*mUnknownData1 = mUD1;
		}
		std::byte* getUnknownData1() {
			return mUnknownData1;
		}
		void setSyncNumber(std::string& mSN) {
			mSyncNumber = mSN;
		}
		std::string getSyncNumber() {
			return mSyncNumber;
		}
		void setUploadScore(float& mUS) {
			mUploadScore = mUS;
		}
		float getUploadScore() {
			return mUploadScore;
		}
		void setPlayCount(int& mPC) {
			mPlayCount = mPC;
		}
		int getPlayCount() {
			return mPlayCount;
		}
		void setIsFav(std::byte& mIF) {
			mIsFav = mIF;
		}
		std::byte getIsFav() {
			return mIsFav;
		}

	private:
		int mSongMapID{};
		std::byte mUnknownData0[4]{};
		std::string mSpeedStall{};
		std::string mSongName{};
		std::string mKeys{};
		std::string mDiffcute{};
		std::string mDiffcuteNumber{};
		std::byte mUnknownData1[4]{};
		std::string mSyncNumber{};
		float mUploadScore{};
		int mPlayCount{};
		std::byte mIsFav{};
	};
}
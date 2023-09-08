#pragma once
#include <vector>
#include <string>
#include <utility>
#include <array>

namespace SavData {
	class SavData::SaveData
	{
	public:
		SaveData();
		~SaveData();
		void setLastPlay(std::string& mLP);
		std::string getLastPlay();
		void setSaveData(std::vector<SavData::SongInfo>& mSD);
		void addSaveData(SavData::SongInfo& mSD);
		std::vector<SavData::SongInfo> getSaveData();

	private:
		std::string mLastPlay{};
		std::vector<SavData::SongInfo> mSaveData{};
	};
	
	class SavData::SongInfo
	{
	public:
		SongInfo();
		~SongInfo();
		void setSongMapID(int& mSMID);
		int getSongMapID();
		void setUnknownData0(std::byte& mUD0);
		std::byte getUnknownData0();
		void setSpeedStall(std::string& mSS);
		std::string getSpeedStall();
		void setSongName(std::string& mSN);
		std::string getSongName();
		void setKeys(std::string& mK);
		std::string getKeys();
		void setDiffcute(std::string& mD);
		std::string getDiffcute();
		void setDiffcuteNumber(std::string& mDN);
		std::string getDiffcuteNumber();
		void setUnknownData1(std::byte& mUD1);
		std::byte getUnknownData1();
		void setSyncNumber(std::string& mSN);
		std::string getSyncNumber();
		void setUploadScore(float& mUS);
		float getUploadScore();
		void setPlayCount(int& mPC);
		int getPlayCount();
		void setIsFav(std::byte& mIF);
		std::byte getIsFav();

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
		int nPlayCount{};
		std::byte mIsFav{};
	};
}
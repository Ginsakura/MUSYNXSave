clear
import delimited "F:\Files\Project_File\Program_Project\Python\MUSYNCSavDecode\musync_data\Acc-SyncFormat.txt", numericcols(2) 
rename v1 delay
rename v2 sync
rename v3 EXTRA
rename v4 Extra
recast int Extra
rename v5 Great
recast int Great
rename v6 Right
recast int Right
rename v7 Miss
recast int Miss
// summarize sync delay EXTRA Extra Great Right Miss, detail
// correlate sync delay EXTRA Extra Great Right Miss
// regress sync delay EXTRA Extra Great Right Miss
summarize sync EXTRA Extra Great Right Miss, detail
correlate sync EXTRA Extra Great Right Miss
regress sync EXTRA Extra Great Right Miss
predict sync_hat
predict e, resid

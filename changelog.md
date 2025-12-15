## 更新日志
### 近期重要更新速览
1. 1.2.2 通过使用UIAutoMation库实现一键自动从控制台获取游玩结果
    $\color{Red}{控制台只显示最近一次的游玩记录，请在下次谱面游玩开始前生成结果}$
    $\color{Red}{控制台关闭后不会保存游玩记录，请在关闭游戏前生成结果}$
    $\color{Red}{结果生成需要使用剪切板，点击按钮后，在结果生成前请不要进行}$ $\color{Red}{** 任何 **}$ $\color{Red}{操作}$
2. 1.2.3 更新游玩记录的存储结构，且 $\color{Red}{不向下兼容}$ ，将`HitDelayHistory.db`修改为`HitDelayHistory_v2.db`
3. 1.2.4 将License从GPLv3切换为MIT
4. 1.2.7 环境更新：`matplotlib 3.7.2->3.9.2`,`numpy 1.25.2->2.0.1`
5. 2.0.0 重构程序
6. 2.0.0 更新游玩记录的存储结构，且 $\color{Red}{不向下兼容}$ ，将`HitDelayHistory_v2.db`修改为`HitDelayHistory.db`，但与`1.2.3`之前版本***结构不同***

### Version 2.0.2
#### Release 1
1. 修复
    1. 修复多次切换谱面筛选时，谱面计数中移除曲目没有清零的bug
    2. 修复SongName.json中的数据错误
    3. 修复数据库更新时可能出现的bug
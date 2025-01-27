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

### Version 1.2.8
#### Release 4
1. 更新
    1. 25年1月3日 本体Assembly-CSharp.dll更新
#### Release 3
1. 更新
    1. #### ***更新12月24日喵赛克新增曲目 (圣诞节更新)***
        - Kirakira Noel Story!! (EZ HD IN)
2. 修复
    1. 修复能够获取版本号时出现Json解析错误的bug
    2. 尝试修复如果4K/6K模式没有一次游玩记录时`Difficulty_ScoreAnalyze`无法加载的bug
    3. 修复最小值赋值错误的bug
3. 优化
    1. 微调难度分布曲线中文本的位置
    2. 修改文件在程序中的存储与释放算法
#### Release 2
2. 修复
    1. ***修复新用户释放资源时，图标文件名称错误的bug***
#### Release 1
1. 更新
    1. #### ***更新09月30日喵赛克新增曲目 (国庆节更新)***
        - Sky Fragment (EZ HD IN)
        - Bright red hertz (EZ HD IN)
        - Zheichour (EZ HD)
        - 双生のネビュラ (EZ HD IN)
    2. 重新修补`Assembly-CSharp.dll`文件
3. 优化
    1. 优化进程查找
    2. 优化文件数据的内部存储方式
    3. 优化文件数据的内部存储编码方式
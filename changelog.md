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

### Version 2.0.0
#### Release 2
1. 更新
    1. #### ***更新2025年01月27日喵赛克新增曲目 (新春联动大更新)***
        - Glazed Color (EZ HD)
        - ENDRUiD (EZ HD IN)
        - Super Nova Project (EZ HD IN)
        - Steel Core Bullet (EZ HD IN)
        - Random (EZ HD IN)
        - Phonon (EZ HD IN)
    2. #### ***更新2025年02月28日喵赛克新增曲目***
        - Awaken In Ruins (EZ HD)
        - Xenolith (EZ HD IN)
    3. ***修补2025年03月03日 游戏资源热更新***
2. 修复
    1. 修复存档解析方案，使用C#实现存档的解析
    2. 修复日志压缩时，压缩文件命名错误
3. 优化
    1. 重构程序
    2. 优化CI配置文件
    3. 优化C#修补代码
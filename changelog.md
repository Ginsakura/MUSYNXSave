## 更新日志
### 近期重要更新速览
1. 1.2.2 通过使用UIAutoMation库实现一键自动从控制台获取游玩结果
    $\color{Red}{控制台只显示最近一次的游玩记录，请在下次谱面游玩开始前生成结果}$
    $\color{Red}{控制台关闭后不会保存游玩记录，请在关闭游戏前生成结果}$
    $\color{Red}{结果生成需要使用剪切板，点击按钮后，在结果生成前请不要进行}$ $\color{Red}{** 任何 **}$ $\color{Red}{操作}$
4. 1.2.7 环境更新：`matplotlib 3.7.2->3.9.2`,`numpy 1.25.2->2.0.1`
7. 3.0.0 完全重构代码, 更新游玩记录的存储结构,
    且 $\color{Red}{不向下兼容}$ ，将`HitDelayHistory.db`版本提高到`v4`, 增加Mode,Difficulty,Combo字段

### Version 3.0.0
#### Release
1. 更新
    1. ***更新2026年02月14日喵赛克联动新增曲目***
        - Miss You (EZ HD)
        - Rainbow (EZ HD)
    1. ***更新2026年04月03日喵赛克联动新增曲目***
        - Vacant Gloria (EZ HD)
        - Memory Accelerator (EZ HD)
2. 修复
    1. 修复重构产生的各种 bug
3. 优化
    1. 更改数据库结构，增加模式、难度、连击字段 (v3 -> v4)
    2. 深度重构代码，使其全面符合 `PEP 8` 规范
    3. 优化 patch 用 C# 代码，关闭控制台的 `快速编辑` 模式；
    3. 控制台提供更丰富的数据输出
    3. 优化`Tookit`中数据库升级迁移逻辑
    3. 优化游戏启动监测逻辑, 降低资源占用
4. 重构
    1. `AllHitAnalyze`: 优化底层数据处理逻辑与图表渲染性能展示
    2. `AvgAcc-SyncAnalyze`: 引入 `Diff` 轴映射，将平面图表重构为 3D 景深散点图
    3. `Diffculty_ScoreAnalyze`: 以更现代、更解耦的架构重新绘制图表并展示数据
    4. `FileEncoding`: 引入防溢出屏障，以更安全的方式处理文件的 meta data，确保跨平台文件操作与 I/O 安全性
    5. `Toolkit`: 完善了文件哈希校验、资源释放的并发安全性设计，并封装了安全的 SQLite 事务流转
    6. `Resource`: 拆分模块, 将其拆分为`config_manager`, `map_info`, `songname_manager`, `save_data_manager`三个独立模块
    7. `bootcfg.json`: 缩减配置项
    7. `HitDelay`: 完全重构代码和界面, 适配最新的(v4)数据库和游戏控制台输出内容

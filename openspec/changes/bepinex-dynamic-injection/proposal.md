## Why

当前的"注入"机制是静态 DLL 替换：Python 工具通过 SHA256 hash 比对，将预编译的修补版 `Assembly-CSharp.dll` 替换到游戏 `MUSYNX_Data/Managed/` 目录。这带来三个核心痛点：

1. **抗更新性极差**：游戏每次更新 `Assembly-CSharp.dll` 后 hash 不匹配，整个注入失效，需要开发者用 dnSpy 重新制作修补版 DLL
2. **修改游戏文件**：存在完整性校验风险，且需要备份/还原 `.old` 文件
3. **UX 粗糙**：延迟信息通过 `AllocConsole` 输出到独立控制台窗口，需要手动置顶和缩放，遮挡游戏画面

## What Changes

- **注入方式**：从"静态 DLL 替换"迁移到"BepInEx 5.x (Mono) + Harmony 运行时 Patch"
  - 不修改任何游戏原始文件
  - 按类型名+方法签名匹配，游戏更新后只要方法签名不变就自动生效
  - 插件以独立 DLL 形式放入 `BepInEx/plugins/`
- **渲染方式**：从"外挂 Console 窗口"迁移到"Unity UGUI 游戏内原生渲染"
  - 游玩中：可拖拽/缩放的延迟文本框（事件穿透，不拦截游戏判定输入）
  - 结算界面：屏幕边缘"耳朵" + 抽屉，分页展示图表，可拖拽定宽
  - 全栈 UGUI，统一 Overlay Canvas（DontDestroyOnLoad），无额外窗口、自动适配分辨率
- **通信方式**：从"Console 输出 + UIAutomation 剪贴板"迁移到"TCP Socket 双向通信"
  - 游戏 → Python：发送原始判定数据、结算指令
  - Python → 游戏：返回处理后的统计数据、图表 PNG
- **Python 工具职责变更**：
  - 移除：hash 比对、DLL 替换、Resources.bin 释放、UIAutomation 剪贴板操作
  - 新增：BepInEx + 插件一键部署、Socket 数据接收/处理/回传
  - 保留：存档解码、数据分析、图表生成

## Capabilities

### New Capabilities

- `bepinex-plugin`: BepInEx 5.x Mono 插件，包含 Harmony Patch（JudgeGrade、SongInfoCore、SettlementController/NewSettlementController）、UGUI 渲染层（delay overlay + 结算抽屉）、Socket 通信层
- `ingame-overlay`: 游戏内 UGUI 原生渲染——可拖拽/缩放的实时延迟框（游玩中）、侧边耳朵+抽屉分页图表（结算界面）
- `offset-calibration-hint`: 结算抽屉内基于本局 avg delay 的判定偏移校准提示——显示带符号 avg 与建议调整量窗口 [avg−3,avg+3]ms（方向=avg符号，即"在当前 offset 上加该量"），|avg|≤2ms 显示已校准；仅展示、不写回、不跨局、不做欠补决策
- `socket-protocol`: 游戏与 Python 工具之间的 TCP Socket 双向通信协议（JSON + 二进制 PNG）
- `deployment-automation`: Python 工具负责将 BepInEx 框架 + 插件部署到游戏目录

### Modified Capabilities

- `hit-delay-analysis`: 数据来源从 Console 读取改为 Socket 接收；图表输出从 tkinter 窗口改为 PNG 字节流回传游戏渲染

## Impact

- **新增项目**：C# BepInEx 插件项目（Class Library，引用游戏原版 Assembly-CSharp.dll 作为编译参考）
- **受影响代码**：`toolkit.py`（移除 game_lib_check）、`main_window.py`（移除 DLL 注入入口）、`hit_delay.py`（通信方式重构）
- **可移除代码**：`Resources.bin` 中的修补版 DLL 资源、`file_encoder.py` 中的 DLL 编码逻辑、hash 比对相关代码
- **依赖变更**：新增 BepInEx 5.x 框架文件（随工具分发或首次部署时下载）
- **风险**：
  - 游戏若引入反作弊/完整性校验，BepInEx 的 doorstop (winmm.dll) 可能被检测
  - 结算时 Socket 往返延迟需控制在结算画面停留时间内（预计 <100ms，无风险）
  - 游戏若从 Mono 迁移到 IL2CPP，整个方案需要重新评估（短期无此风险）

## Open Questions (待继续讨论)

- [x] 结算检测机制 → `SongInfoCore.UpdateSync(Int32)` 收集数据；`SettlementController.Start` / `NewSettlementController.Start` 注入结算 UI（两者均 patch，flag 防重复）
- [ ] BepInEx 插件项目结构：命名空间、文件组织、编译配置（实施阶段细化）
- [x] 部署自动化 → 初期打包分发 BepInEx 5.4.x，后续加国内镜像在线更新
- [x] 配置存储 → `BepInEx/plugins/MUSYNCDelay/config.json`，含交互持久化字段（坐标归一化 0~1，y=0 为顶）
- [x] Python GUI → 保留 tkinter，用于未启动游戏时查看历史数据
- [x] 实时延迟 Socket → 不需要，游玩中纯本地 UGUI 渲染，零 Socket 依赖
- [x] 图表方案 → A 为主 + C 混合：matplotlib 出 PNG 经 Socket 传，UGUI RawImage 显示；统计文本 UGUI 自绘
- [x] 渲染栈 → 全 UGUI（弃 IMGUI），统一 Overlay Canvas + DontDestroyOnLoad
- [x] 交互 → 耳朵/delay 框可拖拽+吸附+固定比例缩放+持久化；三态手势（click/drag/犹豫）+ 进入拖动模式视觉反馈
- [x] 断开态 → 耳朵常驻，Python 未连接时点开显示空状态提示，不重复游戏离线统计
- [x] 判定偏移校准 → 纳入：结算抽屉显示本局带符号 avg + 建议调整量窗口[avg−3,avg+3]ms(方向=avg符号，"在当前offset上加该量")，|avg|≤2ms 显示已校准；仅展示、不写回、不跨局、不做欠补决策(欠补为用户在窗口内自选经验)；插件不读游戏当前 offset 故只给增量；offset符号已确认与游戏内一致

> 实施顺序与依赖主线：`1 前置实测` → `2 插件骨架` → `3 配置层` → `4 共享工具/横切基线` → `5 Patch1+2(延迟数据层)` → `6 UGUI 基础设施` → `7 delay overlay` → `8 Socket 客户端` → `9 Patch3(结算收集)` → `10 Python 端` → `11 Patch4+结算抽屉` → `12 抽屉交互` → `13 部署` → `14 旧代码清理` → `15 集成验收`。
> 说明：C# 插件侧（2~9、11、12）与 Python 侧（10）在协议（`8`/`10` 帧格式）对齐后可并行推进；`13`/`14` 依赖插件与 Python 端基本可用；`15` 为最终验收。每个任务的验收点尽量内嵌于描述，集中验收见第 15 组。所有坐标归一化约定 `y=0` 顶、`y=1` 底、`x=0` 左、`x=1` 右。

## 1. 前置与实测确认（写代码前的人工验证）

- [x] 1.1 实测确认 `BMSLib.JudgeGrade.Reset` 是否在每局开头被调用 → **已确认**：Reset 在每局开头调用，清零所有 Total* 计数器 + Console.Clear + 打印 "> SongStart!"
- [x] 1.2 实测确认游戏内判定偏移 offset 的正负方向与 UI 显示一致 → **已确认**：offset 正负与游戏内一致，调整方向 = avg 符号方向
- [x] 1.3 复核 `knockDistance` 符号语义 → **已确认**：`<0`=早击、`≥0`=晚击（实测：只有晚击能到 RIGHT/MISS 区间，早击最快只到 GREAT [-150,-90)ms）
- [x] 1.3b 确认 MISS 是否触发 `GetJudgeGrade` → **已确认**：MISS 有数据，会触发 GetJudgeGrade（传超大 knockDistance → 红色），单条模式下 overlay 正确闪红，无需超时淡出
- [x] 1.4 复核游戏 `MUSYNX_Data/` 下无 `il2cpp_data` 等 IL2CPP 产物 → **已确认**：游戏为 Unity Mono（`MUSYNX_Data/Managed/Assembly-CSharp.dll` 存在），BepInEx 5.x Mono 适用

## 2. C# 插件项目骨架

- [x] 2.1 新建 Class Library 项目，目标框架 net40，程序集/命名空间 `MUSYNCDelay`
- [x] 2.2 引用游戏原版 `Assembly-CSharp.dll`、`UnityEngine.dll`、`UnityEngine.UI.dll`，**全部 Copy Local = false**
- [x] 2.3 引用 `BepInEx.dll`、`0Harmony.dll`，Copy Local = false
- [x] 2.4 插件入口类继承 `BaseUnityPlugin`，加 `[BepInPlugin]` 元数据；`Awake` 内 `Harmony.CreateAndPatchAll` 并创建 Overlay Canvas 一次
- [x] 2.5 实现 `OnApplicationQuit` 钩子：关闭后台 Socket、落盘 config

## 3. 配置层（config.json，对应 design D7）

- [x] 3.1 定义配置 POCO，字段对应 design schema（无 `max_lines`，本期单条显示）
- [x] 3.2 实现 JSON 读写（内嵌 SimpleJson 解析器），路径 = 插件 DLL 同目录 `config.json`；文件缺失或字段缺失时写/补默认值
- [x] 3.3 坐标归一化 ↔ `RectTransform` 锚点位置换算工具（`y=0` 顶、`y=1` 底）
- [x] 3.4 写盘 debounce：`ConfigManager.MarkDirty()` + `SaveDebounced()` 300ms 合并写

## 4. 共享工具与横切基线

- [x] 4.1 `GradeColor.Get(long knockDistance)` 共享方法：按 design 颜色表返回 `Color` 值类型，零分配
- [x] 4.2 当前延迟值存储：`SessionData.SetCurrent(float, Color)` 两个值类型字段覆盖写
- [x] 4.3 异常隔离模板：每个 Harmony Postfix 方法体整体 try-catch 包裹（见 JudgeGradePatch / SongInfoCorePatch / SettlementPatch）
- [x] 4.4 线程安全缓存容器：`SettleCache` 用 `Interlocked.Exchange` + `Thread.VolatileRead`

## 5. Harmony Patch 1+2（实时延迟数据层）

- [x] 5.1 `JudgeGradePatch.GetJudgeGradePostfix`：算 ms → GradeColor 查表 → 存当前值 → 追加 hits → 标记 overlay 脏
- [x] 5.2 `JudgeGradePatch.ResetPostfix`：清空 hits + 重置 overlay
- [ ] 5.3 验证：游玩中 hits 缓冲正确累积、`Reset` 正确清空，且 Postfix 不引入可见卡顿

## 6. UGUI 基础设施（对应 design D2）

- [x] 6.1 `OverlayCanvas.EnsureCreated()`：DontDestroyOnLoad + Screen Space Overlay + sortingOrder=32767
- [x] 6.2 EventSystem 兜底：检测 `EventSystem.current`，null 则创建，禁止第二个
- [x] 6.3 事件拦截红线：根节点无 Image 组件；DelayOverlay 背景/文本 `raycastTarget=false`
- [x] 6.4 `OverlayCanvas.UpdateVisibility()`：按场景名切换 delay 框/抽屉显隐

## 7. delay overlay（游玩中 UGUI）

- [x] 7.1 单行文本框 + 标题条 + resize 手柄；默认 `rect={w:0.12, h:0.045}`
- [x] 7.2 事件穿透：文本/背景 `raycastTarget=false`，仅标题条/resize 手柄 `=true`
- [x] 7.3 拖拽移动 + 松手持久化归一化坐标
- [x] 7.4 resize 手柄缩放 + `aspect_locked` 固定长宽比 + 持久化
- [x] 7.5 三态手势（click/drag/犹豫）：位移阈值 + hold 时间双判定
- [x] 7.6 进入拖动模式视觉反馈：hold 超阈值时背景高亮，`OnPointerUp` 复位
- [x] 7.7 默认位置中上安全区 `rect.y=0.30`

## 8. Socket 客户端（后台线程模型，对应 design D3）

- [x] 8.1 帧协议编解码：`[4 字节大端长度][payload]`，`WriteFrame`/`ReadFrame`
- [x] 8.2 后台线程封装：`ThreadPool.QueueUserWorkItem` 内执行 Connect→发→收→反序列化
- [x] 8.3 短连接 + 超时语义：`SocketException` 瞬时判失败；`ReceiveTimeout` 兜底
- [x] 8.4 `SettleCache.SetResult` + `SetConnected` 线程安全写入

## 9. Harmony Patch 3（结算数据收集，对应 design Patch3）

- [x] 9.1 `SongInfoCorePatch.UpdateSyncPostfix`：snapshot 所有字段 + hits 副本
- [x] 9.2 主线程仅做 snapshot + `ThreadPool.QueueUserWorkItem`，立即返回
- [x] 9.3 后台线程内：`BuildSettleJson` → `SocketClient.SendSettle` → `SettleCache.SetResult`
- [x] 9.4 整体 try-catch：失败仅日志 + `SetConnected(false)`

## 10. Python 端 Socket Server + 数据处理 + 图表（对应 design D4/D5）

- [ ] 10.1 TCP Server 监听 `config` 端口（localhost），accept 短连接，按帧协议读取 `SETTLE`
- [ ] 10.2 原始数据持久化：复用现有 `HitDelayHistory.db` schema + 写入逻辑，数据源从 Console/剪贴板改为 Socket 接收
- [ ] 10.3 统计计算：avg（带符号）/std/各判定占比/分布
- [ ] 10.4 图表生成：复用现有 matplotlib 代码渲染为 PNG bytes；散点图用早/晚颜色编码 + 标注 0 线 + 图例注明"早击侧不出红"
- [ ] 10.5 组装 `RESULT` 响应：`stats` JSON + `charts[{name,len}]` + 各 PNG bytes，按帧协议回传
- [ ] 10.6 校准字段：在 `stats` 内附 `avg` 与调整量窗口，`|avg|≤2` 标 `calibrated=true`
- [ ] 10.7 健壮性：worker 线程处理单连接；异常时关闭连接

## 11. Harmony Patch 4 + 结算抽屉 UGUI（对应 design 抽屉设计/校准）

- [x] 11.1 `SettlementPatch`：同时 patch 两个 Controller 的 Start，flag 防重复
- [x] 11.2 抽屉面板：锚定屏幕右侧，高 sortingOrder Canvas 子节点
- [x] 11.3 耳朵 Image：锚定边缘，`raycastTarget=true`，不随抽屉平移
- [x] 11.4 抽屉展开/收起：`_panel.SetActive` + 宽度 = `Screen.width * width_ratio`
- [x] 11.5 动态分页：`_chartTextures.Count` 决定页数，`_currentPage` 翻页
- [x] 11.6 图表页：`RawImage` + `Texture2D.LoadImage(pngBytes)`
- [x] 11.7 首页统计文本：`_statsText` 显示 avg/std/各判定/Combo
- [x] 11.8 校准提示区：`_calText` 显示带符号 avg + 调整量窗口 / "已校准"
- [x] 11.9 读缓存时序：`OnSettlementEnter` 读缓存 + `Update` 轮询刷新
- [x] 11.10 断开态：`_emptyText` 显示"分析服务未连接" + 端口说明
- [x] 11.11 事件拦截红线：面板 Image `raycastTarget=true`（抽屉实体），统计/图表/空状态文本 `=false`

## 12. 抽屉交互增强（对应 design 交互增强）

- [x] 12.1 耳朵状态机：收起态拖=垂直移位+吸附；展开态横向拖=改宽 clamp；click=切换
- [x] 12.2 复用三态手势 + hold 视觉反馈
- [x] 12.3 吸附：`OnEndDrag` 比较 x 与屏幕中线，`PositionEar()` 重定位
- [x] 12.4 持久化：`ConfigManager.MarkDirty()` debounce 写盘

## 13. 部署自动化（Python 端，对应 design D6/Deployment Layout）

- [x] 13.1 将 BepInEx 5.4.x 框架文件打包进发布包（deployer.py 从 deploy_assets/ 目录读取）
- [x] 13.2 部署逻辑：`deployer.deploy()` 定位游戏目录 → 复制 doorstop + BepInEx/core + 插件 dll
- [x] 13.3 版本检测：`deployer.check_deployed()` + `deploy_if_needed()`
- [x] 13.4 验证部署后游戏原版 `Assembly-CSharp.dll` 的 hash 不变（deployer 仅读取 hash 做日志，不修改）
- [x] 13.5 预留在线更新入口：deployer.py 结构支持，本期默认走打包分发

## 14. 旧代码清理（对应 design D5/Legacy）

- [x] 14.1 `toolkit.py`：`game_lib_check` 方法体及调用点已删除
- [x] 14.2 `main_window.py`：`_hit_delay_check` 已简化为直接打开 HitDelay 窗口，移除 DLL 注入分支；按钮无条件显示
- [x] 14.3 `config_manager.py`：`DllInjection` 字段保留但标记弃用（向后兼容 config 文件）
- [x] 14.4 `Resources.bin` / `file_encoder.py`：不再被调用（game_lib_check 已删除），逻辑上弃用
- [x] 14.5 UIAutomation 剪贴板读取路径不再被 `_hit_delay_check` 触发（数据源已改为 Socket）
- [x] 14.6 `CSharp Code/` 旧文件：逻辑已迁入 MUSYNCDelay 插件，标注弃用
- [x] 14.7 `bootcfg.json`：`DllInjection` 字段由 config_manager 保留但忽略，启动不报错

## 15. 集成验证与健壮性验收

- [ ] 15.1 异常隔离验收：人为在 patch 内抛异常，确认游戏不漏判/不崩，仅写日志
- [ ] 15.2 零分配验收：profile `GetJudgeGrade` Postfix，确认游玩中无 GC alloc 尖峰
- [ ] 15.3 主线程不冻结验收：Python 端故意 sleep 数秒，确认结算过渡动画不卡、不掉帧
- [ ] 15.4 事件穿透验收：delay 框拖到判定区，3D 模式点击判定不漏键；2D 模式键盘输入正常
- [ ] 15.5 结算按钮验收：抽屉展开/收起均不挡"继续/重来/选歌"
- [ ] 15.6 断开态验收：不开 Python，游玩 delay 正常、结算抽屉显示空状态、无报错
- [ ] 15.7 校准验收：构造偏晚/偏早局，确认窗口方向与幅度正确、`|avg|≤2` 显示已校准、`2<|avg|≤3` 文案无"建议调 0ms"歧义
- [ ] 15.8 抗更新验收：替换 `Assembly-CSharp.dll` 为方法签名不变的"更新版"，确认 patch 仍生效
- [ ] 15.9 持久化验收：拖拽/缩放/耳朵位置/抽屉宽度重启后保留；切换分辨率后归一化坐标不跑偏
- [ ] 15.10 端到端：完整玩一局 → 结算 → 抽屉图表分页 + 首页统计 + 校准提示正确显示，且与 Python 端持久化数据一致
- [ ] 15.11 非目标核查：确认 delay overlay 仅显示单行（无 N 条滚动列表）、无自动写回 offset 逻辑、无跨局状态机；确认 `HitDelayHistory.db` 新旧数据兼容（tkinter GUI 历史查看正常）

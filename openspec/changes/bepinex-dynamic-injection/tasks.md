> 实施顺序与依赖主线：`1 前置实测` → `2 插件骨架` → `3 配置层` → `4 共享工具/横切基线` → `5 Patch1+2(延迟数据层)` → `6 UGUI 基础设施` → `7 delay overlay` → `8 Socket 客户端` → `9 Patch3(结算收集)` → `10 Python 端` → `11 Patch4+结算抽屉` → `12 抽屉交互` → `13 部署` → `14 旧代码清理` → `15 集成验收`。
> 说明：C# 插件侧（2~9、11、12）与 Python 侧（10）在协议（`8`/`10` 帧格式）对齐后可并行推进；`13`/`14` 依赖插件与 Python 端基本可用；`15` 为最终验收。每个任务的验收点尽量内嵌于描述，集中验收见第 15 组。所有坐标归一化约定 `y=0` 顶、`y=1` 底、`x=0` 左、`x=1` 右。

## 1. 前置与实测确认（写代码前的人工验证）

- [x] 1.1 实测确认 `BMSLib.JudgeGrade.Reset` 是否在每局开头被调用 → **已确认**：Reset 在每局开头调用，清零所有 Total* 计数器 + Console.Clear + 打印 "> SongStart!"
- [ ] 1.2 实测确认游戏内判定偏移 offset 的正负方向与 UI 显示一致，据此定校准方向常量取值（design 记"调整方向 = avg 符号方向"，与游戏同向）
- [x] 1.3 复核 `knockDistance` 符号语义 → **已确认**：`<0`=早击、`≥0`=晚击（实测：只有晚击能到 RIGHT/MISS 区间，早击最快只到 GREAT [-150,-90)ms）
- [x] 1.3b 确认 MISS 是否触发 `GetJudgeGrade` → **已确认**：MISS 有数据，会触发 GetJudgeGrade（传超大 knockDistance → 红色），单条模式下 overlay 正确闪红，无需超时淡出
- [ ] 1.4 复核游戏 `MUSYNX_Data/` 下无 `il2cpp_data` 等 IL2CPP 产物，确认 Mono 前提成立（BepInEx 5.x Mono 适用）

## 2. C# 插件项目骨架

- [ ] 2.1 新建 Class Library 项目，目标框架对齐 BepInEx 5 / Unity Mono（net35 或 net40，按 BepInEx 5.4 模板），程序集/命名空间 `MUSYNCDelay`
- [ ] 2.2 引用游戏原版 `Assembly-CSharp.dll`、`UnityEngine.dll`、`UnityEngine.UI.dll`，**全部 Copy Local = false**（不得把巨大游戏 dll 打进插件目录）
- [ ] 2.3 引用 `BepInEx.dll`、`0Harmony.dll`，Copy Local = false（随框架分发，见第 13 组）
- [ ] 2.4 插件入口类继承 `BaseUnityPlugin`，加 `[BepInPlugin]` 元数据；`Awake` 内 `Harmony.CreateAndPatchAll` 并创建 Overlay Canvas 一次
- [ ] 2.5 实现 `OnApplicationQuit` 钩子：关闭后台 Socket、落盘 config

## 3. 配置层（config.json，对应 design D7）

- [ ] 3.1 定义配置 POCO，字段对应 design schema：`network{host,port,read_timeout_ms}`、`gesture{drag_distance_px,hold_ms}`、`delay_overlay{enabled,rect,aspect_locked,font_size,alpha}`、`drawer{ear{side,y},width_ratio,min_width_ratio,max_width_ratio}`（无 `max_lines`，本期单条显示）
- [ ] 3.2 实现 JSON 读写，路径 = 插件 DLL 同目录 `config.json`；文件缺失或字段缺失时写/补默认值
- [ ] 3.3 坐标归一化 ↔ `RectTransform` 锚点位置换算工具（`y=0` 顶、`y=1` 底）
- [ ] 3.4 写盘 debounce：拖拽/缩放过程中不每次刷盘，停手后延迟（如 300~500ms）合并写一次

## 4. 共享工具与横切基线

- [ ] 4.1 `Color GradeColor(long knockDistance)` 共享方法：按 design 颜色表（早/晚两列）返回 `Color` 值类型，零分配；UGUI overlay 与 Python 图表颜色编码共用同一阈值表（Python 侧同步一份）
- [ ] 4.2 当前延迟值存储：两个值类型字段 `float currentDelayMs` + `Color currentColor`（单条模式，无环形缓冲，无 GC）；每次打击覆盖写
- [ ] 4.3 异常隔离模板：约定每个 Harmony Postfix 方法体整体 try-catch 包裹，捕获后仅写 BepInEx Logger，绝不向游戏抛异常
- [ ] 4.4 线程安全缓存容器：用 `Interlocked.Exchange` 交换引用 / `volatile` 标志，承载后台 Socket 线程写入、主线程读取的结算结果

## 5. Harmony Patch 1+2（实时延迟数据层）

- [ ] 5.1 `[HarmonyPatch(typeof(JudgeGrade),"GetJudgeGrade")]` Postfix：算 `ms = knockDistance/10000.0f` → `GradeColor` 查表 → 存当前值（float+Color 覆盖写）→ 追加本局 hits 缓冲 → 标记 overlay 文本脏（SetText 仅此时调一次）；满足每帧零分配 + try-catch
- [ ] 5.2 `[HarmonyPatch(typeof(JudgeGrade),"Reset")]` Postfix：清空本局 hits 缓冲 + 重置 overlay（结合 1.1 的确认结果）
- [ ] 5.3 验证：游玩中 hits 缓冲正确累积、`Reset` 正确清空，且 Postfix 不引入可见卡顿

## 6. UGUI 基础设施（对应 design D2）

- [ ] 6.1 创建 `DontDestroyOnLoad` 的 `Screen Space - Overlay` Canvas + `GraphicRaycaster`，`sortingOrder` 高于游戏原生 Canvas
- [ ] 6.2 EventSystem 兜底：创建 Overlay Canvas 时检测 `EventSystem.current`，为 null 则 `new GameObject("MUSYNCDelay_EventSystem").AddComponent<EventSystem>()` 并加 InputModule；已有则复用，**禁止创建第二个**
- [ ] 6.3 事件拦截红线核查：Overlay Canvas 根节点及所有空白/装饰/透明填充 Image 全部 `RaycastTarget=false`，逐节点确认（避免挡死游戏原生按钮）
- [ ] 6.4 游玩场景显示 delay 框、结算场景显示抽屉的显隐控制（按场景/状态切换，跨场景对象不重复创建）

## 7. delay overlay（游玩中 UGUI）

- [ ] 7.1 文本框布局：标题条 + **单行**文本区（显示当前一次打击的延迟值+颜色）+ 右下角 resize 手柄；默认尺寸 `rect={w:0.12, h:0.045}`（单行紧凑）
- [ ] 7.2 事件穿透：文本区/背景 `RaycastTarget=false`（不拦游戏判定），仅标题条/resize 手柄 `=true`
- [ ] 7.3 拖拽移动（按住标题条/空白手柄）+ 松手持久化归一化坐标
- [ ] 7.4 resize 手柄缩放，`aspect_locked` 时固定长宽比 + 持久化
- [ ] 7.5 三态手势组件（click/drag/犹豫）：`OnPointerDown` 记起点+时刻，`OnDrag` 位移超 `gesture.drag_distance_px` 置 `isDragging`，`OnPointerUp` 做最终判定；阈值读 config
- [ ] 7.6 进入拖动模式视觉反馈：协程监测 hold 超 `gesture.hold_ms` 且未 drag 时高亮/缩放脉冲，`OnPointerUp` 复位
- [ ] 7.7 默认位置中上安全区（`rect.y≈0.30`），避开 3D 模式判定区 `y∈[0.75,0.85]`

## 8. Socket 客户端（后台线程模型，对应 design D3）

- [ ] 8.1 帧协议编解码：`[4 字节大端长度][payload]`；支持 JSON 文本帧与"JSON 头 + 二进制 PNG"混合帧
- [ ] 8.2 后台线程/Task 封装：Connect→发→收→反序列化全部离主线程执行
- [ ] 8.3 短连接 + 超时语义：Connect refused 瞬时判失败；读超时取 `network.read_timeout_ms` 兜底
- [ ] 8.4 结果线程安全写入静态缓存（`Interlocked.Exchange`），并维护连接状态标志供断开态 UI 读取

## 9. Harmony Patch 3（结算数据收集，对应 design Patch3）

- [ ] 9.1 `[HarmonyPatch(typeof(SongInfoCore),"UpdateSync")]` Postfix：snapshot `SongId/MaxComboThis/SyncNumberThis/NewRecordThis` + `JudgeGrade` 六个 Total + 本局 hits[]
- [ ] 9.2 主线程仅做 snapshot + 启动后台 Task，立即返回，**不阻塞主线程**
- [ ] 9.3 后台 Task 内：序列化 `SETTLE` 包（字段集见 design）→ 调第 8 组客户端 → 写缓存
- [ ] 9.4 整体 try-catch：失败仅日志，缓存置"未连接/失败"态，不影响游戏结算流程

## 10. Python 端 Socket Server + 数据处理 + 图表（对应 design D4/D5）

- [ ] 10.1 TCP Server 监听 `config` 端口（localhost），accept 短连接，按帧协议读取 `SETTLE`
- [ ] 10.2 原始数据持久化：复用现有 `HitDelayHistory.db` schema（`toolkit.py` `create_new_database`）+ 写入逻辑（`hit_delay.py` INSERT），数据源从 Console/剪贴板改为 Socket 接收，写入格式不变，确保新旧数据兼容
- [ ] 10.3 统计计算：avg（带符号）/std/各判定占比/分布
- [ ] 10.4 图表生成：复用现有 matplotlib 代码渲染为 PNG bytes；散点图用早/晚颜色编码 + 标注 0 线 + 图例注明"早击侧不出红"；分布图体现非对称
- [ ] 10.5 组装 `RESULT` 响应：`stats` JSON + `charts[{name,len}]` + 各 PNG bytes，按帧协议回传
- [ ] 10.6 校准字段：在 `stats` 内附 `avg` 与调整量窗口（方向=`sign(avg)`、幅度=`[max(0,|avg|-3), |avg|+3]`），`|avg|≤2` 标 `calibrated=true`
- [ ] 10.7 健壮性：matplotlib 首次 import 等耗时不阻塞 accept 循环（worker 线程/线程池处理单连接）；异常时不回传半包，关闭连接即可

## 11. Harmony Patch 4 + 结算抽屉 UGUI（对应 design 抽屉设计/校准）

- [ ] 11.1 `[HarmonyPatch(typeof(SettlementController),"Start")]` 与 `[HarmonyPatch(typeof(NewSettlementController),"Start")]` Postfix，用 flag 防重复注入
- [ ] 11.2 抽屉面板：独立高 `sortingOrder` Canvas，`RectTransform` 锚定屏幕一侧
- [ ] 11.3 耳朵 Button：锚定边缘，不随抽屉平移
- [ ] 11.4 抽屉滑入/滑出：协程 lerp `anchoredPosition`（手写，不引 DOTween），默认宽 `drawer.width_ratio=0.5`
- [ ] 11.5 动态分页：页数 = 响应 `charts` 数组长度，发几张图建几页；分页控件（左右箭头 + `n/total` 或页签）
- [ ] 11.6 图表页：`RawImage` + `Texture2D.LoadImage(pngBytes)` 解码显示
- [ ] 11.7 首页统计文本：UGUI `Text` 自绘 avg/std/各判定占比
- [ ] 11.8 校准提示区：读 `stats` 校准字段，显示带符号 avg + "向[正/负]方向调整 a~b ms"，或 `calibrated` 时显示"已校准/无需调整"；方向经单一符号常量集中控制
- [ ] 11.9 读缓存时序：`Start` 时缓存就绪→渲染；未就绪→loading + 轮询刷新（覆盖 Python 卡 >7.7s 的极罕见情况）
- [ ] 11.10 断开态：缓存为"未连接"→抽屉显示空状态提示（端口/启动说明），**不画本地统计**（不重复游戏离线数据）
- [ ] 11.11 事件拦截红线核查（抽屉节点）：根/空白/透明 `=false`，仅耳朵/手柄/分页按钮/抽屉实体 `=true`，确保不挡原生"继续/重来/选歌"

## 12. 抽屉交互增强（对应 design 交互增强）

- [ ] 12.1 耳朵状态机：收起态拖=垂直移位+松手按中线吸附左/右边；展开态横向拖=改宽 clamp `[min_width_ratio,max_width_ratio]`；位移未超阈值=点击切换展开/收起
- [ ] 12.2 复用第 7 组三态手势组件 + 进入拖动模式视觉反馈
- [ ] 12.3 吸附：`OnPointerUp` 比较当前 x 与屏幕中线，lerp 到目标边锚点
- [ ] 12.4 抽屉宽度/耳朵位置持久化（debounce 写盘，复用 3.4）

## 13. 部署自动化（Python 端，对应 design D6/Deployment Layout）

- [ ] 13.1 将 BepInEx 5.4.x 框架文件打包进发布包（初期打包分发）
- [ ] 13.2 部署逻辑：定位游戏目录 → 复制 `winmm.dll`/`doorstop_config.ini`/`BepInEx/core` → 复制插件 dll 到 `BepInEx/plugins/MUSYNCDelay/`
- [ ] 13.3 版本检测：已部署且版本匹配则跳过；框架或插件升级时覆盖更新
- [ ] 13.4 验证部署后游戏原版 `Assembly-CSharp.dll` 的 hash 不变（确认未触碰游戏文件）
- [ ] 13.5 预留在线更新入口（国内镜像下载 BepInEx）：本期可仅留接口/TODO，默认走打包分发

## 14. 旧代码清理（对应 design D5/Legacy）

- [ ] 14.1 `toolkit.py`：移除 `game_lib_check` 及其 hash 比对/重命名 `.old`/释放 `Resources.bin` 的逻辑，及相关调用点
- [ ] 14.2 `main_window.py`：移除 `_hit_delay_check` 的 DLL 注入分支与 `DllInjection` 相关 UI/逻辑
- [ ] 14.3 `config_manager.py`：移除或弃用 `DllInjection` 字段（按迁移策略二选一，保持 config 读写不报错）
- [ ] 14.4 `Resources.bin` / `file_encoder.py`：移除嵌入的修补版 `Assembly-CSharp.dll` 资源与 dll 编码逻辑
- [ ] 14.5 移除 UIAutomation 剪贴板读取路径（旧 `hit_delay` 数据来源）与 Console 窗口管理代码
- [ ] 14.6 `CSharp Code/` 旧文件处置：`Console.cs` 整体弃用；`JudgeGrade.cs`/`SongInfoCore.cs` 逻辑已迁入插件——标注弃用/归档或移除（按偏好）
- [ ] 14.7 `musync_data/bootcfg.json`：`DllInjection` 字段移除或忽略，确保启动不报错

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

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  游戏进程 (MUSYNX.exe, Unity Mono)                              │
│                                                                 │
│  BepInEx Doorstop (winmm.dll) → BepInEx Core → Plugin Loader   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  MUSYNCDelay Plugin                                     │   │
│  │                                                         │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌────────────┐  │   │
│  │  │ Harmony Layer │  │ Render Layer  │  │ Comm Layer │  │   │
│  │  │               │  │               │  │            │  │   │
│  │  │ Patch:        │  │ DelayOverlay  │  │ TCP Client │  │   │
│  │  │ • JudgeGrade  │──▶│ (UGUI)       │  │            │  │   │
│  │  │ • SongInfoCore│  │               │  │ 发送原始数据│  │   │
│  │  │               │  │ SettlePanel   │◀─│ 接收分析结果│  │   │
│  │  └───────────────┘  │ (结算图表)    │  └────────────┘  │   │
│  │                      └───────────────┘                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │ TCP localhost
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Python 进程 (MUSYNCSavDecode)                                  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Socket Server│  │ Data Process │  │ Chart Generator      │  │
│  │              │──▶│              │──▶│ (matplotlib → PNG)   │  │
│  │ 接收原始数据 │  │ 统计/分析    │  │                      │  │
│  │ 回传结果     │◀─│ 持久化存储   │◀─│ 返回 PNG bytes       │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 保留功能: 存档解码、songname 管理、部署自动化            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Decisions

### D1: 注入框架选择 BepInEx 5.x (Mono)

- 游戏确认为 Unity Mono（`MUSYNX_Data/Managed/Assembly-CSharp.dll`）
- BepInEx 是最成熟的 Unity Mono modding 框架
- 通过 Doorstop (winmm.dll 代理) 引导，不修改游戏原始文件
- Harmony 按方法签名匹配 patch，天然抗游戏更新

### D2: 渲染方案 = UGUI 统一（delay overlay + 结算抽屉）

- 游戏为 Built-in Render Pipeline（无 Unity.RenderPipelines.*.dll）
- 游戏目录有 UnityEngine.UI.dll → UGUI (Canvas) 可用
- **修订说明（已确认）**：原计划"游玩延迟用 IMGUI、结算用 UGUI"。因交互需求升级（delay 框需拖拽 + 缩放 + 持久化，且**不能拦截游戏判定输入**），IMGUI 的"简单"优势消失，而 UGUI 的 `RaycastTarget` 事件穿透能力是关键 → **确定 delay overlay 也改 UGUI，全栈统一 UGUI，弃用 IMGUI**。
- 统一 UGUI 的额外收益：一个 `DontDestroyOnLoad` 的 Overlay Canvas 跨场景存在，游玩场景显示 delay 框、结算场景显示抽屉，生命周期统一管理
- 事件穿透解决输入冲突：文本/图表区域 `RaycastTarget=false`（触摸/点击穿透给游戏判定），仅拖拽手柄/耳朵 `RaycastTarget=true` → 无论键鼠或触屏都不干扰游玩
- **Overlay Canvas 事件拦截红线**：Overlay Canvas 的**根节点及所有空白/装饰/透明填充区域必须 `RaycastTarget=false`**，只有真实交互控件（耳朵、resize 手柄、抽屉面板实体、分页按钮）才 `=true`。否则一个全屏透明 Image 会把结算界面原生的"继续/重来"按钮、选歌按钮的事件全部挡死——这是 UGUI 叠层最常见的"界面点不动"bug，实施时务必逐节点核查
- **EventSystem 依赖**：UGUI 拖拽/点击强依赖场景内存在 `EventSystem` + Canvas 上的 `GraphicRaycaster`。插件需在创建 Overlay Canvas 时检测 `EventSystem.current`，若为 null 则兜底 `new GameObject("MUSYNCDelay_EventSystem").AddComponent<EventSystem>()`（并加 StandaloneInputModule / InputSystemUIInputModule）；若游戏已有 EventSystem 则复用，**禁止创建第二个**（两个 EventSystem 会抢事件）
- 补充理由：交互设计采用 press/up/drag 事件分离 + 位移&时间双阈值的手势模型，天然映射 UGUI EventSystem 接口（`IPointerDownHandler`/`IPointerUpHandler`/`IDragHandler`）；IMGUI 无事件分离，需每帧轮询 `Input.GetMouseButton*` 手动拼装状态机，更糙且易错 → 进一步坐实统一 UGUI（已确认）

### D3: 通信使用 TCP Socket (localhost)，短连接 + 瞬时失败判定

- 游玩中：实时延迟仅本地渲染（UGUI），不走 Socket（零延迟、零依赖）
- 结算时：一次性发送原始数据 → Python 处理 → 回传结果
- 选择 TCP 而非 UDP：localhost 下 TCP `Connect` 在 Python 未启动时**立即**抛 `SocketException`（connection refused，无需等超时），断开判定比 UDP ping-pong 更简单可靠
- 连接模式：结算时短连接（Connect→发→收→关），localhost Connect 开销 <1ms
- 超时语义：Connect refused = 瞬时（Python 没开）；读超时 1~2s 兜底（Python 开着但卡住，如 matplotlib 首次 import）
- **线程模型（重要）**：Socket 的 Connect/发/收/反序列化**全部在后台线程**执行；主线程（UpdateSync Postfix）只做"数据 snapshot + 启动后台 Task"，**绝不阻塞主线程**。理由：音游主线程冻结会直接卡过渡动画/掉帧，体验硬伤；即便 Python 卡 2~3s（matplotlib 首次 import），也只在后台等，主线程无感
- 主线程与后台线程的数据交换：后台线程完成后用线程安全方式（`Interlocked.Exchange` 引用 / `volatile` 标志）写入静态缓存；结算 Start 读缓存，未就绪则显示 loading/空状态并可轮询刷新
- 协议：JSON 文本 + 二进制 PNG 混合（长度前缀分帧）

### D4: 图表方案 = A 为主 + C 混合（已确定）

- 主体方案 A：Python matplotlib 出图 → PNG bytes → Unity `Texture2D.LoadImage()` → 抽屉内 RawImage 显示
- 统计文本（avg/std/分布数字）用 UGUI Text 在抽屉首页自绘（方案 C 的轻量部分）
- 确定理由：结算采用"侧边抽屉 + 分页"设计，抽屉展开后空间接近全屏，足以容纳高清 PNG 图表；分页天然对应多张 PNG
- 复用现有 matplotlib 代码、localhost 传输 <5ms、避免在 C# 重写绘图逻辑
- 图表在结算场景加载前 ~7.7s 已由 Python 生成并缓存，点开抽屉时立即可用，无加载等待

### D5: Python 工具职责精简

- 移除：hash 比对、DLL 文件替换、Resources.bin 中嵌入修补版 DLL
- 移除：UIAutomation 剪贴板操作、Console 窗口管理
- 新增：Socket Server（数据接收/处理/回传），仅结算时被调用
- 新增：BepInEx + 插件部署自动化
- 保留：存档解码、数据分析逻辑、图表生成
- 保留：tkinter GUI（用于未启动游戏时查看历史数据，使用频率低但保留）

### D6: BepInEx 框架分发策略

- 优先：在线下载（国内镜像：ghproxy / Gitee Release / 自建 OSS）
- 备选：打包分发（BepInEx 5.4.x 约 5~8MB，框架极少更新，维护成本低）
- 初期可先做打包分发，后续加在线更新

### D7: 插件配置使用 JSON

- 存储路径：`BepInEx/plugins/MUSYNCDelay/config.json`（与插件 DLL 同目录）
- 不使用 BepInEx 内置 ConfigEntry（.cfg 格式），改用自定义 JSON 以便灵活扩展
- 坐标约定：所有归一化坐标 `y=0` 为屏幕**顶部**、`y=1` 为底部（与截图/像素直觉一致）；`x=0` 左、`x=1` 右；`rect` 的 (x,y) 为框左上角。归一化以适配分辨率变化，实现时换算为 RectTransform 锚点位置
- 配置内容（含交互持久化字段）：

```json
{
  "network": { "host": "127.0.0.1", "port": 26531, "read_timeout_ms": 1500 },
  "gesture": { "drag_distance_px": 5, "hold_ms": 300 },
  "delay_overlay": {
    "enabled": true,
    "rect": { "x": 0.02, "y": 0.30, "w": 0.12, "h": 0.045 },
    "aspect_locked": true,
    "font_size": 24,
    "alpha": 0.85
  },
  "drawer": {
    "ear": { "side": "right", "y": 0.5 },
    "width_ratio": 0.5,
    "min_width_ratio": 0.3,
    "max_width_ratio": 0.95
  }
}
```

- 注：`delay_overlay.rect.y=0.30` 为中上安全区默认值，避开 3D 模式判定区（y∈[0.75,0.85]，见交互章节实测）

## Game Structure (from Assembly-CSharp.dll analysis)

### 关键类与方法

| 类 | 命名空间 | 关键方法/属性 | 用途 |
| --- | --- | --- | --- |
| `JudgeGrade` | BMSLib | `GetJudgeGrade(Int64)`, `Reset()`, `TotalEx/Exact/Great/Right/Miss/Combo` | 判定逻辑 + 统计 |
| `SongInfoCore` | Global | `UpdateSync(Int32)`, `SongId`, `SyncNumberThis`, `MaxComboThis` | 歌曲信息 + 结算触发 |
| `SettlementController` | Global | `Awake()`, `Start()`, `Again()`, `BackToSelectSong()` | 旧版结算场景 |
| `NewSettlementController` | Global | `Awake()`, `Start()`, `Again()`, `BackToSelectSong()` | 新版结算场景 |
| `UI0X_SongPlayer` | Global | `WaitingToNextScene(String, Boolean)`, `playStatus` | 游玩主控 (X=A~J 多皮肤) |
| `PlayModeJudge` | BMSLib | `Invoke(knockTime, playTime, insertTime, isRunInUpdate)` | 判定委托 |
| `PlayerScore` | Global | `Reset()`, `UpdateScore()`, `AddScore()` | 分数累加 |

### PlayModeJudge 委托签名

```csharp
public delegate bool PlayModeJudge(long knockTime, long playTime, long insertTime, bool isRunInUpdate);
// knockTime = 玩家按键时刻
// playTime  = 当前播放时刻
// insertTime = 音符应被击中时刻
// knockDistance (传给 GetJudgeGrade) = knockTime - insertTime 或 playTime - insertTime
```

### UpdateSync 方法体 (结算触发点)

```csharp
internal void UpdateSync(int maxCombo)
{
    this.MaxComboThis = maxCombo;
    this.SyncNumberThis = JudgeGrade.GetSyncNumber(maxCombo);
    UserMemory.AddPlayCount(this.SongId);
    if (this.SyncNumberThis > this.saveInfo.SyncNumber)
    {
        this.saveInfo.SyncNumber = this.SyncNumberThis;
        this.NewRecordThis = true;
    }
    else
    {
        this.NewRecordThis = (this.SongId == 0);
    }
    this.UploadScore();
}
```

### 结算场景切换时序

```
歌曲结束
  │
  ├─ SongInfoCore.UpdateSync(maxCombo) 被调用   ← 数据收集点
  │
  ├─ UI0X_SongPlayer.WaitingToNextScene(sceneName, isSongOver=true)
  │    ├─ songOver = true
  │    ├─ WaitForSeconds(4f)                    ← 4秒过渡
  │    ├─ 背景渐变动画 (~1.7s)
  │    ├─ WaitingClean(2f, true)                ← 2秒清理
  │    └─ SceneManager.LoadScene(sceneName)     ← 加载结算场景
  │
  ▼
SettlementController.Start() / NewSettlementController.Start()  ← UI 注入点
```

**时序余量**：UpdateSync 到结算场景 Start() 之间有 ~7.7 秒间隔，Socket 往返 (<100ms) 绰绰有余。

## Harmony Patch Design

### Patch 1: 实时延迟采集

```csharp
[HarmonyPatch(typeof(JudgeGrade), "GetJudgeGrade")]
[HarmonyPostfix]
static void JudgePostfix(long knockDistance)
{
    float delayMs = knockDistance / 10000.0f;
    // 1. 映射颜色等级 (复用现有阈值逻辑)
    // 2. 写入预分配环形缓冲 + 标记 UGUI Text 脏（脏标记驱动，非每帧重绘）
    // 3. 追加到本局 hits 缓冲区 (结算时发送)
}
```

### Patch 2: 新一局重置

```csharp
// 已确认：Reset 在每局开头被调用（清零所有 Total* + Console.Clear + "> SongStart!"）
[HarmonyPatch(typeof(JudgeGrade), "Reset")]
[HarmonyPostfix]
static void ResetPostfix()
{
    // 清空本局 hits 缓冲区
    // 重置 DelayOverlay 当前值
}
```

### Patch 3: 结算数据收集 + Socket 发送

```csharp
[HarmonyPatch(typeof(SongInfoCore), "UpdateSync")]
[HarmonyPostfix]
static void SettleDataPostfix(SongInfoCore __instance, int maxCombo)
{
    // 此时所有数据已就绪:
    //   __instance.SongId, MaxComboThis, SyncNumberThis, NewRecordThis
    //   JudgeGrade.TotalEx/Exact/Great/Right/Miss/Combo
    //   本局 hits 缓冲区 (所有 knockDistance)
    //
    // 1. 主线程：snapshot 本局数据引用（不做重序列化，<1ms）
    // 2. 主线程：启动后台 Task，立即返回（不阻塞主线程！）
    //    后台线程内：JSON 序列化 → TCP Connect → 发 → 收 → 反序列化
    //               → 线程安全写入静态缓存（Interlocked.Exchange / volatile）
    // 3. 结算 Start（约 7.7s 后，主线程）读缓存：
    //    就绪 → 渲染；未就绪（Python 卡 >7.7s 的极罕见情况）→ loading/空状态 + 轮询刷新
}
```

### Patch 4: 结算界面 UI 注入

```csharp
[HarmonyPatch(typeof(SettlementController), "Start")]
[HarmonyPatch(typeof(NewSettlementController), "Start")]
[HarmonyPostfix]
static void SettlementUIPostfix(MonoBehaviour __instance)
{
    // 检查是否已注入 (防重复)
    // 在结算场景的 GameObject 上创建 Canvas
    // 挂载 SettlePanel 组件
    // SettlePanel 读取缓存的 Socket 响应，渲染统计 + 图表
}
```

### Patch 健壮性约束（横切要求）

- **异常隔离**：每个 Postfix 方法体**整体 try-catch 包裹**，捕获后仅写 BepInEx Logger，**绝不向游戏抛异常**。Harmony 在某些配置下会把 patch 异常传播回原方法，对 `GetJudgeGrade` 这种判定核心方法，一次未捕获异常可能导致漏判/崩溃。插件 bug 不能拖垮游戏主循环
- **高频 patch 零/低分配**：`GetJudgeGrade` 每帧每音符调用一次，其 Postfix **禁止**每帧 `new List/数组/字符串`、字符串拼接、LINQ、`ToString` 格式化、写日志。单条模式下只需存"当前一个 float + 一个 Color"两个字段（值类型，无分配）；`SetText` 仅在每次打击时调一次（频率=音符频率，非每帧），拼一个短串如 `"3.2"` 允许一次 Gen0 短命分配，可接受。颜色映射用查表/分支返回 `Color` 结构体。目标：Postfix 单次 < 几微秒、每帧 0 GC alloc
- **线程安全**：后台 Socket 线程与主线程共享的缓存/队列，用 `Interlocked`/`volatile`/锁保护；主线程读、后台线程写的引用交换用 `Interlocked.Exchange`，避免半写状态
- **生命周期**：Overlay Canvas 与 DontDestroyOnLoad 对象在插件 `Awake` 创建一次；`OnApplicationQuit` 时关闭后台 Socket、落盘 config

## Data Flow

### 游玩中 (实时延迟显示)

```
JudgeGrade.GetJudgeGrade(knockDistance)  [主线程，高频]
    │
    ├─ [Harmony Postfix, try-catch 包裹, 每帧 0 分配]
    │   捕获 knockDistance → 算 ms → 查表得颜色
    │   存当前值 (float delayMs + Color color)  ← 两个值类型字段，无 GC
    │   标记 UGUI Text 脏（SetText 仅打击时调一次，非每帧）
    │
    └─ DelayOverlay (UGUI) 显示当前一条延迟（单行）
         文本/背景 RaycastTarget=false → 不拦游戏判定
```

**单条 vs N 条**：本期 overlay 仅显示**当前一次打击**的延迟值（单行），不做 N 条滚动列表。理由：单行更紧凑、更不挡视线、贴合"看当前这一击偏多少"的直觉；N 条历史滚动列表作为**非目标**留待未来可选变更。MISS 已确认会触发 `GetJudgeGrade`（传超大 knockDistance → 红），故单条模式下 MISS 时 overlay 正确闪红，无需超时淡出。

### 结算时 (数据分析 + 图表)

```
t=0s    SongInfoCore.UpdateSync(maxCombo)  [主线程]
        │
        ├─ [Postfix] snapshot: SongId, maxCombo, JudgeGrade 统计, hits[]
        └─ 启动后台 Task（主线程立即返回，不阻塞）
                 │
                 ▼  [后台线程]
                 TCP Connect → Send 原始数据 → Python
                                  │
                                  ├─ 存储原始数据
                                  ├─ 计算统计量
                                  ├─ 生成图表 (matplotlib → PNG)
                                  └─ Send ← {stats, PNG bytes}
                 收响应 → 反序列化 → 线程安全写入静态缓存

t=0~7.7s  过渡动画 (WaitingToNextScene 协程)  [主线程照常跑，无冻结]

t=7.7s  SettlementController.Start() / NewSettlementController.Start()  [主线程]
        │
        └─ [Postfix] 创建 UGUI Canvas
             └─ SettlePanel 读缓存：就绪→渲染统计+图表；未就绪→loading/空状态+轮询
```

## Legacy Code Reuse (from CSharp Code/)

旧版（dnSpy 改 IL + 外挂 Console）代码中有两块逻辑可直接迁移到新插件，一块整体弃用。

### 颜色映射表 — 直接复用 (JudgeGrade.cs)

单位换算：`knockDistance / 10000.0f = 毫秒`。

**符号语义（已实测确定）**：`knockDistance < 0` = 早击（early / fast），`knockDistance ≥ 0` = 晚击（late / slow）。依据：实测中只有晚击（slow）能落入 (150,250]ms 的 RIGHT 与 (250,280)ms 的 MISS；而用最快手速早击也只能到 GREAT [-150,-90)ms。故**正值=晚、负值=早**。

阈值与颜色（摘自旧 `GetJudgeGrade`，列名已绑定早/晚语义）：

| \|knockDistance\| | 延迟 (ms) | 早击 (<0) | 晚击 (≥0) |
| --- | --- | --- | --- |
| < 50000 | < 5 | Cyan | Cyan |
| < 100000 | < 10 | Yellow | DarkCyan |
| < 450000 | < 45 | DarkYellow | Blue |
| < 900000 | < 90 | Green | Magenta |
| < 1500000 | < 150 | DarkMagenta | DarkMagenta |
| ≥ 1500000 | ≥ 150 | Red | Red |

- 用途：UGUI 实时延迟文字颜色 + 结算散点图颜色编码
- 新插件应抽成共享方法，如 `Color GradeColor(long knockDistance)`，UGUI overlay 与图表共用

**非对称判定窗口（实测，影响图表呈现）**：

- 游戏原生判定等级窗口（ms；与上表颜色分档是**两套独立刻度**，颜色是连续延迟的细粒度可视化，等级是粗粒度判定）：早击侧有效下界约 -150（GREAT [-150,-90)），晚击侧上界约 +280（MISS (250,280)，RIGHT (150,250]）
- 推论 1（早击红档为死区）：早击侧 |delay| 物理上到不了 ≥150ms → 上表早击列的 Red 档（≥150ms）是**理论死区**，正常游玩不出现；早击有效颜色顶到 DarkMagenta（[90,150) 档）。散点图颜色图例可据此注明"早击侧不出红"
- 推论 2（分布天然非对称）：散点图/分布图 x 轴应标注 0 线，晚击尾更长；颜色图例用"早/晚"而非"±"
- 推论 3（avg 符号有物理含义）：本局平均延迟 avg 的符号现在可解读——avg>0 = 整体偏晚，avg<0 = 整体偏早。这是判定偏移校准洞察的数据基础；校准建议已纳入本变更（展示调整量窗口形态，见下"校准功能"，已决）
- 潜在方向 → 已细化为下方"校准功能"

**校准功能（判定偏移 offset 闭环建议，已决纳入）——边界与形态均已决**：

- 范围边界（已定）：游戏内 offset 精确到 ms，含**判定偏移**与**音画偏移**两项；本插件**只负责判定偏移**，不触碰音画偏移
- 符号约定（已确认）：offset 正负与游戏内一致——avg>0(偏晚)时 offset 往正调补偿，avg<0(偏早)时往负调，即"offset 调整方向 = avg 符号方向"，与游戏 offset 设置同向。实现上调整方向经单一符号常量集中控制，万一某游戏版本相反可一处翻转
- **插件不做收敛/不记轮次（已决）**：插件每局独立给调整量窗口 [avg−3, avg+3]，不记录"第几次玩/上次欠补多少"，不做多局综合、不做欠补决策。用户的"欠补"口诀（第一次小2~3 / 第二次小1~2 / 第三次±1）是**用户在窗口内自选调整量**的个人经验，非插件逻辑
- 经验表（验证窗口能容纳用户的欠补选择；斜杠记法 = 本局avg / 当前生效offset，"设定X" = 用户本轮自选调到的offset，调整量 = 设定 − 当前）：

  | 迭代 | 本局 avg | 插件窗口 [avg−3, avg+3] | 用户实选调整量 | 落窗口/容差 |
  | --- | --- | --- | --- | --- |
  | 1 | +7 | [+4, +10] | +5（欠补2） | ✓ |
  | 2 | -3 | [-6, 0] | -2（欠补1） | ✓ |
  | 3 | +1 | （容差内，不显示窗口） | 0（不调） | ✓ 容差 |

  三轮实选调整量均落在窗口（或容差）内，证明 ±3 半宽合理

- **形态（已决）**：仅展示，不写回、不跟踪跨局。每局结算显示：
  - 本局 avg delay = X ms（带符号）
  - 建议**调整量窗口**（注意：是"在当前 offset 上加该量"，**不是**"调整到某值"。原理：插件不读取游戏当前 offset（不逆向），物理上无法给目标值，故只给增量；用户自行把所选调整量加到游戏当前 offset 上）
  - 窗口 = 带符号区间 [avg−3, avg+3] ms，即"以 avg 为中心、±3ms 的调整量置信窗口"。显示时拆成 方向 + 幅度：方向 = sign(avg)（正=补偿偏晚、负=补偿偏早，与游戏 offset 同向）；幅度 = [max(0, |avg|−3), |avg|+3] ms。文案形如"向[正/负]方向调整 a~b ms"
  - 用户已确认区间为 [avg−3, avg+3]（先前 [avg−3, avg−2] 系笔误）；此窗口是置信/合理范围，**非**欠补算法——欠补多少由用户在窗口内凭经验自选（见上经验表）
- **不做跨局/迭代判定（已决）**：插件不记录"第几次玩/上次欠补多少"，不做多局综合。用户的三轮表仅为说明其在窗口内"欠补"手感的**经验参考**，非待实现的状态机
- **收敛容差（已决）**：|avg| ≤ 2ms 视为已校准，不显示调整窗口，改显示"已校准/无需调整"
  - 实现注记：当 2 < |avg| ≤ 3 时窗口跨0，幅度下界经 max(0, |avg|−3) 夹为0，文案显示"0~b ms（即也可不调整）"，语义清晰，无"建议调0ms"歧义
- **不自动写回（已决）**：不逆向游戏 offset 存储，不修改游戏配置；用户看建议后手动去游戏设置填

### 结算数据字段集 — 直接复用 (SongInfoCore.cs 旧 UpdateSync)

旧版向 Console 打印 `SID, SN(SyncNumberThis), MC(MaxComboThis), TC(JudgeGrade.TotalCombo)`。新协议 `SETTLE` 包应至少包含：

- `SongId`, `SyncNumberThis`, `MaxComboThis`, `NewRecordThis`
- `JudgeGrade` 统计：`TotalEx / TotalExact / TotalGreat / TotalRight / TotalMiss / TotalCombo`
- 本局 `hits[]`：每个元素为 `knockDistance`（用于散点图/分布图）

### 弃用项 — 整体不迁移 (Console.cs)

`AllocConsole` / `SetWindowPos` 置顶 / 重定向 `Console.Out` / 禁用 QuickEdit —— 全部弃用。新方案无任何控制台窗口，由 UGUI 完全替代（IMGUI 方案亦弃用）。

## Settlement Drawer UI Design

### 原结算界面布局（截图分析）

- 顶部居中：标题 `RESULT` + 难度键位（如 `4KHD`）
- 左半：`EXACT / GREAT / RIGHT / MISS` 四行判定统计（计数 + 百分比；EXACT 行含本次/历史双数字）
- 右上：`COMBO x/y` + 百分比
- 右中：`ALL COMBO!` 大图标
- 左下：`SYNC.RATE`
- 底部：`重来` / `继续` 两个按钮

**结论**：原界面已排满，硬塞图表会破坏布局 → 侧边抽屉方案正确。

### 抽屉（Drawer）交互

```
收起态:                          展开态:
┌──────────────────────┐        ┌──────────────────────┐
│   原结算界面          │        │   原结算界面   ┌─────┐│
│                  [▶] │  点击  │            │ 抽屉 ││
│   (耳朵 tab)         │ ────▶ │  图表分页   │ 面板 ││
│                      │        │  ◀ 1/3 ▶   │     ││
└──────────────────────┘        └──────────────────────┘
```

- 触发器：屏幕边缘一个"小耳朵" tab（建议右边缘中部，避开底部按钮），始终可见，视觉侵入低
- 展开：点击耳朵 → 抽屉面板从边缘滑入，覆盖在原结算界面之上
- 内容：`ScrollRect` + 分页，每页一张图表（`RawImage` ← PNG `Texture2D`）
- 分页控件：左右箭头 + `n / total` 页码，或顶部页签
- 收起：再次点击耳朵，或点击面板外区域 → 滑出

### UGUI 实现要点

- 独立 `Canvas`，`Screen Space - Overlay`，`sortingOrder` 高于原结算 Canvas（确保盖住原界面）
- 抽屉 `RectTransform` 锚定屏幕一侧；滑入/滑出用协程 lerp `anchoredPosition`（不引 DOTween 依赖，手写 lerp 即可）
- 耳朵 `Button` 锚定边缘，不随抽屉平移
- 图表 `RawImage`：`Texture2D.LoadImage(pngBytes)` 解码 Python 传来的 PNG
- 首页统计文本用 UGUI `Text` 自绘（avg / std / 各判定占比），其余页放 PNG 图表

### 交互增强（拖拽 / 吸附 / 缩放 / 默认宽度 / 动态分页 / 断开态）

**耳朵（ear）状态机**——同一控件按抽屉状态切换拖拽语义，避免手势冲突：

```
抽屉收起态:
  点击耳朵(位移<阈值)  → 展开抽屉
  拖动耳朵            → 移动耳朵位置(垂直) + 松手按屏幕中线吸附左/右边
抽屉展开态:
  点击耳朵(位移<阈值)  → 收起抽屉
  横向拖动耳朵        → 调整抽屉宽度(clamp [min,max])，松手持久化
```

- 三态手势判定（耳朵与 delay 框共用，解决"拖 vs 点 vs 犹豫"）：
  - **click** = 位移 ≤ `gesture.drag_distance_px` **且** hold ≤ `gesture.hold_ms` → 触发点击语义（展开/收起）
  - **drag** = 位移 > `gesture.drag_distance_px` → 触发拖拽语义（移位/改宽/移框）
  - **犹豫态（无操作）** = 位移 ≤ 阈值 **且** hold > `gesture.hold_ms` → 吞掉本次交互，不误触（处理"按住犹豫又松开"）
  - 实现：`OnPointerDown` 记起点+起始时刻；`OnDrag` 中位移超阈值置 `isDragging`；`OnPointerUp` 做最终三态判定
  - **进入拖动模式视觉反馈（已确认特性）**：协程监测 hold 时长，超过 `gesture.hold_ms` 且尚未触发 drag 时，对控件施加视觉反馈（耳朵/框体高亮描边或轻微缩放脉冲），明确告知"已进入拖动模式，松手即按拖拽处理"；`OnPointerUp` 后复位。避免用户"按住犹豫"时不知当前会被判成 click 还是 drag
  - 阈值默认 `drag_distance_px=5`、`hold_ms=300`，均写入 config 可调（正常点击 press 约 80~150ms，300ms 分界可过滤慢点击/犹豫）
- 吸附：耳朵拖拽 `OnPointerUp` 时比较当前 x 与屏幕中线，lerp 到目标边锚点
- 默认展开宽度 = 屏幕宽 50%（`drawer.width_ratio`）

**判定线与输入冲突实测**（决定 delay 框放置策略与穿透必要性）：

- 点击/触摸判定区仅在界面**下 15~25%**（归一化 y∈[0.75,0.85]），且**仅 3D 模式**生效
- **2D 模式仅键盘输入**（移动端移植 PC 的残留）→ 指针 Raycast 拦截对 2D 判定零影响
- 音符自顶部落下，注意力焦点通常**提前于**判定线（偏上）
- 推论：
  - delay 框默认位置放中上安全区（y≈0.3），避开下 15~25% 判定区，降低初始遮挡概率
  - 但用户可自由拖到任意位置（含判定区）→ 事件穿透（D2 `RaycastTarget=false`）**仍必要**，使"放哪都安全"不依赖用户自觉
  - 耳朵默认 y=0.5（中部），远离判定区，其 `RaycastTarget=true` 在 3D 模式也安全
  - 穿透方案对 2D/3D 两模式均安全（2D 无指针判定，3D 靠穿透），统一方案成立

**delay 文本框（游玩中）**：

- 整体可拖动（按住框体空白处/标题条），松手持久化归一化坐标
- 右下角 resize 手柄，拖动改宽高，**固定长宽比**（`aspect_locked`）
- 关键：框体文本区 `RaycastTarget=false`，仅手柄/标题条接收拖拽事件 → 不拦截游戏判定输入（见 D2 事件穿透）

**动态分页**：抽屉页数 = Python 响应 `charts` 数组长度，发几张图建几页，不固定页数

**断开态（Python 未连接）**：

- 不重复显示游戏已有的离线统计（游戏结算界面本身已含 EXACT/COMBO/SYNC.RATE 等）
- 抽屉无图表/统计可显示 → 耳朵点开显示空状态提示（"分析服务未连接"+ 端口/启动说明），不画本地统计
- 游玩 delay overlay 不受连接影响（纯本地渲染）

### 与 D4 的关系

抽屉空间大 + 分页 → 适合高清 PNG → 确认 D4 = A 为主 + C 混合。

## Socket Protocol (Draft)

```
帧格式: [4 bytes length (big-endian)] [payload]

游戏 → Python:
  {"cmd":"HIT","sid":123,"delay":32000,"combo":456}
  {"cmd":"SETTLE","sid":123,"maxcombo":800,"hits":[...]}

Python → 游戏:
  {"cmd":"RESULT","stats":{...},"charts":[{"name":"scatter","len":45230}]}
  [followed by raw PNG bytes for each chart]
```

## Deployment Layout

```
游戏目录/
├── MUSYNX.exe
├── winmm.dll                    ← BepInEx Doorstop
├── doorstop_config.ini          ← Doorstop 配置
├── BepInEx/
│   ├── core/                    ← BepInEx 框架
│   │   ├── BepInEx.dll
│   │   ├── 0Harmony.dll
│   │   └── ...
│   └── plugins/
│       └── MUSYNCDelay/
│           ├── MUSYNCDelay.dll  ← 你的插件
│           └── config.json      ← 插件配置 (JSON)
└── MUSYNX_Data/Managed/
    └── Assembly-CSharp.dll      ← 原版，不动
```

## Non-Goals (本期不做，留待未来可选变更)

- **N 条历史滚动列表**：游玩中 delay overlay 仅显示当前一条延迟值（单行），不做 N 条滚动/队列显示。若未来有需求（如观察连续偏移趋势），可作为独立变更加入
- **自动写回游戏 offset**：校准提示仅展示调整量窗口，不逆向/修改游戏配置文件
- **跨局收敛状态机**：插件不记录"第几次玩/上次欠补多少"，不做多局综合校准决策
- **音画偏移**：游戏内有两项 offset（判定偏移 + 音画偏移），本插件只负责判定偏移

## Python 端数据持久化（复用现有逻辑）

现有 Python 工具已通过 sqlite 实现完整的历史记录读写，新方案**复用**而非重写：

- 数据库文件：`musync_data/HitDelayHistory.db`
- Schema（当前版本 v4，见 `toolkit.py` `create_new_database`）：

  | 列 | 类型 | 说明 |
  | --- | --- | --- |
  | SongMapName | TEXT | 谱面名（PK 之一） |
  | RecordTime | TEXT | 记录时间（PK 之一） |
  | Diff | INTEGER | 难度 |
  | Mode | TEXT | 模式（4K/6K 等） |
  | Combo | TEXT | 如 "706/706" |
  | AvgDelay | REAL | 平均延迟 ms |
  | AllKeys | INTEGER | 总键数 |
  | AvgAcc | REAL | 平均准确率 |
  | HitMap | BLOB | 逐键延迟序列化数据 |

- 写入逻辑：`hit_delay.py` 的 `INSERT INTO HitDelayHistory`（结算时写入）
- 读取/分析逻辑：`all_hit_analyze.py`（全打击分析）、`hit_delay.py`（历史查看）
- Schema 迁移：`toolkit.py` 的 `check_database_version` + `update_database`（v0→v4 瀑布式）
- 新方案变更点：数据源从"Console 读取 + 剪贴板"改为"Socket 接收"，但**写入格式和 schema 不变**，确保新旧数据兼容、tkinter GUI 的历史查看功能无需改动

## Risks & Mitigations

| 风险 | 概率 | 影响 | 缓解 |
| ------ | ------ | ------ | ------ |
| 游戏方法签名变更 | 低 | Patch 失效 | Harmony 报错日志明确，改一行 attribute 即可 |
| 反作弊检测 Doorstop | 极低 | 无法启动 | MUSYNX 是单机音游，无在线反作弊 |
| UGUI Canvas 注入失败 / 缺 EventSystem | 低 | overlay/抽屉不显示 | 插件自建 Canvas + 兜底创建 EventSystem；日志告警 |
| overlay 拖拽拦截游戏判定输入 | 中(若用 IMGUI) | 误触/漏键 | 改用 UGUI + `RaycastTarget` 事件穿透，仅手柄接收事件 |
| Socket 连接失败 (Python 未启动) | 中 | 结算无图表 | TCP Connect refused 瞬时判定 → 抽屉空状态提示；游玩 delay 不受影响 |
| 拖拽/点击手势冲突 | 中 | 误展开/误移动 | 位移阈值区分点击与拖拽；耳朵按抽屉状态切换拖拽语义 |
| Mono → IL2CPP 迁移 | 极低(短期) | 方案失效 | 需完全重新设计，但无迁移迹象 |

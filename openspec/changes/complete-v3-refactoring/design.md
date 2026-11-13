## Context

MUSYNCSavDecode 3.0 重构已将数据层、工具层、分析层完成现代化改造，形成了清晰的无循环依赖层级架构（L0-L5）。但 UI 层（`main_window.py`）和部分中间模块仍保留旧版 C# 风格代码。当前新旧模块并存，风格割裂：

- 新模块：`class Foo:` / `snake_case` / `self._logger` / `dict[str, list]`
- 旧模块：`class Foo(object):` / `PascalCase` / `self.logger` / `List[...]`

项目为单人维护的桌面工具，无外部 API 消费者，Tkinter 回调绑定是方法重命名的唯一内部调用方。

## Goals / Non-Goals

**Goals:**

- 所有 `musync_save/` 模块达到一致的代码风格（命名、继承、Logger、类型注解、docstring）
- 移除所有被注释的旧代码、未使用导入、备用方法等死代码
- `main_window.py` 方法名全面 snake_case 化，Tkinter 回调绑定同步更新
- 补全 `MessageBoxEnum` 枚举
- 清理根目录空文件 `tmp.py`

**Non-Goals:**

- 不重构 UI 布局方式（保留 `place()` 硬编码坐标，不迁移到 grid/pack）
- 不重构 `uiautomation.py`（第三方内嵌库，保持原样）
- 不改变模块间的依赖层级和导入拓扑
- 不改变任何业务逻辑和数据处理流程
- 不实现 README 中的 UDP 通信替代方案（那是独立变更）
- 不添加单元测试（当前项目无测试框架配置）

## Decisions

### D1: 方法重命名策略——逐模块原地重命名

**决定**：对 `main_window.py` 中的 PascalCase 方法逐一重命名为 snake_case，同时更新所有 Tkinter `command=`、`bind()` 回调引用。

**替代方案**：
- 保留旧名 + 添加 snake_case 别名 → 增加代码量，违背清理目标
- 重写整个 `main_window.py` → 风险过大，可能引入 UI 回归

**理由**：原地重命名是最小变更路径，且项目无外部调用方，只需确保内部引用一致。

### D2: Logger 统一为私有属性 `self._logger`

**决定**：将 `save_data_manager.py` 和 `songname_manager.py` 中的 `self.logger` 改为 `self._logger`。

**理由**：Logger 是内部实现细节，不应作为公有 API 暴露。新模块已统一使用 `self._logger`，旧模块应对齐。

### D3: 类型注解统一为 Python 3.10+ 内置泛型

**决定**：移除 `from typing import List, Dict` 等导入，改用 `list[...]`、`dict[...]`、`X | None` 语法。

**理由**：新模块已采用此风格，且项目打包环境（PyInstaller + pythonnet）已确认支持 Python 3.10+。

### D4: 死代码直接删除，不保留注释

**决定**：被注释的旧代码（`NewStyle`/`OldStyle` 分支、`win32api` 导入、`_on_closing_bak` 等）直接删除。

**替代方案**：保留为历史参考 → 有 git 历史，无需在代码中保留。

**理由**：git 历史是唯一的"旧代码存档"，代码中不应有注释掉的死代码。

### D5: 变更顺序——自底向上

**决定**：按依赖层级从低到高执行：L0 模块（`save_data_manager`、`songname_manager`）→ L5 模块（`all_hit_analyze`、`musync_save_decode`）→ 顶层（`main_window`）→ 最后清理（`hit_delay` 死代码、`tmp.py`）。

**理由**：先稳定底层，再处理上层，避免重命名底层方法时上层引用断裂。

## Risks / Trade-offs

- **[Tkinter 回调断裂]** → 方法重命名后，若遗漏某处 `command=self.OldName` 绑定，运行时才会报 AttributeError。**缓解**：重命名后全文搜索旧方法名，确保零残留；逐函数重命名而非批量替换。
- **[`debug_launcher.py` 中的 `DEBUG()` 函数]** → 该函数可能直接调用 `main_window.py` 中的方法。**缓解**：重命名时同步检查 `debug_launcher.py` 和 `launcher.py` 的引用。
- **[docstring 修正遗漏]** → 旧类名引用可能散布在多处。**缓解**：全文搜索 `MusyncSavDecodeGUI`、`MUSYNCSavProcess`、`HitAnalyze` 等旧名。
- **[无测试覆盖]** → 项目无自动化测试，重构正确性依赖手动验证。**缓解**：重构后手动运行程序，验证主窗口、击打延迟、各分析图表功能正常。

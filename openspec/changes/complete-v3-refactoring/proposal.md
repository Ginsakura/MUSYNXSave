## Why

3.0 大版本重构已完成约 70-75%：数据层（`config_manager`、`map_info`、`save_data_manager`、`songname_manager`）、工具层（`toolkit`）、分析层（`hit_delay`、`difficulty_score_analyze`、`acc_sync_diff_analyze`、`sync_data_analyzer`）均已完成现代化改造。但 UI 层（`main_window.py`）仍是最大技术债务，`all_hit_analyze.py` 和 `musync_save_decode.py` 处于"逻辑已更新、外壳未翻新"的中间状态。新旧模块在命名风格、类继承、Logger 持有方式、类型注解等方面存在明显不一致，增加维护成本和认知负担。现在是完成剩余重构、统一代码风格的最佳时机。

## What Changes

- **统一代码风格**：所有模块采用一致的命名规范（snake_case 方法名）、类继承风格（移除 `(object)` 显式继承）、Logger 持有方式（统一为 `self._logger` 私有属性）、类型注解风格（使用 Python 3.10+ 内置泛型语法）
- **重构 `main_window.py`**：将 PascalCase 方法名改为 snake_case、清理被注释的旧代码（`NewStyle`/`OldStyle` 分支、`win32api`/`PIL` 导入）、修正 docstring 中的旧类名引用、移除永真条件 `if 1 :` 等残留
- **翻新 `all_hit_analyze.py`**：移除 `(object)` 继承、修正 docstring 旧类名、清理注释掉的 `super()` 调用
- **翻新 `musync_save_decode.py`**：移除 `(object)` 继承、修正 docstring 旧类名、清理被注释的反射代码
- **清理死代码**：移除 `hit_delay.py` 中的 `_on_closing_bak` 备用方法、`save_data_manager.py` 中未使用的 `List` 导入、根目录空文件 `tmp.py`
- **补全 TODO**：完成 `main_window.py` 中 `MessageBoxEnum` 枚举的补全

## Capabilities

### New Capabilities

- `code-style-consistency`: 定义项目统一的代码风格规范——命名约定、类继承、Logger 模式、类型注解、docstring 标准，作为所有模块的基准约束
- `ui-layer-refactor`: `main_window.py` 的全面现代化——方法重命名、死代码清理、UI 初始化逻辑整理、docstring 修正
- `legacy-module-cleanup`: `all_hit_analyze.py`、`musync_save_decode.py`、`hit_delay.py` 等模块的外壳翻新与死代码移除

### Modified Capabilities

（无现有 spec 需要修改）

## Impact

- **受影响代码**：`musync_save/` 下所有 Python 模块，重点是 `main_window.py`、`all_hit_analyze.py`、`musync_save_decode.py`、`hit_delay.py`、`save_data_manager.py`、`songname_manager.py`
- **API 影响**：`main_window.py` 中 PascalCase 方法重命名为 snake_case，若有外部调用方（如 `debug_launcher.py` 中的 `DEBUG()` 函数）需同步更新
- **依赖**：无新增依赖；可能移除对 `win32api`/`PIL` 的注释引用（实际已不使用）
- **风险**：方法重命名需确保 Tkinter 回调绑定（`command=`、`bind()`）全部同步更新，避免运行时 AttributeError

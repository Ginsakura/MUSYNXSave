## ADDED Requirements

### Requirement: main_window 方法名全面 snake_case 化
`main_window.py` 中所有 PascalCase 方法 SHALL 重命名为 snake_case。重命名映射至少包括：`RefreshSave` → `_refresh_save`、`DataLoad` → `_data_load`、`SelectPath` → `_select_path`、`DoubleClick` → `_on_double_click`、`SortClick` → `_on_sort_click`、`StartGame` → `_start_game`、`UpdateWindowInfo` → `_update_window_info`、`UpdateEnum` → `_update_enum`、`CheckGameRunning` → `_check_game_running`。

#### Scenario: 所有旧方法名不再存在
- **WHEN** 全文搜索 `main_window.py` 中的 PascalCase 方法定义（`def [A-Z]`）
- **THEN** 不存在任何 PascalCase 方法定义

#### Scenario: 外部调用方同步更新
- **WHEN** 检查 `debug_launcher.py` 和 `launcher.py` 中对 `main_window.py` 方法的引用
- **THEN** 所有引用均使用新的 snake_case 方法名

### Requirement: 移除 main_window 中的永真条件
`main_window.py` 中的 `if 1 :` 永真条件 SHALL 被移除，其内部代码块 SHALL 减少一级缩进。

#### Scenario: 永真条件被清除
- **WHEN** 检查 `main_window.py` 中的条件语句
- **THEN** 不存在 `if 1 :` 或等效的永真条件

### Requirement: 补全 MessageBoxEnum 枚举
`main_window.py` 中的 `MessageBoxEnum` SHALL 补全所有需要的枚举成员，移除 `# TODO: 补全` 注释。

#### Scenario: 枚举完整可用
- **WHEN** 检查 `MessageBoxEnum` 的定义
- **THEN** 枚举包含所有在代码中实际使用的成员，且不存在 TODO 注释

### Requirement: 清理 main_window 中的 SubWindow 残留
`main_window.py` 中已被注释的 `SubWindow` 调用和未使用的 `Toplevel` 导入 SHALL 被移除。若 `SubWindow` 类本身不再被任何代码引用，SHALL 一并移除。

#### Scenario: SubWindow 残留被清除
- **WHEN** 检查 `main_window.py` 中的 `SubWindow` 引用
- **THEN** 不存在被注释的 `SubWindow` 调用；若 `SubWindow` 类无活跃引用，则类定义也已移除

## ADDED Requirements

### Requirement: 类定义不使用显式 object 继承
所有 `musync_save/` 模块中的类定义 SHALL 使用 `class Foo:` 形式，MUST NOT 使用 `class Foo(object):` 形式。

#### Scenario: 旧式继承被移除
- **WHEN** 检查 `musync_save/` 下任意 Python 模块的类定义
- **THEN** 不存在 `(object)` 显式继承

### Requirement: 方法命名统一为 snake_case
所有 `musync_save/` 模块中的实例方法和类方法 SHALL 使用 snake_case 命名。MUST NOT 存在 PascalCase 方法名。

#### Scenario: main_window 方法重命名
- **WHEN** 检查 `main_window.py` 中的所有方法定义
- **THEN** 所有方法名均为 snake_case 格式（如 `_on_refresh`、`_data_load`、`_select_path`）

#### Scenario: Tkinter 回调绑定同步更新
- **WHEN** 方法从 PascalCase 重命名为 snake_case
- **THEN** 所有 `command=`、`bind()`、`after()` 等 Tkinter 回调引用 MUST 同步更新为新方法名

### Requirement: Logger 持有方式统一为私有属性
所有需要 Logger 的类 SHALL 使用 `self._logger` 作为 Logger 实例属性名。MUST NOT 使用 `self.logger`（公有属性）。

#### Scenario: save_data_manager Logger 统一
- **WHEN** 检查 `save_data_manager.py` 中的 Logger 引用
- **THEN** 所有 `self.logger` 已替换为 `self._logger`

#### Scenario: songname_manager Logger 统一
- **WHEN** 检查 `songname_manager.py` 中的 Logger 引用
- **THEN** 所有 `self.logger` 已替换为 `self._logger`

### Requirement: 类型注解使用 Python 3.10+ 内置泛型语法
所有 `musync_save/` 模块 SHALL 使用 `list[...]`、`dict[...]`、`tuple[...]`、`X | None` 等内置泛型语法。MUST NOT 从 `typing` 模块导入 `List`、`Dict`、`Tuple`、`Optional` 等已废弃的泛型别名。

#### Scenario: typing 泛型导入被移除
- **WHEN** 检查 `musync_save/` 下任意 Python 模块的导入语句
- **THEN** 不存在 `from typing import List, Dict, Tuple, Optional` 等导入（`Any`、`Final` 等非泛型类型除外）

### Requirement: Docstring 准确反映当前类名
所有类的 docstring SHALL 使用当前类名，MUST NOT 引用旧版类名（如 `MusyncSavDecodeGUI`、`MUSYNCSavProcess`、`HitAnalyze`）。

#### Scenario: 旧类名引用被清除
- **WHEN** 全文搜索 `musync_save/` 目录中的 `MusyncSavDecodeGUI`、`MUSYNCSavProcess`、`HitAnalyze` 字符串
- **THEN** 不存在任何匹配结果

### Requirement: 无被注释的死代码
所有 `musync_save/` 模块 MUST NOT 包含被注释掉的旧代码块（包括被注释的导入语句、被注释的逻辑分支、被注释的方法调用）。

#### Scenario: 注释代码被清除
- **WHEN** 检查 `main_window.py` 中的注释行
- **THEN** 不存在被注释的 `import win32api`、`NewStyle`/`OldStyle` 分支、`super()` 调用等旧代码
